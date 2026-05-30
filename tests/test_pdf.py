"""Testes de download de PDF sem rede real."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ojs_scrape.pdf import download_pdf


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
