"""Testes de exportadores e CLI."""

from __future__ import annotations

import json
from pathlib import Path

from ojs_scrape.cli import (
    _active_article_count,
    _export_outputs,
    _normalize_date,
    _resolve_output_paths,
    build_parser,
)
from ojs_scrape.exporters import to_bibtex, to_csv, to_json
from ojs_scrape.models import Article


def test_normalize_date_year_start_and_end() -> None:
    assert _normalize_date("2024") == "2024-01-01"
    assert _normalize_date("2025", is_until=True) == "2025-12-31"
    assert _normalize_date("2024-03-15") == "2024-03-15"
    assert _normalize_date(None) is None


def test_active_article_count_excludes_deleted_records() -> None:
    articles = [Article(article_id=1), Article(article_id=2, deleted=True)]

    assert _active_article_count(articles) == 1


def test_parser_accepts_pdf_limit_option() -> None:
    opts = build_parser().parse_args(["https://example.org/journal", "--pdf", "--pdf-limit", "3"])

    assert opts.pdf is True
    assert opts.pdf_limit == 3


def test_parser_accepts_multiple_output_formats() -> None:
    opts = build_parser().parse_args(
        ["https://example.org/journal", "--format", "json", "csv", "bibtex"]
    )

    assert opts.output_formats == ["json", "csv", "bibtex"]


def test_parser_defaults_to_json_output_format() -> None:
    opts = build_parser().parse_args(["https://example.org/journal"])

    assert opts.output_formats == ["json"]


def test_resolve_output_paths_uses_base_name_and_format_extensions(tmp_path: Path) -> None:
    paths = _resolve_output_paths(str(tmp_path / "coleta"), ["json", "csv", "bibtex"])

    assert paths == [
        str(tmp_path / "coleta.json"),
        str(tmp_path / "coleta.csv"),
        str(tmp_path / "coleta.bib"),
    ]


def test_resolve_output_paths_defaults_to_json_base_name() -> None:
    assert _resolve_output_paths(None, ["json"]) == ["ojs_scrape_output.json"]


def test_resolve_output_paths_replaces_known_extension() -> None:
    assert _resolve_output_paths("coleta.json", ["csv"]) == ["coleta.csv"]


def test_export_outputs_writes_all_requested_formats(tmp_path: Path) -> None:
    article = Article(article_id=1, title="Afro-Ásia", creators=["Brasil, Eric"])

    paths = _export_outputs([article], str(tmp_path / "coleta"), ["json", "csv", "bibtex"])

    assert paths == [
        str(tmp_path / "coleta.json"),
        str(tmp_path / "coleta.csv"),
        str(tmp_path / "coleta.bib"),
    ]
    assert json.loads((tmp_path / "coleta.json").read_text())[0]["title"] == "Afro-Ásia"
    assert "Afro-Ásia" in (tmp_path / "coleta.csv").read_text()
    assert "@article" in (tmp_path / "coleta.bib").read_text()


def test_to_json_serializes_unicode() -> None:
    article = Article(article_id=1, title="Afro-Ásia", creators=["Brasil, Eric"])

    output = to_json([article])
    data = json.loads(output)

    assert data[0]["title"] == "Afro-Ásia"


def test_to_csv_joins_list_fields() -> None:
    article = Article(
        article_id=1,
        title="A",
        creators=["Silva, Maria", "Santos, João"],
        palavras_chave=["história", "OJS"],
        dates=["2024-01-01"],
    )

    output = to_csv([article])

    assert "Silva, Maria; Santos, João" in output
    assert "história; OJS" in output


def test_to_bibtex_sanitizes_key_and_escapes_values() -> None:
    article = Article(
        article_id=56443,
        title="Zimbos & Libongos {teste}",
        creators=["Puntoni, Pedro"],
        doi="10.9771/aa.v0i69.56443",
        dates=["2024-10-21"],
        pages="8-53",
        url="https://periodicos.ufba.br/index.php/afroasia/article/view/56443",
        sources=["Afro-Ásia; No. 69 (2024); 8-53"],
    )

    output = to_bibtex([article])

    assert "@article{Puntoni_2024_56443," in output
    assert "Zimbos \\& Libongos \\{teste\\}" in output
    assert "pages = {8-53}" in output
