# OJS-Scrape

Ferramenta CLI em Python para coleta estruturada de dados de periódicos acadêmicos hospedados em OJS (Open Journal Systems).

## Decisão metodológica: por que NÃO usar Firecrawl MCP

O Firecrawl foi testado como método de coleta para a revista Afro-Ásia. Resultado:

- `extract`: ~41 créditos/artigo. O plano free de 1000 créditos/mês esgota em ~24 artigos.
- `scrape`: ~1 crédito/página. Funciona, mas é desnecessário para metadados já disponíveis via OAI-PMH.
- `map`: não mapeou bem páginas OJS.
- Dependência de API key e serviço comercial para dados acadêmicos já expostos por protocolo aberto.

**Decisão**: usar **OAI-PMH** como fonte primária. Usar scraping apenas como complemento leve para dados não cobertos pelo protocolo, como mapeamento artigo → edição e links de PDF.

## Método

**Primário**: OAI-PMH (`{base_url}/oai`) para metadados Dublin Core:

- título
- autores
- resumo
- palavras-chave
- DOI
- data
- fonte/revista
- idioma
- identificadores

**Complementar**: `requests` + BeautifulSoup para:

- identificar artigos dentro de edições específicas;
- enriquecer seção, páginas e link de PDF a partir da TOC;
- baixar PDFs quando solicitado.

Validação com periódicos OJS reais:

- Afro-Ásia: 127 registros no recorte 2024-2025 via OAI-PMH. As edições n. 69, 70 e 71 retornam 104 registros quando cruzadas com suas TOCs.
- História da Historiografia: 842 artigos exportados na coleta completa; 256 artigos no recorte de publicação 2020-2026. Essa revista revelou dois casos tratados pelo pacote: caracteres de controle inválidos no XML OAI-PMH e diferença entre `datestamp` OAI e data de publicação (`dc:date`).
- RENBIO: metadados e PDFs públicos validados em lote, com URL pública terminada em `/index` normalizada para o endpoint OAI-PMH correto.
- Revista Brasileira de Sociologia (RBS): metadados validados; download de PDFs validado por amostragem com `--pdf-limit`, incluindo galleys numéricos e links OJS que precisam ser convertidos de `/article/view/...` para `/article/download/...`.

Observação sobre datas: `--from` e `--until` são interpretados como recorte por data de publicação. O OAI-PMH usa esses parâmetros como `datestamp`; por isso o pacote aplica também filtro local por `dc:date` para evitar que artigos antigos atualizados recentemente entrem no recorte.

## Escopo e limites de compatibilidade

O `ojs-scrape` não promete funcionar com qualquer periódico OJS.

Formulação segura: o pacote coleta metadados de periódicos OJS que exponham OAI-PMH público e baixa PDFs públicos quando os artigos usam galleys OJS acessíveis por URL padrão ou detectável.

Para metadados, a compatibilidade depende de:

- OAI-PMH habilitado e acessível sem autenticação;
- respostas XML legíveis, mesmo que exijam limpeza de caracteres de controle inválidos;
- exposição de metadados Dublin Core suficientes (`dc:title`, `dc:creator`, `dc:date`, `dc:identifier`, etc.);
- ausência de bloqueios por IP, CAPTCHA, Cloudflare ou rate limit agressivo.

Para PDFs, a compatibilidade depende de:

- artigos com PDF disponível;
- PDFs públicos, sem login ou embargo;
- galleys OJS acessíveis por links padrão ou detectáveis nas páginas dos artigos;
- servidor estável o suficiente para downloads sucessivos;
- links de PDF que não estejam quebrados.

Metadados tendem a ser mais confiáveis do que PDFs. A razão é metodológica: OAI-PMH é um protocolo padronizado para colheita de metadados; já o acesso aos PDFs depende da configuração local de galleys, permissões, tema OJS e plugins de cada revista.

Antes de baixar uma coleção inteira de PDFs, teste uma amostra:

```bash
ojs-scrape <URL> --from 2024 --until 2025 --pdf --pdf-limit 3 --pdf-dir pdfs_teste/
```

Se a amostra funcionar, rode o lote completo sem `--pdf-limit`.

