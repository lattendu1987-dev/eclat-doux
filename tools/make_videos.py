"""Crée une courte vidéo verticale (Reels, TikTok, Shorts) par guide, à partir de ses images Pinterest.

Sortie : static/videos/<slug>.mp4 (720 x 1280, ~12 s, sans son : ajoutez une musique tendance
dans l'application au moment de publier). Les vidéos existantes ne sont pas refaites.
Usage : python tools/make_videos.py [--force]
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import make_pins  # noqa: E402

W, H, FPS, SLIDE = 720, 1280, 30, 3.2
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def slide(img_path: Path, out: Path):
    im = Image.open(img_path).convert("RGB")
    bg = im.resize((W, int(im.height * W / im.width))).resize((W, H)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.35)
    fw = W - 60
    fg = im.resize((fw, int(im.height * fw / im.width)))
    bg.paste(fg, ((W - fw) // 2, (H - fg.height) // 2))
    bg.save(out)


def end_card(out: Path, line1: str, line2: str, color):
    im = Image.new("RGB", (W, H), color)
    d = ImageDraw.Draw(im)
    for text, font, y in [(line1, ImageFont.truetype(FONT, 58), H // 2 - 90), (line2, ImageFont.truetype(SANS, 40), H // 2 + 30)]:
        w = d.textlength(text, font=font)
        d.text(((W - w) / 2, y), text, font=font, fill=(255, 255, 255))
    im.save(out)


def main():
    force = "--force" in sys.argv
    cfg, folder = make_pins.VERSIONS[0][0], make_pins.VERSIONS[0][1]  # version française
    dark = make_pins.PALETTE[0]
    color = tuple(int(dark[i:i + 2], 16) for i in (1, 3, 5))
    out_dir = ROOT / "static" / "videos"
    out_dir.mkdir(parents=True, exist_ok=True)
    for g in make_pins.load_toml(cfg)["guide"]:
        target = out_dir / f"{g['slug']}.mp4"
        if target.exists() and not force:
            continue
        imgs = [ROOT / "static" / folder / f"{g['slug']}{s}.png" for s in ("", "-b", "-c")]
        imgs = [p for p in imgs if p.exists()]
        if not imgs:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            frames = []
            for i, p in enumerate(imgs):
                slide(p, tmp / f"s{i}.png")
                frames.append(tmp / f"s{i}.png")
            end_card(tmp / "end.png", "Guide gratuit", "Lien dans la bio 👆".replace(" 👆", ""), color)
            frames.append(tmp / "end.png")
            inputs, filters = [], []
            for i, f in enumerate(frames):
                inputs += ["-loop", "1", "-t", str(SLIDE), "-i", str(f)]
                filters.append(f"[{i}:v]scale={W*2}:{H*2},zoompan=z='min(zoom+0.0009,1.08)':d={int(SLIDE*FPS)}:s={W}x{H}:fps={FPS},setsar=1[v{i}]")
            chain, last, offset = [], "v0", SLIDE - 0.4
            for i in range(1, len(frames)):
                chain.append(f"[{last}][v{i}]xfade=transition=slideleft:duration=0.4:offset={offset:.2f}[x{i}]")
                last, offset = f"x{i}", offset + SLIDE - 0.4
            fc = ";".join(filters + chain)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", f"[{last}]",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                            str(target)], check=True)
        print(target.relative_to(ROOT), round(target.stat().st_size / 1e6, 2), "Mo")


if __name__ == "__main__":
    main()
