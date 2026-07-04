"""煽り文句・誇張表現の検出ツール。"""
from __future__ import annotations

import re

# 「AI驚き屋」に典型的な決め台詞・誇張表現パターン
HYPE_PATTERNS: list[str] = [
    r"人類(の)?(未来|歴史)が変わる",
    r"もう(後戻り|元に戻)れない",
    r"知らないと(損|やばい|終わり)",
    r"(仕事|職業)が(なくなる|奪われる|消える)",
    r"(世界|業界)が(一変|激変)",
    r"これは(やばい|ヤバい|終わった|終わり)",
    r"誰も.*(気づいて|知らない)",
    r"衝撃(の)?(結果|事実|展開)",
    r"控えめに言って",
    r"今すぐ.*(乗り遅れる|手遅れ)",
    r"シンギュラリティ",
    r"バズって(いる|る)",
    r"神(アプデ|アップデート|ツール|モデル)",
    r"完全に(理解|終了)した",
    r"次元が違う",
    r"覇権(を)?(握る|取る)",
    r"エンジニアは(オワコン|不要|いらない)",
    r"(数年|数ヶ月|数か月)で(仕事|人類).*(なくなる|消える)",
]

_COMPILED = [re.compile(p) for p in HYPE_PATTERNS]


def scan(text: str) -> dict:
    """テキスト中の煽り文句・誇張表現パターンをスキャンする。

    Args:
        text: 判定対象の投稿本文。

    Returns:
        hit_count: マッチしたパターン数。
        matched_phrases: マッチした実際の文字列のリスト。
    """
    matched: list[str] = []
    for pattern in _COMPILED:
        m = pattern.search(text)
        if m:
            matched.append(m.group(0))
    return {"hit_count": len(matched), "matched_phrases": matched}
