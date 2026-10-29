# Éclat Doux

Guides d'achat de soins et de beauté pour l'hiver (FR, EN, PL), avec liens d'affiliation Amazon et AliExpress (Awin).

- **Site** : https://lattendu1987-dev.github.io/eclat-doux/
- **Contenu** : `config/site.toml` (FR), `config/site_en.toml` (EN), `config/site_pl.toml` (PL)
- **Kit de partage** (non référencé) : https://lattendu1987-dev.github.io/eclat-doux/kit-partage.html

```bash
python -m eclat site                      # génère le site dans public/
python -m unittest discover -s tests -t .
python tools/make_pins.py                 # images Pinterest (Chrome/Chromium)
```

Chaque mise à jour de `main` régénère le site et le publie sur la branche `gh-pages`.
Règles : pas de faux avis, pas de prix, aucune allégation médicale pour les cosmétiques.
