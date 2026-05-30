# Progress: OJS-Scrape

## Session 1 — 2026-05-30

### Decisões
- Abandonar Firecrawl MCP como método principal.
- Usar OAI-PMH como fonte primária de metadados.
- Usar scraping leve (`requests` + BeautifulSoup) apenas como complemento para TOCs e PDFs.
- Citar o Holmes (Oddone & Andrade, 2006) como inspiração conceitual descontinuada.
- Licenciar o projeto como GPL v3.

### Resultados
- Projeto criado em `~/documentos/repos/ojs-scrape`.
- OAI-PMH da Afro-Ásia validado: 127 registros no recorte 2024-2025.
- Primeiro pacote Python criado com `uv`.
- Primeiro commit: `5fb73fd`.

## Session 2 — 2026-05-30

### Revisão para padrões atuais de Python
- Migrou o pacote para layout `src/`.
- Atualizou `pyproject.toml`:
  - runtime deps: `requests`, `beautifulsoup4`;
  - dev deps: `ruff`, `mypy`, `pytest`, `pytest-cov`, `types-requests`;
  - Ruff configurado para lint e format;
  - MyPy em modo `strict`;
  - build Hatchling configurado para `src/ojs_scrape`.
- Adicionou `src/ojs_scrape/py.typed` (PEP 561).
- Refatorou modelos com `dataclass(slots=True)` e type aliases Python 3.12.
- Refatorou cliente OAI-PMH:
  - suporta URL base ou endpoint `/oai` direto;
  - tem context manager e `close()`;
  - trata XML inválido;
  - extrai DOI normalizado;
  - extrai páginas de `dc:source` quando `dc:coverage` não existe.
- Corrigiu CLI:
  - `--until 2025` agora vira `2025-12-31`;
  - múltiplos `--set` agora coletam cada set e fazem merge por identificador;
  - filtro por edições cruza OAI-PMH + TOC e enriquece seção/páginas/PDF.
- Refatorou exportadores:
  - JSON, CSV e BibTeX tipados;
  - BibTeX com chave sanitizada e escaping básico.
- Refatorou scraping de TOC:
  - parser HTML separado de requisição para teste unitário;
  - suporta estrutura OJS 3 (`h3.title a`, galley PDF etc.).
- Corrigiu download de PDF:
  - tenta a URL recebida diretamente antes de acrescentar `/download`;
  - sanitiza filename;
  - reutiliza `requests.Session` em lote.
- Reorganizou testes:
  - unit tests rápidos por padrão;
  - integração com rede marcada com `@pytest.mark.integration` e executada via `--run-integration`.

### Validação real
- `uv run ruff check .` → passou.
- `uv run ruff format --check .` → passou.
- `uv run mypy` → passou, 0 issues em 8 source files.
- `uv run pytest -q` → 12 passed, 4 skipped.
- `uv run pytest -q --run-integration` → 16 passed.
- `uv build` → gerou wheel e sdist.
- CLI validada com Afro-Ásia:
  - recorte 2024-2025: 127 registros;
  - filtro por autor `Puntoni`: 1 registro;
  - edições 2785, 2858, 2964: 104 registros com seção/páginas;
  - sets `afroasia:ART` + `afroasia:DOS`: 51 registros.

### Observação
- A revisão independente via `delegate_task` falhou por erro externo de credencial OpenAI (`no-key-required`), problema conhecido da configuração de delegação. A revisão automatizada local foi feita com Ruff, MyPy, pytest, integração real, build e scan estático de segurança.

## Session 3 — 2026-05-30

### Teste com História da Historiografia
- URL testada: `https://www.historiadahistoriografia.com.br/revista`.
- Endpoint OAI-PMH válido: `https://www.historiadahistoriografia.com.br/revista/oai`.
- Repositório identificado como: `História da Historiografia: International Journal of Theory and History of Historiography`.
- `ListSets` retornou 60 sets.

### Problemas encontrados e corrigidos
- Algumas respostas OAI-PMH da revista incluem caracteres de controle inválidos em XML 1.0 (`\x02`) dentro de `dc:description`.
  - Correção: parser remove caracteres proibidos por XML 1.0 antes de chamar `ElementTree`, mantendo warning no log.
  - Teste de regressão adicionado.
- O filtro `--from/--until` usava o `datestamp` OAI-PMH como recorte efetivo.
  - Problema: nessa revista, artigos de 2009 foram atualizados depois de 2020 e apareciam no recorte `--from 2020`.
  - Correção: CLI agora usa OAI-PMH como pré-filtro e aplica filtro local por `dc:date`, isto é, data de publicação.
  - Teste de regressão adicionado.
- A CLI informava a contagem de registros coletados como se fosse a contagem exportada.
  - Problema: registros OAI-PMH deletados são ignorados pelos exportadores.
  - Correção: mensagem final distingue artigos exportados e registros deletados ignorados.

### Resultados de validação
- Coleta completa da História da Historiografia:
  - 906 registros OAI-PMH coletados;
  - 842 artigos exportados;
  - 64 registros deletados ignorados.
- Recorte `--from 2020 --until 2026-05-30`:
  - 256 artigos exportados;
  - distribuição: 2020=43, 2021=34, 2022=47, 2023=40, 2024=42, 2025=30, 2026=20.
- Múltiplos sets `revista:AR revista:ED` no mesmo recorte:
  - 26 artigos exportados.
- Filtro por edição `--issues 55`:
  - 7 artigos exportados;
  - `section` preenchida em 7/7;
  - `pdf_url` preenchida em 7/7.
- Exportações:
  - CSV 2020-2026: 256 linhas;
  - BibTeX 2020-2026: 256 entradas.

### Quality gate
- `uv run ruff check .` → passou.
- `uv run ruff format --check .` → passou.
- `uv run mypy` → passou, 0 issues em 8 source files.
- `uv run pytest -q` → 15 passed, 4 skipped.
- `uv run pytest -q --run-integration` → 19 passed.
- `uv build` → gerou wheel e sdist.

## Session 4 — 2026-05-30

### Documentação para agentes
- Criou `AGENTS.md` na raiz do repositório.
- O arquivo orienta agentes de código sobre:
  - escopo do pacote;
  - decisão metodológica por OAI-PMH;
  - processo de desenvolvimento com Hermes Agent;
  - comandos de setup, uso e quality gate;
  - semântica de datas (`dc:date` vs. `datestamp` OAI);
  - tratamento de XML inválido;
  - sets, edições e TOC;
  - exportação e arquivos gerados;
  - convenções de Git (`main`, nunca `master`).
- Atualizou `README.md` com seção sobre o processo de desenvolvimento com Hermes Agent.
- Explicitou que Hermes Agent foi usado como ferramenta de trabalho e automação, não como fonte de autoridade acadêmica.
