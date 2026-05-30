"""CLI para ojs-scrape."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .exporters import to_bibtex, to_csv, to_json
from .filters import filter_by_author, filter_by_date_range, filter_by_issue_ids, filter_by_set
from .oaipmh import OAIPMHClient
from .toc import find_issue_urls, scrape_issue_toc

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ojs-scrape",
        description="Coleta de dados estruturados de periódicos OJS via OAI-PMH",
    )
    parser.add_argument("url", help="URL base do periódico OJS")
    parser.add_argument("--from", dest="from_date", help="Data inicial (YYYY-MM-DD ou YYYY)")
    parser.add_argument("--until", dest="until_date", help="Data final (YYYY-MM-DD ou YYYY)")
    parser.add_argument("--set", dest="set_specs", nargs="+", help="Sets OAI-PMH para filtrar (ex: ART DOS)")
    parser.add_argument("--issues", nargs="+", help="IDs das edições (issue view IDs do OJS)")
    parser.add_argument("--author", help="Filtrar por nome de autor (substring)")
    parser.add_argument("--pdf", action="store_true", help="Baixar PDFs dos artigos")
    parser.add_argument("--pdf-dir", default="pdfs", help="Diretório para PDFs (default: pdfs/)")
    parser.add_argument("--format", dest="output_format", choices=["json", "csv", "bibtex"], default="json")
    parser.add_argument("-o", "--output", help="Arquivo de saída")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay entre requisições em segundos (default: 1.0)")
    parser.add_argument("--timeout", type=float, default=30.0, help="Timeout em segundos (default: 30.0)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Saída verbosa")
    parser.add_argument("-q", "--quiet", action="store_true", help="Saída mínima")
    return parser


def main(args: list[str] | None = None) -> int:
    parser = build_parser()
    opts = parser.parse_args(args)

    # Configurar logging
    if opts.quiet:
        level = logging.WARNING
    elif opts.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Normalizar datas (YYYY → YYYY-MM-DD)
    from_date = _normalize_date(opts.from_date)
    until_date = _normalize_date(opts.until_date, is_until=True)

    # Inicializar cliente OAI-PMH
    client = OAIPMHClient(opts.url, delay=opts.delay, timeout=opts.timeout)

    # Identify
    journal = client.identify()
    logger.info(f"Repositório: {journal.repository_name}")
    logger.info(f"OAI endpoint: {journal.oai_base_url}")
    logger.info(f"Data mais antiga: {journal.earliest_datestamp}")

    # Coletar sets
    sets = client.list_sets()
    journal.sets = sets
    logger.info(f"Sets disponíveis: {len(sets)}")
    for s in sets:
        logger.debug(f"  {s.spec} → {s.name}")

    # Coletar registros via OAI-PMH
    set_spec = opts.set_specs[0] if opts.set_specs else None
    logger.info(f"Coletando registros (from={from_date or 'início'}, until={until_date or 'agora'}, set={set_spec or 'todos'})")

    articles = list(client.list_records(
        from_date=from_date,
        until_date=until_date,
        set_spec=set_spec,
    ))
    logger.info(f"Registros coletados: {len(articles)}")

    # Filtrar por sets adicionais (se o usuário passou múltiplos)
    if opts.set_specs and len(opts.set_specs) > 1:
        # O OAI-PMH só suporta 1 set por requisição; filtrar os demais localmente
        articles = filter_by_set(articles, opts.set_specs)

    # Filtrar por edições (via scrape de TOC)
    if opts.issues:
        issue_articles = {}
        for issue_id in opts.issues:
            issue_url = f"{opts.url.rstrip('/')}/issue/view/{issue_id}"
            logger.info(f"Scraping TOC da edição {issue_id}...")
            toc = scrape_issue_toc(issue_url, timeout=opts.timeout)
            issue_articles.update(toc["articles"])
        articles = filter_by_issue_ids(articles, issue_articles)
        logger.info(f"Após filtro por edições: {len(articles)} artigos")

    # Filtrar por autor
    if opts.author:
        articles = filter_by_author(articles, opts.author)
        logger.info(f"Após filtro por autor '{opts.author}': {len(articles)} artigos")

    # Download de PDFs
    if opts.pdf:
        from .pdf import download_pdf
        for article in articles:
            if article.url:
                download_pdf(article.url, opts.pdf_dir, timeout=opts.timeout)

    # Exportar
    output_path = opts.output or f"ojs_scrape_output.{opts.output_format}"
    if opts.output_format == "json":
        to_json(articles, output_path)
    elif opts.output_format == "csv":
        to_csv(articles, output_path)
    elif opts.output_format == "bibtex":
        to_bibtex(articles, output_path)

    logger.info(f"Saída: {output_path} ({len(articles)} artigos)")
    return 0


def _normalize_date(date_str: str | None, is_until: bool = False) -> str | None:
    """Converte YYYY → YYYY-01-01 (from) ou YYYY-12-31 (until) para compatibilidade OAI-PMH."""
    if date_str and len(date_str) == 4 and date_str.isdigit():
        return f"{date_str}-12-31" if is_until else f"{date_str}-01-01"
    return date_str


if __name__ == "__main__":
    sys.exit(main())