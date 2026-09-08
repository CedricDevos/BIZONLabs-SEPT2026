#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "social-preview.png"
FONT_DIR = ROOT / "assets" / "fonts"
WIDTH = 1200
HEIGHT = 630


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size=size)


def draw_wordmark(draw: ImageDraw.ImageDraw) -> None:
    mark_font = font("ZalandoSansExpanded-Bold.ttf", 104)
    lab_font = font("ZalandoSans-Medium.ttf", 42)
    x = 96
    y = 176
    draw.text((x, y), "BIZON", font=mark_font, fill=(255, 255, 255, 242))
    draw.text((x + 10, y + 116), "LABS", font=lab_font, fill=(255, 255, 255, 170))


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

    draw.rectangle((72, 72, WIDTH - 72, HEIGHT - 72), outline=(255, 255, 255, 30), width=1)

    draw_wordmark(draw)

    line_font = font("ZalandoSans-Medium.ttf", 54)
    text = "Next Generation LNPs"
    bbox = draw.textbbox((0, 0), text, font=line_font)
    draw.text((WIDTH - 96 - (bbox[2] - bbox[0]), 386), text, font=line_font, fill=(255, 255, 255, 214))

    draw.line((96, 492, WIDTH - 96, 492), fill=(124, 112, 235, 84), width=2)

    composed = Image.alpha_composite(image.convert("RGBA"), overlay)
    composed.convert("RGB").save(OUT, quality=94)


if __name__ == "__main__":
    main()
