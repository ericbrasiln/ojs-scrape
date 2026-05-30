# AGENTS.md

Guia para agentes de código que forem usar ou modificar este repositório.

## Escopo do projeto

`ojs-scrape` é uma ferramenta Python para coletar metadados estruturados de periódicos OJS.

Fonte primária: OAI-PMH.

Complemento permitido: scraping leve de TOC com `requests` + BeautifulSoup para mapear artigo → edição, seção, páginas e PDF.

Não use Firecrawl, Selenium ou navegador headless para metadados que já existem via OAI-PMH.

## Contexto metodológico

Este pacote nasceu de uma comparação entre scraping comercial e protocolo aberto.

Firecrawl foi testado e descartado para coleta sistemática de OJS porque consome créditos e duplica dados já expostos pelo OAI-PMH.

A decisão metodológica central é: primeiro usar protocolos abertos; só complementar com scraping leve quando o OAI-PMH não traz o dado.

## Processo de desenvolvimento com Hermes Agent

O código inicial, a refatoração e os testes foram conduzidos com apoio do Hermes Agent, em interação com o pesquisador Eric Brasil.

O processo usado foi:

1. validar empiricamente endpoints OAI-PMH reais;
2. implementar a menor CLI funcional;
3. testar com revistas concretas, especialmente Afro-Ásia e História da Historiografia;
4. transformar falhas reais em testes de regressão;
5. refatorar para padrões atuais de Python;
6. passar quality gates antes de commit.

Hermes Agent foi usado como ferramenta de trabalho, não como fonte de autoridade acadêmica.

Decisões de método, escopo e interpretação histórica pertencem ao pesquisador.

## Comandos básicos

Instalar dependências:

```bash
uv sync
```

Ajuda da CLI:

```bash
uv run ojs-scrape --help
```

Coleta básica:

```bash
uv run ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  -o output.json
```

Exportar CSV:

```bash
uv run ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --format csv \
  -o output.csv
```

Filtrar por edições OJS:

```bash
uv run ojs-scrape "https://periodicos.ufba.br/index.php/afroasia" \
  --from 2024 \
  --until 2025 \
  --issues 2785 2858 2964 \
  -o output.json
```

## Quality gate obrigatório

Antes de declarar uma mudança concluída, rode:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest -q
uv build
```

Quando a mudança afetar rede, OAI-PMH, TOC ou integração com OJS real, rode também:

```bash
uv run pytest -q --run-integration
```

## Padrões de código

- Python `>=3.12`.
- Layout `src/`.
- `pyproject.toml` é a fonte de configuração.
- Use `dataclass(slots=True)` para modelos simples.
- Mantenha tipagem compatível com MyPy strict.
- Use Ruff para format e lint.
- Use `requests` e BeautifulSoup para scraping leve.
- Não adicione `lxml` sem necessidade real no código.
- Não adicione dependências pesadas para resolver casos que OAI-PMH cobre.

## Semântica de datas

Cuidado: no protocolo OAI-PMH, `from` e `until` filtram por `datestamp`, isto é, data de atualização do registro.

Para o usuário da CLI, `--from` e `--until` devem significar data de publicação.

Por isso o pacote usa OAI-PMH como pré-filtro e aplica filtro local por `dc:date`.

Não remova esse filtro local.

Sem ele, artigos antigos atualizados recentemente entram em recortes como `--from 2020`.

## XML OAI-PMH inválido

Algumas instalações OJS retornam caracteres proibidos por XML 1.0 dentro de campos Dublin Core.

Caso validado: História da Historiografia retornou `\x02` dentro de `dc:description`.

O parser deve:

1. tentar interpretar o XML cru;
2. se falhar por `ElementTree.ParseError`, remover caracteres de controle inválidos;
3. tentar interpretar novamente;
4. registrar warning.

Não transforme isso em silêncio total.

## Sets, edições e TOC

Sets OAI-PMH normalmente representam seções, não edições.

Exemplos:

- `afroasia:ART`
- `afroasia:DOS`
- `revista:AR`
- `revista:ED`

Não assuma que existe `set=issue:69`.

Para filtrar edições, use a TOC:

```text
{base_url}/issue/view/{issue_id}
```

Depois cruze os IDs de artigo com os registros OAI-PMH.

## Exportação

JSON preserva todos os campos do modelo `Article`.

CSV é propositalmente reduzido para uso tabular.

BibTeX deve manter escaping básico para caracteres especiais.

Registros OAI-PMH com `status="deleted"` não devem ser exportados.

A CLI deve informar a diferença entre registros coletados e artigos exportados.

## Arquivos gerados

Não versione saídas locais de coleta.

Diretórios e arquivos de dados devem ficar em `data/`, que está no `.gitignore`.

Também não versione PDFs baixados em massa.

## Estrutura principal

```text
src/ojs_scrape/
├── cli.py        # argparse CLI
├── oaipmh.py     # cliente OAI-PMH e parser XML
├── models.py     # Article, OJSJournal, OAISet
├── filters.py    # filtros por autor, edição, set e data de publicação
├── toc.py        # scraping leve de TOC OJS
├── pdf.py        # download de PDFs
├── exporters.py  # JSON, CSV, BibTeX
└── py.typed      # marcador PEP 561
```

## Testes

Testes unitários não devem depender de rede.

Testes com rede devem usar o marcador `integration` e só rodar com:

```bash
uv run pytest -q --run-integration
```

Quando corrigir bug encontrado em revista real, adicione teste de regressão sem rede sempre que possível.

## Git

Branch principal: `main`.

Nunca crie nem publique `master`.

Commits devem usar mensagens convencionais:

```text
feat: ...
fix: ...
refactor: ...
docs: ...
test: ...
chore: ...
```

Não faça push sem pedido explícito do usuário.

## Para agentes Hermes

Se estiver trabalhando dentro do Hermes Agent:

- carregue a skill `ojs-scrape` antes de editar este repositório;
- use ferramentas de arquivo para leitura e patch;
- rode comandos reais para validar;
- atualize a skill `ojs-scrape` se descobrir uma regra reutilizável;
- registre fatos permanentes apenas quando forem úteis em sessões futuras.

## Critério de conclusão

Uma tarefa só está concluída quando houver:

1. artefato criado ou código alterado;
2. validação executada com saída real;
3. documentação atualizada, se a semântica mudou;
4. working tree limpo ou status Git explicado ao usuário.
