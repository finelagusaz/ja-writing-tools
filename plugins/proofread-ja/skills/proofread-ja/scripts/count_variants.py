#!/usr/bin/env python3
"""表記揺れの出現数と行番号を機械的に数える。

数えるのは文字列として一意に決まるものだけ。どちらに統一するか、
用法による使い分けかどうかの判断は、このスクリプトの外で行う。

使い方:
    python3 count_variants.py 原稿.md
    python3 count_variants.py 原稿.txt --count こと 事 --count 行う 行なう
    cat 原稿.txt | python3 count_variants.py -
    python3 count_variants.py 原稿.md --json

行番号は空行を含めて 1 から数える。Markdown（.md / .markdown、または
--markdown 指定）では、fenced code block・インラインコード・インデント
コードブロックを数える対象から外す。
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

KATAKANA_RUN = re.compile(r"[ァ-ヴヽヾ][ァ-ヴヽヾー]*")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
INDENTED = re.compile(r"^(?: {4,}|\t)")
JA = r"[ぁ-んァ-ヴー一-龥々]"

# (ラベル, {表記名: 正規表現}) — 文字種だけで決まる揺れ
CHAR_CLASSES = [
    ("数字の全角/半角", {"半角": r"[0-9]+", "全角": r"[０-９]+"}),
    ("英字の全角/半角", {"半角": r"[A-Za-z]+", "全角": r"[Ａ-Ｚａ-ｚ]+"}),
    ("波ダッシュ/全角チルダ", {"〜 (U+301C)": "〜", "～ (U+FF5E)": "～"}),
    ("句読点の系統", {"、。": r"[、。]", "，．": r"[，．]"}),
    ("丸括弧の全角/半角", {"全角（）": r"[（）]", "半角()": r"[()]"}),
    ("感嘆符・疑問符の全角/半角", {"全角！？": r"[！？]", "半角!?": rf"(?<={JA})[!?]"}),
    (
        "日本語と英数字の間のスペース",
        {
            "スペースあり": rf"(?:{JA} [A-Za-z0-9]|[A-Za-z0-9] {JA})",
            "スペースなし": rf"(?:{JA}[A-Za-z0-9]|[A-Za-z0-9]{JA})",
        },
    ),
]


def mask_code(lines, markdown):
    """コード領域を同じ長さの空白に置き換える（行番号と桁位置を保つ）。"""
    if not markdown:
        return list(lines)
    out, in_fence, prev_blank, prev_indented_code = [], False, True, False
    for line in lines:
        blank = line.strip() == ""
        # インデントコードは、空行の直後か、直前のインデントコードに続く行だけ
        indented_code = bool(INDENTED.match(line)) and not blank and (prev_blank or prev_indented_code)
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(" " * len(line))
        elif in_fence or indented_code:
            out.append(" " * len(line))
        else:
            out.append(INLINE_CODE.sub(lambda m: " " * len(m.group()), line))
        prev_indented_code = indented_code and not in_fence
        prev_blank = blank
    return out


def occurrences(lines, pattern):
    """(件数, 出現行のリスト) を返す。"""
    rx = re.compile(pattern)
    count, where = 0, []
    for no, line in enumerate(lines, 1):
        n = len(rx.findall(line))
        if n:
            count += n
            where.append(no)
    return count, where


def long_vowel_variants(lines):
    """語末の長音符の有無だけが違うカタカナ語の組を探す（例: ユーザー / ユーザ）。

    カタカナの連続を一語として数えるので、「ユーザ」が「ユーザー」の中で
    二重に数えられることはない。複合語（ユーザーインターフェース）の内部は
    対象外。
    """
    counts, where = defaultdict(int), defaultdict(list)
    for no, line in enumerate(lines, 1):
        for word in KATAKANA_RUN.findall(line):
            counts[word] += 1
            if not where[word] or where[word][-1] != no:
                where[word].append(no)
    groups = []
    for word in sorted(counts):
        if not word.endswith("ー") and len(word) >= 2 and word + "ー" in counts:
            groups.append(
                {
                    "label": f"長音符の有無: {word}ー / {word}",
                    "variants": [
                        {"form": word + "ー", "count": counts[word + "ー"], "lines": where[word + "ー"]},
                        {"form": word, "count": counts[word], "lines": where[word]},
                    ],
                }
            )
    return groups


def char_class_variants(lines):
    groups = []
    for label, forms in CHAR_CLASSES:
        variants = []
        for form, pattern in forms.items():
            count, where = occurrences(lines, pattern)
            variants.append({"form": form, "count": count, "lines": where})
        if sum(1 for v in variants if v["count"]) >= 2:
            groups.append({"label": label, "variants": variants})
    return groups


def requested_counts(lines, groups_of_terms):
    """--count で指定された語を数える。長い語から先に照合するので、
    「ユーザ」は「ユーザー」の一部としては数えない。"""
    groups = []
    for terms in groups_of_terms:
        ordered = sorted(set(terms), key=len, reverse=True)
        rx = re.compile("|".join(re.escape(t) for t in ordered))
        counts = {t: 0 for t in terms}
        where = {t: [] for t in terms}
        for no, line in enumerate(lines, 1):
            for m in rx.finditer(line):
                t = m.group()
                counts[t] += 1
                if not where[t] or where[t][-1] != no:
                    where[t].append(no)
        groups.append(
            {
                "label": "指定語: " + " / ".join(terms),
                "variants": [{"form": t, "count": counts[t], "lines": where[t]} for t in terms],
            }
        )
    return groups


def fmt_lines(nums, limit=12):
    shown = ", ".join(f"L{n}" for n in nums[:limit])
    return shown + (f" ほか{len(nums) - limit}行" if len(nums) > limit else "")


def main():
    ap = argparse.ArgumentParser(description="表記揺れの出現数と行番号を数える")
    ap.add_argument("path", help="原稿ファイル。標準入力から読むときは -")
    ap.add_argument("--count", nargs="+", action="append", default=[], metavar="語",
                    help="出現数を比べたい語の組（繰り返し指定可）")
    ap.add_argument("--markdown", action="store_true", help="拡張子に関わらずコード領域を除外する")
    ap.add_argument("--json", action="store_true", help="JSON で出力する")
    args = ap.parse_args()

    if args.path == "-":
        text, markdown = sys.stdin.read(), args.markdown
    else:
        p = Path(args.path)
        text = p.read_text(encoding="utf-8")
        markdown = args.markdown or p.suffix.lower() in (".md", ".markdown")
    lines = mask_code(text.splitlines(), markdown)

    groups = requested_counts(lines, args.count) + long_vowel_variants(lines) + char_class_variants(lines)
    result = {"lines": len(lines), "code_excluded": markdown, "groups": groups}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"全{len(lines)}行" + ("（コード領域は除外）" if markdown else ""))
    if not groups:
        print("機械的に数えられる表記の混在は見つかりませんでした。")
    for g in groups:
        print(f"\n■ {g['label']}")
        for v in g["variants"]:
            print(f"  {v['form']}: {v['count']}箇所" + (f"（{fmt_lines(v['lines'])}）" if v["lines"] else ""))


if __name__ == "__main__":
    main()
