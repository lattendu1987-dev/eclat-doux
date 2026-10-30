"""Générateur du site statique de guides d'achat (affiliation Amazon.fr).

`python -m eclat site` écrit le site dans public/ à partir de config/site.toml.
Aucun cookie, aucun outil de mesure tiers : pas de bannière de consentement nécessaire (RGPD).
"""

from __future__ import annotations

import html
import shutil
from pathlib import Path
from urllib.parse import quote_plus

from . import config

ASSETS = Path(__file__).resolve().parent / "site_assets"
DISCLOSURE = (
    "En tant que Partenaire Amazon, je réalise un bénéfice sur les achats remplissant les conditions "
    "requises, sans frais supplémentaires pour vous. Nous n'avons pas testé "
    "chaque produit : nos guides expliquent les critères à vérifier."
)


def e(s: str) -> str:
    return html.escape(s, quote=True)


def amazon_url(query: str, tag: str) -> str:
    url = f"https://www.amazon.fr/s?k={quote_plus(query)}"
    return f"{url}&tag={quote_plus(tag)}" if tag else url


def page(site: dict, title: str, description: str, body: str, path: str, image: str = "baume-levres-gercees") -> str:
    full_title = title if title == site["name"] else f"{title} · {site['name']}"
    canonical = site["base_url"].rstrip("/") + "/" + ("" if path == "index.html" else path)
    return f"""<!doctype html>
<html lang="fr-FR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(site['base_url'].rstrip('/') + '/pins/' + image + '.png')}">
<meta property="og:image:width" content="1000">
<meta property="og:image:height" content="1500">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:locale" content="fr_FR">
<meta name="theme-color" content="#3a1d2e">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌸</text></svg>">
<link rel="alternate" type="application/rss+xml" title="Éclat Doux" href="feed.xml">
<link rel="stylesheet" href="style.css">
<script>document.documentElement.classList.add("js")</script>
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="top">
  <a class="brand" href="./"><span aria-hidden="true">🌸</span> {e(site['name'])}</a>
  <nav aria-label="Navigation principale"><a href="./#guides">Guides</a><a href="meilleures-ventes.html">Top ventes</a><a href="a-propos.html">À propos</a><a href="en/">EN</a><a href="pl/">PL</a></nav>
</header>
<div class="disclosure" role="note">{e(DISCLOSURE)} <a href="divulgation.html">En savoir plus</a></div>
<main id="contenu">
{body}
</main>
<footer class="foot">
  <p><strong>{e(site['name'])}</strong> — {e(site['tagline'])}</p>
  <p><a href="divulgation.html">Divulgation</a> · <a href="confidentialite.html">Confidentialité</a> · <a href="mentions-legales.html">Mentions légales</a> · <a href="a-propos.html">À propos</a></p>
  <p class="muted">Mis à jour le {e(site['updated'])}. Amazon et le logo Amazon sont des marques d'Amazon.com, Inc. ou de ses filiales.</p>
</footer>
<script src="stores.js" defer></script>
<script src="app.js" defer></script>
</body>
</html>
"""


def guide_card(g: dict) -> str:
    return f"""<a class="card reveal" href="{e(g['slug'])}.html">
  <span class="card-icon" aria-hidden="true">{e(g['icon'])}</span>
  <h3>{e(g['title'])}</h3>
  <p>{e(g['description'])}</p>
  <span class="card-cta">Lire le guide →</span>
</a>"""


def index_body(site: dict, guides: list[dict]) -> str:
    cards = "\n".join(guide_card(g) for g in guides)
    return f"""<section class="hero">
  <div class="snow" aria-hidden="true"></div>
  <p class="eyebrow">Guides d'achat indépendants</p>
  <h1>Le froid dessèche la peau.<br><span>Choisissez les bons soins, sans vous tromper.</span></h1>
  <p class="lead">{e(site['tagline'])} Des critères clairs, sans faux avis, pour acheter une seule fois et bien.</p>
  <a class="btn" href="#guides">Voir les guides</a>
</section>
<section id="guides" class="section">
  <h2 class="reveal">Nos guides</h2>
  <div class="grid">
{cards}
  </div>
</section>
<section class="section promise reveal">
  <h2>Notre façon de faire</h2>
  <ul class="checks">
    <li>Nous expliquons <strong>quoi vérifier</strong> avant d'acheter, selon vos besoins réels.</li>
    <li>Nous n'inventons <strong>ni avis ni tests</strong>.</li>
    <li>Nous n'affichons <strong>pas de prix</strong> qui pourraient être périmés : vous les voyez à jour sur Amazon.fr.</li>
  </ul>
</section>"""


