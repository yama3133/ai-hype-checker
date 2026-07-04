# AI驚き屋発見器 ブログ記事

日英2言語 × DEV.to / AWS Builder Center の計4本構成。

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

## 投稿前のTODO

- [ ] `screenshot-score-05.png`（スコア5点・堅実の例）と `screenshot-score-72.png`（スコア72点・驚き屋の例）を実際のXの投稿から取得し、マスキングした上で `assets/` に配置する
- [ ] DEV.toのfront matterで `published: false` → 投稿確定後 `true` に変更
- [ ] DEV.to投稿時は本文中の `./assets/...` パスを、エディタの画像アップロード機能でアップロードした後の実URLに置き換える(DEV.toはMarkdown内の相対パス画像を直接扱えないため)
- [ ] Builder Center側はカバー画像・タグをUI側で別途設定する
- [ ] `tags` はDEV.toの規約(最大4個、英数字)を確認して調整(現状: ai, bedrock, agentcore, vercel)
