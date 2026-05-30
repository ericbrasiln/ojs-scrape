# PDFs

O download de PDFs é opcional.

Metadados são mais confiáveis que PDFs, porque OAI-PMH é protocolo padronizado.
PDFs dependem da configuração local da revista, dos galleys e das permissões de acesso.

## Teste por amostragem

Antes de baixar uma coleção inteira, teste poucos PDFs:

```bash
ojs-scrape "https://rbs.sbsociologia.com.br/rbs/index" \
  --from 2026 \
  --until 2026-05-30 \
  --pdf \
  --pdf-limit 2 \
  --pdf-dir pdfs_teste/ \
  -o rbs_2026.json
```

Se funcionar, rode sem `--pdf-limit`.

## Lote completo

```bash
ojs-scrape "https://rbs.sbsociologia.com.br/rbs/index" \
  --from 2020 \
  --until 2026-05-30 \
  --pdf \
  --pdf-dir pdfs/ \
  -o rbs_2020_2026.json
```

## Como o pacote encontra PDFs

A sequência de tentativas inclui:

1. URL direta do artigo;
2. link de galley na página do artigo;
3. conversão de `/article/view/{id}/{galley}` para `/article/download/{id}/{galley}`;
4. priorização de galleys oficiais sobre PDFs externos citados em referências.

Galleys podem ser:

- numéricos, como `579`;
- textuais, como `pdf_53`;
- faixas ou rótulos, como `759-775`.

## Falhas esperadas

O download pode falhar quando:

- o artigo não tem PDF;
- o PDF exige login;
- o PDF está sob embargo;
- o link está quebrado;
- o tema/plugin OJS altera o padrão dos galleys;
- há bloqueio por IP, CAPTCHA, Cloudflare ou rate limit agressivo.
