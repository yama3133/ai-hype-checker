---
title: "X(旧Twitter)の「AI驚き屋」をAIエージェントで見抜く「AI驚き屋発見器」を作った"
published: false
description: "Strands Agentの2つのツールでX投稿の誇張度を0〜100点でスコア化し、Bedrock AgentCore RuntimeとVercelで動かした話。"
tags: ai, bedrock, agentcore, vercel
cover_image: ./assets/thumbnail-ja.jpg
canonical_url: https://github.com/yama3133/ai-hype-checker
---

> **TL;DR**
> X（旧Twitter）の投稿を貼り付けると、「AI驚き屋」度を0〜100点でスコア化してくれる小さなStrands Agentを作った。**Bedrock AgentCore Runtime**上で動き、**Vercel上のNext.js**から呼び出す。スコアが70を超えると画面全体が赤くなる。
>
> - 本番: https://ai-hype-checker.vercel.app
> - リポジトリ: https://github.com/yama3133/ai-hype-checker

![AI驚き屋発見器サムネイル](./assets/thumbnail-ja.jpg)

## 「AI驚き屋」という現象

X のAI界隈にしばらくいると、この手の投稿を必ず見かける。「これは人類の未来が変わる」「エンジニアはもうオワコン」「なぜ誰も騒いでいないのか信じられない」——具体性はゼロなのに煽り度だけは最大値、という投稿群。この現象は「AI驚き屋」という名前がすでについているくらい、はっきりした型がある。理由付きで「これは中身があるのか、それとも煽りだけなのか」を教えてくれる、正直な小さいツールが欲しかった。

AIを使ってAI驚き屋を見抜く、というのは若干ブーメラン気味な構成だが、そこは割り切った。

## できること

投稿本文を貼り付けて判定ボタンを押すと、以下が返ってくる。

- **0〜100点の驚き屋度スコア**
- **verdict**：堅実 / やや誇張 / 驚き屋
- 判定に至った**理由**の箇条書き
- 判定の根拠になった**具体的なフレーズ**（投稿本文からそのまま引用）

X APIとの連携、スクレイピング、タイムライン監視は一切やっていない。投稿本文は自分でコピーして貼り付ける方式にした。これは意図的なスコープカットで、X APIの検索・タイムライン取得は月額$200前後からと、個人開発の一機能として組み込むには重すぎると判断したため。

## 実際の投稿2件で試した結果

同じツールで、実在するX投稿2件を判定した結果を載せる（実際の投稿から取得したスクリーンショットのため、投稿者のアカウント名・アイコンはマスキング済み）。

![スコア5点の例(堅実)](./assets/screenshot-score-05.png)

*具体的なベンチマーク名・モデル名・出典リンクが含まれている投稿。スコア5点、verdict「堅実」。*

![スコア72点の例(驚き屋)](./assets/screenshot-score-72.png)

*決まり文句の煽り表現だけで構成され、検証可能な要素が一切ない投稿。スコア72点、verdict「驚き屋」——実際に画面も赤くなった。*

## 構成図

![構成図](./assets/diagram-ja.png)

- **フロントエンド**: Next.js 16 on Vercel。1ページ、テキストエリア1つ、ボタン1つ
- **エージェント実行環境**: Bedrock **AgentCore Runtime**（ARM64コンテナ、CodeBuildでクラウドビルド、ローカルDocker不要）
- **エージェントフレームワーク**: **Strands Agents**。2つの`@tool`関数 + モデル自身の判断
- **モデル**: Amazon Bedrock経由のClaude Sonnet 4.6
- **認証**: Vercelからは、このRuntime ARNのみに`bedrock-agentcore:InvokeAgentRuntime`を限定したIAMユーザーのアクセスキーで呼び出している（理由は後述）

## エージェントの中身

面白いのはLLM呼び出しそのものより、判断の前段でグラウンディングする2つの小さなツールの方だ。

```python
@tool
def scan_hype_phrases(text: str) -> dict:
    """投稿本文から煽り文句・誇張表現のパターンをスキャンする。"""
    return hype_scan.scan(text)  # 「人類の未来が変わる」「知らないと損」等の
                                   # 正規表現マッチ

@tool
def check_evidence_density(text: str) -> dict:
    """URL・数値・モデル名・ベンチマーク言及の有無をチェックする。"""
    return evidence_check.check(text)  # has_url / has_numbers /
                                         # has_model_name / has_benchmark_reference
```

エージェントはこの2ツールを呼んだ上で、自身のテキスト理解と統合して1つのJSON判定を返す。想定より重要だった点が1つある。`verdict`フィールドは**翻訳しない固定の英語コード**（`hype` / `exaggerated` / `grounded`）にし、`reasons`（理由）配列だけをUIの表示言語に合わせて生成させている。UI側は色分けのキーとして安定した値が必要な一方、読む人間は自分の言語で理由を読みたい——この2つの要求を1つのLLM生成文字列に混ぜ込むと、いずれ破綻すると判断したためだ。

## 日英切り替えと「画面が赤くなる」演出

UIは日本語・英語に対応している（`localStorage` + `navigator.language`による自動判定、過去のプロジェクトと同じパターン）。選択中の言語は投稿本文と一緒にエージェントへ送られるので、UIの表示文言だけでなく判定理由も選んだ言語で返ってくる。

ちょっとした演出として、スコアが70を超えると画面全体の背景が赤くなる。見出しや説明文の文字色は白系に切り替え、判定結果カードは白のままにして、読みやすさは確保している。「スコアが出る」のと「スコアを体感する」のは別物だと思う。

## 今回スコープ外にしたこと

- X API連携（自動収集・タイムライン監視）
- アカウント単位の過去投稿との整合性チェック
- 判定結果のシェア画像自動生成

Strands Agent 1つ、ツール2つ、ページ1枚という、正真正銘の小さいプロジェクトだが、**AgentCore Runtime + Strands Agents + Vercel**という組み合わせを、どのピースも無理なく素直に組める例にはなったと思う。

- 本番: https://ai-hype-checker.vercel.app
- リポジトリ: https://github.com/yama3133/ai-hype-checker
