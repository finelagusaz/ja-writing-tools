# ja-writing-tools

## スキル評価（skill-creator）

- サブエージェントには `plugins/<skill>/skills/<skill>/SKILL.md` を Read させる。Skill ツールで呼べるインストール版（`anthropic-skills:proofread-ja` 等）は古い版のことがある
- モデル比較は Agent の `model` 指定で行い、各実行に自分のモデルID を `outputs/model.txt` へ書かせて、実際に動いたモデルを確かめる
- 評価用ワークスペースはリポジトリの外（scratchpad）に置く。`.gitignore` は `*-workspace/` を除外していない
- 明らかな誤りだけの題ではモデルの差が出ない。直してはいけない箇所（罠）と、文脈依存の同音異義語（「人事移動」「責任を追求」）を入れる
- `aggregate_benchmark` は構成ディレクトリ名の辞書順で先頭2つだけを比べ、Delta は「先頭 − 2番目」。基準にしたい側が先頭に来る名前（`a_haiku` / `b_sonnet`）を付ける
