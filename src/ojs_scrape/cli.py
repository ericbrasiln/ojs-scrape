"""CLI para ojs-scrape."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from .exporters import to_bibtex, to_csv, to_json
from .filters import filter_by_author, filter_by_issue_ids
from .models import Article
from .oaipmh import OAIPMHClient
from .pdf import download_pdfs
from .toc import scrape_issue_toc

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Cria o parser de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="ojs-scrape",
        description="Coleta de dados estruturados de periódicos OJS via OAI-PMH",
    )
    parser.add_argument("url", help="URL base do periódico OJS ou endpoint /oai")
    parser.add_argument("--from", dest="from_date", help="Data inicial (YYYY-MM-DD ou YYYY)")
    parser.add_argument("--until", dest="until_date", help="Data final (YYYY-MM-DD ou YYYY)")
    parser.add_argument(
        "--set",
        dest="set_specs",
        nargs="+",
        help="Sets OAI-PMH para filtrar (ex: afroasia:ART afroasia:DOS)",
    )
    parser.add_argument("--issues", nargs="+", help="IDs das edições (issue view IDs do OJS)")
    parser.add_argument("--author", help="Filtrar por nome de autor (substring)")
    parser.add_argument("--pdf", action="store_true", help="Baixar PDFs dos artigos")
    parser.add_argument("--pdf-dir", default="pdfs", help="Diretório para PDFs (default: pdfs/)")
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["json", "csv", "bibtex"],
        default="json",
    )
    parser.add_argument("-o", "--output", help="Arquivo de saída")
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay mínimo entre requisições em segundos (default: 1.0)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Timeout de rede em segundos (default: 30.0)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Saída verbosa")
    parser.add_argument("-q", "--quiet", action="store_true", help="Saída mínima")
    return parser


def main(args: Sequence[str] | None = None) -> int:
    """Ponto de entrada da CLI."""
    parser = build_parser()
    opts = parser.parse_args(args)
    _configure_logging(verbose=opts.verbose, quiet=opts.quiet)

    from_date = _normalize_date(opts.from_date)
    until_date = _normalize_date(opts.until_date, is_until=True)

    with OAIPMHClient(opts.url, delay=opts.delay, timeout=opts.timeout) as client:
        journal = client.identify()
        logger.info("Repositório: %s", journal.repository_name)
        logger.info("OAI endpoint: %s", journal.oai_base_url)
        logger.info("Data mais antiga: %s", journal.earliest_datestamp)

        sets = client.list_sets()
        journal.sets = sets
        logger.info("Sets disponíveis: %s", len(sets))
        for oai_set in sets:
            logger.debug("  %s → %s", oai_set.spec, oai_set.name)

        articles = _collect_articles(
            client=client,
            from_date=from_date,
            until_date=until_date,
            set_specs=opts.set_specs,
        )

    if opts.issues:
        articles = _filter_by_issues(
            base_url=opts.url,
            issue_ids=opts.issues,
            articles=articles,
            timeout=opts.timeout,
        )

    if opts.author:
        articles = filter_by_author(articles, opts.author)
        logger.info("Após filtro por autor %r: %s artigos", opts.author, len(articles))

    if opts.pdf:
        downloaded = download_pdfs(articles, opts.pdf_dir, timeout=opts.timeout)
        logger.info("PDFs baixados: %s", len(downloaded))

    output_path = opts.output or f"ojs_scrape_output.{opts.output_format}"
    _export(articles, output_path, opts.output_format)
    logger.info("Saída: %s (%s artigos)", output_path, len(articles))
    return 0


def _collect_articles(
    client: OAIPMHClient,
    from_date: str | None,
    until_date: str | None,
    set_specs: Sequence[str] | None,
) -> list[Article]:
    if not set_specs:
        logger.info(
            "Coletando registros (from=%s, until=%s, set=todos)",
            from_date or "início",
            until_date or "agora",
        )
        articles = list(client.list_records(from_date=from_date, until_date=until_date))
        logger.info("Registros coletados: %s", len(articles))
        return articles

    articles_by_id: dict[str, Article] = {}
    for set_spec in set_specs:
        logger.info(
            "Coletando registros (from=%s, until=%s, set=%s)",
            from_date or "início",
            until_date or "agora",
            set_spec,
        )
        for article in client.list_records(
            from_date=from_date,
            until_date=until_date,
            set_spec=set_spec,
        ):
            articles_by_id[article.oai_identifier] = article

    articles = list(articles_by_id.values())
    logger.info("Registros coletados: %s", len(articles))
    return articles


def _filter_by_issues(
    base_url: str,
    issue_ids: Sequence[str],
    articles: Sequence[Article],
    timeout: float,
) -> list[Article]:
    issue_articles = {}
    base_url = base_url.rstrip("/").removesuffix("/oai")
    for issue_id in issue_ids:
        issue_url = f"{base_url}/issue/view/{issue_id}"
        logger.info("Scraping TOC da edição %s", issue_id)
        toc = scrape_issue_toc(issue_url, timeout=timeout)
        issue_articles.update(toc["articles"])

    filtered = filter_by_issue_ids(articles, issue_articles)
    logger.info("Após filtro por edições: %s artigos", len(filtered))
    return filtered


def _export(articles: Sequence[Article], output_path: str, output_format: str) -> None:
    if output_format == "json":
        to_json(articles, output_path)
    elif output_format == "csv":
        to_csv(articles, output_path)
    elif output_format == "bibtex":
        to_bibtex(articles, output_path)
    else:  # pragma: no cover — protegido por argparse choices
        raise ValueError(f"Formato de saída não suportado: {output_format}")


def _configure_logging(*, verbose: bool, quiet: bool) -> None:
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _normalize_date(date_str: str | None, *, is_until: bool = False) -> str | None:
    """Converte YYYY para YYYY-01-01 ou YYYY-12-31."""
    if date_str and len(date_str) == 4 and date_str.isdigit():
        return f"{date_str}-12-31" if is_until else f"{date_str}-01-01"
    return date_str


if __name__ == "__main__":
    sys.exit(main())
