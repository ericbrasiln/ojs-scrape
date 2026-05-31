# Instalação

## Instalação a partir do PyPI

O pacote está publicado no PyPI:

```bash
pip install ojs-scrape
```

Depois:

```bash
ojs-scrape --help
```

## Sistemas operacionais

Até o momento, o `ojs-scrape` foi testado pelo mantenedor em Linux.

Como é um pacote Python puro, com dependências portáveis (`requests` e `beautifulsoup4`), a expectativa é que também funcione em Windows com Python 3.12 ou superior.

Essa compatibilidade ainda não foi validada em ambiente Windows.
Testes específicos em Windows estão previstos.

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
