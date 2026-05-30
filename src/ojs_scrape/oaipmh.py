"""Cliente OAI-PMH para periódicos OJS."""

from __future__ import annotations

import logging
import re
import time
import xml.etree.ElementTree as ET
from collections.abc import Iterator, Mapping

import requests

from . import __version__
from .models import Article, OAISet, OJSJournal

logger = logging.getLogger(__name__)

NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
}

USER_AGENT = f"ojs-scrape/{__version__} (+https://github.com/ericbrasil/ojs-scrape)"
DOI_RE = re.compile(r"10\.\d{4,9}/\S+", re.IGNORECASE)
PAGES_RE = re.compile(r"(?<!\d)(\d+\s*[-\u2013\u2014]\s*\d+)(?!\d)")
ARTICLE_ID_RE = re.compile(r"article/(\d+)")
INVALID_XML_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


class OAIPMHError(Exception):
    """Erro retornado pelo servidor OAI-PMH."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"OAI-PMH error [{code}]: {message}")


class OAIPMHParseError(Exception):
    """Erro ao interpretar XML retornado por um endpoint OAI-PMH."""


class OAIPMHClient:
    """Cliente para o protocolo OAI-PMH."""

    def __init__(self, base_url: str, delay: float = 1.0, timeout: float = 30.0):
        """Cria um cliente OAI-PMH.

        Args:
            base_url: URL base do periódico OJS ou URL direta do endpoint `/oai`.
            delay: intervalo mínimo entre requisições ao mesmo servidor.
            timeout: timeout de rede em segundos.
        """
        normalized = base_url.rstrip("/")
        if normalized.endswith("/oai"):
            self.oai_url = normalized
            self.base_url = normalized.removesuffix("/oai")
        else:
            self.base_url = normalized
            self.oai_url = f"{self.base_url}/oai"

        self.delay = max(delay, 0.0)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._journal: OJSJournal | None = None
        self._last_request_at = 0.0

    def __enter__(self) -> OAIPMHClient:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        """Fecha a sessão HTTP interna."""
        self.session.close()

    def _request(self, params: Mapping[str, str]) -> ET.Element:
        """Faz uma requisição OAI-PMH e retorna o elemento raiz do XML."""
        self._wait_rate_limit()
        response = self.session.get(self.oai_url, params=params, timeout=self.timeout)
        response.raise_for_status()
        self._last_request_at = time.monotonic()

        root = _parse_xml_content(response.content, response.url)

        error_elem = root.find("oai:error", NS)
        if error_elem is not None:
            code = error_elem.get("code", "unknown")
            message = (error_elem.text or "").strip()
            raise OAIPMHError(code, message)

        return root

    def _wait_rate_limit(self) -> None:
        if self.delay <= 0 or self._last_request_at == 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    def identify(self) -> OJSJournal:
        """Executa `Identify` e retorna informações do repositório."""
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
        """Executa `ListSets` e retorna todos os sets disponíveis.

        Alguns repositórios OAI-PMH não implementam sets. Nesses casos retorna lista vazia.
        """
        sets: list[OAISet] = []
        params = {"verb": "ListSets"}

        while True:
            try:
                root = self._request(params)
            except OAIPMHError as exc:
                if exc.code == "noSetHierarchy":
                    return []
                raise

            for set_elem in root.findall(".//oai:set", NS):
                sets.append(
                    OAISet(
                        spec=_text(set_elem, "oai:setSpec"),
                        name=_text(set_elem, "oai:setName"),
                    )
                )

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
    ) -> Iterator[Article]:
        """Executa `ListRecords` e gera artigos via paginação."""
        params = _record_params("ListRecords", metadata_prefix, from_date, until_date, set_spec)

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

    def get_record(self, identifier: str, metadata_prefix: str = "oai_dc") -> Article | None:
        """Executa `GetRecord` para um identificador específico."""
        root = self._request(
            {"verb": "GetRecord", "identifier": identifier, "metadataPrefix": metadata_prefix}
        )
        record = root.find(".//oai:record", NS)
        if record is None:
            return None
        return self._parse_record(record)

    def list_identifiers(
        self,
        metadata_prefix: str = "oai_dc",
        from_date: str | None = None,
        until_date: str | None = None,
        set_spec: str | None = None,
    ) -> Iterator[tuple[str, bool]]:
        """Executa `ListIdentifiers`, mais leve que `ListRecords`."""
        params = _record_params("ListIdentifiers", metadata_prefix, from_date, until_date, set_spec)

        while True:
            root = self._request(params)
            for header in root.findall(".//oai:header", NS):
                identifier = _text(header, "oai:identifier")
                deleted = header.get("status") == "deleted"
                yield (identifier, deleted)

            token = _resumption_token(root)
            if token is None:
                break
            params = {"verb": "ListIdentifiers", "resumptionToken": token}

    def _parse_record(self, record: ET.Element) -> Article | None:
        """Converte um elemento `<record>` em `Article`."""
        header = record.find("oai:header", NS)
        if header is None:
            return None

        identifier = _text(header, "oai:identifier")
        datestamp = _text(header, "oai:datestamp")
        deleted = header.get("status") == "deleted"
        article_id = _article_id_from_identifier(identifier)
        set_specs = [
            _clean_text(elem.text) for elem in header.findall("oai:setSpec", NS) if elem.text
        ]

        article = Article(
            oai_identifier=identifier,
            article_id=article_id,
            url=f"{self.base_url}/article/view/{article_id}" if article_id else "",
            datestamp=datestamp,
            deleted=deleted,
            set_spec=set_specs[0] if set_specs else "",
            set_specs=set_specs,
            dates=[datestamp] if datestamp else [],
        )

        dc = record.find(".//oai_dc:dc", NS)
        if dc is None or deleted:
            return article

        article.title = _dc_text(dc, "dc:title")
        article.creators = _dc_texts(dc, "dc:creator")
        article.subjects = _dc_texts(dc, "dc:subject")
        article.descriptions = _dc_texts(dc, "dc:description")
        article.publishers = _dc_texts(dc, "dc:publisher")
        article.contributors = _dc_texts(dc, "dc:contributor")
        article.dates = _dc_texts(dc, "dc:date") or article.dates
        article.identifiers = _dc_texts(dc, "dc:identifier")
        article.types = _dc_texts(dc, "dc:type")
        article.formats = _dc_texts(dc, "dc:format")
        article.sources = _dc_texts(dc, "dc:source")
        article.languages = _dc_texts(dc, "dc:language")
        article.coverages = _dc_texts(dc, "dc:coverage")
        article.rights = _dc_texts(dc, "dc:rights")

        article.palavras_chave = article.subjects
        article.resumo = article.descriptions[0] if article.descriptions else ""
        article.doi = _extract_doi(article.identifiers)
        article.pages = _extract_pages([*article.coverages, *article.sources])

        return article


def _record_params(
    verb: str,
    metadata_prefix: str,
    from_date: str | None,
    until_date: str | None,
    set_spec: str | None,
) -> dict[str, str]:
    params = {"verb": verb, "metadataPrefix": metadata_prefix}
    if from_date:
        params["from"] = from_date
    if until_date:
        params["until"] = until_date
    if set_spec:
        params["set"] = set_spec
    return params


def _parse_xml_content(content: bytes, source_url: str) -> ET.Element:
    """Interpreta XML OAI-PMH, removendo caracteres proibidos por XML 1.0.

    Alguns OJS antigos expõem caracteres de controle dentro de campos Dublin Core.
    O exemplo observado na História da Historiografia foi ``\\x02`` em
    ``dc:description``. Esses caracteres tornam o XML inválido, embora o resto da
    resposta seja aproveitável.
    """
    try:
        return ET.fromstring(content)
    except ET.ParseError as original_error:
        text = content.decode("utf-8", errors="replace")
        cleaned = INVALID_XML_CHAR_RE.sub("", text)
        if cleaned != text:
            try:
                logger.warning(
                    "Resposta OAI-PMH continha caracteres de controle XML inválidos; "
                    "eles foram removidos antes do parse: %s",
                    source_url,
                )
                return ET.fromstring(cleaned.encode("utf-8"))
            except ET.ParseError:
                pass

        msg = f"Resposta XML inválida de {source_url}: {original_error}"
        raise OAIPMHParseError(msg) from original_error


def _text(parent: ET.Element | None, tag: str) -> str:
    if parent is None:
        return ""
    elem = parent.find(tag, NS)
    return _clean_text(elem.text) if elem is not None else ""


def _dc_text(dc: ET.Element, tag: str) -> str:
    elem = dc.find(tag, NS)
    return _clean_text(elem.text) if elem is not None else ""


def _dc_texts(dc: ET.Element, tag: str) -> list[str]:
    return [_clean_text(elem.text) for elem in dc.findall(tag, NS) if _clean_text(elem.text)]


def _clean_text(text: str | None) -> str:
    return " ".join((text or "").split())


def _resumption_token(root: ET.Element) -> str | None:
    token_elem = root.find(".//oai:resumptionToken", NS)
    token = _clean_text(token_elem.text) if token_elem is not None else ""
    return token or None


def _article_id_from_identifier(identifier: str) -> int:
    match = ARTICLE_ID_RE.search(identifier)
    return int(match.group(1)) if match else 0


def _extract_doi(identifiers: list[str]) -> str:
    for raw_identifier in identifiers:
        value = raw_identifier.strip()
        value = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.IGNORECASE)
        match = DOI_RE.search(value)
        if match:
            return match.group(0).rstrip(".,;)")
    return ""


def _extract_pages(values: list[str]) -> str:
    for value in values:
        match = PAGES_RE.search(value)
        if match:
            return re.sub(
                r"\s+",
                "",
                match.group(1).replace("\u2013", "-").replace("\u2014", "-"),
            )
    return ""
