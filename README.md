# marinasilva180.com.br

Página estática que redireciona `marinasilva180.com.br` (domínio remetente dos e-mails da campanha)
para o site oficial, `https://marinasilva.org.br/`. Hospedada no GitHub Pages.

- `index.html` e `404.html`: redirecionamento imediato (meta refresh + JavaScript), com `canonical`
  apontando para o site oficial e `noindex` para não competir no Google.
- `CNAME`: domínio personalizado do GitHub Pages.

DNS (registro.br): 4 registros A da raiz para os IPs do GitHub Pages e `www` em CNAME para
`guipfranco.github.io`.