def guide_body(g: dict, tag: str) -> str:
    parts = [f"""<article class="guide">
<header class="guide-head reveal">
  <p class="eyebrow"><span aria-hidden="true">{e(g['icon'])}</span> Guide d'achat</p>
  <h1>{e(g['title'])}</h1>
  <p class="lead">{e(g['intro'])}</p>
</header>"""]
    for s in g.get("sections", []):
        parts.append(f'<section class="block reveal"><h2>{e(s["h"])}</h2>')
        for p in s.get("p", []):
            parts.append(f"<p>{e(p)}</p>")
        if s.get("bullets"):
            parts.append('<ul class="checks">' + "".join(f"<li>{e(b)}</li>" for b in s["bullets"]) + "</ul>")
        parts.append("</section>")
    picks = "".join(
        f"""<li class="pick reveal"><div><h3>{e(p['label'])}</h3><p>{e(p['why'])}</p></div>
<a class="btn btn-small" href="{e(amazon_url(p['query'], tag))}" rel="sponsored nofollow noopener" target="_blank">Voir les prix sur Amazon.fr</a>
<a class="btn btn-small btn-ali" hidden href="#" data-ali="{e(p['query'])}" rel="sponsored nofollow noopener" target="_blank">Voir aussi sur AliExpress</a></li>"""
        for p in g.get("picks", [])
    )
    parts.append(f'<section class="block"><h2 class="reveal">Où chercher</h2><ul class="picks">{picks}</ul>'
                 f'<p class="muted small">Liens d\'affiliation. Les prix et la disponibilité changent : vérifiez-les sur Amazon.fr.</p></section>')
    if g.get("faq"):
        faq = "".join(f"<details class=\"reveal\"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>" for f in g["faq"])
        parts.append(f'<section class="block"><h2 class="reveal">Questions fréquentes</h2>{faq}</section>')
    parts.append('<p class="back"><a href="./#guides">← Tous les guides</a></p></article>')
    return "\n".join(parts)


