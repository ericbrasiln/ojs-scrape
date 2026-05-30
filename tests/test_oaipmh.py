"""Testes para o cliente OAI-PMH."""

import pytest
from ojs_scrape.oaipmh import OAIPMHClient
from ojs_scrape.models import Article, OAISet


class TestOAIPMHClient:
    """Testes com endpoint real da Afro-Ásia."""

    BASE_URL = "https://periodicos.ufba.br/index.php/afroasia"

    @pytest.fixture
    def client(self):
        return OAIPMHClient(self.BASE_URL, delay=0.5)

    def test_identify(self, client):
        journal = client.identify()
        assert journal.repository_name == "Afro-Ásia"
        assert "periodicos.ufba.br" in journal.oai_base_url
        assert journal.earliest_datestamp

    def test_list_sets(self, client):
        sets = client.list_sets()
        assert len(sets) > 0
        specs = [s.spec for s in sets]
        assert any("ART" in s for s in specs)

    def test_list_records_with_date_filter(self, client):
        articles = list(client.list_records(from_date="2024-01-01", until_date="2024-12-31"))
        assert len(articles) > 0
        for a in articles:
            assert isinstance(a, Article)
            assert a.title  # deve ter título
            assert a.oai_identifier  # deve ter ID

    def test_list_records_pagination(self, client):
        """Testa se paginação via resumptionToken funciona."""
        # Coletar pelo menos 101 registros para forçar paginação
        count = 0
        for _ in client.list_records(from_date="2020-01-01"):
            count += 1
            if count >= 101:
                break
        assert count >= 101

    def test_get_record(self, client):
        identifier = "oai:ojs.periodicos.ufba.br:article/56443"
        article = client.get_record(identifier)
        assert article is not None
        assert article.article_id == 56443
        assert article.title

    def test_article_has_dublin_core_fields(self, client):
        """Verifica se os campos Dublin Core são preenchidos."""
        articles = list(client.list_records(from_date="2024-01-01", until_date="2024-12-31"))
        # Encontrar um artigo não-deletado com metadados completos
        article = next((a for a in articles if not a.deleted and a.creators), None)
        assert article is not None
        assert article.creators  # autores
        assert article.descriptions  # resumo
        assert article.subjects  # palavras-chave
        assert article.doi  # DOI


class TestModels:
    """Testes dos modelos de dados."""

    def test_article_to_dict(self):
        article = Article(
            oai_identifier="oai:test:article/123",
            article_id=123,
            title="Test Article",
            creators=["Silva, Maria"],
            doi="10.1234/test",
            resumo="Um resumo de teste",
        )
        d = article.to_dict()
        assert d["article_id"] == 123
        assert d["title"] == "Test Article"
        assert d["doi"] == "10.1234/test"


class TestFilters:
    """Testes dos filtros."""

    def test_filter_by_author(self):
        from ojs_scrape.filters import filter_by_author

        articles = [
            Article(title="A", creators=["Puntoni, Pedro"]),
            Article(title="B", creators=["Silva, Maria"]),
            Article(title="C", creators=["Puntoni, Pedro", "Outro, Autor"]),
        ]
        result = filter_by_author(articles, "Puntoni")
        assert len(result) == 2

    def test_filter_by_date_range(self):
        from ojs_scrape.filters import filter_by_date_range

        articles = [
            Article(title="A", dates=["2024-10-17T22:16:39Z"]),
            Article(title="B", dates=["2025-01-15"]),
            Article(title="C", dates=["2023-06-01"]),
        ]
        result = filter_by_date_range(articles, from_year=2024, until_year=2025)
        assert len(result) == 2