## Processo de desenvolvimento com Hermes Agent

Este pacote foi desenvolvido com apoio do [Hermes Agent](https://github.com/NousResearch/hermes-agent), em diálogo com o pesquisador Eric Brasil.

O processo combinou:

- validação empírica de endpoints OAI-PMH reais;
- comparação entre Firecrawl e protocolo aberto;
- implementação incremental da CLI;
- testes com revistas concretas, sobretudo Afro-Ásia e História da Historiografia;
- transformação de falhas reais em testes de regressão;
- refatoração para padrões atuais de Python;
- validação com Ruff, MyPy, pytest e build via `uv`.

Hermes Agent foi usado como ferramenta de trabalho e automação. As decisões metodológicas e acadêmicas permaneceram sob julgamento humano.

Agentes de código que forem usar ou modificar este repositório devem ler [`AGENTS.md`](AGENTS.md).

## Instalação para desenvolvimento

```bash
git clone <repo>
cd ojs-scrape
uv sync
```

Executar a CLI local:

```bash
uv run ojs-scrape --help
```

## Uso

```bash
# Coletar metadados da Afro-Ásia (2024-2025)
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --until 2025

# Salvar JSON
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 --until 2025 \
  -o afro_asia_2024_2025.json

# Filtrar por sets/seções OAI-PMH
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 --until 2025 \
  --set afroasia:ART afroasia:DOS

# Filtrar por edições OJS (IDs internos da URL /issue/view/{id})
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 --until 2025 \
  --issues 2785 2858 2964

# Buscar por autor
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 --until 2025 \
  --author "Puntoni"

# Exportar CSV ou BibTeX
ojs-scrape <URL> --from 2024 --until 2025 --format csv -o dados.csv
ojs-scrape <URL> --from 2024 --until 2025 --format bibtex -o dados.bib

# Baixar PDFs junto com metadados
ojs-scrape <URL> --from 2024 --until 2025 --pdf --pdf-dir pdfs/

# Testar rapidamente se o download de PDFs funciona sem baixar tudo
ojs-scrape <URL> --from 2024 --until 2025 --pdf --pdf-limit 3 --pdf-dir pdfs_teste/
```

## Estrutura

```text
src/ojs_scrape/
├── cli.py        # Interface CLI (argparse)
├── oaipmh.py     # Cliente OAI-PMH (Identify, ListSets, ListRecords, GetRecord)
├── models.py     # Dataclasses tipadas: Article, OJSJournal, OAISet
├── toc.py        # Scraping leve de TOCs OJS
├── pdf.py        # Download de PDFs
├── filters.py    # Filtros por edição, autor, set e data
├── exporters.py  # JSON, CSV, BibTeX
└── py.typed      # Marcador PEP 561
```

Dependências de runtime: `requests`, `beautifulsoup4`. Sem API keys. Sem Firecrawl. Sem Selenium.

## Qualidade de código

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest -q
uv run pytest -q --run-integration
uv build
```

Padrões adotados:

- layout `src/`;
- `pyproject.toml` como fonte única de configuração;
- Python `>=3.12`;
- type aliases com sintaxe `type`;
- dataclasses com `slots=True`;
- pacote tipado com `py.typed`;
- Ruff para lint/format;
- MyPy em modo `strict`;
- testes unitários separados de testes de integração.

## Licença

GNU General Public License v3 — em alinhamento com o espírito do PKP Open Harvester Systems (GPL v2). Consulte o arquivo [LICENSE](LICENSE).

## Referência

O Holmes foi um harvester OAI-PMH desenvolvido por Nanci Oddone e Ricardo Sodré Andrade (LABHD/UFBA) sobre o PKP Open Harvester Systems. Coletou metadados de 26 provedores e 13k+ documentos. Está descontinuado, mas validou o método. O `ojs-scrape` retoma essa abordagem com nova implementação em Python.

Referência:

- Oddone, Nanci; Andrade, Ricardo Sodré. "Sistema de acesso à informação baseado em Open Archives: a experiência do Holmes." In: *SNBU — Seminário Nacional de Bibliotecas Universitárias*, 14., 2006, Salvador. Disponível em: http://repositorio.febab.org.br/items/show/5703
