"""Scraping de TOCs (Table of Contents) de edições OJS."""

from __future__ import annotations

import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "ojs-scrape/0.1.0"


def scrape_issue_toc(issue_url: str, timeout: float = 30.0) -> dict:
    """
    Faz scrape da TOC de uma edição OJS e retorna mapeamento de article_id → info.

    Args:
        issue_url: URL da edição (ex: https://periodicos.ufba.br/index.php/afroasia/issue/view/2785)

    Returns:
        dict com chaves:
        - articles: dict[article_id, dict] com título, seção, url
        - issue_number: str (se disponível)
        - sections: list[str]
    """
    resp = requests.get(issue_url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = {}
    sections = []

    # OJS 3: artigos estão em divs com classe 'obj_article_summary'
    for article_div in soup.find_all("div", class_="obj_article_summary"):
        # URL do artigo
        link = article_div.find("a", class_="title")
        if not link:
            continue

        href = link.get("href", "")
        title = link.get_text(strip=True)

        # Extrair article_id da URL
        id_match = re.search(r"/article/view/(\d+)", href)
        if not id_match:
            continue
        article_id = int(id_match.group(1))

        # Seção
        section_header = article_div.find_previous("h2", class_=re.compile(r"section"))
        section = section_header.get_text(strip=True) if section_header else ""
        if section and section not in sections:
            sections.append(section)

        # Autores
        authors_elem = article_div.find("div", class_="authors")
        authors = authors_elem.get_text(strip=True) if authors_elem else ""

        # Páginas
        pages_elem = article_div.find("div", class_="pages")
        pages = pages_elem.get_text(strip=True) if pages_elem else ""

        # Galley (PDF link)
        pdf_url = ""
        galley = article_div.find("a", class_=re.compile(r"galley"))
        if galley:
            pdf_url = galley.get("href", "")

        articles[article_id] = {
            "title": title,
            "url": href,
            "section": section,
            "authors": authors,
            "pages": pages,
            "pdf_url": pdf_url,
        }

    # Issue number (do título da página)
    issue_title = soup.find("h1")
    issue_number = issue_title.get_text(strip=True) if issue_title else ""

    return {
        "articles": articles,
        "issue_number": issue_number,
        "sections": sections,
    }


def find_issue_urls(
    base_url: str, archive_path: str = "issue/archive", timeout: float = 30.0
) -> list[dict]:
    """
    Faz scrape da página de arquivo do periódico e retorna lista de edições.

    Returns:
        list de dicts com chaves: url, number, year, volume
    """
    url = f"{base_url.rstrip('/')}/{archive_path}"
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    issues = []

    for issue_elem in soup.find_all("a", href=re.compile(r"/issue/view/\d+")):
        href = issue_elem.get("href", "")
        title = issue_elem.get_text(strip=True)
        if not href or "view" not in href:
            continue

        issues.append({
            "url": href if href.startswith("http") else f"{base_url.rstrip('/')}/{href.lstrip('/')}",
            "title": title,
        })

    return issues