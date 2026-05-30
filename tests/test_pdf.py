"""Testes de download de PDF sem rede real."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ojs_scrape.models import Article
from ojs_scrape.pdf import download_pdf, download_pdfs


class FakeResponse:
    def __init__(self, content: bytes, content_type: str, url: str) -> None:
        self.headers = {"Content-Type": content_type}
        self.content = content
        self.text = content.decode("utf-8", errors="replace")
        self.url = url

    def raise_for_status(self) -> None:
        return None


class FakePdfResponse:
    def __init__(self) -> None:
        self.headers = {"Content-Type": "application/pdf"}
        self.content = b"%PDF-1.4 fake"
        self.text = ""
        self.url = "https://example.org/pdf"

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.closed = False

    def get(self, url: str, **_kwargs: Any) -> FakePdfResponse:
        self.calls.append(url)
        return FakePdfResponse()

    def close(self) -> None:
        self.closed = True


class FakeRenbioSession:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(self, url: str, **_kwargs: Any) -> FakeResponse:
        self.calls.append(url)
        if url.endswith("/article/download/259/86"):
            return FakeResponse(b"%PDF-1.4 real", "application/pdf", url)
        html = b"""\
<!doctype html>
<a class="galley-link btn btn-primary pdf" href="/index.php/sbenbio/article/view/259/86">PDF</a>
"""
        return FakeResponse(html, "text/html; charset=utf-8", url)


class FakeRbsSession:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(self, url: str, **_kwargs: Any) -> FakeResponse:
        self.calls.append(url)
        if url.endswith("/article/download/499/pdf_53"):
            return FakeResponse(b"%PDF-1.4 rbs", "application/pdf", url)
        html = b"""\
<!doctype html>
<a href="https://example.org/reference.pdf">https://example.org/reference.pdf</a>
<a class="obj_galley_link pdf" href="/rbs/article/view/499/pdf_53">PDF</a>
"""
        return FakeResponse(html, "text/html; charset=utf-8", url)


def test_download_pdf_tries_received_url_first_and_sanitizes_filename(tmp_path: Path) -> None:
    session = FakeSession()

    result = download_pdf(
        "https://periodicos.ufba.br/index.php/afroasia/article/view/56443/34401",
        tmp_path,
        filename="../56443.pdf",
        session=session,  # type: ignore[arg-type]
    )

    assert result == tmp_path / "56443.pdf"
    assert result.read_bytes().startswith(b"%PDF")
    assert session.calls == [
        "https://periodicos.ufba.br/index.php/afroasia/article/view/56443/34401"
    ]
    assert not session.closed


def test_download_pdfs_skips_existing_article_pdf(tmp_path: Path) -> None:
    existing = tmp_path / "259.pdf"
    existing.write_bytes(b"%PDF already here")

    downloaded = download_pdfs(
        [Article(article_id=259, url="https://example.org/article/view/259")], tmp_path
    )

    assert downloaded == [existing]


def test_download_pdfs_limit_only_processes_sample(tmp_path: Path) -> None:
    articles = [
        Article(article_id=1, url="https://example.org/article/view/1"),
        Article(article_id=2, url="https://example.org/article/view/2"),
        Article(article_id=3, url="https://example.org/article/view/3"),
    ]
    for article in articles[:2]:
        (tmp_path / f"{article.article_id}.pdf").write_bytes(b"%PDF already here")

    downloaded = download_pdfs(articles, tmp_path, limit=2)

    assert downloaded == [tmp_path / "1.pdf", tmp_path / "2.pdf"]


def test_download_pdf_converts_ojs_galley_view_url_to_download(tmp_path: Path) -> None:
    session = FakeRenbioSession()

    result = download_pdf(
        "https://renbio.org.br/index.php/sbenbio/article/view/259",
        tmp_path,
        filename="259.pdf",
        session=session,  # type: ignore[arg-type]
    )

    assert result == tmp_path / "259.pdf"
    assert result.read_bytes().startswith(b"%PDF")
    assert "https://renbio.org.br/index.php/sbenbio/article/download/259/86" in session.calls


def test_download_pdf_converts_ojs_textual_galley_view_url_to_download(tmp_path: Path) -> None:
    session = FakeRbsSession()

    result = download_pdf(
        "https://rbs.sbsociologia.com.br/rbs/article/view/499",
        tmp_path,
        filename="499.pdf",
        session=session,  # type: ignore[arg-type]
    )

    assert result == tmp_path / "499.pdf"
    assert result.read_bytes().startswith(b"%PDF")
    assert "https://rbs.sbsociologia.com.br/rbs/article/download/499/pdf_53" in session.calls
