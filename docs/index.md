# OJS-Scrape

`ojs-scrape` é um pacote Python e uma ferramenta de linha de comando para coletar metadados estruturados de periódicos hospedados em OJS.

!!! note "Escopo ético e vínculo institucional"
    O `ojs-scrape` é desenvolvido sem fins lucrativos e sem pretensão de acessar dados sigilosos, contornar controles de acesso ou alterar informações nos servidores das instituições.

    A ferramenta é produzida no âmbito das pesquisas do [Laboratório de Humanidades Digitais da UFBA (LABHDUFBA)](https://labhdufba.github.io/).

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
  -o afro_asia_2024_2025
```

## Método

OJS já expõe metadados por OAI-PMH.
Esse protocolo é gratuito, padronizado e feito para colheita de metadados.

Por isso, o pacote usa OAI-PMH como fonte primária e restringe o scraping leve aos dados complementares que não aparecem no protocolo.

## Compatibilidade

O pacote não promete funcionar com qualquer periódico OJS.

Formulação segura:

> `ojs-scrape` coleta metadados de periódicos OJS com OAI-PMH público e baixa PDFs públicos quando os artigos usam galleys OJS acessíveis por URL padrão ou detectável.

Para detalhes, consulte [Compatibilidade](compatibility.md).

## Citação, créditos e transparência

Se usar o pacote em pesquisa, ensino, desenvolvimento ou análise institucional, consulte [Citação](citation.md).

Agradecimentos, vínculo com o LABHDUFBA e nota de transparência sobre uso de IA estão em [Créditos e transparência](credits-transparency.md).

## Desenvolvimento

O plano público de desenvolvimento está em [Roadmap](roadmap.md).

Mudanças por versão ficam no [`CHANGELOG.md`](https://github.com/ericbrasiln/ojs-scrape/blob/main/CHANGELOG.md) do repositório.
