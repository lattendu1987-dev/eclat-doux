"""Page « Black Friday » : liens vers les pages officielles d'offres d'Amazon, pays par pays,
et rappel des guides pour bien choisir avant d'acheter. Aucun prix ni promo inventée."""

from __future__ import annotations

from urllib.parse import quote_plus

from . import config
from .site import e

TEXT = {
    "fr": {
        "title": "Black Friday 2026 : les offres, et nos conseils pour bien acheter",
        "desc": "Black Friday le 27 novembre et Cyber Monday le 30 : les pages officielles d'offres Amazon, pays par pays, et nos guides pour choisir sans se tromper.",
        "eyebrow": "🖤 Black Friday · 27 novembre",
        "lead": "Le Black Friday a lieu le vendredi 27 novembre 2026, suivi du Cyber Monday le 30. Voici les pages officielles d'offres d'Amazon dans votre pays, et nos guides pour vérifier les bons critères avant de profiter d'une promo.",
        "h_deals": "Les offres officielles, par pays",
        "h_tips": "3 réflexes avant d'acheter",
        "tips": ["Vérifiez d'abord les critères dans nos guides : une promo n'est une bonne affaire que si le produit vous convient.",
                 "Comparez le prix avec les semaines précédentes : une grosse remise affichée ne veut pas toujours dire prix bas.",
                 "Regardez la date de livraison et les conditions de retour, surtout pour les cadeaux de Noël."],
        "h_guides": "Nos guides pour bien choisir",
        "deals": "Voir les offres",
        "note": "Liens d'affiliation lorsque disponibles. Les offres, prix et dates sont ceux affichés par Amazon au moment de votre visite.",
    },
    "en": {
        "title": "Black Friday 2026: the deals, and how to buy smart",
        "desc": "Black Friday on November 27 and Cyber Monday on November 30: Amazon's official deal pages by country, plus our guides to choose well.",
        "eyebrow": "🖤 Black Friday · November 27",
        "lead": "Black Friday falls on Friday, November 27, 2026, followed by Cyber Monday on the 30th. Here are Amazon's official deal pages in your country, and our guides to check the right criteria before grabbing a discount.",
        "h_deals": "Official deals, by country",
        "h_tips": "3 habits before you buy",
        "tips": ["Check the criteria in our guides first: a deal is only a good deal if the product suits you.",
                 "Compare with prices from previous weeks: a big displayed discount doesn't always mean a low price.",
                 "Check delivery dates and return policies, especially for Christmas gifts."],
        "h_guides": "Our guides to choose well",
        "deals": "See the deals",
        "note": "Affiliate links where available. Deals, prices and dates are those shown by Amazon at the time of your visit.",
    },
}


def deals_url(store: dict) -> str:
    u = f"https://{store['domain']}/deals"
    return f"{u}?tag={quote_plus(store['tag'])}" if store.get("tag") else u


def codes_html(lang: str) -> str:
    """Codes promo AliExpress (config/promo_codes.toml), avec lien suivi Awin vers la page de la campagne."""
    from urllib.parse import quote
    if not (config.CONFIG_DIR / "promo_codes.toml").exists():
        return ""
    data = config.load_toml("promo_codes.toml")
    c = data.get(lang)
    if not c:
        return ""
    url = f"https://www.awin1.com/cread.php?awinmid={c['mid']}&awinaffid={data['affid']}&ued={quote(c['landing'], safe='')}"
    h = "Codes promo" if lang == "fr" else "Promo codes"
    btn = "Voir les offres" if lang == "fr" else "See the deals on"
    sep = " : " if lang == "fr" else ": "
    rows = "".join(f'<li><strong>{e(code)}</strong>{sep}{e(txt)}</li>' for code, txt in c["codes"])
    periods = "".join(f"<li>{e(x)}</li>" for x in c["periods"])
    return (f'<section class="block reveal"><h2>{e(h)} {e(c["store"])}</h2><ul>{periods}</ul><ul class="checks">{rows}</ul>'
            f'<p class="muted small">{e(c["note"])}</p>'
            f'<p><a class="btn btn-small" href="{e(url)}" rel="sponsored nofollow noopener" target="_blank">{e(btn)} {e(c["store"])}</a></p></section>')


def body(lang: str, first: str, guides: list[dict]) -> str:
    t = TEXT[lang]
    stores = sorted(config.load_toml("bestsellers.toml")["store"], key=lambda s: s["domain"] != first)
    cards = "".join(
        f'<section class="kit reveal"><h3>{e(s["flag"])} {e(s[lang])}</h3><div class="bs-links">'
        f'<a class="btn btn-small" href="{e(deals_url(s))}" rel="sponsored nofollow noopener" target="_blank">{e(t["deals"])}</a></div></section>'
        for s in stores)
    tips = "".join(f"<li>{e(x)}</li>" for x in t["tips"])
    recent = sorted(guides, key=lambda g: g.get("date", ""), reverse=True)
    links = "".join(f'<li><a href="{e(g["slug"])}.html">{e(g["icon"])} {e(g["title"])}</a></li>' for g in recent)
    return f"""<article class="guide">
<header class="guide-head reveal"><p class="eyebrow">{e(t['eyebrow'])}</p><h1>{e(t['title'])}</h1><p class="lead">{e(t['lead'])}</p></header>
<section class="block reveal"><h2>{e(t['h_tips'])}</h2><ul class="checks">{tips}</ul></section>
{codes_html(lang)}
<h2 class="reveal">{e(t['h_deals'])}</h2>
{cards}
<section class="block reveal"><h2>{e(t['h_guides'])}</h2><ul>{links}</ul></section>
<p class="muted small">{e(t['note'])}</p>
</article>"""
