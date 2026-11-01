"""Génère une image Pinterest (1000 x 1500) par guide dans static/pins/.

Usage : python tools/make_pins.py [chemin_vers_chrome]
Nécessite Chromium ou Chrome (mode headless).
"""

import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eclat.config import load_toml  # noqa: E402

TEMPLATE = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
html{{background:#3a1d2e}}html,body{{margin:0;width:100vw;height:100vh;overflow:hidden}}
body{{font-family:"DejaVu Sans",system-ui,sans-serif;color:#f4f1ea;
background:radial-gradient(120% 90% at 15% 0%,#8a4a6b 0%,#3a1d2e 62%);display:flex;flex-direction:column;
justify-content:space-between;padding:110px 90px 90px;box-sizing:border-box;position:relative}}
.snow{{position:absolute;inset:0;opacity:.35;background-image:
radial-gradient(4px 4px at 60px 80px,#fff 50%,transparent 51%),radial-gradient(3px 3px at 300px 200px,#fff 50%,transparent 51%),
radial-gradient(5px 5px at 520px 120px,#fff 50%,transparent 51%),radial-gradient(3px 3px at 760px 260px,#fff 50%,transparent 51%),
radial-gradient(4px 4px at 880px 60px,#fff 50%,transparent 51%);background-size:1000px 330px}}
.tag{{display:inline-block;background:#c2577a;color:#fff;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
font-size:30px;padding:14px 26px;border-radius:999px}}
.icon{{font-size:190px;line-height:1;margin:60px 0 30px}}
h1{{font-family:"DejaVu Serif",Georgia,serif;font-size:{size}px;line-height:1.12;margin:0 0 36px;letter-spacing:-.01em}}
p{{font-size:40px;line-height:1.4;margin:0;color:#dfe6ee}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:34px;border-top:2px solid rgba(255,255,255,.2);padding-top:40px}}
.brand{{font-family:"DejaVu Serif",Georgia,serif;font-weight:700;font-size:44px}}
.cta{{color:#f6c1d1;font-weight:700}}
</style></head><body><div class="snow"></div>
<div><span class="tag">{tag}</span><div class="icon">{icon}</div><h1>{title}</h1><p>{desc}</p></div>
<div class="foot"><span class="brand">🌸 {brand}</span><span class="cta">{cta}</span></div>
</body></html>"""


def find_chrome(arg):
    for c in [arg, "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", shutil.which("google-chrome"),
              shutil.which("chromium"), shutil.which("chromium-browser")]:
        if c and Path(c).exists():
            return c
    raise SystemExit("Chrome/Chromium introuvable")


VERSIONS = [
    # (fichier de config, dossier de sortie, étiquette, marque, appel à l'action, séparateur du titre)
    ("site.toml", "pins", "Guide d'achat", "Éclat Doux", "Lire le guide →", " : "),
    ("site_en.toml", "pins/en", "Buying guide", "Soft Glow", "Read the guide →", ":"),
]


def main():
    chrome = find_chrome(sys.argv[1] if len(sys.argv) > 1 else None)
    for cfg, folder, tag, brand, cta, sep in VERSIONS:
        out = ROOT / "static" / folder
        out.mkdir(parents=True, exist_ok=True)
        for g in load_toml(cfg)["guide"]:
            title = g["title"].split(sep)[0].strip()
            size = 92 if len(title) < 40 else 80
            page = TEMPLATE.format(icon=g["icon"], title=html.escape(title), desc=html.escape(g["description"]),
                                   size=size, tag=html.escape(tag), brand=html.escape(brand), cta=html.escape(cta))
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
                f.write(page)
            target = out / f"{g['slug']}.png"
            subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                            "--window-size=1000,1500", f"--screenshot={target}", f"file://{f.name}"],
                           check=True, capture_output=True)
            print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()

# Couleurs des variantes B et C (tools/make_variants.py) : foncé, accent, clair, doux.
PALETTE = ("#3a1d2e", "#c2577a", "#fbf6f4", "#f6c1d1")
BRAND_ICON = "🌸"
