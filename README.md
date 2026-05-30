# OJS-Scrape

Ferramenta CLI em Python para coleta estruturada de dados de periódicos acadêmicos hospedados em OJS (Open Journal Systems).

## Por que NÃO usar Firecrawl MCP

O Firecrawl (API de web scraping comercial) foi testado como método de coleta. Resultados negativos:

- `extract`: ~41 credits/artigo → plano free (1000/mês) esgota em ~24 artigos
- `scrape`: ~1 credit/página → viável em custo, mas OAI-PMH faz o mesmo grátis
- `map`: não funciona com OJS (retorna 1 link)
- Rate limiting agressivo, créditos esgotam rápido
- Dependência de API key e serviço comercial para dados que já estão abertos

**Decisão**: OJS já expõe metadados via **OAI-PMH** (protocolo aberto, gratuito, padronizado). Usar scraping para dados que o OAI-PMH fornece gratuitamente é a abordagem errada.

## Método: OAI-PMH + scraping leve

**Primário**: OAI-PMH (`{base_url}/oai/`) — coleta de metadados completos (título, autores, resumo, palavras-chave, DOI, data, páginas) via Dublin Core. Sem custo, sem API key, sem rate limiting agressivo. Suporta recorte temporal (`from`/`until`) e filtro por seção (`set`).

**Complementar**: Scraping leve com `requests` + BeautifulSoup para:
- Mapear artigos a edições (OAI-PMH filtra por seção, não por edição)
- Obter links de PDF (OAI-PMH não fornece URL direta do PDF)

Valicão com Afro-Ásia: 127 registros 2024-2025, Dublin Core com resumo e palavras-chave, paginação via resumptionToken. Ver `findings.md`.

## Instalação

```bash
pip install ojs-scrape
# ou
pipx install ojs-scrape
```

## Uso

```bash
# Coletar metadados da Afro-Ásia (2024-2025)
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --until 2025

# Filtrar por seção
ojs-scrape <URL> --from 2024 --set ART DOS

# Filtrar por edição
ojs-scrape <URL> --issues 69 70 71

# Buscar por autor
ojs-scrape <URL> --from 2024 --author "Puntoni"

# Com download de PDFs
ojs-scrape <URL> --from 2024 --pdf

# Formato de saída
ojs-scrape <URL> --from 2024 --format csv
ojs-scrape <URL> --from 2024 --format bibtex

# Arquivo de saída
ojs-scrape <URL> --from 2024 -o dados.json
```

## Arquitetura

```
ojs_scrape/
├── cli.py        # Interface CLI (argparse)
├── oaipmh.py     # Cliente OAI-PMH (Identify, ListSets, ListRecords)
├── models.py     # Dataclass Article
├── toc.py        # Scraping de TOCs (mapeamento article_id → issue)
├── pdf.py        # Download de PDFs
├── filters.py    # Filtros: edição, autor
└── exporters.py  # JSON, CSV, BibTeX
```

Dependências: `requests`, `beautifulsoup4`. Sem API keys. Sem Firecrawl. Sem Selenium.

## Licença

GNU General Public License v3 — em alinhamento com o espírito do PKP Open Harvester Systems (GPL v2). Consulte o arquivo [LICENSE](LICENSE).

## Referência

O [Holmes](http://www.holmes.feudo.org) foi um harvester OAI-PMH desenvolvido por Nanci Oddone e Ricardo Sodré Andrade (LABHD/UFBA) sobre o PKP Open Harvester Systems. Coletou metadados de 26 provedores e 13k+ documentos. Descontinuado, mas validou o método. O ojs-scrape retoma essa abordagem com nova implementação em Python.

Referência:
- Oddone, Nanci; Andrade, Ricardo Sodré. "Sistema de acesso à informação baseado em Open Archives: a experiência do Holmes." In: *SNBU — Seminário Nacional de Bibliotecas Universitárias*, 14., 2006, Salvador. Disponível em: http://repositorio.febab.org.br/items/show/5703