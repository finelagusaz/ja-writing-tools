# ja-writing-tools

日本語ライティング支援のための Claude Code プラグイン。
校正・推敲など、日本語特有の課題に対応するスキルを提供します。

## 収録スキル

| スキル           | 説明                       |
|------------------|----------------------------|
| `proofread-ja`   | 日本語テキストの校正       |
| `refine-ja`      | 日本語文章の推敲・リライト |

### proofread-ja（日本語校正）

インストール後、Claude Code 上で以下のように話しかけるだけで自動的に起動します。

- 「校正して」
- 「誤字脱字チェック」
- 「表記揺れ確認」
- 「軽くチェック」
- 「しっかり校正」

校正対象のテキストは、直接貼り付け・ファイルパス指定・エディタでの選択のいずれでも渡せます。

#### チェック内容

- **誤字脱字** — 同音異義語、タイプミス、変換ミス
- **表記揺れ** — 漢字/ひらがな、カタカナ長音、全角/半角の統一
- **文法** — ら抜き言葉、さ入れ言葉、重複表現
- **文体** — 敬体/常体の混在、人称の統一

対応文書タイプ: 小説・創作文 / 技術文書 / ブログ記事 / ビジネス文書

### refine-ja（文章推敲・リライト）

「推敲して」「リライトして」と話しかけると、文章のブラッシュアップを支援します。

- **モード**: 小説、ブログ、技術文書、ビジネス、標準
- **機能**: 表現の強化、リズムの調整、言い換え提案、構成案など

使用例:

- 「この文章をブログ風に明るくして」
- 「技術文書として、もっとあいまいな表現をなくして」
- 「小説の推敲をして。情景描写を増やしたい」

## インストール

Claude Code で以下を順番に実行してください。

### 1. マーケットプレイスに追加

```sh
/plugin marketplace add finelagusaz/ja-writing-tools
```

### 2. 追加されたことを確認（任意）

```sh
/plugin marketplace list
```

表示された一覧から、インストールしたいプラグイン名を選んでください。

- `ja-writing-tools-proofread-ja`（`proofread-ja` スキル）
- `ja-writing-tools-refine-ja`（`refine-ja` スキル）

### 3. 選んだプラグインをインストール

```sh
/plugin install <plugin-name>
```

例:

```sh
/plugin install ja-writing-tools-proofread-ja
```

### 4. インストールされたことを確認（任意）

```sh
/plugin list
```

## ライセンス

MIT

## 開発メモ（複数プラグイン運用）

新しいプラグインを公開する場合は、`plugins/<skill>/` 配下に `.claude-plugin/plugin.json` と `skills/<skill>/` を作成し、`.claude-plugin/marketplace.json` の `plugins` 配列にエントリを追加します。
ユーザーは `/plugin marketplace list` で一覧を見て、`/plugin install <plugin-name>` で任意のプラグインを選択してインストールできます。
