"""Filtros para artigos coletados via OAI-PMH."""

from __future__ import annotations

import re

from .models import Article


def filter_by_author(articles: list[Article], query: str, case_sensitive: bool = False) -> list[Article]:
    """
    Filtra artigos por nome de autor (busca substring).

    Args:
        articles: lista de artigos
        query: nome ou parte do nome do autor
        case_sensitive: busca sensível a maiúsculas

    Returns:
        lista filtrada de artigos
    """
    if not case_sensitive:
        query = query.lower()

    results = []
    for article in articles:
        if article.deleted:
            continue
        for creator in article.creators:
            target = creator if case_sensitive else creator.lower()
            if query in target:
                results.append(article)
                break
    return results


def filter_by_issue_ids(articles: list[Article], issue_articles: dict[int, dict]) -> list[Article]:
    """
    Filtra artigos que pertencem a edições específicas.

    Args:
        articles: lista de artigos (do OAI-PMH)
        issue_articles: dict mapeando article_id → info (do scrape da TOC)

    Returns:
        lista de artigos que estão nas edições especificadas
    """
    return [a for a in articles if a.article_id in issue_articles]


def filter_by_set(articles: list[Article], set_specs: list[str]) -> list[Article]:
    """
    Filtra artigos por set OAI-PMH (seção).

    Args:
        articles: lista de artigos
        set_specs: lista de set specs (ex: ['afroasia:ART', 'afroasia:DOS'])

    Returns:
        lista filtrada
    """
    return [a for a in articles if a.set_spec in set_specs]


def filter_by_date_range(articles: list[Article], from_year: int | None = None, until_year: int | None = None) -> list[Article]:
    """
    Filtra artigos por ano de publicação.

    Nota: geralmente não necessário se o OAI-PMH já foi consultado com from/until.

    Args:
        articles: lista de artigos
        from_year: ano inicial
        until_year: ano final

    Returns:
        lista filtrada
    """
    results = []
    for article in articles:
        if article.deleted or not article.dates:
            continue
        # Extrair ano da primeira data
        year_match = re.search(r"(\d{4})", article.dates[0])
        if not year_match:
            continue
        year = int(year_match.group(1))
        if from_year and year < from_year:
            continue
        if until_year and year > until_year:
            continue
        results.append(article)
    return results