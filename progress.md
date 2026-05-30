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
