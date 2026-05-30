# Progress: OJS-Scrape

## Session 1 — 2026-05-30

### Atividades
1. Testou Firecrawl MCP para coleta da Afro-Ásia
   - `scrape` funciona, custa ~1 credit/página
   - `extract` funciona, custa ~41 credits/artigo (insustentável)
   - `map` não funciona com OJS
   - Créditos esgotados após 11 artigos via extract + 3 TOC scrapes
2. Criou skill `firecrawl-ojs-scraper` (agora obsoleta para este projeto)
3. Identificou OAI-PMH como alternativa correta
4. Analisou referência Holmes (GEDINFO/UFBA) — harvester OAI-PMH com PKP OAI Harvester
5. Iniciou planejamento do projeto ojs-scrape
6. Criou arquivos de planejamento: task_plan.md, findings.md, progress.md
7. Documentou razões para não usar Firecrawl

### Decisões da Sessão
- Abandonar Firecrawl MCP como método principal
- OAI-PMH como fonte primária de metadados
- Scraping leve (requests+BS4) como complemento para PDFs
- Projeto em ~/documentos/repos/ojs-scrape/

### Próximo Passo
- Validar endpoint OAI-PMH da Afro-Ásia
- Testar sickle (lib Python OAI-PMH)
- Refinar prompt/arquitetura com thread of thought