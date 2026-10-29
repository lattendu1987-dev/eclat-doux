"""Revenus d'affiliation : simulation prudente, sans dépense.

Hypothèses (à remplacer par les données réelles du tableau de bord Amazon dès qu'elles existent) :
- taux de clic vers Amazon depuis un guide : 10-20 % ;
- taux d'achat sur Amazon après le clic : 5-10 % (hypothèse, aucune donnée officielle) ;
- Amazon rémunère tout le panier acheté dans les 24 h suivant le clic ;
- commission « Beauté » Amazon.fr : à confirmer (barème juin 2025, à confirmer dans l'espace Partenaires).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AffiliateScenario:
    name: str
    monthly_visits: int
    click_rate: float
    buy_rate: float
    basket: float
    commission_rate: float


@dataclass(frozen=True)
class AffiliateResult:
    scenario: AffiliateScenario
    clicks: float
    orders: float
    sales: float
    commission: float


def run(s: AffiliateScenario) -> AffiliateResult:
    clicks = s.monthly_visits * s.click_rate
    orders = clicks * s.buy_rate
    sales = orders * s.basket
    return AffiliateResult(s, round(clicks, 1), round(orders, 1), round(sales, 2),
                           round(sales * s.commission_rate, 2))


def default_scenarios() -> list[AffiliateScenario]:
    return [
        AffiliateScenario("Démarrage (mois 1-3)", 500, 0.15, 0.06, 55, 0.03),
        AffiliateScenario("Croissance (mois 4-9)", 5_000, 0.15, 0.07, 60, 0.035),
        AffiliateScenario("Établi (12 mois et plus)", 30_000, 0.15, 0.08, 60, 0.035),
    ]


def table_md() -> str:
    rows = ["| Scénario | Visites/mois | Clics vers Amazon | Achats | Ventes générées | **Commission/mois** |",
            "|---|---|---|---|---|---|"]
    for s in default_scenarios():
        r = run(s)
        rows.append(f"| {s.name} | {s.monthly_visits:,} | {r.clicks:,.0f} | {r.orders:,.0f} | "
                    f"{r.sales:,.0f} € | **{r.commission:,.0f} €** |".replace(",", " "))
    return "\n".join(rows)
