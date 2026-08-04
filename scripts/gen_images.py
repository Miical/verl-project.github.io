#!/usr/bin/env python3
"""Render the post cover images that are drawn rather than photographed.

Everything here is drawn from scratch with Pillow so the repository carries no
third-party image assets. Colours track the palette in assets/css/main.css.
Bringing your own cover is fine too -- just commit it next to the post.

Usage:
    python3 scripts/gen_images.py                       # regenerate all covers
    python3 scripts/gen_images.py --list                # show what would be built
"""

from __future__ import annotations

import argparse
import pathlib
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("error: Pillow is required -- pip install pillow")

W, H = 1200, 630

BG = (13, 17, 23)
BG_GLOW = (23, 36, 64)
ACCENT = (127, 165, 240)
TEXT = (230, 236, 245)
MUTED = (157, 173, 196)
RULE = (35, 45, 60)


def _font_dir() -> pathlib.Path:
    """DejaVu ships with matplotlib, and matplotlib is easier to rely on here
    than a particular system font package."""
    try:
        import matplotlib
    except ImportError:  # pragma: no cover
        sys.exit("error: matplotlib is required for its bundled DejaVu fonts")
    return pathlib.Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"


FONTS = _font_dir()


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=f) <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def base_canvas() -> Image.Image:
    """Dark background with a soft teal glow bleeding in from the top left."""
    img = Image.new("RGB", (W, H), BG)

    glow = Image.new("RGB", (W // 6, H // 6), BG)
    gd = ImageDraw.Draw(glow)
    gw, gh = glow.size
    for i in range(28, 0, -1):
        t = i / 28
        colour = tuple(int(BG[c] + (BG_GLOW[c] - BG[c]) * (1 - t) ** 2) for c in range(3))
        gd.ellipse([-gw * 0.30 - i * 2, -gh * 0.55 - i * 2, gw * 0.75 + i * 2, gh * 0.60 + i * 2], fill=colour)
    img.paste(glow.resize((W, H), Image.LANCZOS), (0, 0))

    d = ImageDraw.Draw(img)
    # Faint grid, a nod to the plots that end up in most of these posts.
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(BG[0] + 5, BG[1] + 6, BG[2] + 6), width=1)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(BG[0] + 5, BG[1] + 6, BG[2] + 6), width=1)

    d.rectangle([0, H - 8, W, H], fill=ACCENT)
    return img


def wordmark(d: ImageDraw.ImageDraw, x: int, y: int) -> int:
    """Draws `[verl]` with dimmed brackets. Returns the x cursor after it."""
    mono = font("DejaVuSansMono-Bold.ttf", 34)
    for ch, colour in (("[", (ACCENT[0] // 2, ACCENT[1] // 2, ACCENT[2] // 2)),
                       ("verl", ACCENT),
                       ("]", (ACCENT[0] // 2, ACCENT[1] // 2, ACCENT[2] // 2))):
        d.text((x, y), ch, font=mono, fill=colour)
        x += int(d.textlength(ch, font=mono))
    return x


def card(title: str, kicker: str, subtitle: str = "") -> Image.Image:
    img = base_canvas()
    d = ImageDraw.Draw(img)

    margin = 80
    x = wordmark(d, margin, margin)
    d.text((x + 16, margin + 6), kicker, font=font("DejaVuSans.ttf", 22), fill=MUTED)

    rule_y = margin + 74
    d.line([(margin, rule_y), (W - margin, rule_y)], fill=RULE, width=1)

    title_font = font("DejaVuSans-Bold.ttf", 62)
    sub_font = font("DejaVuSans.ttf", 26)
    title_lines = wrap(d, title, title_font, W - margin * 2)[:4]
    sub_lines = wrap(d, subtitle, sub_font, W - margin * 2)[:2] if subtitle else []

    # Centre the text block between the rule and the footer URL, so a one-line
    # title does not leave a hole in the middle of the card.
    line_h, sub_h, gap = 78, 38, 14
    block_h = len(title_lines) * line_h + (gap + len(sub_lines) * sub_h if sub_lines else 0)
    region_top, region_bottom = rule_y + 30, H - margin - 60
    y = region_top + max(0, (region_bottom - region_top - block_h) // 2)

    for line in title_lines:
        d.text((margin, y), line, font=title_font, fill=TEXT)
        y += line_h

    if sub_lines:
        y += gap
        for line in sub_lines:
            d.text((margin, y), line, font=sub_font, fill=MUTED)
            y += sub_h

    d.text(
        (margin, H - margin - 20),
        "verl-project.github.io",
        font=font("DejaVuSansMono.ttf", 22),
        fill=(ACCENT[0] - 60, ACCENT[1] - 40, ACCENT[2] - 40),
    )
    return img


# (output path, title, kicker, subtitle)
TARGETS: list[tuple[str, str, str, str]] = [
    (
        "content/posts/2026-08-04-introducing-the-verl-blog/cover.png",
        "Introducing the verl blog",
        "Announcement",
        "verl now has its own blog.",
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="print targets without writing them")
    args = parser.parse_args()

    for path, title, kicker, subtitle in TARGETS:
        out = pathlib.Path(path)
        if args.list:
            print(out)
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        card(title, kicker, subtitle).save(out, "PNG", optimize=True)
        print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
