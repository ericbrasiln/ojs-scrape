# CLI

::: ojs_scrape.cli
    options:
      show_root_heading: true
      show_source: true
      members:
        - build_parser
        - main

## Ajuda da linha de comando

```bash
ojs-scrape --help
```

Opções principais:

- `--from`: data inicial do recorte;
- `--until`: data final do recorte;
- `--set`: sets/seções OAI-PMH;
- `--issues`: IDs internos de edições OJS;
- `--author`: filtro local por autor;
- `--format`: um ou mais formatos: `json`, `csv`, `bibtex`; padrão: `json`;
- `-o`/`--output`: nome base da saída, sem extensão; o pacote adiciona `.json`, `.csv` ou `.bib`;
- `--pdf`: baixa PDFs públicos;
- `--pdf-limit`: limita a quantidade de PDFs baixados para teste;
- `--pdf-dir`: diretório de saída dos PDFs;
- `--delay`: intervalo mínimo entre requisições;
- `--timeout`: timeout de rede.
