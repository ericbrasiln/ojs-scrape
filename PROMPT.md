# OJS-Scrape — Prompt de Projeto (Thread of Thought)

## Pensamento 1: O problema real

O usuário (historiador) precisa coletar dados de periódicos acadêmicos publicados em plataformas OJS. Não é scraping genérico — é **coleta de metadados acadêmicos**. O Firecrawl falhou porque era o instrumento errado: um martelo quando precisávamos de uma chave.

A questão central: **OJS já expõe seus dados via OAI-PMH**. É um protocolo projetado exatamente para isso — coleta de metadados por máquinas. Usar scraping para extrair dados que já estão disponíveis via API padronizada é como rasgar o envelope para ler a carta ao invés de abri-lo.

Esse insight não é novo. O **Holmes** (GEDINFO/UFBA), desenvolvido por Nanci Oddone e Ricardo Sodré Andrade (membro do LABHD/UFBA), já fez isso para periódicos de Ciência da Informação: 26 provedores, 13k+ documentos. O Holmes foi descontinuado, mas validou o método. Referência: Oddone & Andrade (2006), "Sistema de acesso à informação baseado em Open Archives: a experiência do Holmes." SNBU, 14., Salvador. http://repositorio.febab.org.br/items/show/5703

O Holmes usava o **PKP Open Harvester Systems** (OHS, GPL v2, arquivado 2024) como base tecnológica — um web app PHP para configurar provedores OAI-PMH e agendar harvesting. Nosso projeto parte do mesmo princípio (OAI-PMH como fonte), mas é uma nova ferramenta, em Python/CLI, implementação independente sem derivação de código.

## Pensamento 2: O que o usuário realmente precisa

Parâmetros que o usuário quer configurar:

1. **Revista** — qual periódico coletar (URL base)
2. **Recorte temporal** — de quando até quando (anos, datas)
3. **Tipo de saída** — só metadados, ou também PDFs?
4. **Filtro por edições** — quero só a n.69, ou 69-71?
5. **Busca por autores** — quero tudo de "Pedro Puntoni"

Cada um desses parâmetros tem uma complexidade diferente no OAI-PMH:

- **Revista**: Endereço base → construir URL do endpoint OAI: `{base}/oai/`
- **Recorte temporal**: `from`/`until` no `ListRecords` — nativo, trivial
- **Tipo de saída**: Metadados = OAI-PMH puro; PDFs = download + mapeamento de URL
- **Filtro por edições**: **Não é nativo**. OAI-PMH filtra por *sets* (que são seções: Artigos, Resenhas, Dossiê), não por edições. Como resolver?
- **Busca por autores**: **Não é nativo**. OAI-PMH não tem query. Filtrar localmente no `dc:creator`.

## Pensamento 3: O problema do filtro por edições

Os sets do OAI-PMH são por **seção** da revista (Artigos, Dossiê, Resenhas), não por número de edição. Isso é uma limitação do protocolo para o nosso caso de uso.

Três abordagens possíveis:

**A. Correlação por data**: Cada edição é publicada em uma data. Se n.69 foi publicado em 2024-10-21, os artigos com essa data provavelmente pertencem à n.69. Problema: vários artigos podem ter datas diferentes (data de submissão vs. publicação vs. aceitação).

**B. Scraping da TOC**: Fazer scrape da página `/issue/view/{id}` para obter a lista de article IDs da edição. Depois cruzar com os registros OAI-PMH. Isso é robusto: a TOC é o "source of truth" para a organização em edições.

**C. Combinação**: Usar OAI-PMH para os metadados completos + scraping light da TOC para mapear article_id → issue. O custo do scraping da TOC é mínimo (1 request por edição, HTML simples).

**Decisão**: Abordagem **C**. OAI-PMH para dados completos, scraping da TOC para mapeamento de edições. O scraping é leve (sem Firecrawl, sem API) — basta `requests` + `BeautifulSoup` em 3 páginas.

## Pensamento 4: PDFs — como baixar?

O Dublin Core via OAI-PMH pode incluir `dc:identifier` com URL do artigo e `dc:format` com "application/pdf". Mas o link direto para o PDF não é padronizado no OAI-PMH.

Estratégia:
1. O registro OAI-PMH tem o article_id (do identifier)
2. URL do artigo: `{base_url}/article/view/{id}`
3. Na página do artigo, o link para PDF geralmente é: `{base_url}/article/view/{id}/{galley_id}` ou `{base_url}/article/view/{id}/download`
4. Scrape leve da página do artigo para encontrar o link exato do PDF
5. Download com `requests` + salvamento em diretório organizado

Ou, mais eficiente:
1. Scrape da TOC da edição (já precisamos disso para o mapeamento issue)
2. A TOC geralmente inclui links diretos para PDFs
3. Cruzar article_id com URL do PDF da TOC

## Pensamento 5: Arquitetura do pipeline

