"""Filtros para artigos coletados via OAI-PMH."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from .models import Article

IssueArticleMetadata = Mapping[str, object]


def filter_by_author(
    articles: Sequence[Article],
    query: str,
    *,
    case_sensitive: bool = False,
) -> list[Article]:
    """Filtra artigos por nome de autor usando busca por substring."""
    needle = query if case_sensitive else query.casefold()

    results: list[Article] = []
    for article in articles:
        if article.deleted:
            continue
        for creator in article.creators:
            target = creator if case_sensitive else creator.casefold()
            if needle in target:
                results.append(article)
                break
    return results


def filter_by_issue_ids(
    articles: Sequence[Article],
    issue_articles: Mapping[int, IssueArticleMetadata],
) -> list[Article]:
    """Filtra e enriquece artigos que pertencem às edições informadas."""
    results: list[Article] = []
    for article in articles:
        metadata = issue_articles.get(article.article_id)
        if metadata is None:
            continue
        _enrich_article_from_issue_metadata(article, metadata)
        results.append(article)
    return results


def filter_by_set(articles: Sequence[Article], set_specs: Sequence[str]) -> list[Article]:
    """Filtra artigos por set OAI-PMH."""
    wanted = set(set_specs)
    return [
        article for article in articles if set(article.set_specs or [article.set_spec]) & wanted
    ]


def filter_by_date_range(
    articles: Sequence[Article],
    from_year: int | None = None,
    until_year: int | None = None,
) -> list[Article]:
    """Filtra artigos por ano de publicação."""
    results: list[Article] = []
    for article in articles:
        if article.deleted or not article.dates:
            continue
        year = _year_from_date(article.dates[0])
        if year is None:
            continue
        if from_year is not None and year < from_year:
            continue
        if until_year is not None and year > until_year:
            continue
        results.append(article)
    return results


def _year_from_date(value: str) -> int | None:
    match = re.search(r"(\d{4})", value)
    return int(match.group(1)) if match else None


def _enrich_article_from_issue_metadata(article: Article, metadata: IssueArticleMetadata) -> None:
    article.section = str(metadata.get("section", article.section or ""))
    article.issue_number = str(metadata.get("issue_number", article.issue_number or ""))
    article.pdf_url = str(metadata.get("pdf_url", article.pdf_url or ""))

    issue_id = metadata.get("issue_id")
    if isinstance(issue_id, int):
        article.issue_id = issue_id

    pages = str(metadata.get("pages", ""))
    if pages and not article.pages:
        article.pages = pages
