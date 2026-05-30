# Compatibilidade

O `ojs-scrape` não promete funcionar com qualquer periódico OJS.

Formulação segura:

> `ojs-scrape` coleta metadados de periódicos OJS que exponham OAI-PMH público e baixa PDFs públicos quando os artigos usam galleys OJS acessíveis por URL padrão ou detectável.

## Metadados

A coleta de metadados depende de:

- OAI-PMH habilitado;
- endpoint `/oai` acessível sem autenticação;
- respostas XML parseáveis ou recuperáveis após limpeza de caracteres de controle inválidos;
- metadados Dublin Core suficientes;
- ausência de bloqueio por IP, login, CAPTCHA, Cloudflare ou rate limit agressivo.

Se um campo não existir no Dublin Core, o pacote exporta o campo vazio.
Ele não inventa resumo, palavras-chave, DOI ou páginas.

## PDFs

O download de PDFs depende de:

- artigo com PDF disponível;
- PDF público, sem login ou embargo;
- galley OJS com URL padrão ou detectável;
- servidor estável durante downloads sucessivos;
- link não quebrado.

## Revistas já testadas

Validações realizadas durante o desenvolvimento:

- Afro-Ásia;
- História da Historiografia;
- RENBIO;
- Revista Brasileira de Sociologia (RBS).

Esses testes aumentam a confiança, mas não garantem compatibilidade universal.
