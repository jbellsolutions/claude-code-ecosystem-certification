#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "course-data.json"
BRAND_DIR = ROOT / "site" / "assets" / "brand"
SLATE_DIR = BRAND_DIR / "slates"

WIDTH = 1400
HEIGHT = 900
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720


def load_data() -> dict:
    return json.loads(DATA_PATH.read_text())


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


DISPLAY_FONT = "/System/Library/Fonts/NewYork.ttf"
DISPLAY_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SANS_FONT = "/System/Library/Fonts/Avenir Next.ttc"


def make_background(width: int, height: int) -> Image.Image:
    img = Image.new("RGB", (width, height), "#efe8db")
    draw = ImageDraw.Draw(img)

    for y in range(height):
        blend = y / max(height - 1, 1)
        r = int(239 - (239 - 32) * blend)
        g = int(232 - (232 - 49) * blend)
        b = int(219 - (219 - 55) * blend)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    for box, fill in [
        ((-120, -80, width // 2, height // 2), (237, 137, 54)),
        ((width // 2, 0, width + 180, height // 2 + 100), (29, 78, 86)),
        ((width // 3, height // 2, width + 140, height + 100), (8, 28, 43)),
    ]:
        blob = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        blob_draw = ImageDraw.Draw(blob)
        blob_draw.ellipse(box, fill=fill + (120,))
        blob = blob.filter(ImageFilter.GaussianBlur(64))
        img = Image.alpha_composite(img.convert("RGBA"), blob).convert("RGB")

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for step in range(-height, width, 58):
        overlay_draw.line(
            [(step, 0), (step + height, height)],
            fill=(255, 255, 255, 22),
            width=2,
        )
    overlay = overlay.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def round_rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def add_glow(base: Image.Image, xy: tuple[int, int, int, int], radius: int, color: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    layer_draw.rounded_rectangle(xy, radius=radius, fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(28))
    return Image.alpha_composite(base.convert("RGBA"), layer)


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def draw_badge(img: Image.Image, center: tuple[int, int], radius: int, top: str, bottom: str) -> None:
    draw = ImageDraw.Draw(img)
    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill="#f2eadc", outline="#183842", width=5)
    draw.ellipse((cx - radius + 16, cy - radius + 16, cx + radius - 16, cy + radius - 16), outline="#ea7f3a", width=4)
    for i in range(18):
        angle = math.radians((360 / 18) * i)
        x1 = cx + math.cos(angle) * (radius - 10)
        y1 = cy + math.sin(angle) * (radius - 10)
        x2 = cx + math.cos(angle) * (radius + 8)
        y2 = cy + math.sin(angle) * (radius + 8)
        draw.line((x1, y1, x2, y2), fill="#ea7f3a", width=3)

    title_font = font(DISPLAY_BOLD, 30)
    sub_font = font(SANS_FONT, 20)
    tw = draw.textbbox((0, 0), top, font=title_font)
    bw = draw.textbbox((0, 0), bottom, font=sub_font)
    draw.text((cx - (tw[2] - tw[0]) / 2, cy - 28), top, font=title_font, fill="#183842")
    draw.text((cx - (bw[2] - bw[0]) / 2, cy + 10), bottom, font=sub_font, fill="#4e5c5e")


def render_hero(data: dict) -> None:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    img = make_background(WIDTH, HEIGHT)
    img = add_glow(img, (72, 82, 890, 796), 38, (245, 237, 224, 96))
    draw = ImageDraw.Draw(img)

    round_rect(draw, (72, 82, 890, 796), 42, fill="#f5efe4", outline="#d6c8b5", width=2)
    round_rect(draw, (930, 112, 1288, 404), 36, fill="#16313a", outline="#ffffff22", width=2)
    round_rect(draw, (930, 438, 1288, 744), 36, fill="#f2eadc", outline="#ffffff44", width=2)

    kicker_font = font(SANS_FONT, 24)
    title_font = font(DISPLAY_FONT, 72)
    headline_font = font(DISPLAY_BOLD, 34)
    body_font = font(SANS_FONT, 26)
    micro_font = font(SANS_FONT, 21)

    draw.text((126, 148), data["kicker"].upper(), font=kicker_font, fill="#ea7f3a")
    title_text = wrap(data["title"], 16)
    draw.multiline_text((126, 190), title_text, font=title_font, fill="#102731", spacing=6)
    title_box = draw.multiline_textbbox((126, 190), title_text, font=title_font, spacing=6)

    headline_y = title_box[3] + 22
    headline_text = wrap(data["headline"], 24)
    draw.multiline_text((126, headline_y), headline_text, font=headline_font, fill="#183842", spacing=6)
    headline_box = draw.multiline_textbbox((126, headline_y), headline_text, font=headline_font, spacing=6)

    body_y = headline_box[3] + 26
    body_text = wrap(data["subheadline"], 36)
    draw.multiline_text((126, body_y), body_text, font=body_font, fill="#4e5c5e", spacing=10)
    body_box = draw.multiline_textbbox((126, body_y), body_text, font=body_font, spacing=10)

    chips = [
        f"{data['stats']['lessonCount']} source-order modules",
        f"{data['stats']['runtime']} of practical instruction",
    ]
    x = 126
    y = body_box[3] + 24
    for chip in chips:
        bbox = draw.textbbox((0, 0), chip, font=micro_font)
        chip_w = bbox[2] - bbox[0] + 36
        round_rect(draw, (x, y, x + chip_w, y + 48), 24, fill="#ede1cf", outline="#d5c2aa")
        draw.text((x + 18, y + 10), chip, font=micro_font, fill="#183842")
        y += 64

    draw.text((974, 150), "Ecosystem Lens", font=font(DISPLAY_BOLD, 32), fill="#f4ead8")
    for idx, pillar in enumerate(
        [("Chat", "Search and quick answers"), ("Cowork", "Business-side workflows"), ("Code", "Deep execution and builds")]
    ):
        top = 206 + idx * 68
        round_rect(draw, (972, top, 1246, top + 54), 24, fill="#24434d", outline="#ffffff22")
        draw.text((996, top + 9), pillar[0], font=font(DISPLAY_BOLD, 22), fill="#f4ead8")
        draw.text((1078, top + 14), pillar[1], font=font(SANS_FONT, 14), fill="#d7e2e0")

    draw.text((974, 468), "Ideal For", font=font(DISPLAY_BOLD, 32), fill="#183842")
    visual_audience = ["Founders and operators", "Executive assistants and VAs", "Recruiting and delivery leads"]
    for idx, item in enumerate(visual_audience):
        top = 522 + idx * 66
        round_rect(draw, (972, top, 1246, top + 52), 24, fill="#fff9ef", outline="#ddcdb8")
        draw.ellipse((990, top + 15, 1006, top + 31), fill="#ea7f3a")
        draw.text((1024, top + 13), item, font=font(SANS_FONT, 16), fill="#4e5c5e")

    draw_badge(img, (1212, 770), 64, "Level One", "Certified")
    img.save(BRAND_DIR / "hero-art.png", quality=95)


def render_social_card(data: dict) -> None:
    width, height = 1600, 900
    img = make_background(width, height)
    img = add_glow(img, (88, 94, 1098, 808), 42, (248, 241, 230, 86))
    draw = ImageDraw.Draw(img)
    round_rect(draw, (88, 94, 1098, 808), 42, fill="#f6efe4", outline="#d6c8b5", width=2)
    draw.text((150, 164), data["kicker"].upper(), font=font(SANS_FONT, 28), fill="#ea7f3a")
    title_text = wrap(data["title"], 16)
    draw.multiline_text((150, 216), title_text, font=font(DISPLAY_FONT, 84), fill="#102731", spacing=8)
    title_box = draw.multiline_textbbox((150, 216), title_text, font=font(DISPLAY_FONT, 84), spacing=8)
    headline_y = title_box[3] + 28
    headline_text = wrap(data["headline"], 22)
    draw.multiline_text((150, headline_y), headline_text, font=font(DISPLAY_BOLD, 46), fill="#183842", spacing=10)
    headline_box = draw.multiline_textbbox((150, headline_y), headline_text, font=font(DISPLAY_BOLD, 46), spacing=10)
    body_y = headline_box[3] + 28
    draw.multiline_text((150, body_y), wrap(data["subheadline"], 36), font=font(SANS_FONT, 28), fill="#4e5c5e", spacing=12)
    draw_badge(img, (1298, 452), 126, "Claude Code", "Level One")
    img.save(BRAND_DIR / "social-card.png", quality=95)


def render_slates(data: dict) -> None:
    SLATE_DIR.mkdir(parents=True, exist_ok=True)

    for kind, title, body, filename in [
        (
            "intro",
            data["title"],
            "A practical certification for prospects, clients, and internal teams who want Claude working across chat, business workflows, and code.",
            BRAND_DIR / "intro-slate.png",
        ),
        (
            "outro",
            "Next Step",
            "Use this one-pager to qualify fit, align stakeholders, and launch a private cohort or implementation sprint.",
            BRAND_DIR / "outro-slate.png",
        ),
    ]:
        img = make_background(VIDEO_WIDTH, VIDEO_HEIGHT)
        draw = ImageDraw.Draw(img)
        round_rect(draw, (84, 82, 1192, 638), 40, fill="#f6efe4", outline="#d9c9b3", width=2)
        draw.text((132, 142), kind.upper(), font=font(SANS_FONT, 22), fill="#ea7f3a")
        title_text = wrap(title, 18)
        draw.multiline_text((132, 182), title_text, font=font(DISPLAY_FONT, 52), fill="#102731", spacing=6)
        title_box = draw.multiline_textbbox((132, 182), title_text, font=font(DISPLAY_FONT, 52), spacing=6)
        body_y = title_box[3] + 24
        draw.multiline_text((132, body_y), wrap(body, 34), font=font(SANS_FONT, 26), fill="#4e5c5e", spacing=10)
        draw_badge(img, (1038, 518), 88, "Claude", "Code")
        img.save(filename, quality=95)

    for index, module in enumerate(data["modules"], start=1):
        img = make_background(VIDEO_WIDTH, VIDEO_HEIGHT)
        draw = ImageDraw.Draw(img)
        round_rect(draw, (82, 80, 1196, 640), 40, fill="#f6efe4", outline="#d9c9b3", width=2)
        draw.text((132, 136), module["orderLabel"].upper(), font=font(SANS_FONT, 22), fill="#ea7f3a")
        title_text = wrap(module["title"], 22)
        draw.multiline_text((132, 182), title_text, font=font(DISPLAY_FONT, 50), fill="#102731", spacing=6)
        title_box = draw.multiline_textbbox((132, 182), title_text, font=font(DISPLAY_FONT, 50), spacing=6)

        headline_y = title_box[3] + 22
        headline_text = wrap(module["headline"], 32)
        draw.multiline_text((132, headline_y), headline_text, font=font(DISPLAY_BOLD, 28), fill="#183842", spacing=8)
        headline_box = draw.multiline_textbbox((132, headline_y), headline_text, font=font(DISPLAY_BOLD, 28), spacing=8)

        body_y = headline_box[3] + 20
        body_text = wrap(module["subheadline"], 42)
        draw.multiline_text((132, body_y), body_text, font=font(SANS_FONT, 20), fill="#4e5c5e", spacing=8)
        round_rect(draw, (132, 574, 356, 618), 22, fill="#ede1cf", outline="#ddcdb8")
        draw.text((154, 585), f"Runtime: {module['duration']}", font=font(SANS_FONT, 18), fill="#183842")
        draw_badge(img, (1048, 508), 94, "Level One", f"{index:02d}")
        img.save(SLATE_DIR / f"{module['id']}.png", quality=95)


def main() -> None:
    data = load_data()
    render_hero(data)
    render_social_card(data)
    render_slates(data)
    print("Rendered brand assets")


if __name__ == "__main__":
    main()
