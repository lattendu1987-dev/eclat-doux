"""Wersja polska: public/pl/, z config/site_pl.toml. Linki do AliExpress PL przez Awin."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote, quote_plus

from . import config
from .site import e

DISCLOSURE = (
    "Strona zawiera linki afiliacyjne: jeśli kupisz coś po kliknięciu, możemy otrzymać prowizję, "
    "bez dodatkowych kosztów dla Ciebie. Nie testowaliśmy każdego produktu: nasze poradniki wyjaśniają, co sprawdzić przed zakupem."
)


def aliexpress_url(query: str, mid: str, affid: str) -> str:
    """Wyszukiwanie na AliExpress PL; z prowizją przez link Awin, gdy znany jest identyfikator programu."""
    target = f"https://pl.aliexpress.com/w/wholesale-{quote(query.replace(' ', '-'))}.html"
    if not (mid and affid):
        return target
    return f"https://www.awin1.com/cread.php?awinmid={quote_plus(mid)}&awinaffid={quote_plus(affid)}&ued={quote(target, safe='')}"


def page(site: dict, title: str, description: str, body: str, path: str) -> str:
    full_title = title if title == site["name"] else f"{title} · {site['name']}"
    canonical = site["base_url"].rstrip("/") + "/" + ("" if path == "index.html" else path)
    root = site["base_url"].rstrip("/").rsplit("/pl", 1)[0] + "/"
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<link rel="alternate" hreflang="pl" href="{e(site['base_url'])}">
<link rel="alternate" hreflang="fr" href="{e(root)}">
<link rel="alternate" hreflang="en" href="{e(root + 'en/')}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(root + 'logo.png')}">
<meta property="og:locale" content="pl_PL">
<meta name="theme-color" content="#3a1d2e">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌸</text></svg>">
<link rel="stylesheet" href="../style.css">
<script>document.documentElement.classList.add("js")</script>
</head>
<body>
<a class="skip" href="#content">Przejdź do treści</a>
<header class="top">
  <a class="brand" href="./"><span aria-hidden="true">🌸</span> {e(site['name'])}</a>
  <nav aria-label="Menu"><a href="./#guides">Poradniki</a><a href="o-nas.html">O nas</a><a href="../">FR</a><a href="../en/">EN</a></nav>
</header>
<div class="disclosure" role="note">{e(DISCLOSURE)} <a href="ujawnienie.html">Więcej</a></div>
<main id="content">
{body}
</main>
<footer class="foot">
  <p><strong>{e(site['name'])}</strong> — {e(site['tagline'])}</p>
  <p><a href="ujawnienie.html">Linki afiliacyjne</a> · <a href="prywatnosc.html">Prywatność</a> · <a href="o-nas.html">O nas</a> · <a href="../">Version française</a> · <a href="../en/">English</a></p>
  <p class="muted">Aktualizacja: {e(site['updated'])}.</p>
</footer>
<script src="../app.js" defer></script>
</body>
</html>
"""


def index_body(site: dict, guides: list[dict]) -> str:
    cards = "\n".join(f"""<a class="card reveal" href="{e(g['slug'])}.html">
  <span class="card-icon" aria-hidden="true">{e(g['icon'])}</span>
  <h3>{e(g['title'])}</h3>
  <p>{e(g['description'])}</p>
  <span class="card-cta">Czytaj poradnik →</span>
</a>""" for g in guides)
    return f"""<section class="hero">
  <div class="snow" aria-hidden="true"></div>
  <p class="eyebrow">Niezależne poradniki zakupowe</p>
  <h1>Mróz wysusza skórę.<br><span>Wybierz właściwą pielęgnację za pierwszym razem.</span></h1>
  <p class="lead">{e(site['tagline'])} Jasne kryteria, bez fałszywych opinii, żeby kupić raz i dobrze.</p>
  <a class="btn" href="#guides">Zobacz poradniki</a>
</section>
<section id="guides" class="section">
  <h2 class="reveal">Nasze poradniki</h2>
  <div class="grid">
{cards}
  </div>
</section>
<section class="section promise reveal">
  <h2>Jak pracujemy</h2>
  <ul class="checks">
    <li>Wyjaśniamy, <strong>co sprawdzić</strong> przed zakupem, na podstawie prawdziwych potrzeb.</li>
    <li>Nigdy nie wymyślamy <strong>opinii ani testów</strong>.</li>
    <li>Nie pokazujemy <strong>cen</strong>, które mogą być nieaktualne: zobaczysz je na bieżąco u sprzedawcy.</li>
  </ul>
</section>"""


