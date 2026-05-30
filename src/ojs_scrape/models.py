"""Modelos de dados para registros OAI-PMH e OJS."""

from __future__ import annotations

from dataclasses import dataclass, field

type JsonScalar = str | int | bool
type JsonValue = JsonScalar | list[str]
type ArticleDict = dict[str, JsonValue]


@dataclass(slots=True)
class OAISet:
    """Representa um set OAI-PMH."""

    spec: str = ""
    name: str = ""


@dataclass(slots=True)
class OJSJournal:
    """Representa um periódico OJS exposto via OAI-PMH."""

    base_url: str = ""
    repository_name: str = ""
    admin_email: str = ""
    earliest_datestamp: str = ""
    oai_base_url: str = ""
    sets: list[OAISet] = field(default_factory=list)


@dataclass(slots=True)
class Article:
    """Representa um artigo de periódico OJS."""

    # Identificação
    oai_identifier: str = ""
    article_id: int = 0
    url: str = ""
    datestamp: str = ""

    # Metadados Dublin Core
    title: str = ""
    subtitle: str = ""
    creators: list[str] = field(default_factory=list)
    subjects: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    publishers: list[str] = field(default_factory=list)
    contributors: list[str] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    identifiers: list[str] = field(default_factory=list)  # DOI, URLs
    types: list[str] = field(default_factory=list)
    formats: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    coverages: list[str] = field(default_factory=list)  # páginas, recorte espacial etc.
    rights: list[str] = field(default_factory=list)

    # Campos derivados
    doi: str = ""
    pages: str = ""
    resumo: str = ""
    palavras_chave: list[str] = field(default_factory=list)

    # Contexto OJS
    set_spec: str = ""
    set_specs: list[str] = field(default_factory=list)
    set_name: str = ""
    issue_id: int = 0
    issue_number: str = ""
    section: str = ""
    pdf_url: str = ""

    # Status
    deleted: bool = False

    def to_dict(self) -> ArticleDict:
        """Converte o artigo em dicionário plano para serialização."""
        return {
            "oai_identifier": self.oai_identifier,
            "article_id": self.article_id,
            "url": self.url,
            "datestamp": self.datestamp,
            "title": self.title,
            "subtitle": self.subtitle,
            "creators": self.creators,
            "subjects": self.subjects,
            "descriptions": self.descriptions,
            "publishers": self.publishers,
            "contributors": self.contributors,
            "dates": self.dates,
            "identifiers": self.identifiers,
            "types": self.types,
            "formats": self.formats,
            "sources": self.sources,
            "languages": self.languages,
            "coverages": self.coverages,
            "rights": self.rights,
            "doi": self.doi,
            "pages": self.pages,
            "resumo": self.resumo,
            "palavras_chave": self.palavras_chave,
            "set_spec": self.set_spec,
            "set_specs": self.set_specs,
            "set_name": self.set_name,
            "issue_id": self.issue_id,
            "issue_number": self.issue_number,
            "section": self.section,
            "pdf_url": self.pdf_url,
            "deleted": self.deleted,
        }
