# AI驚き屋発見器 ブログ記事

## 初回リリース記事(日英2言語 × DEV.to / AWS Builder Center の計4本)

- `ja/dev-to.md` — DEV.to投稿用(front matter付き、日本語)
- `ja/builder-center.md` — Builder Center投稿用(front matterなし、日本語)
- `en/dev-to.md` — DEV.to投稿用(front matter付き、英語)
- `en/builder-center.md` — Builder Center投稿用(front matterなし、英語)
- `make_images.py` — 構成図(PNG)とサムネイル(PNG/JPG)を日英で生成するスクリプト。`uv run --with pillow python3 make_images.py`で再生成可能
- `assets/` — 生成画像・素材一式
  - `diagram-ja.png` / `diagram-en.png` — アーキテクチャ構成図
  - `thumbnail-ja.png` / `thumbnail-ja.jpg` / `thumbnail-en.png` / `thumbnail-en.jpg` — カバー画像(1200x630)
  - `source-photo-surprised-man.png` — サムネイルに使っている驚き顔の素材写真(ユーザー提供、AI生成画像)
  - `screenshot-score-05.png` / `screenshot-score-72.png` — **未配置**。実際のXの投稿を判定した結果のスクリーンショットを、投稿者のアカウント名・アイコンをマスキングしたうえでこのファイル名で配置する

### 初回リリース記事、投稿前のTODO

- [ ] `screenshot-score-05.png`（スコア5点・堅実の例）と `screenshot-score-72.png`（スコア72点・驚き屋の例）を実際のXの投稿から取得し、マスキングした上で `assets/` に配置する
- [ ] DEV.toのfront matterで `published: false` → 投稿確定後 `true` に変更
- [ ] DEV.to投稿時は本文中の `./assets/...` パスを、エディタの画像アップロード機能でアップロードした後の実URLに置き換える(DEV.toはMarkdown内の相対パス画像を直接扱えないため)
- [ ] Builder Center側はカバー画像・タグをUI側で別途設定する
- [ ] `tags` はDEV.toの規約(最大4個、英数字)を確認して調整(現状: ai, bedrock, agentcore, vercel)

## Web検索ファクトチェック機能追加記事(英語のみ × DEV.to / AWS Builder Center の計2本、2026-07-21)

AgentCore Web Searchでのファクトチェック機能追加を扱う記事。テキストは英語版のみ(日本語版は未作成)。

- `en/dev-to-factcheck.md` — DEV.to投稿用(front matter付き)。Title 57字・Description 153字(いずれも規約内)
- `en/builder-center-factcheck.md` — Builder Center投稿用(front matterなし)
  - Title (<=60字): `My AI Hype Detector Now Fact-Checks Claims, Not Just Tone`
  - Description (<=160字): `My AI Hype Detector used to grade tone. Now it uses Bedrock AgentCore's Web Search tool to check if a post's claims are actually true, with real sources.`
- `make_images_factcheck.py` — この記事専用の構成図(JPG)とサムネイル(PNG)を生成するスクリプト。`uv run --with pillow python3 make_images_factcheck.py`で再生成可能
- `assets/diagram-factcheck-en.jpg` — 構成図(既存パイプライン+AgentCore Gateway/Web Searchの追加部分をNEWバッジ付きで図示)
- `assets/thumbnail-factcheck-en.png` — カバー画像(1200x630、claimカードのモックアップ入り)
- `assets/screenshot-factcheck-en.png` — 実際のアプリ(ローカル)をPlaywrightで撮影した本物のスクリーンショット。テスト投稿文はこちらで作成した文章なのでマスキング不要

### この記事、投稿前のTODO

- [ ] DEV.toのfront matterで `published: false` → 投稿確定後 `true` に変更
- [ ] DEV.to投稿時は本文中の `./assets/...` パスを実URLに置き換える
- [ ] Builder Center側はTitle/Description/カバー画像・タグをUI側で設定する(上記の値を使用)

## Web Search Tool 東京リージョン対応・日本語検証記事(Qiita日本語 + DEV.to/Builder Center英語の計3本、2026-08-14)

