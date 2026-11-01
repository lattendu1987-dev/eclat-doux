"""Génère 2 images Pinterest supplémentaires par guide (variantes B et C), pour publier
plusieurs épingles différentes vers le même guide. Les images existantes ne sont pas refaites.

Usage : python tools/make_variants.py [--force]
"""

import html
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import make_pins  # noqa: E402

PALETTE = make_pins.PALETTE  # dark, accent, light, soft

BASE = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1000px;height:1500px;overflow:hidden;background:{bg}}}
body{{font-family:"DejaVu Sans",system-ui,sans-serif;box-sizing:border-box;position:relative}}
h1{{font-family:"DejaVu Serif",Georgia,serif;letter-spacing:-.01em;margin:0}}
{css}</style></head><body>{body}</body></html>"""

B_CSS = """body{{padding:90px;display:flex;flex-direction:column;justify-content:space-between;color:{dark}}}
.card{{background:#fff;border-radius:48px;padding:80px 70px;box-shadow:0 30px 80px rgba(0,0,0,.12)}}
.tag{{display:inline-block;background:{accent};color:#fff;font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:30px;padding:14px 26px;border-radius:999px}}
.icon{{font-size:170px;line-height:1;margin:50px 0 30px}}
h1{{font-size:{size}px;line-height:1.1;margin-bottom:34px}}
ul{{list-style:none;padding:0;margin:0;font-size:36px;line-height:1.45;color:#3b3b3b}}
li{{margin:14px 0;padding-left:56px;position:relative}}li:before{{content:"✓";position:absolute;left:0;color:{accent};font-weight:700}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:34px}}
.brand{{font-family:"DejaVu Serif",Georgia,serif;font-weight:700;font-size:42px}}
.cta{{background:{dark};color:#fff;padding:20px 34px;border-radius:999px;font-weight:700}}"""

C_CSS = """.top{{height:640px;background:{accent};display:flex;align-items:center;justify-content:center;font-size:330px}}
.bottom{{position:absolute;top:640px;left:0;right:0;bottom:0;background:{dark};color:#fff;padding:80px 90px;display:flex;flex-direction:column;justify-content:space-between}}
.kicker{{color:{soft};font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:30px;margin-bottom:26px}}
h1{{font-size:{size}px;line-height:1.1}}
p{{font-size:38px;line-height:1.4;color:#e8e2e6;margin:30px 0 0}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:34px;border-top:2px solid rgba(255,255,255,.2);padding-top:36px}}
.brand{{font-family:"DejaVu Serif",Georgia,serif;font-weight:700;font-size:42px}}
.cta{{color:{soft};font-weight:700}}"""


def bullets(g):
    out = []
    for s in g.get("sections", []):
        for b in s.get("bullets", []):
            short = b.split(":")[0].strip().rstrip(".")
            if 8 < len(short) < 60:
                out.append(short)
    return out[:3]


def render(chrome, page, target):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(page)
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=1000,1500", f"--screenshot={target}", f"file://{f.name}"], check=True, capture_output=True)


def main():
    force = "--force" in sys.argv
    chrome = make_pins.find_chrome(None)
    dark, accent, light, soft = PALETTE
    for cfg, folder, tag, brand, cta, sep in make_pins.VERSIONS:
        out = ROOT / "static" / folder
        out.mkdir(parents=True, exist_ok=True)
        icon_brand = make_pins.BRAND_ICON
        for g in make_pins.load_toml(cfg)["guide"]:
            title = g["title"].split(sep)[0].strip()
            hook = g["title"].split(sep, 1)[1].strip() if sep in g["title"] else g["description"]
            hook = hook[0].upper() + hook[1:]
            e = html.escape
            tb = out / f"{g['slug']}-b.png"
            if force or not tb.exists():
                items = "".join(f"<li>{e(b)}</li>" for b in bullets(g))
                body = (f'<div class="card"><span class="tag">{e(tag)}</span><div class="icon">{g["icon"]}</div>'
                        f'<h1>{e(title)}</h1><ul>{items}</ul></div>'
                        f'<div class="foot"><span class="brand">{icon_brand} {e(brand)}</span><span class="cta">{e(cta)}</span></div>')
                css = B_CSS.format(dark=dark, accent=accent, size=84 if len(title) < 40 else 70)
                render(chrome, BASE.format(bg=light, css=css, body=body), tb)
                print(tb.relative_to(ROOT))
            tc = out / f"{g['slug']}-c.png"
            if force or not tc.exists():
                body = (f'<div class="top">{g["icon"]}</div><div class="bottom"><div><div class="kicker">{e(title)}</div>'
                        f'<h1>{e(hook)}</h1><p>{e(g["description"])}</p></div>'
                        f'<div class="foot"><span class="brand">{icon_brand} {e(brand)}</span><span class="cta">{e(cta)}</span></div></div>')
                css = C_CSS.format(dark=dark, accent=accent, soft=soft, size=72 if len(hook) < 60 else 60)
                render(chrome, BASE.format(bg=dark, css=css, body=body), tc)
                print(tc.relative_to(ROOT))


if __name__ == "__main__":
    main()
