"""Exportação de artigos em formatos tabulares e bibliográficos."""

from __future__ import annotations

import csv
import json
import re
from collections.abc import Sequence
from io import StringIO
from pathlib import Path

from .models import Article

PathLike = str | Path

CSV_FIELDS = [
    "article_id",
    "title",
    "creators",
    "doi",
    "pages",
    "resumo",
    "palavras_chave",
    "dates",
    "set_spec",
    "section",
    "issue_number",
    "url",
    "pdf_url",
    "oai_identifier",
]


def to_json(articles: Sequence[Article], output: PathLike | None = None, indent: int = 2) -> str:
    """Exporta artigos como JSON."""
    data = [article.to_dict() for article in articles if not article.deleted]
    result = json.dumps(data, ensure_ascii=False, indent=indent)

    if output is not None:
        Path(output).write_text(result, encoding="utf-8")

    return result


def to_csv(articles: Sequence[Article], output: PathLike | None = None) -> str:
    """Exporta artigos como CSV."""
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()

    for article in articles:
        if article.deleted:
            continue
        row = article.to_dict()
        row["creators"] = "; ".join(article.creators)
        row["palavras_chave"] = "; ".join(article.palavras_chave)
        row["dates"] = "; ".join(article.dates)
        writer.writerow(row)

    result = buffer.getvalue()

    if output is not None:
        Path(output).write_text(result, encoding="utf-8")

    return result


def to_bibtex(articles: Sequence[Article], output: PathLike | None = None) -> str:
    """Exporta artigos como BibTeX."""
    entries: list[str] = []

    for index, article in enumerate((a for a in articles if not a.deleted), start=1):
        key = _bibtex_key(article, index)
        fields = _bibtex_fields(article)
        lines = [f"@article{{{key},"]
        lines.extend(f"  {name} = {{{_bibtex_escape(value)}}}," for name, value in fields)
        lines.append("}")
        entries.append("\n".join(lines))

    result = "\n\n".join(entries)

    if output is not None:
        Path(output).write_text(result, encoding="utf-8")

    return result


def _bibtex_fields(article: Article) -> list[tuple[str, str]]:
    fields = [("title", article.title)]
    if article.creators:
        fields.append(("author", " and ".join(article.creators)))
    if article.doi:
        fields.append(("doi", article.doi))
    if article.dates:
        fields.append(("year", article.dates[0][:4]))
    if article.pages:
        fields.append(("pages", article.pages))
    if article.url:
        fields.append(("url", article.url))
    if article.sources:
        fields.append(("journal", article.sources[0]))
    if article.palavras_chave:
        fields.append(("keywords", "; ".join(article.palavras_chave)))
    return [(name, value) for name, value in fields if value]


def _bibtex_key(article: Article, index: int) -> str:
    author_name = article.creators[0].split(",", maxsplit=1)[0] if article.creators else "unknown"
    year = article.dates[0][:4] if article.dates else "nodate"
    article_suffix = str(article.article_id or index)
    raw_key = f"{author_name}_{year}_{article_suffix}"
    return re.sub(r"[^A-Za-z0-9_:-]+", "_", raw_key).strip("_")


def _bibtex_escape(value: str) -> str:
    return (
        value.replace("\\", "\\textbackslash{}")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("&", "\\&")
    )
