"""AI驚き屋発見器 ブログ用の構成図(PNG)とサムネイル(PNG/JPG)を日英で生成する。

実行: uv run --with pillow python3 make_images.py
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

EN_BOLD = "/System/Library/Fonts/Helvetica.ttc"
JA_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"

INDIGO = (79, 70, 229)
RED = (220, 38, 38)
RED_DEEP = (127, 29, 29)
GREEN = (22, 163, 74)
AMBER = (217, 119, 6)
INK = (23, 23, 23)
WHITE = (250, 250, 250)
GRAY = (113, 113, 122)
BOX_BG = (255, 255, 255)
BOX_BORDER = (82, 82, 91)
LINE = (161, 161, 170)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def centered_text(draw, cx, y, text, f, fill):
    bbox = draw.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw / 2, y), text, font=f, fill=fill)


def box(draw, x, y, w, h, label, ff, fill=BOX_BG, border=BOX_BORDER, text_fill=INK, fs=24, line_gap=10):
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=16, fill=fill, outline=border, width=3)
    f = font(ff, fs)
    lines = label.split("\n")
    line_h = f.size + line_gap
    total_h = line_h * len(lines)
    ty = y + (h - total_h) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        tw = bbox[2] - bbox[0]
        draw.text((x + (w - tw) // 2, ty), line, font=f, fill=text_fill)
        ty += line_h


def arrow(draw, p1, p2, color=LINE, width=5):
    x1, y1 = p1
    x2, y2 = p2
    draw.line([p1, p2], fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 18
    a1, a2 = angle + math.pi - 0.4, angle + math.pi + 0.4
    pts = [
        (x2, y2),
        (x2 + size * math.cos(a1), y2 + size * math.sin(a1)),
        (x2 + size * math.cos(a2), y2 + size * math.sin(a2)),
    ]
    draw.polygon(pts, fill=color)


DIAGRAM_TEXT = {
    "ja": dict(
        eyebrow="AI / Amazon Bedrock AgentCore / Strands Agents",
        title="AI驚き屋発見器 — 構成図",
        flow_caption="① 貼り付け　→　② InvokeAgentRuntime　→　③ Converse API",
        box_user="Xの投稿\n(テキストを貼り付け)",
        box_web="Next.js on Vercel\n判定UI + /api/judge",
        box_agent="AgentCore Runtime\nStrands Agent\n・scan_hype_phrases\n・check_evidence_density",
        box_model="Claude Sonnet 4.6\n(Amazon Bedrock)",
        result_title="判定結果",
        result_body="0〜100の驚き屋度スコア + verdict + 理由\nスコアが70を超えると画面が赤くなる",
        legend=["堅実", "やや誇張", "驚き屋"],
        font=JA_BOLD,
    ),
    "en": dict(
        eyebrow="AI / Amazon Bedrock AgentCore / Strands Agents",
        title="AI Hype Detector — Architecture",
        flow_caption="1. paste  ->  2. InvokeAgentRuntime  ->  3. Converse API",
        box_user="X post\n(paste text)",
        box_web="Next.js on Vercel\njudge UI + /api/judge",
        box_agent="AgentCore Runtime\nStrands Agent\n- scan_hype_phrases\n- check_evidence_density",
        box_model="Claude Sonnet 4.6\n(Amazon Bedrock)",
        result_title="Result",
        result_body="0-100 hype score + verdict + reasons\nScreen turns red when score > 70",
        legend=["Grounded", "Exaggerated", "Hype"],
        font=EN_BOLD,
    ),
}


def draw_diagram(lang: str) -> None:
    t = DIAGRAM_TEXT[lang]
    ff = t["font"]
    W, H = 1600, 900
    img = Image.new("RGB", (W, H), (250, 250, 252))
    draw = ImageDraw.Draw(img)

    draw.text((60, 40), t["eyebrow"], font=font(ff, 22), fill=INDIGO)
    draw.text((60, 74), t["title"], font=font(ff, 40), fill=INK)
    draw.line([(60, 140), (W - 60, 140)], fill=LINE, width=1)
    centered_text(draw, W // 2, 160, t["flow_caption"], font(ff, 22), GRAY)

    bw, bh = 320, 200
    gap = 60
    total_w = bw * 4 + gap * 3
    x0 = (W - total_w) // 2
    y0 = 240

    boxes = [t["box_user"], t["box_web"], t["box_agent"], t["box_model"]]
    borders = [BOX_BORDER, INDIGO, INDIGO, AMBER]
    sizes = [24, 24, 19, 24]
    xs = []
    for i, label in enumerate(boxes):
        x = x0 + i * (bw + gap)
        xs.append(x)
        box(draw, x, y0, bw, bh, label, ff, border=borders[i], fs=sizes[i])

    for i in range(3):
        ax1 = xs[i] + bw
        ax2 = xs[i + 1]
        ay = y0 + bh // 2
        arrow(draw, (ax1 + 6, ay), (ax2 - 6, ay), color=INDIGO, width=5)

    ry = y0 + bh + 90
    rw, rh = 980, 150
    rx = (W - rw) // 2
    draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=16, outline=RED, width=3, fill=(254, 242, 242))
    centered_text(draw, W // 2, ry + 16, t["result_title"], font(ff, 24), RED_DEEP)
    f_body = font(ff, 20)
    ty = ry + 54
    for line in t["result_body"].split("\n"):
        centered_text(draw, W // 2, ty, line, f_body, (80, 20, 20))
        ty += 30

    mx = xs[3] + bw // 2
    arrow(draw, (mx, y0 + bh + 6), (mx, ry - 6), color=RED, width=5)

    chip_y = H - 70
    chip_colors = [GREEN, AMBER, RED]
    cx = 60
    f_chip = font(ff, 18)
    for label, color in zip(t["legend"], chip_colors):
        tb = draw.textbbox((0, 0), label, font=f_chip)
        w = tb[2] - tb[0] + 36
        draw.rounded_rectangle([(cx, chip_y), (cx + w, chip_y + 40)], radius=20, outline=color, width=2)
        centered_text(draw, cx + w // 2, chip_y + 9, label, f_chip, color)
        cx += w + 16

    img.save(ASSETS / f"diagram-{lang}.png", "PNG")


THUMB_TEXT = {
    "ja": dict(
        eyebrow="個人開発 / Amazon Bedrock AgentCore",
        title_lines=["AI驚き屋", "発見器"],
        subtitle_lines=["Xの「AI驚き屋」を", "AIエージェントで見抜く"],
        badge_label="驚き屋度",
        tags="#AI  #AgentCore  #Strands  #Vercel",
        font=JA_BOLD,
    ),
    "en": dict(
        eyebrow="Side Project / Amazon Bedrock AgentCore",
        title_lines=["AI Hype", "Detector"],
        subtitle_lines=["Catching AI hype-mongers on X", "with an AI agent"],
        badge_label="Hype Score",
        tags="#AI  #AgentCore  #Strands  #Vercel",
        font=EN_BOLD,
    ),
}


def draw_thumbnail(lang: str) -> None:
    t = THUMB_TEXT[lang]
    ff = t["font"]
    W, H = 1200, 630

    photo = Image.open(ASSETS / "source-photo-surprised-man.png").convert("RGB")
    pw, ph = photo.size
    scale = max(W / pw, H / ph)
    nw, nh = int(pw * scale), int(ph * scale)
    photo = photo.resize((nw, nh))
    left = (nw - W) // 2
    top = (nh - H) // 2
    photo = photo.crop((left, top, left + W, top + H))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for x in range(W):
        t_ = min(1.0, x / (W * 0.62))
        alpha = int(215 * (1 - t_))
        odraw.line([(x, 0), (x, H)], fill=(10, 10, 20, max(alpha, 0)))
    for y in range(H - 80, H):
        odraw.line([(0, y), (W, y)], fill=(10, 10, 20, 150))

    img = Image.alpha_composite(photo.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (8, H)], fill=RED)

    draw.text((60, 50), t["eyebrow"], font=font(ff, 22), fill=(252, 165, 165))
    draw.line([(60, 88), (200, 88)], fill=RED, width=3)

    title_font = font(ff, 84)
    for i, line in enumerate(t["title_lines"]):
        draw.text((60, 126 + i * 94), line, font=title_font, fill=WHITE)

    sub_font = font(ff, 27)
    sy = 126 + len(t["title_lines"]) * 94 + 18
    for line in t["subtitle_lines"]:
        draw.text((60, sy), line, font=sub_font, fill=(228, 228, 231))
        sy += 35

    bx, by, bd = W - 210, 55, 150
    draw.ellipse([(bx, by), (bx + bd, by + bd)], outline=RED, width=5, fill=(22, 8, 8))
    centered_text(draw, bx + bd // 2, by + 26, "97", font(ff, 56), RED)
    centered_text(draw, bx + bd // 2, by + bd - 40, t["badge_label"], font(ff, 16), (252, 165, 165))

    draw.text((60, H - 50), t["tags"], font=font(ff, 19), fill=(212, 212, 216))

    img.save(ASSETS / f"thumbnail-{lang}.png", "PNG")
    img.convert("RGB").save(ASSETS / f"thumbnail-{lang}.jpg", "JPEG", quality=92)


def main() -> None:
    for lang in ("ja", "en"):
        draw_diagram(lang)
        draw_thumbnail(lang)
    print("done")


if __name__ == "__main__":
    main()
