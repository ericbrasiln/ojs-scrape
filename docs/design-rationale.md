# OJS-Scrape — Design rationale

Este documento registra as decisões de método e arquitetura que orientaram o `ojs-scrape`.

Ele não é documentação de uso.
Para uso da CLI, consulte o `README.md`.

## Problema

O pacote responde a uma necessidade recorrente em pesquisa acadêmica: coletar metadados estruturados de periódicos hospedados em OJS.

O caso inicial foi a revista Afro-Ásia.
A tentativa com Firecrawl mostrou que scraping comercial funciona para páginas pontuais, mas não é o método adequado para coleta sistemática de metadados OJS.

A razão é simples: o OJS já expõe metadados por OAI-PMH.
OAI-PMH é um protocolo aberto feito para colheita de metadados por máquinas.

Usar scraping pesado para dados já publicados em OAI-PMH adiciona custo, fragilidade e dependência externa sem ganho metodológico proporcional.

## Referência histórica

A opção por OAI-PMH tem precedente no campo da Ciência da Informação no Brasil.

O Holmes, desenvolvido por Nanci Oddone e Ricardo Sodré Andrade no âmbito do GEDINFO/UFBA, foi um harvester OAI-PMH voltado a periódicos de Ciência da Informação.
Ele coletou metadados de 26 provedores e mais de 13 mil documentos.

Referência:

- Oddone, Nanci; Andrade, Ricardo Sodré. "Sistema de acesso à informação baseado em Open Archives: a experiência do Holmes." In: *SNBU — Seminário Nacional de Bibliotecas Universitárias*, 14., 2006, Salvador. Disponível em: http://repositorio.febab.org.br/items/show/5703

O Holmes usava o PKP Open Harvester Systems.
O `ojs-scrape` retoma o princípio de coleta via OAI-PMH, mas é uma implementação independente em Python.
Nenhum código do Holmes ou do PKP OHS foi reutilizado.

## Requisitos de pesquisa

O pacote foi desenhado para permitir:

1. definir a revista por URL base;
2. coletar por recorte temporal;
3. exportar metadados em formatos úteis;
4. filtrar por edições OJS específicas;
5. buscar autores por correspondência local;
6. baixar PDFs públicos quando disponíveis;
7. validar PDFs por amostragem antes de lotes longos.

Esses requisitos combinam recursos nativos do OAI-PMH com complementos leves de HTML.

## Decisão principal

Fonte primária: OAI-PMH.

Complemento: scraping leve com `requests` e BeautifulSoup.

Não usar:

- Firecrawl como método principal;
- Selenium;
- navegador headless;
- scraping pesado para metadados que já estão no OAI-PMH.

## OAI-PMH como fonte primária

A URL base de uma revista OJS normalmente permite derivar o endpoint:

```text
{base_url}/oai
```

A coleta usa os verbos principais:

- `Identify` para validar o repositório;
- `ListSets` para identificar seções;
- `ListRecords` para colher metadados Dublin Core;
- `resumptionToken` para paginação.

Campos Dublin Core usados:

- `dc:title` → título;
- `dc:creator` → autores;
- `dc:subject` → palavras-chave;
- `dc:description` → resumo;
- `dc:date` → data de publicação;
- `dc:identifier` → DOI e URLs;
- `dc:type` → tipo;
- `dc:format` → formato;
- `dc:coverage` ou `dc:source` → páginas, quando disponíveis.

## Datas

OAI-PMH usa `from` e `until` como filtro por `datestamp`, isto é, data de atualização do registro.

Para uso acadêmico, a expectativa é filtrar por data de publicação.
Por isso o pacote usa o recorte OAI-PMH como pré-filtro e depois aplica filtro local por `dc:date`.

Essa decisão evita que artigos antigos, atualizados recentemente, apareçam indevidamente em recortes recentes.

## Filtro por edições

Sets OAI-PMH em OJS costumam representar seções, não edições.

Exemplos:

- Artigos;
- Dossiê;
- Resenhas;
- Editorial.

Por isso, filtrar por edição exige complemento via TOC.

Estratégia adotada:

1. coletar metadados via OAI-PMH;
2. acessar a página `/issue/view/{issue_id}`;
3. extrair IDs dos artigos listados na edição;
4. cruzar IDs da TOC com IDs dos registros OAI-PMH;
5. enriquecer os artigos com seção, páginas e possível link de PDF.

Essa abordagem preserva o OAI-PMH como fonte principal dos metadados e usa HTML apenas para a informação que o protocolo não fornece diretamente.

## Busca por autor

OAI-PMH não oferece consulta por autor.

A busca por autor é feita localmente, sobre `dc:creator`, com correspondência case-insensitive por substring.

Essa solução é simples e cobre variações usuais de consulta, como sobrenome ou parte do nome.

## PDFs

