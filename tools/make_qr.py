"""Crée des QR codes (cartes PNG prêtes à imprimer ou partager) pour les liens importants.
Sortie : static/qr/<nom>.png. Nécessite : pip install qrcode
Usage : python tools/make_qr.py
"""

import sys
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import make_pins  # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def card(url: str, title: str, out: Path):
    dark = make_pins.PALETTE[0]
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=16, border=2)
    q.add_data(url)
    q.make(fit=True)
    code = q.make_image(fill_color=dark, back_color="white").convert("RGB").resize((760, 760), Image.NEAREST)
    im = Image.new("RGB", (900, 1100), "white")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 880, 1080), radius=40, outline=dark, width=6)
    im.paste(code, (70, 60))
    f1, f2 = ImageFont.truetype(FONT, 54), ImageFont.truetype(SANS, 26)
    for text, font, y in [(title, f1, 860), (url.replace("https://", ""), f2, 950)]:
        w = d.textlength(text, font=font)
        if w > 820:
            font = ImageFont.truetype(font.path, int(font.size * 820 / w))
            w = d.textlength(text, font=font)
        d.text(((900 - w) / 2, y), text, font=font, fill=dark)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)
    print(out.relative_to(ROOT))


def main():
    for name, title, url in make_pins.QR_LINKS:
        card(url, title, ROOT / "static" / "qr" / f"{name}.png")


if __name__ == "__main__":
    main()
