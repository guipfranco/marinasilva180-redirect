"""Gera o site estático de marinasilva180.com.br a partir de paginas/*.md.

Uso: python build.py
Saída: index.html, <slug>/index.html, robots.txt, sitemap.xml, 404.html (raiz do repo,
que é o que o GitHub Pages serve).

Cada arquivo em paginas/ começa com um cabeçalho de linhas `chave: valor`, uma linha em
branco, e o corpo em Markdown. Chaves: slug (vazio = página inicial), titulo (title da aba),
pergunta (h1), descricao (meta description), resposta (a resposta curta, vai no bloco do topo
e no JSON-LD), tipo (Article ou FAQPage), atualizado (AAAA-MM-DD). Numa página FAQPage, cada
`## ` vira uma pergunta do schema e o texto até o próximo `## ` vira a resposta.
"""
import datetime
import json
import pathlib
import re
import sys

import markdown

RAIZ = pathlib.Path(__file__).parent
DOMINIO = "https://marinasilva180.com.br"
CNPJ = ""  # CNPJ da campanha; vazio enquanto o jurídico não confirmar o texto do rodapé
NOME = "Marina Silva 180"

PAGINAS = sorted(RAIZ.glob("paginas/*.md"))

MD = markdown.Markdown(extensions=["tables", "attr_list"])

CSS = """
:root{--verde:#004a3e;--areia:#ffebc5;--areia-card:#fde3bf;--amarelo:#fec800;--escuro:#1a2b35;
--azul:#1863dc;--teal-texto:#1d7a61;--branco:#fff}
*{box-sizing:border-box}
html{font-size:17px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--areia);color:var(--escuro);font-family:"Plus Jakarta Sans","Segoe UI",Arial,sans-serif;line-height:1.55}
a{color:var(--azul)}
header.topo{background:var(--verde);color:var(--areia);padding:16px}
header.topo .linha{max-width:860px;margin:0 auto;display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap}
header.topo a{color:var(--areia);text-decoration:none}
header.topo .marca{font-family:Montserrat,"Arial Black",Arial,sans-serif;font-weight:900;font-size:22px;letter-spacing:-.5px}
header.topo .marca b{color:var(--amarelo)}
header.topo nav a{font-size:15px;margin-left:16px}
main{max-width:860px;margin:0 auto;padding:32px 16px 48px}
h1{font-family:Rubik,"Segoe UI",Arial,sans-serif;font-weight:800;color:var(--verde);font-size:clamp(28px,5vw,40px);line-height:1.15;margin:0 0 16px;letter-spacing:-.3px}
h2{font-family:Rubik,"Segoe UI",Arial,sans-serif;font-weight:700;color:var(--verde);font-size:24px;line-height:1.2;margin:40px 0 12px}
h3{font-family:Rubik,"Segoe UI",Arial,sans-serif;font-weight:700;font-size:19px;margin:28px 0 8px}
p,li{max-width:70ch}
.resposta{background:var(--verde);color:var(--areia);border-radius:16px;padding:20px 24px;margin:0 0 32px;font-size:19px;line-height:1.45}
.resposta p{margin:0;max-width:none}
.resposta strong,.resposta b{color:var(--amarelo)}
.resposta a{color:var(--amarelo)}
.hero{display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:center;background:var(--verde);color:var(--areia);border-radius:16px;padding:24px;margin:0 0 32px}
.hero .numero{font-family:Montserrat,"Arial Black",Arial,sans-serif;font-weight:900;font-size:clamp(72px,16vw,128px);line-height:.9;color:var(--amarelo);letter-spacing:-4px}
.hero p{margin:0;font-size:19px;max-width:none}
.hero a{color:var(--amarelo)}
@media (max-width:520px){.hero{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:15px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid rgba(0,74,62,.25);vertical-align:top}
th{color:var(--verde)}
tr.dest td{background:var(--areia-card);font-weight:700}
.atualizado{font-size:14px;color:var(--teal-texto);margin:0 0 24px}
.fontes{font-size:15px}
.fontes li{margin-bottom:4px}
footer{background:var(--verde);color:var(--areia);padding:32px 16px;font-size:14px}
footer .linha{max-width:860px;margin:0 auto}
footer a{color:var(--amarelo)}
footer p{max-width:none;margin:0 0 8px}
ul.lista-paginas{padding-left:20px}
ul.lista-paginas li{margin-bottom:8px}
:focus-visible{outline:3px solid var(--amarelo);outline-offset:2px}
"""

FONTES_HEAD = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Plus+Jakarta+Sans:wght@400;600;700&family=Rubik:wght@700;800&display=swap" rel="stylesheet">"""


def ler(caminho):
    texto = caminho.read_text(encoding="utf-8")
    cab, corpo = texto.split("\n\n", 1)
    meta = {}
    for linha in cab.splitlines():
        chave, _, valor = linha.partition(":")
        meta[chave.strip()] = valor.strip()
    meta["corpo"] = corpo
    meta["slug"] = meta.get("slug", "")
    meta["url"] = DOMINIO + "/" + (meta["slug"] + "/" if meta["slug"] else "")
    return meta