AgentCore Gateway Web Search Toolの東京リージョン(ap-northeast-1)対応にあわせ、日本語クエリの言語対応とレイテンシを既存us-east-1本番Gatewayと比較検証した速報記事。

- `ja/qiita-tokyo.md` — Qiita投稿用(front matterなし、日本語)。タイトル: `待望の東京リージョン、AgentCore Web Search Toolの日本語対応を検証してみた`
- `en/dev-to-tokyo.md` — DEV.to投稿用(front matter付き、英語)。Title 52字・Description 146字(いずれも規約内)
- `en/builder-center-tokyo.md` — Builder Center投稿用(front matterなし、英語)
  - Title (<=60字): `AgentCore Web Search Reaches Tokyo: Testing Japanese`
  - Description (<=160字): `Bedrock AgentCore's Web Search tool just launched in Tokyo. I spun up a temp Gateway there and compared Japanese search results against us-east-1.`
- `make_images_tokyo.py` — この記事専用の構成図(JPG、日英)とサムネイル(PNG、英語のみ)を生成するスクリプト。`uv run --with pillow python3 make_images_tokyo.py`で再生成可能
- `assets/diagram-tokyo-ja.jpg` / `assets/diagram-tokyo-en.jpg` — 構成図(検証スクリプト→us-east-1/Tokyo両Gateway→Web Searchコネクタ→レイテンシ比較→結論、をフロー図示)
- `assets/thumbnail-tokyo-en.png` — カバー画像(1200x630、英語のみ)

### この記事、投稿前のTODO

- [ ] DEV.toのfront matterで `published: false` → 投稿確定後 `true` に変更
- [ ] DEV.to投稿時は本文中の `./assets/...` パスを実URLに置き換える
- [ ] Builder Center側はTitle/Description/カバー画像・タグをUI側で設定する(上記の値を使用)
- [ ] Qiitaはタグ(AWS, Bedrock, AgentCore, 生成AI等)をUI側で設定する

## アプリ概要+根拠密度チェックの穴とファクトチェック追加の経緯記事(Qiita日本語のみ、2026-08-29投稿完了)

初回リリース記事(アプリの概要・構成・元々の2ツール・日英UI/赤画面演出)と、`check_evidence_density`がURL・モデル名・数値の「有無」しか見ておらず内容の真偽を判定していなかった穴の発見〜Web検索ファクトチェック機能(fact_check、出典の捏造防止、プロンプトインジェクション対策)追加までの経緯を、1本のQiita記事にまとめた。捏造投稿(架空の「Claude Opus 5.2」)で実際に検証しながら説明している。本文中に画像は埋め込んでいない([[feedback-no-thumbnail-embedding]]踏襲、qiita-tokyo.mdと同じ方針)。

- `ja/qiita-factcheck-gap.md` — Qiita投稿用(front matterなし、日本語)。タイトル: `「モデル名とURLさえ書けば堅実判定」だったAI驚き屋発見器に、本物のファクトチェックを足した`
- `make_images_overview.py` — この記事に添える構成図・フロー図(いずれも日本語・JPG)を生成するスクリプト。AWS公式Architecture Icons(実物、docs/blog/assets/icons/に配置)を使用。`uv run --with pillow python3 make_images_overview.py`で再生成可能
- `assets/diagram-overview-ja.jpg` — 構成図。ユーザー/Vercel(AWS Cloud外)→AgentCore Runtime→AgentCore Gateway→外部Web検索、AgentCore Runtime→Bedrock(Claude Sonnet 4.6)の全体像
- `assets/flow-overview-ja.jpg` — 判定フロー図。投稿貼り付けから判定、スコア70点超で画面が赤くなる分岐までを図示
- `assets/icons/` — AWS公式Architecture Icons(Amazon Bedrock、Amazon Bedrock AgentCore、AWS IAM等)とResource Icons(Client、Globe、Magnifying-Glass)の実物SVG/PNG。次の構成図作成でも再利用可能

### この記事、投稿状況

Qiita投稿完了(2026-08-29、本人確認)。公開URLは未確認。
