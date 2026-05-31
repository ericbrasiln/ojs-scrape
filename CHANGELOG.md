# Changelog

Todas as mudanças relevantes do `ojs-scrape` são registradas neste arquivo.

O formato segue a lógica de [Keep a Changelog](https://keepachangelog.com/), com adaptações para o contexto do projeto.

## [Unreleased]

### Added

- `--format` agora aceita múltiplos formatos na mesma execução, por exemplo `--format json csv bibtex`.
- `-o`/`--output` agora é tratado como nome base sem extensão; a CLI gera `.json`, `.csv` ou `.bib` conforme o formato exportado.
- Metadados `.zenodo.json` para arquivamento automático de releases futuras via Zenodo-GitHub.

### Documented

- Link e badges do pacote no PyPI em destaque no README e na página inicial da documentação.
- Fluxo de citação com Zenodo: o DOI deve ser copiado do depósito real criado pelo Zenodo após a release, sem DOI manualmente inventado antes do arquivamento.
- Etapa de conferência do Zenodo no processo de publicação de versão.

## [0.1.0] - 2026-05-30

Primeira versão alpha do pacote Python e da ferramenta CLI.

### Added

- Cliente OAI-PMH para periódicos OJS com suporte a `Identify`, `ListSets`, `ListRecords` e `GetRecord`.
- Coleta de metadados Dublin Core via `oai_dc`.
- Filtro por data de publicação usando `dc:date`, com OAI-PMH usado como pré-filtro por `datestamp`.
- Filtros locais por autor, set/seção OAI-PMH e IDs de edições OJS.
- Scraping leve de TOC para mapear artigos a edições, seções, páginas e galleys públicos.
- Exportação em JSON, CSV e BibTeX.
- Download opcional de PDFs públicos.
- Opção `--pdf-limit` para testar downloads de PDF em amostras pequenas antes de lotes completos.
- Suporte a URLs públicas de revistas terminadas em `/index`.
- Layout moderno de pacote Python com `src/`, Hatchling, `py.typed`, Ruff, MyPy strict e pytest.
- Testes unitários e testes de integração marcados com `integration`.
- Documentação pública com MkDocs Material e referência de API com mkdocstrings.
- Workflow GitHub Actions para validar documentação em pull requests e publicar no GitHub Pages em pushes para `main`.
- `CITATION.cff` com metadados de citação acadêmica.

### Fixed

- Correção da semântica temporal da CLI: `--from` e `--until` representam data de publicação, não apenas `datestamp` OAI-PMH.
- Expansão correta de anos abreviados: `--until 2025` passa a cobrir até `2025-12-31`.
- Tratamento de caracteres de controle inválidos em XML OAI-PMH antes do parse.
- Exclusão de registros OAI-PMH marcados como deletados.
- Contagem final da CLI separando registros coletados, artigos exportados e registros deletados ignorados.
- Coleta com múltiplos `--set`, com merge por identificador OAI-PMH.
- Detecção de galleys OJS numéricos, textuais e baseados em faixas de página.
- Conversão de URLs `/article/view/...` para `/article/download/...` quando necessário.
- Priorização de links oficiais de galley OJS sobre PDFs externos citados nas referências dos artigos.
- Download de PDF retomável por arquivo existente não vazio.

### Documented

- Escopo ético da ferramenta.
- Limites de compatibilidade com OJS.
- Diferença entre confiabilidade de metadados via OAI-PMH e confiabilidade de PDFs via galleys públicos.
- Uso recomendado de `--pdf-limit` como smoke test de PDFs.
- Inspiração conceitual no Holmes e no PKP Open Harvester Systems, sem derivação de código.
- Transparência sobre uso de IA generativa no desenvolvimento e documentação.

### Validated

- Afro-Ásia.
- História da Historiografia.
- RENBIO.
- Revista Brasileira de Sociologia (RBS).

As validações indicam compatibilidade com periódicos OJS reais, mas não implicam compatibilidade universal com qualquer instalação OJS.
