"""Page « Meilleures ventes » : liens vers les classements officiels d'Amazon, pays par pays."""

from __future__ import annotations

from urllib.parse import quote_plus

from . import config
from .site import e

TEXT = {
    "fr": {
        "title": "Meilleures ventes beauté sur Amazon, dans le monde",
        "desc": "Les classements officiels d'Amazon pour la beauté, mis à jour en continu, pays par pays.",
        "lead": "Les classements ci-dessous sont ceux d'Amazon : ils sont mis à jour automatiquement, environ toutes les heures. Choisissez votre pays pour voir ce qui se vend le plus en ce moment en soins et en beauté.",
        "note": "Liens d'affiliation lorsque disponibles. Les classements, prix et disponibilités sont ceux d'Amazon au moment de votre visite.",
        "h": "Choisissez votre pays",
    },
    "en": {
        "title": "Amazon beauty best sellers, worldwide",
        "desc": "Amazon's official beauty rankings, updated continuously, country by country.",
        "lead": "These are Amazon's own rankings: they update automatically, about every hour. Pick your country to see what's selling best right now in skincare and beauty.",
        "note": "Affiliate links where available. Rankings, prices and availability are Amazon's at the time of your visit.",
        "h": "Pick your country",
    },
}


def url(store: dict, path: str) -> str:
    u = f"https://{store['domain']}/{path}/"
    return f"{u}?tag={quote_plus(store['tag'])}" if store.get("tag") else u


def body(lang: str, first: str) -> str:
    data = config.load_toml("bestsellers.toml")
    t = TEXT[lang]
    stores = sorted(data["store"], key=lambda s: s["domain"] != first)
    cards = []
    for s in stores:
        links = "".join(
            f'<a class="btn btn-small" href="{e(url(s, l["path"]))}" rel="sponsored nofollow noopener" target="_blank">'
            f'{e(l["icon"])} {e(l[lang])}</a>'
            for l in data["lists"]
        )
        cards.append(f'<section class="kit reveal"><h3>{e(s["flag"])} {e(s[lang])}</h3>'
                     f'<div class="bs-links">{links}</div></section>')
    return f"""<article class="guide">
<header class="guide-head reveal"><p class="eyebrow">🌍 Amazon</p><h1>{e(t['title'])}</h1><p class="lead">{e(t['lead'])}</p></header>
<h2 class="reveal">{e(t['h'])}</h2>
{''.join(cards)}
<p class="muted small">{e(t['note'])}</p>
</article>"""


def stores_js() -> str:
    """Boutiques Amazon pour lesquelles un identifiant Partenaire existe, par pays du visiteur."""
    import json
    data = config.load_toml("bestsellers.toml")
    m = {s["region"]: {"d": s["domain"], "t": s["tag"]} for s in data["store"] if s.get("tag") and s.get("region")}
    js = "window.PAC_STORES = " + json.dumps(m, separators=(",", ":")) + ";\n"
    if (config.CONFIG_DIR / "aliexpress.toml").exists():
        ali = config.load_toml("aliexpress.toml")
        a = {r: p["mid"] for p in ali["program"] for r in p["regions"]}
        js += "window.PAC_ALI = " + json.dumps({"affid": ali["affid"], "mid": a}, separators=(",", ":")) + ";\n"
    return js
