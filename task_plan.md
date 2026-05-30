# Task Plan: OJS-Scrape — Ferramenta de coleta de dados de periódicos OJS

## Goal
Criar uma ferramenta CLI em Python que coleta dados estruturados de periódicos OJS via OAI-PMH (primário) + scraping leve (complementar), com parâmetros configuráveis: revista, recorte temporal, tipo de saída (metadados/PDFs), filtro por edições e busca por autores.

## Current Phase
Phase 2 — Protótipo OAI-PMH

## Phases

### Phase 1: Arquitetura
- [x] Investigar referência Holmes/OAI-PMH
- [x] Definir arquitetura: OAI-PMH primário + scraping complementar
- [x] Consolidar decisões de arquitetura em `docs/design-rationale.md`
- [x] Validar viabilidade testando endpoint OAI-PMH da Afro-Ásia
- **Status:** complete

### Phase 2: Protótipo OAI-PMH
- [ ] Cliente OAI-PMH: Identify, ListSets, ListRecords, GetRecord
- [ ] Parser de XML OAI-PMH → dataclasses Python
- [ ] Teste com Afro-Ásia (3 edições, 2024-2025)
- [ ] Manipulação de resumptionToken (paginação)
- **Status:** pending

### Phase 3: CLI e Parâmetros
- [ ] Interface CLI com argparse/click
- [ ] Parâmetros: --url, --from, --until, --format, --output, --sets
- [ ] Filtro por autores (busca local no Dublin Core creator)
- [ ] Filtro por edições (set spec OAI-PMH)
- **Status:** pending

### Phase 4: Exportação e PDFs
- [ ] Exportadores: JSON (padrão), CSV, BibTeX
- [ ] Download de PDFs (construção de URL, fallback scraping)
- [ ] Organização de diretórios de saída
- **Status:** pending

### Phase 5: Robustez e Documentação
- [ ] Tratamento de erros e barreiras (rate limiting, timeouts)
- [ ] Retry/backoff para requests
- [ ] Documentação de uso (README, exemplos)
- [ ] Testes automatizados
- **Status:** pending

## Key Questions
1. ~~O endpoint OAI-PMH da Afro-Ásia responde corretamente?~~ ✅ Sim. 127 registros 2024-2025, Dublin Core com título, autores, resumo, palavras-chave, DOI, data.
2. O OAI-PMH oferece set por edição (issue)? Ou só por seção (Artigos, Resenhas)? → Sets são por SEÇÃO (ART, RES, DOS, etc.), não por edição. Filtrar por edição exigirá scraping da TOC ou parse do datestamp.
3. ~~O Dublin Core via OAI-PMH inclui resumo e palavras-chave?~~ ✅ Sim. `dc:description` = resumo, `dc:subject` = palavras-chave.
4. Como mapear article ID do OAI-PMH para URL de PDF no OJS? → ID OAI = `oai:ojs.periodicos.ufba.br:article/{id}`. URL OJS = `{base_url}/article/view/{id}`. PDF = `{base_url}/article/view/{id}/download` (testar).
5. Precisamos de `curl_cffi` como fallback para sites com proteção anti-bot? → Provavelmente não. OAI-PMH é XML puro. OJS acadêmicos raramente usam proteção pesada.
6. Vale a pena suportar outras plataformas além de OJS (Scielo, SciELO Preprints)? → Avaliar na Phase 5. OAI-PMH é padrão inter-plataforma.

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| OAI-PMH como fonte primária | Protocolo padrão do OJS, gratuito, suporta recorte temporal e sets |
| Scraping leve como complemento | Para dados não disponíveis via OAI-PMH (PDFs, capas, etc.); usar requests+BS4, sem headless browser |
| CLI com argparse | Simples, sem dependências extras; evoluir para click se necessário |
| Busca por autores local (não no servidor) | OAI-PMH não suporta busca por autor; filtrar no cliente via Dublin Core creator |
| Não usar código do PKP OHS (GPL v2) | Implementação independente em Python; sem derivação de código PHP; mas licença GPL v3 em alinhamento com o espírito do OHS |
| Referenciar Holmes/OHS como inspiração conceitual | Citar Oddone & Andrade (2006) — validação do método OAI-PMH para periódicos brasileiros |
| Licença GPL v3 | Diálogo com a tradição do PKP OHS (GPL v2); software livre forte para projeto acadêmico de dados abertos |

## Errors Encountered

Nenhum erro histórico mantido neste plano.

## Notes
- Atualizar status das fases conforme progresso
- Reler este plano antes de decisões maiores
- Testar endpoint OAI-PMH o mais cedo possível (validação da arquitetura)
- Verificar se `sickle` (lib Python OAI-PMH) é viável ou se é melhor implementar client do zero