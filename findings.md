# Findings: OJS-Scrape

## Escopo de compatibilidade do ojs-scrape

O pacote não deve ser descrito como compatível com qualquer revista OJS.

Formulação segura: `ojs-scrape` coleta metadados de periódicos OJS que exponham OAI-PMH público e baixa PDFs públicos quando os artigos usam galleys OJS acessíveis por URL padrão ou detectável.

### Metadados

O caminho de metadados é o mais confiável, pois usa OAI-PMH. Ainda assim, depende de:

- endpoint `/oai` habilitado e público;
- respostas XML parseáveis ou recuperáveis após limpeza de caracteres de controle inválidos;
- metadados Dublin Core suficientes;
- ausência de bloqueio por login, IP, CAPTCHA, Cloudflare ou rate limit agressivo.

Se o Dublin Core não trouxer resumo, palavras-chave, DOI ou páginas, o pacote deve exportar o campo vazio. Não deve inventar metadados ausentes.

### PDFs

O caminho de PDFs é menos garantido que o de metadados. Depende de:

- artigo ter PDF;
- PDF estar público, sem login ou embargo;
- galley OJS usar URL padrão ou detectável;
- servidor responder de forma estável durante downloads sucessivos;
- link do PDF não estar quebrado.

Para evitar coletas lentas desnecessárias, validar primeiro com:

```bash
ojs-scrape <URL> --from 2024 --until 2025 --pdf --pdf-limit 3 --pdf-dir pdfs_teste/
```

Se a amostra funcionar, rodar o lote completo sem `--pdf-limit`.

## Validação OAI-PMH — Afro-Ásia (2026-05-30)

### Teste realizado com sucesso
```
curl "https://periodicos.ufba.br/index.php/afroasia/oai/?verb=Identify"
→ repositoryName: Afro-Ásia, protocolVersion: 2.0, earliestDatestamp: 2016-12-01
```

```
curl "...?verb=ListSets"
→ 23 sets: afroasia:ART (Artigos), afroasia:RES (Resenhas), afroasia:DOS (Dossiê), etc.
```

```
curl "...?verb=ListRecords&metadataPrefix=oai_dc&from=2024-01-01&until=2025-12-31"
→ 127 registros, 100 por página (resumptionToken para paginação)
→ Dublin Core inclui: title, creator, subject (kw), description (resumo), date, identifier, type
```

### Mapeamento de campos Dublin Core → Metadados
| Dublin Core | Campo | Exemplo |
|-------------|-------|---------|
| `dc:title` | Título | "Zimbos e Libongos: a moeda..." |
| `dc:creator` | Autores | "Puntoni, Pedro" |
| `dc:subject` | Palavras-chave | "Angola, Sistema monetário" |
| `dc:description` | Resumo | "Desde o século XVI..." |
| `dc:date` | Data publicação | "2024-10-21" |
| `dc:identifier` | DOI + URL | "10.9771/aa.v0i69.56443" |
| `dc:type` | Tipo | "article" |
| `dc:format` | Formato | "application/pdf" |
| `dc:coverage` | Páginas | "8-53" |

### Estrutura do ID OAI-PMH
- Identificador: `oai:ojs.periodicos.ufba.br:article/{article_id}`
- Número article_id corresponde ao ID usado nas URLs OJS
- URL do artigo: `{base_url}/article/view/{article_id}`
- URL do PDF: `{base_url}/article/view/{article_id}/download` (a verificar)

### Sets Disponíveis
Sets são por **seção** (não por edição/issue):
- `afroasia:ART` = Artigos
- `afroasia:RES` = Resenhas  
- `afroasia:DOS` = Dossiê
- `afroasia:Deb` = Debate
- `afroasia:EXP` = Expediente
- `afroasia:ENT` = Entrevista
- `afroasia:MEM` = Memória
- etc.

**Implicação**: Para filtrar por edição (n.69, n.70, n.71), é necessário:
1. Coletar registros via OAI-PMH filtrando por data
2. Complementar com info de issue via scraping da TOC OU parse do datestamp + correlação

## OAI-PMH em Plataformas OJS

### Endpoint Padrão
Todo OJS 3.x expõe: `{base_url}/oai/`
Exemplo: `https://periodicos.ufba.br/index.php/afroasia/oai/`

