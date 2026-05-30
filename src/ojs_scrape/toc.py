"""Scraping leve de TOCs (Table of Contents) de edições OJS."""

from __future__ import annotations

import logging
import re
from typing import TypedDict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from . import __version__

logger = logging.getLogger(__name__)

USER_AGENT = f"ojs-scrape/{__version__}"
ISSUE_RE = re.compile(r"/issue/view/(\d+)")
ARTICLE_RE = re.compile(r"/article/view/(\d+)")
SECTION_CLASS_RE = re.compile(r"section")
GALLEY_CLASS_RE = re.compile(r"(galley|pdf|obj_galley_link)")


class TocArticle(TypedDict):
    """Metadados mínimos de um artigo extraídos da TOC."""

    title: str
    url: str
    section: str
    authors: str
    pages: str
    pdf_url: str
    issue_id: int
    issue_number: str


class IssueToc(TypedDict):
    """Resultado do scrape da TOC de uma edição OJS."""

    articles: dict[int, TocArticle]
    issue_id: int
    issue_number: str
    sections: list[str]


class IssueInfo(TypedDict):
    """Informação básica de uma edição na página de arquivo."""

    issue_id: int
    url: str
    title: str


def scrape_issue_toc(issue_url: str, timeout: float = 30.0) -> IssueToc:
    """Faz scrape da TOC de uma edição OJS e retorna article_id → metadados."""
    response = requests.get(issue_url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return _parse_issue_toc_html(response.text, issue_url)


def find_issue_urls(
    base_url: str,
    archive_path: str = "issue/archive",
    timeout: float = 30.0,
) -> list[IssueInfo]:
    """Faz scrape da página de arquivo do periódico e retorna edições disponíveis."""
    archive_url = urljoin(f"{base_url.rstrip('/')}/", archive_path)
    response = requests.get(archive_url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    issues_by_id: dict[int, IssueInfo] = {}

    for issue_elem in soup.find_all("a", href=ISSUE_RE):
        href = str(issue_elem.get("href", ""))
        issue_id = _issue_id_from_url(href)
        if issue_id == 0:
            continue
        issues_by_id[issue_id] = {
            "issue_id": issue_id,
            "url": urljoin(archive_url, href),
            "title": _node_text(issue_elem),
        }

    return list(issues_by_id.values())


def _parse_issue_toc_html(html: str, issue_url: str) -> IssueToc:
    soup = BeautifulSoup(html, "html.parser")
    articles: dict[int, TocArticle] = {}
    sections: list[str] = []
    issue_id = _issue_id_from_url(issue_url)
    issue_number = _node_text(soup.find("h1"))

    for article_div in soup.find_all("div", class_="obj_article_summary"):
        link = article_div.select_one("h3.title a, a.title, a[id^='article-']")
        if not isinstance(link, Tag):
            continue

        href = str(link.get("href", ""))
        article_id = _article_id_from_url(href)
        if article_id == 0:
            continue

        section_header = _find_section_header(article_div)
        section = _node_text(section_header)
        if section and section not in sections:
            sections.append(section)

        articles[article_id] = {
            "title": _node_text(link),
            "url": urljoin(issue_url, href),
            "section": section,
            "authors": _node_text(article_div.find("div", class_="authors")),
            "pages": _node_text(article_div.find("div", class_="pages")),
            "pdf_url": _pdf_url(article_div, issue_url),
            "issue_id": issue_id,
            "issue_number": issue_number,
        }

    return {
        "articles": articles,
        "issue_id": issue_id,
        "issue_number": issue_number,
        "sections": sections,
    }


def _find_section_header(article_div: Tag) -> Tag | None:
    section_header = article_div.find_previous("h2", class_=SECTION_CLASS_RE)
    if isinstance(section_header, Tag):
        return section_header

    section_header = article_div.find_previous("h2")
    return section_header if isinstance(section_header, Tag) else None


def _pdf_url(article_div: Tag, issue_url: str) -> str:
    galley = article_div.find("a", class_=GALLEY_CLASS_RE)
    if not isinstance(galley, Tag):
        return ""
    return urljoin(issue_url, str(galley.get("href", "")))


def _node_text(node: object | None) -> str:
    if isinstance(node, Tag):
        return " ".join(node.get_text(" ", strip=True).split())
    return ""


def _issue_id_from_url(url: str) -> int:
    match = ISSUE_RE.search(url)
    return int(match.group(1)) if match else 0


def _article_id_from_url(url: str) -> int:
    match = ARTICLE_RE.search(url)
    return int(match.group(1)) if match else 0
