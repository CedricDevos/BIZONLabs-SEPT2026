#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "social-preview.png"
FONT_DIR = ROOT / "assets" / "fonts"
ICON = ROOT / "assets" / "logos" / "bison-icon-white.svg"
WIDTH = 1200
HEIGHT = 630
LEFT = 96


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size=size)


def load_bison_icon(size: int) -> Image.Image:
    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "bison-icon.png"
        subprocess.run(
            ["sips", "-s", "format", "png", str(ICON), "--out", str(output)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        icon = Image.open(output).convert("RGBA")
        bounds = icon.getbbox()
        if bounds:
            icon = icon.crop(bounds)
        icon.thumbnail((size, size), Image.Resampling.LANCZOS)
        return icon


def draw_wordmark(draw: ImageDraw.ImageDraw) -> None:
    mark_font = font("ZalandoSansExpanded-Bold.ttf", 92)
    lab_font = font("ZalandoSans-Medium.ttf", 37)
    x = 236
    y = 176
    draw.text((x, y), "BIZON", font=mark_font, fill=(255, 255, 255, 242))
    draw.text((x + 8, y + 102), "LABS", font=lab_font, fill=(255, 255, 255, 166))


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), (2, 0, 8))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for radius, alpha in [(680, 88), (430, 46), (250, 28)]:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        layer_draw.ellipse((860 - radius, 180 - radius, 860 + radius, 180 + radius), fill=(31, 0, 94, alpha))
        overlay.alpha_composite(layer.filter(ImageFilter.GaussianBlur(80)))

    for x in range(-160, WIDTH + 160, 86):
        opacity = 12 if x % 172 == 0 else 7
        draw.line([(x, 0), (x + 235, HEIGHT)], fill=(255, 255, 255, opacity), width=1)

    draw.rectangle((72, 72, WIDTH - 72, HEIGHT - 72), outline=(255, 255, 255, 28), width=1)

    icon = load_bison_icon(112)
    overlay.alpha_composite(icon, (LEFT, 210))
    draw_wordmark(draw)

    line_font = font("ZalandoSans-Regular.ttf", 34)
    text = "next-generation lipid nanoparticles."
    draw.text((LEFT, 394), text, font=line_font, fill=(255, 255, 255, 166))

    draw.line((LEFT, 486, WIDTH - LEFT, 486), fill=(124, 112, 235, 68), width=2)

    composed = Image.alpha_composite(image.convert("RGBA"), overlay)
    composed.convert("RGB").save(OUT, quality=94)


if __name__ == "__main__":
    main()
