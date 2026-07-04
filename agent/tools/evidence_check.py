"""技術的根拠密度の検出ツール。"""
from __future__ import annotations

import re

_URL_RE = re.compile(r"https?://\S+")
_NUMBER_RE = re.compile(r"\d+(\.\d+)?\s*(%|パーセント|倍|億|万|B|M|tokens?|トークン)")
_MODEL_NAME_RE = re.compile(
    r"(GPT-?\d|Claude(-?\d)?|Gemini(\s?\d)?|Llama(\s?\d)?|Sonnet|Opus|Haiku|"
    r"o\d(-mini)?|DeepSeek|Mistral|Qwen)",
    re.IGNORECASE,
)
_BENCHMARK_RE = re.compile(
    r"(ベンチマーク|benchmark|MMLU|HumanEval|SWE-bench|GPQA|Arena|論文|arXiv|公式ブログ|リリースノート)",
    re.IGNORECASE,
)


def check(text: str) -> dict:
    """具体的な数値・モデル名・引用元の有無から根拠情報密度をチェックする。

    Args:
        text: 判定対象の投稿本文。

    Returns:
        has_url: 引用URLの有無。
        has_numbers: 具体的な数値表現の有無。
        has_model_name: 固有のモデル名の有無。
        has_benchmark_reference: ベンチマーク/論文等への言及の有無。
        evidence_score: 0-4の根拠情報密度スコア（高いほど具体的）。
    """
    has_url = bool(_URL_RE.search(text))
    has_numbers = bool(_NUMBER_RE.search(text))
    has_model_name = bool(_MODEL_NAME_RE.search(text))
    has_benchmark_reference = bool(_BENCHMARK_RE.search(text))
    evidence_score = sum([has_url, has_numbers, has_model_name, has_benchmark_reference])
    return {
        "has_url": has_url,
        "has_numbers": has_numbers,
        "has_model_name": has_model_name,
        "has_benchmark_reference": has_benchmark_reference,
        "evidence_score": evidence_score,
    }
