"""English twin of the site, built into public/en/ from config/site_en.toml.

Same design and assets as the French site (referenced from the parent folder).
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote_plus

from . import config
from .site import e

DISCLOSURE = (
    "As an Amazon Associate I earn from qualifying purchases, at no extra cost to you. "
    "We haven't tested every product: our guides explain what to check before buying."
)


def amazon_url(query: str, tag: str, domain: str) -> str:
    url = f"https://{domain}/s?k={quote_plus(query)}"
    return f"{url}&tag={quote_plus(tag)}" if tag else url


def page(site: dict, title: str, description: str, body: str, path: str, image: str = "") -> str:
    full_title = title if title == site["name"] else f"{title} · {site['name']}"
    canonical = site["base_url"].rstrip("/") + "/" + ("" if path == "index.html" else path)
    fr_home = site["base_url"].rstrip("/").rsplit("/en", 1)[0] + "/"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<link rel="alternate" hreflang="en" href="{e(site['base_url'])}">
<link rel="alternate" hreflang="fr" href="{e(fr_home)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(fr_home + ('pins/en/' + image + '.png' if image else 'logo.png'))}">
<meta property="og:locale" content="en_US">
<meta name="theme-color" content="#3a1d2e">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌸</text></svg>">
<link rel="stylesheet" href="../style.css">
<script>document.documentElement.classList.add("js")</script>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="top">
  <a class="brand" href="./"><span aria-hidden="true">🌸</span> {e(site['name'])}</a>
  <nav aria-label="Main"><a href="./#guides">Guides</a><a href="best-sellers.html">Best sellers</a><a href="about.html">About</a><a href="../">FR</a><a href="../pl/">PL</a></nav>
</header>
<div class="disclosure" role="note">{e(DISCLOSURE)} <a href="disclosure.html">Learn more</a></div>
<main id="content">
{body}
</main>
<footer class="foot">
  <p><strong>{e(site['name'])}</strong> — {e(site['tagline'])}</p>
  <p><a href="disclosure.html">Disclosure</a> · <a href="privacy.html">Privacy</a> · <a href="about.html">About</a> · <a href="../">Version française</a></p>
  <p class="muted">Updated {e(site['updated'])}. Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates.</p>
</footer>
<script src="../stores.js" defer></script>
<script src="../app.js" defer></script>
</body>
</html>
"""


def index_body(site: dict, guides: list[dict]) -> str:
    cards = "\n".join(f"""<a class="card reveal" href="{e(g['slug'])}.html">
  <span class="card-icon" aria-hidden="true">{e(g['icon'])}</span>
  <h3>{e(g['title'])}</h3>
  <p>{e(g['description'])}</p>
  <span class="card-cta">Read the guide →</span>
</a>""" for g in guides)
    return f"""<section class="hero">
  <div class="snow" aria-hidden="true"></div>
  <p class="eyebrow">Independent buying guides</p>
  <h1>Cold weather dries out skin.<br><span>Pick the right care, the first time.</span></h1>
  <p class="lead">{e(site['tagline'])} Clear criteria, no fake reviews, so you buy once and buy right.</p>
  <a class="btn" href="#guides">See the guides</a>
</section>
<section id="guides" class="section">
  <h2 class="reveal">Our guides</h2>
  <div class="grid">
{cards}
  </div>
</section>
<section class="section promise reveal">
  <h2>How we work</h2>
  <ul class="checks">
    <li>We explain <strong>what to check</strong> before buying, based on real needs.</li>
    <li>We never make up <strong>reviews or tests</strong>.</li>
    <li>We don't show <strong>prices</strong> that could be outdated: you see them live on Amazon.</li>
  </ul>
</section>"""