```
Input: URL base do periódico, parâmetros (datas, edições, autores, pdf)

Step 1: Identify
  → GET {base}/oai/?verb=Identify
  → Confirma que é OJS, obtém info do repositório

Step 2: ListSets
  → GET {base}/oai/?verb=ListSets
  → Mapeia seções disponíveis (para filtro e informação)

Step 3: ListRecords (com from/until/set)
  → GET {base}/oai/?verb=ListRecords&metadataPrefix=oai_dc&from=X&until=Y
  → Pagina via resumptionToken até esgotar
  → Parse XML → lista de registros Dublin Core

Step 4 (se filtro por edição):
  → Scrape TOCs das edições desejadas
  → Extrair article_ids por edição
  → Filtrar registros OAI-PMH: só os que estão na edição X

Step 5 (se busca por autor):
  → Filtrar localmente por dc:creator (case-insensitive, substring)

Step 6 (se PDFs):
  → Para cada artigo, construir/obter URL do PDF
  → Download e salvamento organizado

Step 7: Exportação
  → JSON / CSV / BibTeX
```

## Pensamento 6: O que torna isso diferente de um harvester genérico?

Harvesters OAI-PMH genéricos (como `sickle`) fazem coleta bruta. O ojs-scrape precisa ir além:

1. **Filtragem inteligente por edições** — cruzando OAI-PMH + TOC
2. **Busca por autores** — filtragem local amigável (substring, case-insensitive)
3. **Download de PDFs** — não só metadados
4. **Saída em formatos úteis** — JSON, CSV, BibTeX (não só XML Dublin Core)
5. **CLI amigável** — não é preciso saber OAI-PMH para usar

## Pensamento 7: Dependências e simplicidade

Quero minimizar dependências. OAI-PMH é XML sobre HTTP. Posso usar:

- `requests` — HTTP (já onipresente)
- `xml.etree.ElementTree` — XML parsing (stdlib)
- `beautifulsoup4` — HTML scraping das TOCs (leve, padrão)
- `click` ou `argparse` — CLI (argparse = stdlib, click = 1 dep)

Não preciso de `sickle` (lib OAI-PMH) — posso implementar o client em ~100 linhas. Isso dá mais controle sobre namespaces XML do OJS (que às vezes têm quirks) e evita dependência desatualizada.

## Pensamento 8: Interface CLI ideal

```bash
# Uso básico: coletar tudo da Afro-Ásia (2024-2025)
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --until 2025

# Com filtro de seção (só artigos e dossiê)
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --set ART DOS

# Com filtro de edição
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --issues 69 70 71

# Busca por autor
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --author "Puntoni"

# Com download de PDFs
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --pdf

# Formato de saída
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --format csv
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 --format bibtex

# Saída em arquivo
ojs-scrape https://periodicos.ufba.br/index.php/afroasia --from 2024 -o afro_asia.json
```

## Pensamento 9: O que pode dar errado?

1. **Namespace XML**: O OJS usa namespaces que variam entre versões. Solução: ser flexível no parser, usar `find()` com wildcard se necessário.
2. **Registros deletados**: OAI-PMH suporta `deletedRecord=persistent`. A Afro-Ásia tem isso. Preciso checar `status="deleted"` nos headers e ignorar.
3. **Rate limiting do servidor**: Mesmo OAI-PMH, alguns servidores limitam requests. Solução: delay configurável entre requisições.
4. **TOC scraping**: O HTML do OJS é previsível, mas instalações customizadas podem quebrar. Solução: fallback — se scraping falha, avisar o usuário e continuar só com OAI-PMH (sem mapeamento de edição).
5. **PDFs protegidos**: Alguns periódicos exigem login para PDFs. Solução: detectar (HTTP 401/403) e avisar.
6. **Encoding**: Periódicos brasileiros podem ter acentos em codificações estranhas. Solução: forçar UTF-8, `requests` já lida com isso.
7. **ResumptionToken**: Pode expirar se demorar muito entre pages. Solução: se falhar, recomeçar do início da coleção.

## Pensamento 10: Resumo da arquitetura final

```
ojs-scrape/
├── ojs_scrape/
│   ├── __init__.py
│   ├── cli.py           # CLI: argparse, entry point
│   ├── oaipmh.py        # Cliente OAI-PMH (Identify, ListSets, ListRecords)
│   ├── models.py        # Article dataclass: titulo, autores, resumo, kw, doi, data, paginas, secao, issue
│   ├── toc.py           # Scraping de TOCs para mapear article_id → issue
│   ├── pdf.py           # Download de PDFs
│   ├── filters.py       # Filtros: por edição, por autor
│   └── exporters.py     # JSON, CSV, BibTeX
├── tests/
│   └── test_oaipmh.py   # Testes com fixtures XML
├── pyproject.toml
└── README.md
```

Dependências mínimas: `requests`, `beautifulsoup4`, `lxml` (opcional, para XML mais robusto).
Sem Firecrawl. Sem Selenium. Sem API keys.