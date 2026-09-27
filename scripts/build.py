#!/usr/bin/env python3
"""Render every license variant from base.md + variants.toml.

Usage:  python build.py [--template base.md] [--config variants.toml] [--out dist]
Needs Python 3.11+ (tomllib). No other dependencies.
"""
import argparse
import itertools
import re
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
    pattern = re.compile(r"[ \t]*" + re.escape(token) + r"[ \t]*\n?")
    return pattern.sub(lambda _: block + "\n" if block else "", text, count=1)


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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="draft/base.md")
    ap.add_argument("--config", default="draft/variants.toml")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()

    template = Path(args.template).read_text(encoding="utf-8")
    cfg = tomllib.loads(Path(args.config).read_text(encoding="utf-8"))
    meta, features = cfg["meta"], cfg.get("features", {})

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # every on/off combination; default state first
    names = list(features)
    for combo in itertools.product([False, True], repeat=len(names)):
        disabled = {n for n, flip in zip(names, combo)
                    if flip == features[n].get("default", True)}
        short, text = render(template, meta, features, disabled)
        path = out_dir / f"{short}-{meta['version']}.md"
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()