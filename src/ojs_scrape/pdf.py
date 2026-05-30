"""Download de PDFs de artigos OJS."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from . import __version__
from .models import Article

logger = logging.getLogger(__name__)

USER_AGENT = f"ojs-scrape/{__version__}"


def download_pdf(
    article_url: str,
    output_dir: str | Path,
    filename: str | None = None,
    timeout: float = 60.0,
    session: requests.Session | None = None,
) -> Path | None:
    """Baixa o PDF de um artigo OJS.

    Tenta primeiro a URL padrão `/download`. Se falhar, procura um link de PDF na página do artigo.
    """
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    http = session or requests.Session()
    close_session = session is None
    try:
        pdf = _fetch_pdf(http, article_url, timeout)
        if pdf is None:
            pdf_url = _direct_download_url(article_url)
            pdf = _fetch_pdf(http, pdf_url, timeout)
        if pdf is None:
            fallback_url = find_pdf_url(article_url, timeout=timeout, session=http)
            pdf = _fetch_pdf(http, fallback_url, timeout) if fallback_url else None

        if pdf is None:
            logger.warning("Não foi possível baixar PDF: %s", article_url)
            return None

        safe_filename = _safe_filename(filename or f"{_article_id(article_url)}.pdf")
        filepath = destination / safe_filename
        filepath.write_bytes(pdf)
        logger.info("PDF baixado: %s", filepath)
        return filepath
    finally:
        if close_session:
            http.close()


def find_pdf_url(
    article_url: str,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> str:
    """Procura a URL de PDF em uma página de artigo OJS."""
    http = session or requests.Session()
    close_session = session is None
    try:
        response = http.get(article_url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = str(link.get("href", ""))
            text = link.get_text(" ", strip=True).casefold()
            if "download" in href.casefold() or "pdf" in text:
                return urljoin(article_url, href)
    except requests.RequestException as exc:
        logger.warning("Falha ao procurar PDF em %s: %s", article_url, exc)
    finally:
        if close_session:
            http.close()

    return ""


def download_pdfs(
    articles: Sequence[Article],
    output_dir: str | Path,
    timeout: float = 60.0,
) -> list[Path]:
    """Baixa PDFs de múltiplos artigos."""
    downloaded: list[Path] = []
    with requests.Session() as session:
        for article in articles:
            url = article.pdf_url or article.url
            if not url:
                continue
            result = download_pdf(
                url,
                output_dir,
                filename=f"{article.article_id}.pdf" if article.article_id else None,
                timeout=timeout,
                session=session,
            )
            if result is not None:
                downloaded.append(result)
    return downloaded


def _fetch_pdf(session: requests.Session, url: str, timeout: float) -> bytes | None:
    if not url:
        return None
    try:
        response = session.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.debug("Falha ao buscar PDF %s: %s", url, exc)
        return None

    content_type = response.headers.get("Content-Type", "").casefold()
    if "pdf" in content_type or response.content.startswith(b"%PDF"):
        return response.content
    return None


def _direct_download_url(article_url: str) -> str:
    return f"{article_url.rstrip('/')}/download"


def _article_id(article_url: str) -> str:
    return article_url.rstrip("/").split("/")[-1] or "article"


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    return name if name.endswith(".pdf") else f"{name}.pdf"
