# OJS-Scrape

`ojs-scrape` é uma ferramenta de linha de comando em Python para coletar metadados estruturados de periódicos hospedados em OJS.

A fonte primária é OAI-PMH.
Scraping leve com `requests` e BeautifulSoup é usado apenas como complemento para páginas de sumário e PDFs públicos.

## O que a ferramenta faz

- coleta metadados Dublin Core via OAI-PMH;
- filtra por data de publicação;
- filtra por autor;
- filtra por sets/seções OAI-PMH;
- cruza registros com edições OJS específicas;
- exporta JSON, CSV e BibTeX;
- baixa PDFs públicos quando disponíveis;
- permite testar PDFs por amostragem com `--pdf-limit`.

## Exemplo rápido

```bash
ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  -o afro_asia_2024_2025.json
```

## Método

OJS já expõe metadados por OAI-PMH.
Esse protocolo é gratuito, padronizado e feito para colheita de metadados.

Por isso, o pacote não usa Firecrawl, Selenium ou navegador headless para dados que já estão disponíveis via OAI-PMH.

## Compatibilidade

O pacote não promete funcionar com qualquer periódico OJS.

Formulação segura:

> `ojs-scrape` coleta metadados de periódicos OJS com OAI-PMH público e baixa PDFs públicos quando os artigos usam galleys OJS acessíveis por URL padrão ou detectável.

Para detalhes, consulte [Compatibilidade](compatibility.md).
