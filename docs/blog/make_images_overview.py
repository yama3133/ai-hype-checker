"""Qiita記事(現状まとめ)用の構成図・フロー図(日本語, JPG)を生成する。

AWS公式Architecture Icons(ダウンロード済みをdocs/blog/assets/icons/に配置)を実物のまま使用し、
フラット2D・グループ化セクション・AWS Cloud枠のスタイルで描画する。

実行: uv run --with pillow python3 make_images_overview.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"

JA_BOLD = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"
JA_REGULAR = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

INK = (23, 23, 23)
GRAY = (100, 100, 108)
LIGHT_GRAY = (150, 150, 158)
LINE = (170, 170, 178)
WHITE = (255, 255, 255)

TEAL = (1, 168, 141)
TEAL_BG = (224, 245, 241)
TEAL_BORDER = (1, 150, 126)
RED = (221, 52, 76)
RED_BG = (253, 226, 231)
CLOUD_BORDER = (35, 47, 61)
CLOUD_BG = (245, 248, 252)
NEUTRAL_BG = (247, 247, 249)
NEUTRAL_BORDER = (200, 200, 206)
GREEN = (22, 163, 74)
GREEN_BG = (224, 246, 233)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_w(draw, text, f) -> int:
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def centered_text(draw, cx, y, text, f, fill):
    w = text_w(draw, text, f)
    draw.text((cx - w / 2, y), text, font=f, fill=fill)
    return w


def rounded_box(draw, x, y, w, h, fill, border, radius=20, width=3):
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=radius, fill=fill, outline=border, width=width)


def rounded_icon(path: Path, size: int, radius_ratio: float = 0.22) -> Image.Image:
    """アイコンPNGを正方形に配置し、角丸マスクをかける(公式アイコンの意匠は変更しない)。"""
    im = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([(0, 0), (size, size)], radius=int(size * radius_ratio), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def paste_icon(canvas: Image.Image, path: Path, cx: int, top: int, size: int, rounded=True):
    icon = rounded_icon(path, size) if rounded else Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    canvas.paste(icon, (int(cx - size / 2), top), icon)


def h_arrow(draw, x1, x2, y, color=LINE, width=4):
    draw.line([(x1, y), (x2 - 14, y)], fill=color, width=width)
    draw.polygon([(x2, y), (x2 - 16, y - 8), (x2 - 16, y + 8)], fill=color)


def v_arrow(draw, x, y1, y2, color=LINE, width=4):
    draw.line([(x, y1), (x, y2 - 14)], fill=color, width=width)
    draw.polygon([(x, y2), (x - 8, y2 - 16), (x + 8, y2 - 16)], fill=color)


def diag_arrow(draw, p1, p2, color=LINE, width=4):
    import math

    x1, y1 = p1
    x2, y2 = p2
    angle = math.atan2(y2 - y1, x2 - x1)
    ex = x2 - 16 * math.cos(angle)
    ey = y2 - 16 * math.sin(angle)
    draw.line([(x1, y1), (ex, ey)], fill=color, width=width)
    a1, a2 = angle + 2.7, angle - 2.7
    draw.polygon(
        [(x2, y2), (x2 + 16 * math.cos(a1), y2 + 16 * math.sin(a1)), (x2 + 16 * math.cos(a2), y2 + 16 * math.sin(a2))],
        fill=color,
    )


# ----------------------------------------------------------------------
# 構成図
# ----------------------------------------------------------------------


def draw_architecture() -> None:
    W, H = 2040, 1040
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    draw.text((60, 36), "Amazon Bedrock AgentCore Runtime + Gateway / Strands Agents", font=font(JA_BOLD, 24), fill=TEAL_BORDER)
    draw.text((60, 72), "AI驚き屋発見器 — 構成図", font=font(JA_BOLD, 46), fill=INK)
    draw.line([(60, 148), (W - 60, 148)], fill=LINE, width=1)
    centered_text(
        draw, W // 2, 172,
        "認証: VercelはこのRuntimeだけに限定したIAMユーザーのアクセスキーでInvokeAgentRuntimeを呼ぶ",
        font(JA_REGULAR, 22), GRAY,
    )

    ROW_Y = 340
    ROW_H = 320

    # --- ユーザー (AWS Cloud外) ---
    user_x, user_w = 60, 280
    rounded_box(draw, user_x, ROW_Y, user_w, ROW_H, NEUTRAL_BG, NEUTRAL_BORDER)
    paste_icon(img, ICONS / "Res_Client_48_Light.png", user_x + user_w // 2, ROW_Y + 34, 110, rounded=False)
    centered_text(draw, user_x + user_w // 2, ROW_Y + 168, "ユーザー", font(JA_BOLD, 24), INK)
    centered_text(draw, user_x + user_w // 2, ROW_Y + 202, "Xの投稿を", font(JA_REGULAR, 18), GRAY)
    centered_text(draw, user_x + user_w // 2, ROW_Y + 228, "コピペで貼り付け", font(JA_REGULAR, 18), GRAY)

    # --- Next.js on Vercel (AWS Cloud外) ---
    vercel_x, vercel_w = 460, 320
    rounded_box(draw, vercel_x, ROW_Y, vercel_w, ROW_H, NEUTRAL_BG, NEUTRAL_BORDER)
    draw.ellipse(
        [(vercel_x + vercel_w // 2 - 46, ROW_Y + 30), (vercel_x + vercel_w // 2 + 46, ROW_Y + 122)],
        outline=CLOUD_BORDER, width=5,
    )
    centered_text(draw, vercel_x + vercel_w // 2, ROW_Y + 54, "▲", font(JA_BOLD, 44), CLOUD_BORDER)
    centered_text(draw, vercel_x + vercel_w // 2, ROW_Y + 168, "Next.js on Vercel", font(JA_BOLD, 24), INK)
    centered_text(draw, vercel_x + vercel_w // 2, ROW_Y + 202, "判定UI", font(JA_REGULAR, 18), GRAY)
    centered_text(draw, vercel_x + vercel_w // 2, ROW_Y + 228, "/api/judge", font(JA_REGULAR, 18), GRAY)

    # --- AWS Cloud枠 ---
    cloud_x0, cloud_y0, cloud_x1, cloud_y1 = 880, 260, 1700, 980
    rounded_box(draw, cloud_x0, cloud_y0, cloud_x1 - cloud_x0, cloud_y1 - cloud_y0, CLOUD_BG, CLOUD_BORDER, radius=28, width=3)
    paste_icon(img, ICONS / "AWS-Cloud-logo_32.png", cloud_x0 + 44, cloud_y0 + 16, 44, rounded=False)
    draw.text((cloud_x0 + 76, cloud_y0 + 14), "AWS Cloud", font=font(JA_BOLD, 20), fill=CLOUD_BORDER)
    draw.text((cloud_x0 + 76, cloud_y0 + 40), "us-east-1", font=font(JA_REGULAR, 15), fill=GRAY)

    # AgentCore Runtime
    rt_x, rt_w, rt_h = 920, 300, ROW_H
    rounded_box(draw, rt_x, ROW_Y, rt_w, rt_h, TEAL_BG, TEAL_BORDER)
    paste_icon(img, ICONS / "Arch_Amazon-Bedrock-AgentCore_48.png", rt_x + rt_w // 2, ROW_Y + 20, 110)
    centered_text(draw, rt_x + rt_w // 2, ROW_Y + 150, "Amazon Bedrock", font(JA_BOLD, 21), INK)
    centered_text(draw, rt_x + rt_w // 2, ROW_Y + 176, "AgentCore Runtime", font(JA_BOLD, 21), INK)
    centered_text(draw, rt_x + rt_w // 2, ROW_Y + 206, "Strands Agent", font(JA_REGULAR, 16), GRAY)
    for i, tool in enumerate(["・scan_hype_phrases", "・check_evidence_density", "・web_search"]):
        centered_text(draw, rt_x + rt_w // 2, ROW_Y + 230 + i * 18, tool, font(JA_REGULAR, 13), GRAY)

    # AgentCore Gateway
    gw_x, gw_w = 1360, 300
    rounded_box(draw, gw_x, ROW_Y, gw_w, rt_h, TEAL_BG, TEAL_BORDER)
    paste_icon(img, ICONS / "Arch_Amazon-Bedrock-AgentCore_48.png", gw_x + gw_w // 2, ROW_Y + 20, 110)
    centered_text(draw, gw_x + gw_w // 2, ROW_Y + 150, "Amazon Bedrock", font(JA_BOLD, 21), INK)
    centered_text(draw, gw_x + gw_w // 2, ROW_Y + 176, "AgentCore Gateway", font(JA_BOLD, 21), INK)
    centered_text(draw, gw_x + gw_w // 2, ROW_Y + 206, "Web Search (MCP)", font(JA_REGULAR, 16), GRAY)
    centered_text(draw, gw_x + gw_w // 2, ROW_Y + 230, "SigV4署名 / AWS_IAM認可", font(JA_REGULAR, 13), GRAY)

    # Amazon Bedrock (Claude Sonnet 4.6)
    bed_x, bed_w, bed_y, bed_h = 920, 300, ROW_Y + ROW_H + 60, 200
    rounded_box(draw, bed_x, bed_y, bed_w, bed_h, TEAL_BG, TEAL_BORDER)
    paste_icon(img, ICONS / "Arch_Amazon-Bedrock_48.png", bed_x + bed_w // 2, bed_y + 18, 100)
    centered_text(draw, bed_x + bed_w // 2, bed_y + 132, "Amazon Bedrock", font(JA_BOLD, 21), INK)
    centered_text(draw, bed_x + bed_w // 2, bed_y + 160, "Claude Sonnet 4.6", font(JA_REGULAR, 18), GRAY)

    # --- 外部Web検索 (AWS Cloud外) ---
    web_x, web_w = 1740, 240
    rounded_box(draw, web_x, ROW_Y, web_w, rt_h, NEUTRAL_BG, NEUTRAL_BORDER)
    paste_icon(img, ICONS / "Res_Globe_48_Light.png", web_x + web_w // 2, ROW_Y + 34, 110, rounded=False)
    centered_text(draw, web_x + web_w // 2, ROW_Y + 168, "外部Web検索", font(JA_BOLD, 22), INK)
    centered_text(draw, web_x + web_w // 2, ROW_Y + 200, "検索結果", font(JA_REGULAR, 16), GRAY)
    centered_text(draw, web_x + web_w // 2, ROW_Y + 224, "(一次情報)", font(JA_REGULAR, 16), GRAY)

    mid_y = ROW_Y + rt_h // 2

    # 矢印
    h_arrow(draw, user_x + user_w, vercel_x, mid_y)
    centered_text(draw, (user_x + user_w + vercel_x) // 2, mid_y - 38, "貼り付け", font(JA_BOLD, 20), GRAY)

    h_arrow(draw, vercel_x + vercel_w, rt_x, mid_y, color=TEAL_BORDER, width=5)
    centered_text(draw, (vercel_x + vercel_w + rt_x) // 2, mid_y - 38, "呼び出し", font(JA_BOLD, 20), TEAL_BORDER)

    h_arrow(draw, rt_x + rt_w, gw_x, mid_y, color=TEAL_BORDER, width=4)
    centered_text(draw, (rt_x + rt_w + gw_x) // 2, mid_y - 38, "検索依頼", font(JA_BOLD, 19), TEAL_BORDER)

    h_arrow(draw, gw_x + gw_w, web_x, mid_y)
    centered_text(draw, (gw_x + gw_w + web_x) // 2, mid_y - 38, "検索", font(JA_BOLD, 19), GRAY)

    v_arrow(draw, rt_x + rt_w // 2, ROW_Y + rt_h, bed_y, color=TEAL_BORDER, width=4)
    draw.text((rt_x + rt_w // 2 + 20, ROW_Y + rt_h + 12), "推論", font=font(JA_BOLD, 18), fill=TEAL_BORDER)

    img.save(ASSETS / "diagram-overview-ja.jpg", "JPEG", quality=94)


# ----------------------------------------------------------------------
# フロー図
# ----------------------------------------------------------------------

STEP_W = 820
STEP_X = 190


def step_box(draw, y, h, num, title, subs, fill=NEUTRAL_BG, border=NEUTRAL_BORDER, title_color=INK):
    rounded_box(draw, STEP_X, y, STEP_W, h, fill, border, radius=18, width=3)
    badge_r = 22
    bx, by = STEP_X + 40, y + 40
    draw.ellipse([(bx - badge_r, by - badge_r), (bx + badge_r, by + badge_r)], fill=border)
    centered_text(draw, bx, by - 15, str(num), font(JA_BOLD, 22), WHITE)
    draw.text((STEP_X + 82, y + 22), title, font=font(JA_BOLD, 24), fill=title_color)
    ty = y + 60
    for s in subs:
        draw.text((STEP_X + 82, ty), s, font=font(JA_REGULAR, 17), fill=GRAY)
        ty += 26


def draw_flow() -> None:
    W, H = 1220, 1820
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    draw.text((60, 36), "AI驚き屋発見器 — 判定フロー", font=font(JA_BOLD, 42), fill=INK)
    draw.text((60, 90), "何をすると何が起きるか。スコアが70点を超えると画面が赤くなる仕組み", font=font(JA_REGULAR, 21), fill=GRAY)
    draw.line([(60, 134), (W - 60, 134)], fill=LINE, width=1)

    cx = W // 2
    y = 172

    step_box(draw, y, 118, 1, "投稿本文を貼り付ける", ["Xの投稿をコピーしてテキストエリアに貼り付ける"])
    y1_bottom = y + 118
    y += 118 + 90
    v_arrow(draw, cx, y1_bottom, y)

    step_box(draw, y, 100, 2, "「判定する」ボタンを押す", [])
    y2_bottom = y + 100
    y += 100 + 90
    v_arrow(draw, cx, y2_bottom, y)

    step_box(draw, y, 118, 3, "AgentCore Runtimeを呼び出す", ["Next.js(Vercel) → InvokeAgentRuntime → Strands Agent"])
    y3_bottom = y + 118
    y += 118 + 90
    v_arrow(draw, cx, y3_bottom, y)

    step_box(
        draw, y, 190, 4, "Strands Agentが3つの視点で分析", [
            "・煽り文句のパターンをスキャン (scan_hype_phrases)",
            "・数値/モデル名/出典の有無をチェック (check_evidence_density)",
            "・主張をWeb検索でファクトチェック (web_search)",
        ],
        fill=TEAL_BG, border=TEAL_BORDER, title_color=TEAL_BORDER,
    )
    y4_bottom = y + 190
    y += 190 + 90
    v_arrow(draw, cx, y4_bottom, y, color=TEAL_BORDER)

    step_box(draw, y, 100, 5, "0〜100点のスコアとverdictを算出", [], fill=TEAL_BG, border=TEAL_BORDER, title_color=TEAL_BORDER)
    y5_bottom = y + 100
    y += 100 + 100
    v_arrow(draw, cx, y5_bottom, y)

    # 分岐(ひし形)
    dia_w, dia_h = 420, 170
    dx0, dy0 = cx - dia_w // 2, y
    dx1, dy1 = cx + dia_w // 2, y + dia_h
    draw.polygon(
        [(cx, dy0), (dx1, (dy0 + dy1) // 2), (cx, dy1), (dx0, (dy0 + dy1) // 2)],
        fill=(255, 247, 230), outline=(180, 130, 20), width=3,
    )
    centered_text(draw, cx, (dy0 + dy1) // 2 - 34, "スコアは", font(JA_BOLD, 22), (140, 100, 10))
    centered_text(draw, cx, (dy0 + dy1) // 2 - 8, "70点を超えたか?", font(JA_BOLD, 22), (140, 100, 10))

    branch_top = dy1 + 110
    box_w = 460
    left_x = 90
    right_x = W - 90 - box_w

    diag_arrow(draw, (dx0, (dy0 + dy1) // 2), (left_x + box_w // 2, branch_top), color=RED, width=4)
    diag_arrow(draw, (dx1, (dy0 + dy1) // 2), (right_x + box_w // 2, branch_top), color=GREEN, width=4)

    lx_label = (dx0 + left_x + box_w // 2) // 2
    draw.text((lx_label - 20, (dy0 + dy1) // 2 + (branch_top - (dy0 + dy1) // 2) // 2 - 30), "超えた", font=font(JA_BOLD, 20), fill=RED)
    rx_label = (dx1 + right_x + box_w // 2) // 2
    draw.text((rx_label - 20, (dy0 + dy1) // 2 + (branch_top - (dy0 + dy1) // 2) // 2 - 30), "超えない", font=font(JA_BOLD, 20), fill=GREEN)

    # 分岐後のボックス
    bh = 220
    rounded_box(draw, left_x, branch_top, box_w, bh, RED_BG, RED, radius=18, width=3)
    centered_text(draw, left_x + box_w // 2, branch_top + 26, "画面全体が赤色に変わる", font(JA_BOLD, 23), RED)
    for i, line in enumerate([
        "見出し・説明文の文字色を白系に切替",
        "結果カード自体は白のままにして",
        "文字は最後まで読める状態を保つ",
    ]):
        centered_text(draw, left_x + box_w // 2, branch_top + 76 + i * 30, line, font(JA_REGULAR, 17), (140, 30, 40))

    rounded_box(draw, right_x, branch_top, box_w, bh, GREEN_BG, GREEN, radius=18, width=3)
    centered_text(draw, right_x + box_w // 2, branch_top + 26, "通常の背景のまま結果を表示", font(JA_BOLD, 23), GREEN)
    for i, line in enumerate([
        "verdictは「堅実」または「やや誇張」",
        "判定理由・検出フレーズ・",
        "ファクトチェック結果を通常表示",
    ]):
        centered_text(draw, right_x + box_w // 2, branch_top + 76 + i * 30, line, font(JA_REGULAR, 17), (20, 90, 60))

    img.save(ASSETS / "flow-overview-ja.jpg", "JPEG", quality=94)


def main() -> None:
    draw_architecture()
    draw_flow()
    print("done")


if __name__ == "__main__":
    main()
