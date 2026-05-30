# Desenvolvimento

## Ambiente

```bash
git clone https://github.com/ericbrasiln/ojs-scrape.git
cd ojs-scrape
uv sync
```

## Quality gate

Antes de declarar uma mudança concluída:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest -q
uv build
```

Quando a mudança afetar rede, OAI-PMH, TOC ou integração com OJS real:

```bash
uv run pytest -q --run-integration
```

## Documentação

Servir localmente:

```bash
uv run --group docs mkdocs serve
```

Build estrito:

```bash
uv run --group docs mkdocs build --strict
```

## Regras de método

- Usar OAI-PMH como fonte primária.
- Usar scraping leve apenas como complemento.
- Transformar falhas reais em testes de regressão.
- Não versionar saídas de coleta nem PDFs.
