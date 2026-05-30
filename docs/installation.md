# Instalação

## Instalação a partir do PyPI

Quando o pacote estiver publicado:

```bash
pip install ojs-scrape
```

Depois:

```bash
ojs-scrape --help
```

## Instalação para desenvolvimento

```bash
git clone https://github.com/ericbrasiln/ojs-scrape.git
cd ojs-scrape
uv sync
```

Executar a CLI local:

```bash
uv run ojs-scrape --help
```

## Dependências de runtime

- `requests`
- `beautifulsoup4`

O pacote não exige API key.

## Dependências de documentação

A documentação usa MkDocs Material e mkdocstrings:

```bash
uv run --group docs mkdocs serve
```

Build estático:

```bash
uv run --group docs mkdocs build --strict
```
