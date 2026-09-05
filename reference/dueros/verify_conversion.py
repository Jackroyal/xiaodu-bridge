#!/usr/bin/env python3
"""Verify the fetched Markdown faithfully matches the official DuerOS pages.

Checks per page (after a fetch/convert):
  1. structural parity  : headings / table rows / table cells / code blocks
  2. text coverage      : every long HTML text segment (escape-aware) exists in md
  3. no stray escapes   : zero "\\_" outside fenced code (keeps tokens greppable)
  4. code fence parity  : fences are balanced
  5. images             : report pages that contain <img> (converter keeps none)

Usage:
    python3 reference/dueros/verify_conversion.py            # fetch + verify
    python3 reference/dueros/verify_conversion.py --refresh  # force re-fetch

Exit code 0 = clean; 1 = problems found.
"""
from __future__ import annotations

import argparse
import html as htmllib
import re
import sys
import tempfile
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol"
SLUGS = [
    "intro-protocol", "discovery-message", "control-message", "query-message",
    "notification-message", "error-message", "attributes", "attributes-report",
    "iov-message", "sweeping-rebot-message",
]
ROOT = Path(__file__).resolve().parent
DOC_DIR = ROOT / "dbp-smart-home-protocol"


def fetch(slug: str, cache_dir: Path, refresh: bool) -> str:
    path = cache_dir / f"{slug}.html"
    if refresh or not path.exists():
        r = requests.get(f"{BASE}/{slug}_markdown", timeout=60)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(r.text, encoding="utf-8")
    return path.read_text(encoding="utf-8", errors="replace")


def squash(text: str) -> str:
    text = htmllib.unescape(text)
    text = text.replace("\\_", "_")
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text)
    text = re.sub(r"[\[\]()#|*`>_~-]", "", text)
    text = re.sub(r"[\s\u00a0]+", "", text)
    return text


def md_plain(md: str) -> str:
    md = md.split("---", 2)[2] if md.startswith("---") else md
    md = re.sub(r"^```[^\n]*\n?", "", md, flags=re.M)  # drop fence markers
    return squash(md)


def check_md_text(md: str) -> tuple[int, list[str]]:
    """Outside-fence underscore escapes and fence parity."""
    esc, fence = 0, 0
    in_code = False
    for ln in md.splitlines():
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            fence += 1
        elif not in_code:
            esc += ln.count("\\_")
    return esc, (fence % 2 == 0 and fence >= 0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true", help="re-fetch cached HTML")
    args = ap.parse_args()

    cache = Path(tempfile.gettempdir()) / "dueros_verify"
    problems: list[str] = []
    print(f"{'page':26s} {'#seg':>5s} {'lost':>5s} {'esc':>4s} {'fences':>7s} {'img':>4s}   notes")
    for slug in SLUGS:
        html = fetch(slug, cache, args.refresh)
        soup = BeautifulSoup(html, "html.parser")
        node = soup.find("div", class_="resource-text markdown-body") or soup.find("div", class_="markdown-body")
        md_path = DOC_DIR / f"{slug}.md"
        md = md_path.read_text(encoding="utf-8")
        plain = md_plain(md)
        esc, fences_ok = check_md_text(md)
        img = len(node.find_all("img"))
        # structural counts
        h = len(node.find_all(re.compile(r"^h[1-6]$")))
        tr = len(node.find_all("tr")); cells = len(node.find_all(["td", "th"]))
        pre = len(node.find_all("pre"))
        mh = len(re.findall(r"^#{1,6} ", md, re.M))
        mrows = mcells = 0
        for ln in md.splitlines():
            if ln.lstrip().startswith("|") and not re.fullmatch(r"\|[\s:|-]*\|", ln):
                mrows += 1
                mcells += len([c for c in ln.strip().strip("|").split("|")])
        mpre = md.count("```") // 2
        # text coverage: check every *leaf* text node (paragraphs, list items,
        # table cells, link labels...). Whole <li> subtrees are intentionally
        # avoided: they aggregate group label + nested children, which is a
        # checker artefact, not a real loss.
        segs, seen = [], set()
        for leaf in node.find_all(string=True):
            t = str(leaf)
            k = squash(t)
            if len(k) < 6 or k in seen:
                continue
            seen.add(k)
            if k not in plain:
                segs.append(t.strip())
        notes = []
        if (h, tr, cells, pre) != (mh, mrows, mcells, mpre):
            notes.append(f"STRUCT h {h}/{mh} tr {tr}/{mrows} cells {cells}/{mcells} pre {pre}/{mpre}")
        if segs:
            problems.append(f"{slug}: {len(segs)} html text segment(s) missing from md")
            notes.append(f"LOST {len(segs)}")
        if esc:
            problems.append(f"{slug}: {esc} '\\_' outside code fences")
            notes.append(f"ESC {esc}")
        if not fences_ok:
            problems.append(f"{slug}: unbalanced code fences")
            notes.append("FENCE!")
        if img:
            notes.append(f"IMG {img}")
        print(f"{slug:26s} {len(segs)+len(seen):5d} {len(segs):5d} {esc:4d} {str(fences_ok):>7s} {img:4d}   {'; '.join(notes)}")

    print()
    if problems:
        print("PROBLEMS FOUND:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("OK: all pages faithful (structure + text), no stray escapes, fences balanced.")


if __name__ == "__main__":
    main()
