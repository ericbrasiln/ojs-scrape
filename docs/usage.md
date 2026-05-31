# Uso

## Coletar metadados

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  -o afro_asia_2024_2025
```

`--from` e `--until` aceitam ano ou data completa.

Exemplos:

```bash
--from 2024
--until 2025
--from 2024-01-01
--until 2025-12-31
```

## Exportar formatos

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --format json csv bibtex \
  -o afro_asia
```

Esse comando gera:

```text
afro_asia.json
afro_asia.csv
afro_asia.bib
```

`--format` aceita um ou mais formatos: `json`, `csv`, `bibtex`.
O padrão é apenas `json`.

`-o`/`--output` recebe o nome base do arquivo, sem extensão.
O pacote adiciona a extensão conforme o formato.

## Exportar apenas BibTeX

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --format bibtex \
  -o afro_asia
```

## Filtrar por autor

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --author "Puntoni" \
  -o puntoni
```

A busca por autor é local, com correspondência por substring sem diferenciar maiúsculas e minúsculas.

## Filtrar por sets/seções

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --set afroasia:ART afroasia:DOS \
  -o artigos_dossie
```

OAI-PMH aceita um set por requisição.
O pacote coleta cada set e deduplica os registros.

## Filtrar por edições OJS

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --issues 2785 2858 2964 \
  -o edicoes_69_71
```

Os números usados em `--issues` são IDs internos das URLs OJS:

```text
/issue/view/{issue_id}
```

O pacote usa a página da edição para mapear artigos para aquela edição.
