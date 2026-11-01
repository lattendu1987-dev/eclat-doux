"""Planning Pinterest : chaque samedi, un fichier « épingles de la semaine » qui publie
1 épingle par jour et par langue pendant les 7 jours suivants (date de publication programmée).

On publie d'abord l'image principale des nouveaux guides, puis les variantes B et C des guides
existants (des images différentes vers les mêmes pages). L'historique est gardé dans
config/pin_plan.json pour ne jamais publier deux fois la même épingle.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

from . import config

PER_DAY = 1  # épingles par jour et par langue
VARIANTS = ("a", "b", "c")


def next_saturday(today: date) -> date:
    return today + timedelta(days=(5 - today.weekday()) % 7)


def pin_id(lang: str, slug: str, variant: str) -> str:
    return f"{lang}:{slug}:{variant}"


def _queue(guides_by_lang: dict[str, list[dict]], done: set[str]) -> dict[str, list[tuple[dict, str]]]:
    queues = {}
    for lang, guides in guides_by_lang.items():
        ordered = sorted(guides, key=lambda g: g.get("date", "0000"))
        q = [(g, "a") for g in reversed(ordered)]  # nouveaux guides d'abord
        for v in VARIANTS[1:]:
            q += [(g, v) for g in ordered]
        queues[lang] = [(g, v) for g, v in q if pin_id(lang, g["slug"], v) not in done]
    return queues


def load() -> dict:
    p = config.CONFIG_DIR / "pin_plan.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"done": [], "weeks": {}}


def save(plan: dict) -> None:
    (config.CONFIG_DIR / "pin_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def week_plan(guides_by_lang: dict[str, list[dict]], today: date, persist: bool = True) -> tuple[str, list[tuple[str, dict, str, str]]]:
    """Renvoie (samedi d'import, [(langue, guide, variante, date de publication)])."""
    plan = load()
    sat = next_saturday(today)
    key = sat.isoformat()
    by_slug = {(lang, g["slug"]): g for lang, gs in guides_by_lang.items() for g in gs}
    # Le planning de la semaine à venir est recalculé à chaque build jusqu'au samedi :
    # un guide publié mardi ou vendredi passe ainsi en tête de la semaine.
    if True:
        earlier = {i for k, ids in plan["weeks"].items() if k < key for i in ids}
        queues = _queue(guides_by_lang, set(plan["done"]) | earlier)
        ids = []
        for lang, q in queues.items():
            ids += [pin_id(lang, g["slug"], v) for g, v in q[: 7 * PER_DAY]]
        plan["weeks"][key] = ids
        if persist:
            save(plan)
    items, counters = [], {}
    for i in plan["weeks"][key]:
        lang, slug, v = i.split(":")
        g = by_slug.get((lang, slug))
        if not g:
            continue
        n = counters.get(lang, 0)
        counters[lang] = n + 1
        items.append((lang, g, v, (sat + timedelta(days=1 + n // PER_DAY)).isoformat()))
    return key, items
