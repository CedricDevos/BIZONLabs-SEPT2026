#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "social-preview.png"
FONT_DIR = ROOT / "assets" / "fonts"
WIDTH = 1200
HEIGHT = 630


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size=size)


def fit_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font_obj)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(-180, WIDTH + 260, 92):
        draw.line([(x, 0), (x + 230, HEIGHT)], fill=(255, 255, 255, 9), width=1)
    for y in range(80, HEIGHT, 92):
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 7), width=1)


def draw_particles(draw: ImageDraw.ImageDraw) -> None:
    random.seed(42)
    particles = []
    for _ in range(38):
        x = random.randint(635, 1130)
        y = random.randint(80, 540)
        r = random.choice([3, 4, 5, 7])
        particles.append((x, y, r))
        alpha = random.randint(58, 132)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(142, 132, 255, alpha))

    for index, (x1, y1, _r1) in enumerate(particles):
        for x2, y2, _r2 in particles[index + 1 :]:
            distance = math.hypot(x1 - x2, y1 - y2)
            if distance < 138:
                alpha = int(38 * (1 - distance / 138))
                draw.line([(x1, y1), (x2, y2)], fill=(142, 132, 255, alpha), width=1)


def draw_wordmark(draw: ImageDraw.ImageDraw) -> None:
    mark_font = font("ZalandoSansExpanded-Bold.ttf", 64)
    lab_font = font("ZalandoSans-Medium.ttf", 30)
    x = 82
    y = 94
    draw.text((x, y), "BIZON", font=mark_font, fill=(255, 255, 255, 242))
    draw.text((x + 10, y + 72), "LABS", font=lab_font, fill=(255, 255, 255, 178))


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), (3, 0, 10))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for radius, alpha in [(540, 90), (380, 58), (250, 42)]:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        layer_draw.ellipse((715 - radius, 280 - radius, 715 + radius, 280 + radius), fill=(42, 0, 122, alpha))
        overlay.alpha_composite(layer.filter(ImageFilter.GaussianBlur(60)))

    draw_grid(draw)
    draw_particles(draw)

    draw.rectangle((70, 70, WIDTH - 70, HEIGHT - 70), outline=(255, 255, 255, 32), width=1)
    draw.line((70, 474, WIDTH - 70, 474), fill=(255, 255, 255, 36), width=1)

    draw_wordmark(draw)

    headline_font = font("ZalandoSans-Medium.ttf", 48)
    body_font = font("ZalandoSans-Regular.ttf", 28)
    eyebrow_font = font("ZalandoSansExpanded-Bold.ttf", 17)

    draw.text((82, 330), "Next-generation lipid nanoparticles", font=eyebrow_font, fill=(150, 141, 255, 220))

    headline = "Building particles with more control, flexibility, and purpose."
    y = 364
    for line in fit_text(draw, headline, headline_font, 735):
        draw.text((82, y), line, font=headline_font, fill=(255, 255, 255, 230))
        y += 58

    body = "A frontier biotechnology company developing a differentiated approach to particle design."
    body_lines = fit_text(draw, body, body_font, 840)
    y = 504
    for line in body_lines[:2]:
        draw.text((82, y), line, font=body_font, fill=(255, 255, 255, 155))
        y += 36

    composed = Image.alpha_composite(image.convert("RGBA"), overlay)
    composed.convert("RGB").save(OUT, quality=94)


if __name__ == "__main__":
    main()