def faq_items(corpo):
    itens = []
    partes = re.split(r"^## +", corpo, flags=re.M)
    for parte in partes[1:]:
        pergunta, _, resposta = parte.partition("\n")
        resposta = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", resposta)
        resposta = re.sub(r"[*_`]", "", resposta).strip()
        itens.append({"@type": "Question", "name": pergunta.strip(),
                      "acceptedAnswer": {"@type": "Answer", "text": resposta}})
    return itens


def jsonld(meta):
    base = {
        "@context": "https://schema.org",
        "@type": meta.get("tipo", "Article"),
        "headline": meta["pergunta"],
        "description": meta["descricao"],
        "url": meta["url"],
        "inLanguage": "pt-BR",
        "dateModified": meta["atualizado"],
        "datePublished": meta.get("publicado", meta["atualizado"]),
        "author": {"@type": "Organization", "name": "Campanha Marina Silva 180, Senado por São Paulo",
                   "url": DOMINIO},
        "publisher": {"@type": "Organization", "name": "Campanha Marina Silva 180", "url": DOMINIO},
        "about": {"@type": "Person", "name": "Marina Silva", "sameAs": [
            "https://marinasilva.org.br/", "https://pt.wikipedia.org/wiki/Marina_Silva",
            "https://www.instagram.com/marinasilvaoficial/", "https://www.youtube.com/@msilvaonline"]},
    }
    if meta.get("tipo") == "FAQPage":
        base["mainEntity"] = faq_items(meta["corpo"])
    return base


def nav(paginas, atual):
    itens = []
    for p in paginas:
        if p["slug"] and p.get("menu"):
            itens.append(f'<a href="/{p["slug"]}/">{p["menu"]}</a>')
    return "\n".join(itens)


def render(meta, paginas):
    MD.reset()
    corpo_html = MD.convert(meta["corpo"])
    resposta = MD.convert(meta["resposta"]) if meta.get("resposta") else ""
    if meta["slug"]:
        topo = f'<h1>{meta["pergunta"]}</h1>\n<div class="resposta">{resposta}</div>'
    else:
        topo = (f'<h1>{meta["pergunta"]}</h1>\n<div class="hero"><div class="numero">180</div>'
                f'<div>{resposta}</div></div>')
    data = datetime.date.fromisoformat(meta["atualizado"]).strftime("%d/%m/%Y")
    rodape_cnpj = f" CNPJ {CNPJ}." if CNPJ else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta["titulo"]}</title>
<meta name="description" content="{meta["descricao"]}">
<link rel="canonical" href="{meta["url"]}">
<meta property="og:title" content="{meta["titulo"]}">
<meta property="og:description" content="{meta["descricao"]}">
<meta property="og:url" content="{meta["url"]}">
<meta property="og:type" content="article">
<meta property="og:locale" content="pt_BR">
{FONTES_HEAD}
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(jsonld(meta), ensure_ascii=False)}</script>
</head>
<body>
<header class="topo"><div class="linha">
<a class="marca" href="/">Marina Silva <b>180</b></a>
<nav>{nav(paginas, meta)}</nav>
</div></header>
<main>
{topo}
<p class="atualizado">Atualizado em {data}. Todo fato desta página tem fonte com link no fim.</p>
{corpo_html}
</main>
<footer><div class="linha">
<p>Propaganda eleitoral. Site mantido pela campanha de Marina Silva ao Senado por São Paulo, Rede Sustentabilidade, número 180, Coligação Desperta São Paulo.{rodape_cnpj} Endereço comunicado à Justiça Eleitoral. Site oficial: <a href="https://marinasilva.org.br/">marinasilva.org.br</a>.</p>
<p>Este site existe para responder, com fontes, as perguntas que as pessoas fazem sobre a candidatura. Encontrou um erro? Escreva para <a href="mailto:equipe@marinasilva180.com.br">equipe@marinasilva180.com.br</a>.</p>
</div></footer>
</body>
</html>
"""


def main():
    paginas = [ler(p) for p in PAGINAS]
    for meta in paginas:
        destino = RAIZ / meta["slug"] / "index.html" if meta["slug"] else RAIZ / "index.html"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(render(meta, paginas), encoding="utf-8")
        print("ok", destino.relative_to(RAIZ))

    urls = "\n".join(
        f"  <url><loc>{m['url']}</loc><lastmod>{m['atualizado']}</lastmod></url>" for m in paginas)
    (RAIZ / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n",
        encoding="utf-8")

    bots = ["*", "Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot",
            "Perplexity-User", "ClaudeBot", "Claude-User", "anthropic-ai", "Google-Extended",
            "Applebot", "Amazonbot", "DuckDuckBot", "YouBot", "Meta-ExternalAgent"]
    robots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {DOMINIO}/sitemap.xml\n"
    (RAIZ / "robots.txt").write_text(robots, encoding="utf-8")

    (RAIZ / "404.html").write_text(render({
        "slug": "404", "url": DOMINIO + "/404.html", "titulo": "Página não encontrada | Marina Silva 180",
        "pergunta": "Essa página não existe", "descricao": "Página não encontrada.",
        "resposta": "O endereço não existe. A página inicial lista tudo o que há no site: "
                    f"[marinasilva180.com.br]({DOMINIO}/).",
        "corpo": "", "atualizado": datetime.date.today().isoformat()}, paginas), encoding="utf-8")
    print("ok sitemap.xml robots.txt 404.html")


if __name__ == "__main__":
    sys.exit(main())
