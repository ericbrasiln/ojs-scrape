# Roadmap

Este roadmap registra o plano público de desenvolvimento do `ojs-scrape`.

Ele substitui logs internos de sessão e planos de trabalho que serviram à fase inicial do projeto.

## Status atual

`ojs-scrape` é um pacote Python e uma ferramenta CLI em estágio alpha.

O pacote já permite:

- coletar metadados de periódicos OJS com OAI-PMH público;
- filtrar artigos por data de publicação, autor, set/seção e IDs de edição OJS;
- exportar dados em JSON, CSV e BibTeX;
- enriquecer registros com dados de TOC quando necessário;
- baixar PDFs públicos quando os galleys OJS são acessíveis;
- testar downloads de PDF com amostragem limitada por `--pdf-limit`;
- validar o comportamento com testes unitários, integração marcada e quality gates locais.

A versão atual não promete compatibilidade universal com qualquer instalação OJS.

## v0.1.0 — primeira publicação pública

Objetivo: publicar uma versão alpha usável e citável.

Tarefas principais:

- revisar metadados de pacote para PyPI;
- validar wheel e sdist em ambiente limpo;
- testar publicação no TestPyPI;
- testar instalação a partir do TestPyPI;
- criar tag `v0.1.0`;
- publicar no PyPI real;
- criar release no GitHub com resumo e limites conhecidos.

Critério de conclusão:

- instalação via `pip install ojs-scrape` funciona;
- `ojs-scrape --help` funciona após instalação limpa;
- a documentação pública está no ar;
- `CITATION.cff` acompanha o repositório e o pacote fonte.

## v0.1.x — estabilização pós-publicação

Objetivo: corrigir problemas encontrados por primeiros usuários e por novos testes com periódicos reais.

Possíveis frentes:

- corrigir bugs de instalação e dependências;
- ajustar documentação a partir de feedback de uso;
- ampliar testes de regressão para OJS reais que apresentem variantes de XML, TOC ou galley;
- melhorar mensagens de erro da CLI;
- documentar melhor falhas de PDF e caminhos de retomada;
- revisar exportação BibTeX com casos de acentuação, subtítulos e nomes compostos.

## v0.2.0 — compatibilidade OJS ampliada

Objetivo: aumentar a cobertura de instalações OJS com configurações diferentes.

Possíveis frentes:

- melhorar descoberta automática de endpoint OAI-PMH;
- ampliar padrões de parsing de TOC;
- ampliar padrões de detecção de galley PDF;
- melhorar identificação de seção, páginas e edição;
- oferecer relatório estruturado de falhas de PDF;
- adicionar mais fixtures HTML/XML derivadas de casos reais, sem depender de rede nos testes unitários;
- melhorar a UX de retomada de downloads longos.

## Futuro

Possibilidades ainda não priorizadas:

- suporte opcional a outros formatos OAI-PMH quando disponíveis, além de `oai_dc`;
- relatórios resumidos em Markdown ou HTML;
- integração com fluxos de revisão bibliográfica e bases de pesquisa;
- comandos auxiliares para diagnóstico de um periódico OJS antes da coleta;
- empacotamento de exemplos reprodutíveis para ensino e oficinas.

## Fora de escopo

O projeto não pretende:

- acessar dados privados;
- contornar login, paywall, embargo, CAPTCHA ou bloqueios institucionais;
- alterar dados em servidores de periódicos;
- usar scraping pesado para metadados já expostos por OAI-PMH;
- substituir curadoria humana, revisão bibliográfica ou julgamento acadêmico;
- garantir download de PDFs quando a revista não oferece galleys públicos acessíveis.

## Critério metodológico permanente

A regra de método permanece:

1. usar OAI-PMH como fonte primária para metadados;
2. usar scraping leve apenas como complemento para dados que o protocolo não expõe diretamente;
3. transformar falhas reais em testes de regressão;
4. distinguir fato verificado, inferência e limite conhecido na documentação.
