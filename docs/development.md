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

Publicação:

- pull requests validam o build da documentação;
- pushes em `main` publicam o site no GitHub Pages via `.github/workflows/docs.yml`.

## Publicação de versão

Antes de publicar uma versão:

1. Atualize a versão em `pyproject.toml`.
2. Atualize a versão em `CITATION.cff`, quando aplicável.
3. Atualize o [`CHANGELOG.md`](https://github.com/ericbrasiln/ojs-scrape/blob/main/CHANGELOG.md).
4. Rode o quality gate completo:

   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy
   uv run pytest -q
   uv run --group docs mkdocs build --strict
   uv build
   uvx twine check dist/*
   ```

5. Teste a instalação limpa do wheel gerado em `dist/`.
6. Publique primeiro no TestPyPI e teste a instalação a partir dele.
7. Crie a tag da versão.
8. Publique no PyPI real.
9. Crie a GitHub Release.
10. Confirme se o Zenodo arquivou a release e gerou DOI.
11. Se houver DOI novo, atualize a documentação de citação em uma mudança posterior.

PyPI não permite reenviar a mesma versão. Se uma versão publicada tiver erro, publique uma nova versão de correção.

O Zenodo lê os metadados de `.zenodo.json` quando arquiva releases sincronizadas pelo GitHub.
Não registre DOI manualmente antes de verificar o depósito real criado pelo Zenodo.

## Regras de método

- Usar OAI-PMH como fonte primária.
- Usar scraping leve apenas como complemento.
- Transformar falhas reais em testes de regressão.
- Não versionar saídas de coleta nem PDFs.

## Roadmap e changelog

- O plano público de desenvolvimento fica em [Roadmap](roadmap.md).
- Mudanças por versão ficam no [`CHANGELOG.md`](https://github.com/ericbrasiln/ojs-scrape/blob/main/CHANGELOG.md) da raiz do repositório.
- Logs internos de sessão não fazem parte da documentação pública do pacote.