def guide_body(site: dict, g: dict) -> str:
    tag, domain = site.get("amazon_tag", ""), site.get("amazon_domain", "www.amazon.com")
    parts = [f"""<article class="guide">
<header class="guide-head reveal">
  <p class="eyebrow"><span aria-hidden="true">{e(g['icon'])}</span> Buying guide</p>
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
<a class="btn btn-small" href="{e(amazon_url(p['query'], tag, domain))}" rel="sponsored nofollow noopener" target="_blank">See prices on Amazon</a></li>"""
        for p in g.get("picks", [])
    )
    parts.append(f'<section class="block"><h2 class="reveal">Where to look</h2><ul class="picks">{picks}</ul>'
                 '<p class="muted small">Affiliate links. Prices and availability change: check them on Amazon.</p></section>')
    if g.get("faq"):
        faq = "".join(f"<details class=\"reveal\"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>" for f in g["faq"])
        parts.append(f'<section class="block"><h2 class="reveal">FAQ</h2>{faq}</section>')
    parts.append('<p class="back"><a href="./#guides">← All guides</a></p></article>')
    return "\n".join(parts)


STATIC_PAGES = {
    "disclosure.html": ("Disclosure", "How this site is funded.", """<article class="guide prose">
<h1>Disclosure</h1>
<p>As an Amazon Associate I earn from qualifying purchases.</p>
<p>When you buy after clicking one of our links, we may receive a commission. The price you pay does not change.</p>
<p>We receive no free products or payments from brands. Our guides present buying criteria; they do not claim to have tested every product.</p>
</article>"""),
    "privacy.html": ("Privacy", "What this site collects.", """<article class="guide prose">
<h1>Privacy policy</h1>
<p><strong>In short: this site collects no personal information.</strong></p>
<ul class="checks"><li>No forms, accounts or newsletter.</li><li>No cookies or analytics set by this site.</li><li>No targeted advertising.</li></ul>
<h2>Hosting</h2>
<p>The site is hosted by GitHub Pages (GitHub, Inc.), which may process technical data such as IP addresses for security, under its own privacy policy.</p>
<h2>Links to Amazon</h2>
<p>When you click a link to Amazon, you leave this site. Amazon may then use cookies, including to attribute the commission, under its own privacy policy.</p>
<h2>Questions</h2>
<p>Open a request on the <a href="https://github.com/lattendu1987-dev/eclat-doux/issues">project page</a>.</p>
</article>"""),
    "about.html": ("About", "Who we are and how our guides are made.", """<article class="guide prose">
<h1>About</h1>
<p>Soft Glow publishes skincare and beauty buying guides, with special attention to winter: cold, wind, indoor heating and dry air.</p>
<ul class="checks"><li>We start from real needs (chapped lips, dry hands, tight skin).</li><li>We list checkable criteria: skin type, key ingredients, texture, format, precautions.</li><li>We link to an Amazon search so you can compare current offers.</li></ul>
<p>We publish no invented reviews and no paid rankings.</p>
</article>"""),
}


def build(out_dir: Path) -> list[str]:
    """Writes the English site into out_dir (public/en). Returns its URLs for the sitemap."""
    data = config.load_toml("site_en.toml")
    site, guides = data["site"], data["guide"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page(site, site["name"], site["tagline"], index_body(site, guides), "index.html"), encoding="utf-8")
    for g in guides:
        name = f"{g['slug']}.html"
        (out_dir / name).write_text(page(site, g["title"], g["description"], guide_body(site, g), name, image=g["slug"]), encoding="utf-8")
    for name, (title, desc, body) in STATIC_PAGES.items():
        (out_dir / name).write_text(page(site, title, desc, body, name), encoding="utf-8")
    from . import bestsellers
    bs = bestsellers.TEXT["en"]
    (out_dir / "best-sellers.html").write_text(page(site, bs["title"], bs["desc"], bestsellers.body("en", "www.amazon.com"), "best-sellers.html"), encoding="utf-8")
    base = site["base_url"].rstrip("/") + "/"
    return [base, f"{base}best-sellers.html"] + [f"{base}{g['slug']}.html" for g in guides] + [f"{base}{n}" for n in STATIC_PAGES]