### Verbos OAI-PMH
| Verbo | Função | Parâmetros |
|-------|--------|------------|
| `Identify` | Info do repositório | nenhum |
| `ListMetadataFormats` | Formatos disponíveis | identificador opcional |
| `ListSets` | Conjuntos (edições/seções) | resumptionToken |
| `ListRecords` | Registros com metadados | from, until, metadataPrefix, set, resumptionToken |
| `GetRecord` | Registro individual | identifier, metadataPrefix |
| `ListIdentifiers` | Só headers/identificadores | from, until, metadataPrefix, set, resumptionToken |

### Formatos de Metadados Comuns
- `oai_dc` — Dublin Core (padrão, sempre disponível)
- `oai_marc` — MARC21
- `oai_mets` — METS (pode incluir estrutura de artigo)

### Campos Dublin Core Tipicos
- `title` → título
- `creator` → autores
- `subject` → palavras-chave/temas
- `description` → resumo/abstract
- `date` → data de publicação
- `identifier` → DOI, URL
- `type` → tipo de documento
- `format` → formato (PDF, HTML)

### Sets no OJS
OJS geralmente expõe sets no formato:
- `journal_path` (set raiz)
- `journal_path:ISSN` ou `journal_path:issue_N`
- Pode variar entre instalações OJS

### Paginação (resumptionToken)
O OAI-PMH retorna no máximo 100 registros por requisição. Se há mais, a resposta inclui `<resumptionToken>` para buscar a próxima página.

## Referência: Holmes (GEDINFO/UFBA) e PKP Open Harvester Systems

### O Holmes
- **Descrição**: Harvester OAI-PMH que coletava metadados de periódicos de Ciência da Informação — **descontinuado**
- **Instituição**: GEDINFO (Grupo de Estudos em Políticas de Documentação e Informação), UFBA
- **Autores**: Nanci Oddone e Ricardo Sodré Andrade (membro do LABHD/UFBA — mesmo laboratório de Eric)
- **Base tecnológica**: PKP Open Harvester Systems (OHS)
- **Escala**: 26 provedores de dados, 13k+ documentos indexados
- **Status**: descontinuado; site offline
- **Relevância para ojs-scrape**: inspiração conceitual — validou que OAI-PMH funciona para coleta sistemática de periódicos brasileiros. O ojs-scrape retoma essa ideia com nova implementação.
- **Citação**: Oddone, Nanci; Andrade, Ricardo Sodré. "Sistema de acesso à informação baseado em Open Archives: a experiência do Holmes." In: *SNBU — Seminário Nacional de Bibliotecas Universitárias*, 14., 2006, Salvador. Disponível em: http://repositorio.febab.org.br/items/show/5703

### PKP Open Harvester Systems (OHS)
- **Repo**: https://github.com/pkp/harvester
- **Status**: **Arquivado** em 31/07/2024 (read-only, sem desenvolvimento ativo)
- **Licença**: **GNU GPL v2**
- **Branch ativa (histórica)**: `ohs-stable-2_3`
- **Linguagem**: PHP (código legado, ~726 commits, última atividade ~8 anos)
- **Componentes**: harvester de registros OAI-PMH, painel admin, indexação de metadados Dublin Core
- **Arquitetura**: Web app PHP com banco de dados, interface de admin para configurar provedores OAI-PMH e agendar harvesting
- **Relevância para ojs-scrape**: inspiração conceitual (demonstra que harvest OAI-PMH funciona), mas código é PHP legado arquivado — não será reutilizado. Nosso projeto é Python/CLI, arquitetura diferente.

### Implicações da licença GPL v2 do OHS
1. **Nosso projeto NÃO é derivado do OHS** — é implementação independente em Python. O código PHP do OHS não é copiado nem adaptado.
2. **Conceitos e protocolos não são protegidos por copyright** — usar OAI-PMH (um padrão aberto) não faz nosso software derivado do OHS.
3. **Podemos usar qualquer licença** no ojs-scrape, pois não há derivação de código.
4. **Referência**: citamos o Holmes e o OHS como **inspiração conceitual e validação do método**, não como base de código.
5. **Se eventualmente copiarmos trechos de lógica** (regex, mapeamentos etc.), a GPL v2 exigiria que nosso projeto também fosse GPL v2 — por isso, evitamos copiar código.

## Bibliotecas Python para OAI-PMH

- **sickle** — cliente OAI-PMH popular, mas pode estar desatualizado
- **pyoai** — outro option, mais antigo
- **Implementação custom** — usando `requests` + `xml.etree.ElementTree` — mais controle, sem dependência de lib de terceiros problemática
- **Avaliar**: testar `sickle` primeiro; se estável, usar; se não, implementar client do zero