"""Testes de integração com endpoint real da Afro-Ásia."""

from __future__ import annotations

import pytest

from ojs_scrape.models import Article
from ojs_scrape.oaipmh import OAIPMHClient

BASE_URL = "https://periodicos.ufba.br/index.php/afroasia"


@pytest.fixture
def client() -> OAIPMHClient:
    return OAIPMHClient(BASE_URL, delay=0.2)


@pytest.mark.integration
def test_identify(client: OAIPMHClient) -> None:
    journal = client.identify()

    assert journal.repository_name == "Afro-Ásia"
    assert "periodicos.ufba.br" in journal.oai_base_url
    assert journal.earliest_datestamp


@pytest.mark.integration
def test_list_sets(client: OAIPMHClient) -> None:
    sets = client.list_sets()
    specs = [oai_set.spec for oai_set in sets]

    assert len(sets) > 0
    assert "afroasia:ART" in specs


@pytest.mark.integration
def test_list_records_with_date_filter(client: OAIPMHClient) -> None:
    articles = list(client.list_records(from_date="2024-01-01", until_date="2024-12-31"))

    assert len(articles) > 0
    assert all(isinstance(article, Article) for article in articles)
    assert all(article.title for article in articles if not article.deleted)


@pytest.mark.integration
def test_get_record(client: OAIPMHClient) -> None:
    article = client.get_record("oai:ojs.periodicos.ufba.br:article/56443")

    assert article is not None
    assert article.article_id == 56443
    assert article.title
    assert article.doi == "10.9771/aa.v0i69.56443"
    assert article.pages == "8-53"