STATIC_PAGES = {
    "divulgation.html": ("Divulgation", "Comment ce site est financé.", """<article class="guide prose">
<h1>Divulgation</h1>
<p>Ce site participe au Programme Partenaires d'Amazon EU, un programme d'affiliation conçu pour permettre à des sites de percevoir une rémunération grâce à la création de liens vers Amazon.fr.</p>
<p>Selon votre pays, certains liens mènent aussi vers AliExpress, via le réseau d'affiliation Awin.</p>
<p>Quand vous achetez après avoir cliqué sur l'un de nos liens, nous pouvons recevoir une commission. Le prix que vous payez ne change pas.</p>
<p>Nous ne recevons ni produits gratuits ni paiements de marques. Nos guides présentent des critères de choix ; ils ne prétendent pas avoir testé chaque produit.</p>
</article>"""),
    "confidentialite.html": ("Confidentialité", "Quels renseignements ce site recueille.", """<article class="guide prose">
<h1>Politique de confidentialité</h1>
<p><strong>En bref : ce site ne recueille aucun renseignement personnel.</strong></p>
<h2>Ce que nous ne faisons pas</h2>
<ul class="checks"><li>Aucun formulaire, aucun compte, aucune newsletter.</li><li>Aucun cookie ni outil de mesure d'audience déposé par ce site.</li><li>Aucune publicité ciblée.</li></ul>
<h2>Hébergement</h2>
<p>Le site est hébergé par GitHub Pages (GitHub, Inc.), qui peut traiter des données techniques comme l'adresse IP pour assurer la sécurité du service, selon sa propre politique de confidentialité.</p>
<h2>Liens vers Amazon.fr</h2>
<p>Quand vous cliquez sur un lien vers Amazon.fr, vous quittez ce site. Amazon peut alors utiliser des cookies, notamment pour attribuer la commission, selon sa propre politique de confidentialité.</p>
<h2>Questions</h2>
<p>Pour toute question sur la protection des renseignements personnels, ouvrez une demande sur la <a href="https://github.com/lattendu1987-dev/eclat-doux/issues">page du projet</a>.</p>
</article>"""),
    "a-propos.html": ("À propos", "Qui sommes-nous et comment nos guides sont faits.", """<article class="guide prose">
<h1>À propos</h1>
<p>Éclat Doux publie des guides d'achat de soins et de beauté, avec une attention particulière à l'hiver : froid, vent, chauffage et air sec.</p>
<h2>Comment nos guides sont faits</h2>
<ul class="checks"><li>Nous partons des besoins concrets (lèvres gercées, mains sèches, peau qui tiraille).</li><li>Nous listons les critères vérifiables : type de peau, ingrédients clés, texture, format, précautions d'emploi.</li><li>Nous renvoyons vers une recherche Amazon.fr pour comparer les offres à jour.</li></ul>
<p>Nous ne publions ni avis inventés ni classements payés.</p>
</article>"""),
    "mentions-legales.html": ("Mentions légales", "Éditeur et hébergeur du site.", """<article class="guide prose">
<h1>Mentions légales</h1>
<h2>Éditeur</h2>
<p>Site édité par un particulier. Conformément à la loi pour la confiance dans l'économie numérique (LCEN), ses coordonnées ont été communiquées à l'hébergeur.</p>
<p>Contact : via la <a href="https://github.com/lattendu1987-dev/eclat-doux/issues">page du projet</a>.</p>
<h2>Hébergeur</h2>
<p>GitHub, Inc. (service GitHub Pages) — 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis — github.com</p>
<h2>Affiliation</h2>
<p>En tant que Partenaire Amazon, l'éditeur réalise un bénéfice sur les achats remplissant les conditions requises. Voir la page <a href="divulgation.html">Divulgation</a>.</p>
</article>"""),
    "404.html": ("Page introuvable", "Cette page n'existe pas.", """<section class="hero small"><h1>Oups, cette page n'existe pas.</h1><a class="btn" href="./">Retour à l'accueil</a></section>"""),
}


