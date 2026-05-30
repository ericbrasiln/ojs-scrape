"""Exportação de dados em diferentes formatos."""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path

from .models import Article


def to_json(articles: list[Article], output: str | Path | None = None, indent: int = 2) -> str:
    """Exporta artigos como JSON.

    Args:
        articles: lista de artigos
        output: caminho do arquivo de saída (se None, retorna string)
        indent: indentação JSON

    Returns:
        string JSON
    """
    data = [a.to_dict() for a in articles if not a.deleted]
    result = json.dumps(data, ensure_ascii=False, indent=indent)

    if output:
        Path(output).write_text(result, encoding="utf-8")

    return result


def to_csv(articles: list[Article], output: str | Path | None = None) -> str:
    """Exporta artigos como CSV.

    Args:
        articles: lista de artigos
        output: caminho do arquivo de saída

    Returns:
        string CSV
    """
    fields = [
        "article_id", "title", "creators", "doi", "pages",
        "resumo", "palavras_chave", "dates", "set_spec", "section",
        "issue_number", "url", "oai_identifier",
    ]

    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()

    for a in articles:
        if a.deleted:
            continue
        row = a.to_dict()
        # Listas → string separada por ;
        row["creators"] = "; ".join(row.get("creators", []))
        row["palavras_chave"] = "; ".join(row.get("palavras_chave", []))
        row["dates"] = "; ".join(row.get("dates", []))
        writer.writerow(row)

    result = buf.getvalue()

    if output:
        Path(output).write_text(result, encoding="utf-8")

    return result


def to_bibtex(articles: list[Article], output: str | Path | None = None) -> str:
    """Exporta artigos como BibTeX.

    Args:
        articles: lista de artigos
        output: caminho do arquivo de saída

    Returns:
        string BibTeX
    """
    entries = []

    for a in articles:
        if a.deleted:
            continue

        # Chave: primeiro_author_ano
        author_name = a.creators[0].split(",")[0].strip() if a.creators else "unknown"
        year = a.dates[0][:4] if a.dates else "nodate"
        key = f"{author_name}_{year}"

        lines = [f"@article{{{key},"]
        lines.append(f'  title = {{{a.title}}},')
        if a.creators:
            authors_bibtex = " and ".join(a.creators)
            lines.append(f'  author = {{{authors_bibtex}}},')
        if a.doi:
            lines.append(f'  doi = {{{a.doi}}},')
        if a.dates:
            lines.append(f'  year = {{{a.dates[0][:4]}}},')
        if a.pages:
            lines.append(f'  pages = {{{a.pages}}},')
        if a.url:
            lines.append(f'  url = {{{a.url}}},')
        if a.sources:
            lines.append(f'  journal = {{{a.sources[0]}}},')
        if a.palavras_chave:
            lines.append(f'  keywords = {{{"; ".join(a.palavras_chave)}}},')
        lines.append("}")

        entries.append("\n".join(lines))

    result = "\n\n".join(entries)

    if output:
        Path(output).write_text(result, encoding="utf-8")

    return result