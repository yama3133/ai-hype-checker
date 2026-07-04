"""AI驚き屋チェッカー Strands Agent 本体。

X(旧Twitter)のAI関連投稿を分析し、誇張・扇動的な「AI驚き屋」表現かどうかを判定する。

CLIで単発実行:
  $ python agent.py run "<投稿本文>"

AgentCore Runtime用:
  $ python agent.py serve
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from strands import Agent
from strands.tools import tool

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

load_dotenv(HERE / ".env")

from tools import evidence_check, hype_scan  # noqa: E402

LOG = logging.getLogger("ai-hype-checker")
logging.basicConfig(level=logging.INFO, format="[%(name)s] %(message)s")

_REASONS_LANGUAGE_INSTRUCTION = {
    "ja": "reasonsフィールドの各要素は日本語で書くこと。",
    "en": "Write each element of the reasons field in English.",
}


def build_system_prompt(lang: str) -> str:
    reasons_lang = _REASONS_LANGUAGE_INSTRUCTION.get(lang, _REASONS_LANGUAGE_INSTRUCTION["ja"])
    return f"""\
あなたはX(旧Twitter)上のAI関連投稿を分析する専門家です。
投稿が「AI驚き屋」（技術的根拠が薄いまま誇張・扇動的な表現でAIの進歩を煽る投稿）に
該当するかどうかを判定してください。

判定手順:
1. scan_hype_phrases ツールで煽り文句・決め台詞の有無を確認する
2. check_evidence_density ツールで具体的な数値・モデル名・引用元など技術的根拠の密度を確認する
3. 上記2つの結果と投稿本文全体の文脈を踏まえて、以下のJSON形式のみで最終判定を返す
   （前後に説明文やコードブロック記法を付けないこと）:

{{"score": <0-100の整数、高いほど驚き屋度が高い>,
 "verdict": "<hype | exaggerated | grounded のいずれか一つ、翻訳せずこの英語コードのまま>",
 "reasons": ["<判定理由を3つ程度>"],
 "flagged_phrases": ["<該当した煽り文句があれば投稿本文からそのまま引用して列挙、なければ空配列>"]}}

判定の目安:
- 煽り文句が多く根拠密度が低い → score高め・verdict="hype"
- 煽り文句はあるが具体的な数値やベンチマーク言及も伴う → score中程度・verdict="exaggerated"
- 煽り文句がほぼなく根拠が具体的 → score低め・verdict="grounded"

{reasons_lang}
flagged_phrasesは投稿本文の原文から引用すること（翻訳しない）。
verdictフィールドは必ず hype / exaggerated / grounded のいずれかの英語コードで返し、翻訳しないこと。
"""


@tool
def scan_hype_phrases(text: str) -> dict:
    """投稿本文から煽り文句・誇張表現のパターンをスキャンする。

    Args:
        text: 判定対象の投稿本文。

    Returns:
        hit_count と matched_phrases を含む辞書。
    """
    return hype_scan.scan(text)


@tool
def check_evidence_density(text: str) -> dict:
    """投稿本文の技術的根拠の密度（数値・モデル名・引用元の有無）をチェックする。

    Args:
        text: 判定対象の投稿本文。

    Returns:
        has_url / has_numbers / has_model_name / has_benchmark_reference / evidence_score を含む辞書。
    """
    return evidence_check.check(text)


def build_agent(lang: str = "ja") -> Agent:
    from strands.models import BedrockModel

    region = os.environ.get("AWS_REGION", "us-east-1")
    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-6",
        region_name=region,
    )
    return Agent(
        model=model,
        system_prompt=build_system_prompt(lang),
        tools=[scan_hype_phrases, check_evidence_density],
    )


def _extract_json(raw: str) -> dict:
    """Agentの応答からJSON部分を取り出す（コードブロック等が混じっても対応）。"""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"JSON not found in response: {raw!r}")
    return json.loads(text[start : end + 1])


_PARSE_FAILURE_MESSAGE = {
    "ja": "応答の解析に失敗しました: {raw}",
    "en": "Failed to parse the model response: {raw}",
}


def judge(text: str, lang: str = "ja") -> dict:
    if lang not in _REASONS_LANGUAGE_INSTRUCTION:
        lang = "ja"
    agent = build_agent(lang)
    result = agent(f"以下の投稿を判定してください:\n\n{text}")
    raw = str(result)
    try:
        return _extract_json(raw)
    except (ValueError, json.JSONDecodeError) as e:
        LOG.warning("JSON解析失敗: %s / raw=%s", e, raw)
        message = _PARSE_FAILURE_MESSAGE[lang].format(raw=raw[:200])
        return {
            "score": None,
            "verdict": "failed",
            "reasons": [message],
            "flagged_phrases": [],
        }


# ----------------------------------------------------------------------
# AgentCore Runtime entrypoint
# ----------------------------------------------------------------------
# AgentCore Runtime にデプロイされた場合は HTTP リクエストで invoke される。
# payload には {"text": "..."} という JSON が来る想定。
try:
    from bedrock_agentcore.runtime import BedrockAgentCoreApp

    app = BedrockAgentCoreApp()

    @app.entrypoint
    def invoke(payload: dict) -> dict:
        text = (payload or {}).get("text", "")
        lang = (payload or {}).get("lang", "ja")
        if not text:
            return {"error": "missing 'text' in payload"}
        return judge(text, lang)
except Exception:
    # ローカル CLI 実行時は runtime SDK が無くてもOK
    app = None


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def cli() -> None:
    args = sys.argv[1:]
    lang = "ja"
    if "--lang" in args:
        i = args.index("--lang")
        lang = args[i + 1] if i + 1 < len(args) else "ja"
        del args[i : i + 2]

    if args and args[0] == "run":
        text = " ".join(args[1:]) if len(args) > 1 else ""
        if not text:
            print('usage: python agent.py run "<投稿本文>" [--lang ja|en]')
            sys.exit(1)
        result = judge(text, lang)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print("ai-hype-checker: 対話モード。Ctrl-Dで終了。")
    try:
        while True:
            try:
                user_input = input("\n投稿本文> ").strip()
            except EOFError:
                print()
                return
            if not user_input:
                continue
            print(json.dumps(judge(user_input, lang), indent=2, ensure_ascii=False))
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    # AgentCore Runtime 用に `python agent.py serve` で HTTP サーバ起動
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        if app is None:
            print("BedrockAgentCoreApp が import 出来ない。bedrock-agentcore パッケージを確認")
            sys.exit(1)
        app.run()
    else:
        cli()