OAI-PMH pode indicar que há PDF, mas não padroniza o link direto do arquivo.

O download de PDFs usa uma sequência de tentativas:

1. URL direta quando disponível;
2. link de galley na página do artigo;
3. conversão de `/article/view/{id}/{galley}` para `/article/download/{id}/{galley}` quando necessário;
4. priorização de links oficiais de galley OJS sobre PDFs externos citados em referências.

Galleys conhecidos podem ser:

- numéricos, como `579`;
- textuais, como `pdf_53`;
- faixas ou rótulos, como `759-775`.

Downloads de PDF são mais lentos e menos previsíveis que metadados.
Por isso o pacote inclui `--pdf-limit N` para validar uma amostra antes de baixar lotes grandes.

Exemplo:

```bash
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --until 2025 \
  --pdf \
  --pdf-limit 3 \
  --pdf-dir pdfs_teste/
```

## Limites de compatibilidade

O pacote não promete funcionar com qualquer periódico OJS.

Formulação segura:

> O `ojs-scrape` coleta metadados de periódicos OJS que exponham OAI-PMH público e baixa PDFs públicos quando os artigos usam galleys OJS acessíveis por URL padrão ou detectável.

Metadados são mais confiáveis que PDFs.
OAI-PMH é protocolo padronizado.
PDFs dependem da configuração local da revista.

Casos que podem falhar:

- OAI-PMH desabilitado;
- endpoint `/oai` bloqueado;
- respostas XML inválidas além da recuperação implementada;
- metadados Dublin Core incompletos;
- PDFs ausentes;
- PDFs sob login ou embargo;
- temas OJS muito customizados;
- plugins que alteram galleys;
- CAPTCHA, Cloudflare, bloqueio por IP ou rate limit agressivo;
- links de PDF externos quebrados.

Quando um caso real falhar, a prioridade é transformar o caso em teste de regressão antes de ampliar heurísticas.

## Dependências

O pacote usa dependências mínimas:

- `requests` para HTTP;
- `xml.etree.ElementTree` para XML;
- `beautifulsoup4` para HTML leve;
- `argparse` para CLI.

A implementação evita dependências pesadas para preservar auditabilidade e reduzir pontos de falha.

## Interface CLI projetada

Exemplos de uso esperados:

```bash
# Coletar metadados da Afro-Ásia, 2024-2025
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --until 2025

# Filtrar por seção OAI-PMH
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --set afroasia:ART afroasia:DOS

# Filtrar por edições OJS
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --until 2025 \
  --issues 2785 2858 2964

# Buscar por autor
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --author "Puntoni"

# Baixar PDFs
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --pdf

# Testar PDFs por amostragem
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --pdf \
  --pdf-limit 3 \
  --pdf-dir pdfs_teste/

# Exportar formatos específicos
ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --format csv \
  -o afro_asia.csv

ojs-scrape https://periodicos.ufba.br/index.php/afroasia \
  --from 2024 \
  --format bibtex \
  -o afro_asia.bib
```

## Arquitetura do pipeline

```text
Entrada: URL base do periódico + parâmetros de coleta

1. Identify
   - valida endpoint OAI-PMH
   - obtém informações do repositório

2. ListSets
   - identifica sets/seções disponíveis

3. ListRecords
   - coleta Dublin Core
   - pagina com resumptionToken
   - ignora registros deletados
   - limpa XML inválido quando possível

4. Filtros locais
   - data de publicação via dc:date
   - autor
   - sets múltiplos

5. Complemento por TOC, se solicitado
   - mapeia article_id para edição
   - enriquece seção, páginas e pdf_url

6. PDFs, se solicitado
   - detecta galley oficial
   - baixa arquivos públicos
   - respeita limite de amostragem quando `--pdf-limit` é usado

7. Exportação
   - JSON
   - CSV
   - BibTeX
```

## Diferença em relação a harvesters genéricos

Harvesters OAI-PMH genéricos coletam registros brutos.
O `ojs-scrape` acrescenta operações voltadas ao trabalho com periódicos OJS:

- filtragem por edição via TOC;
- busca local por autor;
- normalização de DOI e URLs;
- exportação em formatos de trabalho;
- download opcional de PDFs públicos;
- amostragem de PDFs;
- tratamento de problemas encontrados em revistas brasileiras reais.

## Decisões de qualidade

O pacote segue:

- layout `src/`;
- Python `>=3.12`;
- Hatchling para build;
- Ruff para lint e formatação;
- MyPy em modo strict;
- pytest para testes;
- marcador `integration` para testes com rede.

Falhas encontradas em revistas reais devem virar testes de regressão sempre que possível.

## Licença

A licença adotada é GNU GPL v3.

A escolha dialoga com o espírito do PKP Open Harvester Systems, licenciado sob GPL v2, mas sem criar derivação de código.
