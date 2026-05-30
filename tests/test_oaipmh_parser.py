"""Testes unitários do parser OAI-PMH."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from ojs_scrape.oaipmh import OAIPMHClient, _parse_xml_content

SAMPLE_RECORD = """\
<record xmlns="http://www.openarchives.org/OAI/2.0/">
  <header>
    <identifier>oai:ojs.periodicos.ufba.br:article/56443</identifier>
    <datestamp>2024-10-21</datestamp>
    <setSpec>afroasia:ART</setSpec>
  </header>
  <metadata>
    <oai_dc:dc
      xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
      xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:title>Zimbos and Libongos</dc:title>
      <dc:creator>Puntoni, Pedro</dc:creator>
      <dc:subject>Angola</dc:subject>
      <dc:subject>História da moeda</dc:subject>
      <dc:description>Resumo do artigo.</dc:description>
      <dc:date>2024-10-21</dc:date>
      <dc:identifier>https://doi.org/10.9771/aa.v0i69.56443</dc:identifier>
      <dc:source>Afro-Ásia; No. 69 (2024); 8-53</dc:source>
      <dc:language>en</dc:language>
    </oai_dc:dc>
  </metadata>
</record>
"""


def test_client_normalizes_ojs_index_urls() -> None:
    client = OAIPMHClient("https://renbio.org.br/index.php/sbenbio/index", delay=0)

    assert client.base_url == "https://renbio.org.br/index.php/sbenbio"
    assert client.oai_url == "https://renbio.org.br/index.php/sbenbio/oai"


def test_parse_record_extracts_dc_and_derived_fields() -> None:
    client = OAIPMHClient("https://periodicos.ufba.br/index.php/afroasia", delay=0)
    record = ET.fromstring(SAMPLE_RECORD)

    article = client._parse_record(record)

    assert article is not None
    assert article.article_id == 56443
    assert article.title == "Zimbos and Libongos"
    assert article.creators == ["Puntoni, Pedro"]
    assert article.palavras_chave == ["Angola", "História da moeda"]
    assert article.resumo == "Resumo do artigo."
    assert article.doi == "10.9771/aa.v0i69.56443"
    assert article.pages == "8-53"
    assert article.set_specs == ["afroasia:ART"]
    assert article.url.endswith("/article/view/56443")


def test_parse_xml_content_removes_invalid_xml_control_characters() -> None:
    xml = b"""\
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
  <ListRecords>
    <record>
      <metadata>
        <description>meta\x02epistemica</description>
      </metadata>
    </record>
  </ListRecords>
</OAI-PMH>
"""

    root = _parse_xml_content(xml, "https://example.test/oai")

    assert "metaepistemica" in "".join(root.itertext())
