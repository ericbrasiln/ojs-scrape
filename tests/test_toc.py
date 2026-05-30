"""Testes do parser de TOC OJS."""

from __future__ import annotations

from ojs_scrape.toc import _parse_issue_toc_html

SAMPLE_TOC_HTML = """\
<html>
  <body>
    <h1>n. 69 (2024)</h1>
    <h2>Artigos</h2>
    <div class="obj_article_summary">
      <h3 class="title">
        <a id="article-56443" href="https://periodicos.ufba.br/index.php/afroasia/article/view/56443">
          Zimbos e Libongos
        </a>
      </h3>
      <div class="meta">
        <div class="authors">Pedro Puntoni</div>
        <div class="pages">8-53</div>
      </div>
      <ul class="galleys_links">
        <li>
          <a class="obj_galley_link pdf" href="https://periodicos.ufba.br/index.php/afroasia/article/view/56443/34401">PDF</a>
        </li>
      </ul>
    </div>
  </body>
</html>
"""


def test_parse_issue_toc_html_extracts_ojs3_article_summary() -> None:
    toc = _parse_issue_toc_html(
        SAMPLE_TOC_HTML,
        "https://periodicos.ufba.br/index.php/afroasia/issue/view/2785",
    )

    article = toc["articles"][56443]

    assert toc["issue_id"] == 2785
    assert toc["issue_number"] == "n. 69 (2024)"
    assert toc["sections"] == ["Artigos"]
    assert article["title"] == "Zimbos e Libongos"
    assert article["section"] == "Artigos"
    assert article["authors"] == "Pedro Puntoni"
    assert article["pages"] == "8-53"
    assert article["pdf_url"].endswith("/article/view/56443/34401")