def guide_body(site: dict, g: dict) -> str:
    mid, affid = site.get("awin_mid", ""), site.get("awin_affid", "")
    parts = [f"""<article class="guide">
<header class="guide-head reveal">
  <p class="eyebrow"><span aria-hidden="true">{e(g['icon'])}</span> Poradnik zakupowy</p>
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
<a class="btn btn-small" href="{e(aliexpress_url(p['query'], mid, affid))}" rel="sponsored nofollow noopener" target="_blank">Zobacz na AliExpress</a></li>"""
        for p in g.get("picks", [])
    )
    parts.append(f'<section class="block"><h2 class="reveal">Gdzie szukać</h2><ul class="picks">{picks}</ul>'
                 '<p class="muted small">Linki afiliacyjne. Ceny, dostępność i czas dostawy się zmieniają: sprawdź je u sprzedawcy.</p></section>')
    if g.get("faq"):
        faq = "".join(f"<details class=\"reveal\"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>" for f in g["faq"])
        parts.append(f'<section class="block"><h2 class="reveal">Pytania</h2>{faq}</section>')
    parts.append('<p class="back"><a href="./#guides">← Wszystkie poradniki</a></p></article>')
    return "\n".join(parts)


STATIC_PAGES = {
    "ujawnienie.html": ("Linki afiliacyjne", "Jak finansowana jest ta strona.", """<article class="guide prose">
<h1>Linki afiliacyjne</h1>
<p>Ta strona zawiera linki afiliacyjne, głównie do AliExpress, za pośrednictwem sieci Awin.</p>
<p>Gdy kupisz coś po kliknięciu jednego z naszych linków, możemy otrzymać prowizję. Cena, którą płacisz, się nie zmienia.</p>
<p>Nie otrzymujemy darmowych produktów ani płatności od marek. Nasze poradniki przedstawiają kryteria wyboru; nie twierdzą, że przetestowaliśmy każdy produkt.</p>
</article>"""),
    "prywatnosc.html": ("Prywatność", "Jakie dane zbiera ta strona.", """<article class="guide prose">
<h1>Polityka prywatności</h1>
<p><strong>W skrócie: ta strona nie zbiera danych osobowych.</strong></p>
<ul class="checks"><li>Brak formularzy, kont i newslettera.</li><li>Brak plików cookie i statystyk ustawianych przez tę stronę.</li><li>Brak reklam targetowanych.</li></ul>
<h2>Hosting</h2>
<p>Strona jest hostowana przez GitHub Pages (GitHub, Inc.), który może przetwarzać dane techniczne, takie jak adresy IP, ze względów bezpieczeństwa, zgodnie z własną polityką prywatności.</p>
<h2>Linki do sprzedawców</h2>
<p>Klikając link do AliExpress, opuszczasz tę stronę. Sieć Awin i sprzedawca mogą wtedy używać plików cookie, m.in. do przypisania prowizji, zgodnie z własnymi zasadami.</p>
<h2>Pytania</h2>
<p>Zgłoś je na <a href="https://github.com/lattendu1987-dev/eclat-doux/issues">stronie projektu</a>.</p>
</article>"""),
    "o-nas.html": ("O nas", "Kim jesteśmy i jak powstają nasze poradniki.", """<article class="guide prose">
<h1>O nas</h1>
<p>Delikatny Blask publikuje poradniki zakupowe o pielęgnacji i urodzie, ze szczególnym uwzględnieniem zimy: mrozu, wiatru, ogrzewania i suchego powietrza.</p>
<ul class="checks"><li>Wychodzimy od konkretnych potrzeb (spierzchnięte usta, suche dłonie, ściągnięta skóra).</li><li>Podajemy sprawdzalne kryteria: typ skóry, kluczowe składniki, konsystencja, format, środki ostrożności.</li><li>Linkujemy do wyszukiwania u sprzedawcy, żebyś mógł porównać aktualne oferty.</li></ul>
<p>Nie publikujemy wymyślonych opinii ani płatnych rankingów.</p>
</article>"""),
}


def build(out_dir: Path) -> list[str]:
    """Zapisuje polską wersję w out_dir (public/pl). Zwraca adresy URL do mapy strony."""
    data = config.load_toml("site_pl.toml")
    site, guides = data["site"], data["guide"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page(site, site["name"], site["tagline"], index_body(site, guides), "index.html"), encoding="utf-8")
    for g in guides:
        name = f"{g['slug']}.html"
        (out_dir / name).write_text(page(site, g["title"], g["description"], guide_body(site, g), name), encoding="utf-8")
    for name, (title, desc, body) in STATIC_PAGES.items():
        (out_dir / name).write_text(page(site, title, desc, body, name), encoding="utf-8")
    base = site["base_url"].rstrip("/") + "/"
    return [base] + [f"{base}{g['slug']}.html" for g in guides] + [f"{base}{n}" for n in STATIC_PAGES]