def kit_page(site: dict, guides: list[dict]) -> str:
    """Page privée (non référencée) : images Pinterest et messages Facebook prêts à publier."""
    promo = config.load_toml("promo.toml") if (config.CONFIG_DIR / "promo.toml").exists() else {}
    base = site["base_url"].rstrip("/") + "/"
    pins = []
    for g in guides:
        link = f"{base}{g['slug']}.html"
        desc = f"{g['description']} Guide gratuit, sans faux avis."
        pins.append(f"""<section class="kit reveal"><img src="pins/{e(g['slug'])}.png" alt="{e(g['title'])}" loading="lazy" width="1000" height="1500">
<p><a class="btn btn-small" href="pins/{e(g['slug'])}.png" download>Enregistrer l'image</a></p>
<p class="label">Titre</p><div class="copy"><span>{e(g['title'].split(' : ')[0])}</span><button type="button">Copier</button></div>
<p class="label">Description</p><div class="copy"><span>{e(desc)}</span><button type="button">Copier</button></div>
<p class="label">Lien</p><div class="copy"><span>{e(link)}</span><button type="button">Copier</button></div></section>""")
    posts = "".join(
        f"""<section class="kit reveal"><h3>{e(fb['titre'])}</h3><div class="copy"><span style="white-space:pre-line">{e(fb['texte'])}</span><button type="button">Copier</button></div></section>"""
        for fb in promo.get("facebook", [])
    )
    body = f"""<article class="guide"><h1>Kit de partage</h1>
<p class="lead">Page de travail, non référencée. Pinterest : enregistrez l'image, puis créez une épingle avec le titre, la description et le lien. Facebook : copiez un message et publiez-le dans un groupe qui accepte ce type de partage.</p>
<h2>Épingles automatiques (Pinterest)</h2><section class="kit reveal">
<p>Sur pinterest.fr (version ordinateur) : Paramètres → « Importer du contenu » / « Création d'Épingles en masse » → importez le fichier.</p>
<p><a class="btn btn-small" href="epingles-toutes.csv" download>Fichier : toutes les épingles</a></p>
<p><a class="btn btn-small" href="epingles-semaine.csv" download>Fichier : épingles de la semaine (FR + EN)</a></p>
<p><a class="btn btn-small" href="epingles-anglais-toutes.csv" download>Fichier : toutes les épingles en anglais</a></p></section>
<h2>Photo de profil</h2><section class="kit reveal"><img src="logo.png" alt="Logo Éclat Doux" width="800" height="800" style="max-width:240px"><p><a class="btn btn-small" href="logo.png" download>Enregistrer le logo</a></p></section>
<h2>Messages Facebook</h2>{posts}
<h2>Épingles Pinterest</h2>{"".join(pins)}</article>
<script>document.querySelectorAll('.copy button').forEach(function(b){{b.addEventListener('click',function(){{
var t=b.previousElementSibling.innerText;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){{b.textContent='Copié ✓';setTimeout(function(){{b.textContent='Copier'}},1500)}}).catch(function(){{b.textContent='Sélectionnez le texte'}});}})}});</script>"""
    html_page = page(site, "Kit de partage", "Kit de partage", body, "kit-partage.html")
    return html_page.replace('<meta name="description"', '<meta name="robots" content="noindex, nofollow">\n<meta name="description"', 1)


BOARDS = {"coffret-cadeau-beaute-noel": "Idées cadeaux beauté", "calendrier-avent-beaute": "Idées cadeaux beauté"}
DEFAULT_BOARD = "Soins de la peau en hiver"
EN_BOARD = "Soft Glow - Winter Skincare Guides"
DEFAULT_DATE = "2026-10-29"


def pins_rows(site: dict, guides: list[dict], since: str | None = None, *, lang: str = "fr") -> list[list[str]]:
    """Lignes pour « Création d'Épingles en masse » de Pinterest."""
    base = site["base_url"].rstrip("/") + "/"
    if lang == "en":
        img_base = base.rsplit("en/", 1)[0] + "pins/en/"
        sep, suffix, board_of = ":", " Free guide, no fake reviews.", (lambda s: EN_BOARD)
        keywords = "skincare, beauty, winter skin, dry skin, buying guide"
    else:
        img_base = base + "pins/"
        sep, suffix, board_of = " : ", " Guide gratuit, sans faux avis.", (lambda s: BOARDS.get(s, DEFAULT_BOARD))
        keywords = "soin, beauté, peau sèche, hiver, guide d'achat"
    rows = []
    for g in sorted(guides, key=lambda g: g.get("date", DEFAULT_DATE)):
        if g.get("epingle_manuelle"):
            continue
        if since and g.get("date", DEFAULT_DATE) < since:
            continue
        rows.append([
            g["title"].split(sep)[0].strip()[:100],
            f"{img_base}{g['slug']}.png",
            board_of(g["slug"]),
            "",
            (g["description"] + suffix)[:500],
            f"{base}{g['slug']}.html",
            "",
            keywords,
        ])
    return rows


def pins_csv(*parts: list[list[str]]) -> str:
    import csv, io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"])
    for rows in parts:
        w.writerows(rows)
    return buf.getvalue()


