#!/usr/bin/env python3
"""Render every license variant from base.md + variants.toml.

Usage:  python build.py [--template base.md] [--config variants.toml] [--out dist]
Needs Python 3.11+ (tomllib). No other dependencies.
"""
import argparse
import itertools
import re
import textwrap
import tomllib
from pathlib import Path

LIST_KEYS = ("permissions", "conditions", "prohibitions")
NUMBERED = re.compile(r"^\s*(\d+)\.\s", re.M)


def continue_list(text: str, key: str, items: list[str]) -> str:
    """Replace {{key}} with items, numbered after the last item in its section."""
    token = "{{" + key + "}}"
    pos = text.find(token)
    if pos == -1:
        return text
    section = text[text.rfind("\n## ", 0, pos) + 1 : pos]
    nums = [int(n) for n in NUMBERED.findall(section)]
    start = (max(nums) if nums else 0) + 1
    block = "\n\n".join(f"{i}. {item}" for i, item in enumerate(items, start))
    # swallow the placeholder's own line (incl. trailing spaces) when empty
    # an empty list also swallows one following blank line, so no double gap is left behind
    pattern = re.compile(r"[ \t]*" + re.escape(token) + r"[ \t]*\n?([ \t]*\n)?")
    return pattern.sub(
        lambda m: (block + "\n" + ("\n" if m.group(1) else "")) if block else "",
        text, count=1)


def render(template: str, meta: dict, features: dict, disabled: set[str]) -> tuple[str, str]:
    lists = {k: [] for k in LIST_KEYS}
    suffixes, shorts = [], []
    for fname, feat in features.items():
        state = "off" if fname in disabled else "on"
        for k in LIST_KEYS:
            lists[k] += feat.get(state, {}).get(k, [])
        if state == "off":
            suffixes.append(feat["suffix"])
            shorts.append(feat["short"])

    name = " ".join([meta["name"], *suffixes])
    short = "-".join([meta["short"], *shorts])

    out = template
    for k in LIST_KEYS:
        out = continue_list(out, k, lists[k])
    for k, v in {"name": name, "short": short, "version": meta["version"]}.items():
        out = out.replace("{{" + k + "}}", v)

    leftover = re.findall(r"\{\{\s*\w+\s*\}\}", out)
    if leftover:
        raise SystemExit(f"Unfilled placeholders in {short}: {leftover}")
    return short, out


def md_to_txt(md: str, width: int = 80) -> str:
    """Strip Markdown down to readable plain text."""
    md = re.sub(r"\[([^\]]+)\]\(\s*\)", r"\1", md)             # [text]() -> text
    md = re.sub(r"\[([^\]]+)\]\(#[^)]*\)", r"\1", md)           # in-page anchors -> text
    md = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", md)     # [text](url) -> text (url)
    md = md.replace("\\[", "[").replace("\\]", "]")               # unescape brackets
    md = re.sub(r"^\*\*(.+?)\*\*[ \t]*\n[ \t]+", "\x00\\1\x00", md, flags=re.M)  # glossary terms
    md = re.sub(r"\*\*(.+?)\*\*", r"\1", md)                      # bold
    def render(block: list[str]) -> str:
        text = re.sub(r" {2,}", " ", " ".join(line.strip() for line in block))
        g = re.match(r"\x00(.+?)\x00(.*)", text)
        if g:
            body = textwrap.fill(g.group(2), width - 4 if width else 10**6,
                                 initial_indent="    ", subsequent_indent="    ",
                                 break_long_words=False, break_on_hyphens=False)
            return g.group(1) + "\n" + body
        m = re.match(r"(#{1,6})\s+(.*)", text)
        if m:
            title = m.group(2).strip()
            return title + "\n" + ("=" if len(m.group(1)) == 1 else "-") * len(title)
        item = re.match(r"(\d+\.|[-*])\s+", text)
        if width:
            text = textwrap.fill(text, width, subsequent_indent=" " * (item.end() if item else 0),
                                 break_long_words=False, break_on_hyphens=False)
        return text

    # split on runs of blank lines, keeping each run so its length carries over to the text
    parts = re.split(r"(\n[ \t]*(?:\n[ \t]*)+)", md.strip())
    out, gap = [], 0
    for i, part in enumerate(parts):
        if i % 2:                                  # a run of blank lines
            gap = part.count("\n")
            continue
        blocks, cur = [], []
        for line in part.splitlines():             # a heading always starts its own block
            if re.match(r"#{1,6}\s", line):
                if cur:
                    blocks.append(cur)
                    cur = []
                blocks.append([line])
            else:
                cur.append(line)
        if cur:
            blocks.append(cur)
        for j, block in enumerate(blocks):
            out.append("\n" * (gap if j == 0 else 2) + render(block))
    return "".join(out) + "\n"


def main_markdown() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="draft/base.md")
    ap.add_argument("--config", default="draft/variants.toml")
    ap.add_argument("--out", default="dist/md")
    ap.add_argument("--txt-out", default="dist/txt")
    ap.add_argument("--formats", nargs="+", choices=["md", "txt"], default=["md", "txt"])
    ap.add_argument("--wrap", type=int, default=80, help="txt line width, 0 = no wrapping")
    args = ap.parse_args()

    template = Path(args.template).read_text(encoding="utf-8")
    cfg = tomllib.loads(Path(args.config).read_text(encoding="utf-8"))
    meta, features = cfg["meta"], cfg.get("features", {})

    dirs = {"md": Path(args.out), "txt": Path(args.txt_out)}
    for fmt in args.formats:
        dirs[fmt].mkdir(parents=True, exist_ok=True)

    # every on/off combination; default state first
    names = list(features)
    for combo in itertools.product([False, True], repeat=len(names)):
        disabled = {n for n, flip in zip(names, combo)
                    if flip == features[n].get("default", True)}
        short, text = render(template, meta, features, disabled)
        for fmt in args.formats:
            path = dirs[fmt] / f"{short}-{meta['version']}.{fmt}"
            path.write_text(text if fmt == "md" else md_to_txt(text, args.wrap), encoding="utf-8")
            print(f"wrote {path}")


if __name__ == "__main__":
    main_markdown()