# Uso

## Coletar metadados

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  -o afro_asia_2024_2025.json
```

`--from` e `--until` aceitam ano ou data completa.

Exemplos:

```bash
--from 2024
--until 2025
--from 2024-01-01
--until 2025-12-31
```

## Exportar CSV

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --format csv \
  -o afro_asia.csv
```

## Exportar BibTeX

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --format bibtex \
  -o afro_asia.bib
```

## Filtrar por autor

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --author "Puntoni" \
  -o puntoni.json
```

A busca por autor é local, com correspondência por substring sem diferenciar maiúsculas e minúsculas.

## Filtrar por sets/seções

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --set afroasia:ART afroasia:DOS \
  -o artigos_dossie.json
```

OAI-PMH aceita um set por requisição.
O pacote coleta cada set e deduplica os registros.

## Filtrar por edições OJS

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --issues 2785 2858 2964 \
  -o edicoes_69_71.json
```

Os números usados em `--issues` são IDs internos das URLs OJS:

```text
/issue/view/{issue_id}
```

O pacote usa a página da edição para mapear artigos para aquela edição.
