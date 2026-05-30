"""Testes de exportadores e CLI."""

from __future__ import annotations

import json

from ojs_scrape.cli import _active_article_count, _normalize_date
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
