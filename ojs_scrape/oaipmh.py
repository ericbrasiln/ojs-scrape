"""Cliente OAI-PMH para periódicos OJS."""

from __future__ import annotations

import logging
import re
import time
import xml.etree.ElementTree as ET
from typing import Generator

import requests

from .models import Article, OAISet, OJSJournal

logger = logging.getLogger(__name__)

# Namespaces OAI-PMH e Dublin Core
NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
}

# User-Agent para requests
USER_AGENT = "ojs-scrape/0.1.0 (https://github.com/ericbrasil/ojs-scrape)"


class OAIPMHError(Exception):
    """Erro retornado pelo servidor OAI-PMH."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"OAI-PMH error [{code}]: {message}")


class OAIPMHClient:
    """Cliente para o protocolo OAI-PMH."""

    def __init__(self, base_url: str, delay: float = 1.0, timeout: float = 30.0):
        """
        Args:
            base_url: URL base do periódico OJS (ex: https://periodicos.ufba.br/index.php/afroasia)
            delay: segundos entre requisições (default 1.0)
            timeout: timeout em segundos (default 30.0)
        """
        self.base_url = base_url.rstrip("/")
        self.oai_url = f"{self.base_url}/oai"
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._journal: OJSJournal | None = None

    def _request(self, params: dict) -> ET.Element:
        """Faz uma requisição OAI-PMH e retorna o elemento raiz do XML."""
        time.sleep(self.delay)
        resp = self.session.get(self.oai_url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        # Verificar erros OAI-PMH
        error_elem = root.find("oai:error", NS)
        if error_elem is not None:
            code = error_elem.get("code", "unknown")
            message = error_elem.text or ""
            raise OAIPMHError(code, message)

        return root

    def identify(self) -> OJSJournal:
        """Executa verb=Identify e retorna info do repositório."""
        if self._journal is not None:
            return self._journal

        root = self._request({"verb": "Identify"})
        identify = root.find("oai:Identify", NS)

        journal = OJSJournal(
            base_url=self.base_url,
            oai_base_url=self.oai_url,
            repository_name=_text(identify, "oai:repositoryName"),
            admin_email=_text(identify, "oai:adminEmail"),
            earliest_datestamp=_text(identify, "oai:earliestDatestamp"),
        )
        self._journal = journal
        return journal

    def list_sets(self) -> list[OAISet]:
        """Executa verb=ListSets e retorna todos os sets disponíveis."""
        sets = []
        params = {"verb": "ListSets"}

        while True:
            root = self._request(params)
            for set_elem in root.findall(".//oai:set", NS):
                spec = _text(set_elem, "oai:setSpec") or ""
                name = _text(set_elem, "oai:setName") or ""
                sets.append(OAISet(spec=spec, name=name))

            # Paginação via resumptionToken
            token = _resumption_token(root)
            if token is None:
                break
            params = {"verb": "ListSets", "resumptionToken": token}

        return sets

    def list_records(
        self,
        metadata_prefix: str = "oai_dc",
        from_date: str | None = None,
        until_date: str | None = None,
        set_spec: str | None = None,
    ) -> Generator[Article, None, None]:
        """
        Executa verb=ListRecords e gera Artigos via paginação.

        Args:
            metadata_prefix: formato de metadados (default: oai_dc)
            from_date: data inicial (formato YYYY-MM-DD)
            until_date: data final (formato YYYY-MM-DD)
            set_spec: set para filtrar (ex: 'afroasia:ART')
        """
        params: dict = {"verb": "ListRecords", "metadataPrefix": metadata_prefix}
        if from_date:
            params["from"] = from_date
        if until_date:
            params["until"] = until_date
        if set_spec:
            params["set"] = set_spec

        while True:
            root = self._request(params)

            for record in root.findall(".//oai:record", NS):
                article = self._parse_record(record)
                if article is not None:
                    yield article

            token = _resumption_token(root)
            if token is None:
                break
            params = {"verb": "ListRecords", "resumptionToken": token}

    def get_record(
        self, identifier: str, metadata_prefix: str = "oai_dc"
    ) -> Article | None:
        """Executa verb=GetRecord para um identificador específico."""
        root = self._request(
            {"verb": "GetRecord", "identifier": identifier, "metadataPrefix": metadata_prefix}
        )
        record = root.find(".//oai:record", NS)
        if record is not None:
            return self._parse_record(record)
        return None

    def list_identifiers(
        self,
        metadata_prefix: str = "oai_dc",
        from_date: str | None = None,
        until_date: str | None = None,
        set_spec: str | None = None,
    ) -> Generator[tuple[str, bool], None, None]:
        """
        Executa verb=ListIdentifiers (mais leve que ListRecords).

        Yields: (identifier, deleted) tuples
        """
        params: dict = {"verb": "ListIdentifiers", "metadataPrefix": metadata_prefix}
        if from_date:
            params["from"] = from_date
        if until_date:
            params["until"] = until_date
        if set_spec:
            params["set"] = set_spec

        while True:
            root = self._request(params)
            for header in root.findall(".//oai:header", NS):
                identifier = _text(header, "oai:identifier") or ""
                deleted = header.get("status") == "deleted"
                yield (identifier, deleted)

            token = _resumption_token(root)
            if token is None:
                break
            params = {"verb": "ListIdentifiers", "resumptionToken": token}

    def _parse_record(self, record: ET.Element) -> Article | None:
        """Converte um elemento <record> em Article."""
        header = record.find("oai:header", NS)
        if header is None:
            return None

        identifier = _text(header, "oai:identifier") or ""
        datestamp = _text(header, "oai:datestamp") or ""
        deleted = header.get("status") == "deleted"

        # Extrair article_id do identifier
        # Formato: oai:ojs.periodicos.ufba.br:article/56443
        article_id = 0
        id_match = re.search(r"article/(\d+)", identifier)
        if id_match:
            article_id = int(id_match.group(1))

        # Extrair set spec
        set_spec = ""
        set_elem = header.find("oai:setSpec", NS)
        if set_elem is not None and set_elem.text:
            set_spec = set_elem.text

        # Metadados Dublin Core
        dc = record.find(".//oai_dc:dc", NS)
        article = Article(
            oai_identifier=identifier,
            article_id=article_id,
            url=f"{self.base_url}/article/view/{article_id}" if article_id else "",
            deleted=deleted,
            set_spec=set_spec,
            dates=[datestamp] if datestamp else [],
        )

        if dc is not None and not deleted:
            article.title = _dc_text(dc, "dc:title")
            article.creators = _dc_texts(dc, "dc:creator")
            article.subjects = _dc_texts(dc, "dc:subject")
            article.descriptions = _dc_texts(dc, "dc:description")
            article.publishers = _dc_texts(dc, "dc:publisher")
            article.contributors = _dc_texts(dc, "dc:contributor")
            article.dates = _dc_texts(dc, "dc:date")
            article.identifiers = _dc_texts(dc, "dc:identifier")
            article.types = _dc_texts(dc, "dc:type")
            article.formats = _dc_texts(dc, "dc:format")
            article.sources = _dc_texts(dc, "dc:source")
            article.languages = _dc_texts(dc, "dc:language")
            article.coverages = _dc_texts(dc, "dc:coverage")
            article.rights = _dc_texts(dc, "dc:rights")

            # Campos derivados
            article.palavras_chave = article.subjects
            article.resumo = article.descriptions[0] if article.descriptions else ""

            # DOI: buscar nos identifiers
            for ident in article.identifiers:
                if ident.startswith("10."):
                    article.doi = ident
                    break

            # Páginas: buscar nas coverages
            for cov in article.coverages:
                if re.match(r"\d+(-\d+)?", cov):
                    article.pages = cov
                    break

        return article


# --- Funções auxiliares ---


def _text(parent: ET.Element | None, tag: str) -> str:
    """Extrai texto de um elemento filho."""
    if parent is None:
        return ""
    elem = parent.find(tag, NS)
    return (elem.text or "").strip() if elem is not None and elem.text else ""


def _dc_text(dc: ET.Element, tag: str) -> str:
    """Extrai o primeiro texto de um elemento Dublin Core."""
    elems = dc.findall(tag, NS)
    if elems and elems[0].text:
        return elems[0].text.strip()
    return ""


def _dc_texts(dc: ET.Element, tag: str) -> list[str]:
    """Extrai todos os textos de elementos Dublin Core com a tag dada."""
    return [e.text.strip() for e in dc.findall(tag, NS) if e.text]


def _resumption_token(root: ET.Element) -> str | None:
    """Extrai o resumptionToken se existir e não estiver vazio."""
    token_elem = root.find(".//oai:resumptionToken", NS)
    if token_elem is not None and token_elem.text and token_elem.text.strip():
        return token_elem.text.strip()
    return None