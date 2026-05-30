"""Download de PDFs de artigos OJS."""

from __future__ import annotations

import logging
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

USER_AGENT = "ojs-scrape/0.1.0"


def download_pdf(
    article_url: str,
    output_dir: str | Path,
    filename: str | None = None,
    timeout: float = 60.0,
) -> Path | None:
    """
    Baixa o PDF de um artigo OJS.

    Tenta primeiro a URL /download, depois faz scrape da página do artigo.

    Args:
        article_url: URL do artigo (ex: https://periodicos.ufba.br/index.php/afroasia/article/view/56443)
        output_dir: diretório de saída
        filename: nome do arquivo (se None, usa article_id)
        timeout: timeout em segundos

    Returns:
        caminho do arquivo baixado ou None se falhou
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Tentar URL de download direto
    pdf_url = f"{article_url.rstrip('/')}/download"

    try:
        resp = requests.get(
            pdf_url, headers={"User-Agent": USER_AGENT}, timeout=timeout, allow_redirects=True
        )
        if resp.status_code == 200 and "pdf" in resp.headers.get("Content-Type", "").lower():
            if filename is None:
                # Extrair ID da URL
                id_match = article_url.rstrip("/").split("/")[-1]
                filename = f"{id_match}.pdf"
            filepath = output_dir / filename
            filepath.write_bytes(resp.content)
            logger.info(f"Downloaded: {filepath}")
            return filepath
    except requests.RequestException as e:
        logger.warning(f"Direct download failed for {article_url}: {e}")

    # Fallback: scrape da página para encontrar link do PDF
    try:
        from bs4 import BeautifulSoup

        resp = requests.get(article_url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            pdf_link = soup.find("a", href=lambda h: h and "/article/view/" in h and "download" in h.lower())
            if pdf_link:
                href = pdf_link.get("href", "")
                if not href.startswith("http"):
                    base = article_url.split("/article/view/")[0]
                    href = f"{base}{href}"
                resp = requests.get(href, headers={"User-Agent": USER_AGENT}, timeout=timeout, allow_redirects=True)
                if resp.status_code == 200 and "pdf" in resp.headers.get("Content-Type", "").lower():
                    if filename is None:
                        filename = f"article_{article_url.rstrip('/').split('/')[-1]}.pdf"
                    filepath = output_dir / filename
                    filepath.write_bytes(resp.content)
                    logger.info(f"Downloaded (fallback): {filepath}")
                    return filepath
    except Exception as e:
        logger.warning(f"PDF fallback failed for {article_url}: {e}")

    logger.warning(f"Could not download PDF for {article_url}")
    return None


def download_pdfs(
    articles: list[dict],
    output_dir: str | Path,
    timeout: float = 60.0,
) -> list[Path]:
    """
    Baixa PDFs de múltiplos artigos.

    Args:
        articles: lista de dicts com chaves 'url' e 'article_id'
        output_dir: diretório de saída
        timeout: timeout por download

    Returns:
        lista de caminhos dos PDFs baixados
    """
    downloaded = []
    for article in articles:
        url = article.get("url", "")
        if not url:
            continue
        result = download_pdf(url, output_dir, timeout=timeout)
        if result:
            downloaded.append(result)
    return downloaded