"""Testes dos modelos e filtros."""

from __future__ import annotations

from ojs_scrape.filters import (
    filter_by_author,
    filter_by_date_range,
    filter_by_issue_ids,
    filter_by_publication_date_range,
)
from ojs_scrape.models import Article, OAISet, OJSJournal


def test_article_to_dict_includes_derived_and_ojs_fields() -> None:
    article = Article(
        oai_identifier="oai:test:article/123",
        article_id=123,
        title="Test Article",
        creators=["Silva, Maria"],
        doi="10.1234/test",
        resumo="Um resumo de teste",
        set_specs=["journal:ART"],
        pdf_url="https://example.org/pdf",
    )

    result = article.to_dict()

    assert result["article_id"] == 123
    assert result["title"] == "Test Article"
    assert result["doi"] == "10.1234/test"
    assert result["set_specs"] == ["journal:ART"]
    assert result["pdf_url"] == "https://example.org/pdf"


def test_ojs_journal_holds_sets() -> None:
    journal = OJSJournal(repository_name="Revista", sets=[OAISet(spec="rev:ART", name="Artigos")])

    assert journal.sets[0].spec == "rev:ART"


def test_filter_by_author_uses_casefold() -> None:
    articles = [
        Article(title="A", creators=["Puntoni, Pedro"]),
        Article(title="B", creators=["Silva, Maria"]),
        Article(title="C", creators=["PUNTONI, Pedro", "Outro, Autor"]),
    ]

    result = filter_by_author(articles, "puntoni")

    assert [article.title for article in result] == ["A", "C"]


def test_filter_by_date_range() -> None:
    articles = [
        Article(title="A", dates=["2024-10-17T22:16:39Z"]),
        Article(title="B", dates=["2025-01-15"]),
        Article(title="C", dates=["2023-06-01"]),
    ]

    result = filter_by_date_range(articles, from_year=2024, until_year=2025)

    assert [article.title for article in result] == ["A", "B"]


def test_filter_by_publication_date_range_uses_dc_date_not_oai_datestamp() -> None:
    articles = [
        Article(title="old updated record", datestamp="2024-01-01", dates=["2009-05-29"]),
        Article(title="inside range", datestamp="2024-01-01", dates=["2021-06-15"]),
        Article(title="after range", datestamp="2026-01-01", dates=["2026-06-01"]),
        Article(title="deleted", datestamp="2024-01-01", dates=["2021-01-01"], deleted=True),
    ]

    result = filter_by_publication_date_range(
        articles,
        from_date="2020-01-01",
        until_date="2026-05-30",
    )

    assert [article.title for article in result] == ["inside range"]


def test_filter_by_issue_ids_enriches_articles() -> None:
    article = Article(article_id=10, title="A")
    issue_articles = {
        10: {
            "section": "Dossiê",
            "pages": "8-53",
            "issue_id": 2785,
            "issue_number": "n. 69 (2024)",
            "pdf_url": "https://example.org/download",
        }
    }

    result = filter_by_issue_ids([article], issue_articles)

    assert result == [article]
    assert article.section == "Dossiê"
    assert article.pages == "8-53"
    assert article.issue_id == 2785
    assert article.pdf_url == "https://example.org/download"
