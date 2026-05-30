"""Modelos de dados para registros OAI-PMH."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Article:
    """Representa um artigo de periódico OJS."""

    # Identificação
    oai_identifier: str = ""
    article_id: int = 0
    url: str = ""

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
    coverages: list[str] = field(default_factory=list)  # páginas
    rights: list[str] = field(default_factory=list)

    # Campos derivados (preenchidos pelo parser)
    doi: str = ""
    pages: str = ""
    resumo: str = ""
    palavras_chave: list[str] = field(default_factory=list)

    # Contexto OJS
    set_spec: str = ""
    set_name: str = ""
    issue_id: int = 0
    issue_number: str = ""
    section: str = ""

    # Status
    deleted: bool = False

    def to_dict(self) -> dict:
        """Converte o artigo em dicionário plano para serialização."""
        return {
            "oai_identifier": self.oai_identifier,
            "article_id": self.article_id,
            "url": self.url,
            "title": self.title,
            "subtitle": self.subtitle,
            "creators": self.creators,
            "subjects": self.subjects,
            "descriptions": self.descriptions,
            "doi": self.doi,
            "pages": self.pages,
            "resumo": self.resumo,
            "palavras_chave": self.palavras_chave,
            "publishers": self.publishers,
            "dates": self.dates,
            "languages": self.languages,
            "coverages": self.coverages,
            "types": self.types,
            "formats": self.formats,
            "identifiers": self.identifiers,
            "set_spec": self.set_spec,
            "section": self.section,
            "issue_id": self.issue_id,
            "issue_number": self.issue_number,
            "deleted": self.deleted,
        }


@dataclass
class OJSJournal:
    """Representa um periódico OJS."""

    base_url: str = ""
    repository_name: str = ""
    admin_email: str = ""
    earliest_datestamp: str = ""
    oai_base_url: str = ""
    sets: list[OAISet] = field(default_factory=list)


@dataclass
class OAISet:
    """Representa um set OAI-PMH."""

    spec: str = ""
    name: str = ""