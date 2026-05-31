# OJS-Scrape

[![PyPI version](https://img.shields.io/pypi/v/ojs-scrape.svg)](https://pypi.org/project/ojs-scrape/)
[![Python versions](https://img.shields.io/pypi/pyversions/ojs-scrape.svg)](https://pypi.org/project/ojs-scrape/)
[![License](https://img.shields.io/pypi/l/ojs-scrape.svg)](https://pypi.org/project/ojs-scrape/)
[![Documentation](https://img.shields.io/badge/docs-ericbrasil.com.br%2Fojs--scrape-blue)](https://ericbrasil.com.br/ojs-scrape/)

Ferramenta CLI e pacote Python para coleta estruturada de dados de periódicos acadêmicos hospedados em OJS (Open Journal Systems).

## Instalação pelo PyPI

O pacote está publicado em:

```text
https://pypi.org/project/ojs-scrape/
```

Instalação:

```bash
pip install ojs-scrape
```

## Escopo ético e vínculo institucional

O `ojs-scrape` é desenvolvido sem fins lucrativos e sem pretensão de acessar dados sigilosos, contornar controles de acesso ou alterar informações nos servidores das instituições.

A ferramenta é produzida no âmbito das pesquisas do [Laboratório de Humanidades Digitais da UFBA (LABHDUFBA)](https://labhdufba.github.io/).

## Decisão metodológica

O `ojs-scrape` usa **OAI-PMH** como fonte primária para metadados.

O scraping leve entra apenas como complemento para dados que o protocolo não cobre diretamente, como mapeamento artigo → edição e links de PDF.

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
- definição de OAI-PMH como fonte primária;
- implementação incremental da CLI;
- testes com revistas concretas, sobretudo Afro-Ásia e História da Historiografia;
- transformação de falhas reais em testes de regressão;
- refatoração para padrões atuais de Python;
- validação com Ruff, MyPy, pytest e build via `uv`.

Hermes Agent foi usado como ferramenta de trabalho e automação. As decisões metodológicas e acadêmicas permaneceram sob julgamento humano.

## Citação

Se usar o `ojs-scrape` em pesquisa, ensino, desenvolvimento ou análise institucional, cite o software.

Citação recomendada:

```text
BRASIL, Eric. OJS-Scrape: coleta de metadados de periódicos OJS via OAI-PMH. Versão 0.1.0. 2026. Software. Disponível em: https://ericbrasil.com.br/ojs-scrape.
```

O repositório inclui um arquivo [`CITATION.cff`](CITATION.cff) com metadados de citação.

## Agradecimentos e transparência

O projeto agradece a Ricardo Sodré Andrade pela referência intelectual e histórica associada ao Holmes e às experiências de colheita de metadados em periódicos científicos.

Agradece também ao [Laboratório de Humanidades Digitais da UFBA (LABHDUFBA)](https://labhdufba.github.io/) pelo ambiente de pesquisa, interlocução e desenvolvimento metodológico em Humanidades Digitais.

Este pacote e sua documentação foram desenvolvidos com apoio de sistemas de IA generativa, em especial o Hermes Agent, usado como ferramenta de automação, programação assistida, revisão técnica, organização documental e execução de testes.

O uso de IA não substitui julgamento acadêmico, revisão humana ou validação empírica. As decisões sobre método, escopo, interpretação, licenciamento e publicação pertencem ao pesquisador responsável.

Agentes de código que forem usar ou modificar este repositório devem ler [`AGENTS.md`](AGENTS.md).

Para o histórico das decisões metodológicas e arquiteturais, consulte [`docs/design-rationale.md`](docs/design-rationale.md).

Para próximas etapas públicas do pacote, consulte [`docs/roadmap.md`](docs/roadmap.md).

Para mudanças por versão, consulte [`CHANGELOG.md`](CHANGELOG.md).

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

## Documentação

A documentação pública do projeto está publicada em:

```text
https://ericbrasil.com.br/ojs-scrape
```

O site usa MkDocs Material com `mkdocstrings` para gerar referência de API a partir do código.

Servir localmente:

```bash
uv run --group docs mkdocs serve
```

Gerar o site estático:

```bash
uv run --group docs mkdocs build --strict
```

A publicação da documentação é feita por GitHub Actions em pushes para `main`, usando GitHub Pages.
Pull requests validam o build da documentação sem publicar.

## Uso

```bash
# Coletar metadados da Afro-Ásia (2024-2025)
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --until 2025

# Salvar JSON
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 --until 2025 \
  -o afro_asia_2024_2025

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

# Exportar mais de um formato ao mesmo tempo
ojs-scrape <URL> --from 2024 --until 2025 --format json csv bibtex -o dados
```

`--format` aceita um ou mais formatos: `json`, `csv`, `bibtex`.
O padrão é apenas `json`.

`-o`/`--output` recebe o nome base do arquivo, sem extensão.
O pacote adiciona a extensão conforme o formato: `.json`, `.csv` ou `.bib`.

```bash
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

Dependências de runtime: `requests`, `beautifulsoup4`. Sem API keys. Sem Selenium.

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
