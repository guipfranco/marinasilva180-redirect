# marinasilva180.com.br

Hub da campanha de Marina Silva ao Senado por São Paulo (Rede, 180): páginas curtas que
respondem, com fonte, o que as pessoas e os assistentes de IA perguntam sobre a candidatura.
Até 2026-10-01 o domínio era só um redirect com `noindex` para marinasilva.org.br.

- Conteúdo: `paginas/*.md` (cabeçalho `chave: valor` + corpo em Markdown). Editar aqui.
- Build: `pip install markdown` e `python build.py`. Gera `index.html`, `<slug>/index.html`,
  `robots.txt`, `sitemap.xml` e `404.html` na raiz, que é o que o GitHub Pages serve.
- Identificação eleitoral: rodapé em toda página (texto em `build.py`; `CNPJ` fica vazio até o
  jurídico confirmar).
- Design: tokens do design system da campanha (`06-design/` no repo marina-senado).

Regras do conteúdo: resposta direta nas primeiras linhas, nenhum fato sem fonte com link,
nenhum ataque a adversário, data de atualização visível, nenhuma pesquisa eleitoral.