def rss_feed(site: dict, guides: list[dict]) -> str:
    """Flux RSS lu par Pinterest pour créer les épingles automatiquement (une par guide)."""
    from datetime import datetime, timezone
    base = site["base_url"].rstrip("/") + "/"
    items = []
    for g in sorted(guides, key=lambda g: g.get("date", site["updated"]), reverse=True):
        if g.get("epingle_manuelle"):
            continue
        d = datetime.strptime(g.get("date", site["updated"]), "%Y-%m-%d").replace(hour=8, tzinfo=timezone.utc)
        link = f"{base}{g['slug']}.html"
        img = f"{base}pins/{g['slug']}.png"
        items.append(f"""  <item>
    <title>{e(g['title'].split(' : ')[0])}</title>
    <link>{e(link)}</link>
    <guid isPermaLink="true">{e(link)}</guid>
    <pubDate>{d.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
    <description>{e(g['description'] + ' Guide gratuit, sans faux avis.')}</description>
    <enclosure url="{e(img)}" type="image/png" length="0"/>
    <media:content url="{e(img)}" medium="image" type="image/png" width="1000" height="1500"/>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
<channel>
  <title>{e(site['name'])}</title>
  <link>{e(base)}</link>
  <description>{e(site['tagline'])}</description>
  <language>fr-FR</language>
{chr(10).join(items)}
</channel>
</rss>
"""


def build(out_dir: Path | None = None) -> Path:
    data = config.load_toml("site.toml")
    site, guides = data["site"], data["guide"]
    tag = site.get("amazon_tag", "")
    out = out_dir or (config.ROOT / "public")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for asset in ASSETS.iterdir():
        shutil.copy(asset, out / asset.name)

    static = config.ROOT / "static"
    if static.exists():
        shutil.copytree(static, out, dirs_exist_ok=True)
    (out / "kit-partage.html").write_text(kit_page(site, guides), encoding="utf-8")

    (out / "index.html").write_text(page(site, site["name"], site["tagline"], index_body(site, guides), "index.html"), encoding="utf-8")
    for g in guides:
        name = f"{g['slug']}.html"
        (out / name).write_text(page(site, g["title"], g["description"], guide_body(g, tag), name, image=g["slug"]), encoding="utf-8")
    for name, (title, desc, body) in STATIC_PAGES.items():
        (out / name).write_text(page(site, title, desc, body, name), encoding="utf-8")

    base = site["base_url"].rstrip("/") + "/"
    from . import bestsellers
    (out / "stores.js").write_text(bestsellers.stores_js(), encoding="utf-8")
    bs = bestsellers.TEXT["fr"]
    (out / "meilleures-ventes.html").write_text(page(site, bs["title"], bs["desc"], bestsellers.body("fr", "www.amazon.fr"), "meilleures-ventes.html"), encoding="utf-8")
    urls = [base] + [f"{base}{g['slug']}.html" for g in guides] + [f"{base}{n}" for n in STATIC_PAGES if n != "404.html"]
    urls.append(f"{base}meilleures-ventes.html")
    from . import site_en
    urls += site_en.build(out / "en")
    from . import site_pl
    urls += site_pl.build(out / "pl")
    sitemap = "\n".join(f"  <url><loc>{e(u)}</loc><lastmod>{site['updated']}</lastmod></url>" for u in urls)
    (out / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}\n</urlset>\n',
        encoding="utf-8")
    (out / "feed.xml").write_text(rss_feed(site, guides), encoding="utf-8")
    from datetime import date, timedelta
    # Guides publiés depuis le dernier import du samedi (le samedi précédant la date de mise à jour).
    upd = date.fromisoformat(site["updated"])
    last_saturday = upd - timedelta(days=((upd.weekday() - 5) % 7) or 7)
    week_ago = (last_saturday + timedelta(days=1)).isoformat()
    en = config.load_toml("site_en.toml")
    (out / "epingles-toutes.csv").write_text(pins_csv(pins_rows(site, guides)), encoding="utf-8")
    (out / "epingles-anglais-toutes.csv").write_text(pins_csv(pins_rows(en["site"], en["guide"], lang="en")), encoding="utf-8")
    (out / "epingles-semaine.csv").write_text(pins_csv(
        pins_rows(site, guides, since=week_ago),
        pins_rows(en["site"], en["guide"], since=week_ago, lang="en")), encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /kit-partage.html\nSitemap: {base}sitemap.xml\n", encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    return out
