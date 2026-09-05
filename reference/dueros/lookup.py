#!/usr/bin/env python3
"""Token-efficient lookup into the DuerOS protocol docs.

Never read a whole 100-200KB file: this finds the relevant section and prints
only the slice you need.

Examples:
    python3 reference/dueros/lookup.py SetTemperature
    python3 reference/dueros/lookup.py SetTemperature -s control-message.md:1606
    python3 reference/dueros/lookup.py 空调 --grep      # search full text, not just headings
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOC_DIR = Path(__file__).resolve().parent / "dbp-smart-home-protocol"
INDEX = DOC_DIR / "sections.tsv"
CONTRACT_DIR = Path(__file__).resolve().parent / "contracts"


def load_index() -> list[tuple[str, int, int, str]]:
    rows = []
    for raw in INDEX.read_text(encoding="utf-8").splitlines()[1:]:
        f, l, v, h = raw.split("\t", 3)
        rows.append((f, int(l), int(v), h))
    return rows


def section_span(lines: list[str], start: int, level: int) -> tuple[int, int]:
    """(end_exclusive) of the section starting at line ``start`` (1-based)."""
    for i in range(start, len(lines)):  # i is 0-based index of line start.. (start is 1-based)
        m = None
        for j, ln in enumerate(lines, start=1):
            if j <= start:
                continue
            stripped = ln.lstrip()
            if stripped.startswith("#"):
                # count heading level
                lv = len(stripped) - len(stripped.lstrip("#"))
                if lv <= level:
                    return j
    return len(lines) + 1


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", help="keyword to find (case-insensitive)")
    ap.add_argument("-s", "--select", help="exact slice source, e.g. control-message.md:1606 (bypasses search)")
    ap.add_argument("--grep", action="store_true", help="also search section body text (slower, more hits)")
    ap.add_argument("--max-lines", type=int, default=200, help="cap lines printed per section (default 200)")
    args = ap.parse_args()

    q = args.query.lower()

    def print_contract_mode() -> bool:
        """Two-tier mode (C): prefer the tiny contracts when a message matches."""
        if args.select or args.grep:
            return False
        hits: list[tuple[Path, int, str]] = []
        if CONTRACT_DIR.is_dir():
            for path in sorted(CONTRACT_DIR.glob("*.md")):
                if path.name == "00-index.md":
                    continue
                for n, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                    m = __import__("re").match(r"^### (.+)$", ln)
                    if m and q in m.group(1).lower():
                        hits.append((path, n, m.group(1)))
        if not hits:
            return False
        by_file: dict[str, tuple[int, str]] = {}
        for path, n, title in hits:
            by_file.setdefault(path.name, (n, title))
        print("== 契约速查（完整字段说明/示例 JSON 见行内 [原文]）==")
        shown = 0
        for fname in sorted(by_file):
            n, title = by_file[fname]
            path = CONTRACT_DIR / fname
            lines = path.read_text(encoding="utf-8").splitlines()
            end_exclusive = len(lines) + 1
            for j, ln in enumerate(lines, start=1):
                if j > n and re.match(r"^#{1,3} ", ln):
                    end_exclusive = j
                    break
            print(f"--- {fname} : {title}  (sed -n '{n},{end_exclusive-1}p' contracts/{fname})")
            for ln in lines[n - 1 : end_exclusive - 1]:
                print(ln)
            print()
            shown += 1
            if shown >= 3:
                print("(更多命中省略；可对单文件用 -s 或直接查原文)")
                break
        return True

    if print_contract_mode():
        return

    if args.select:
        fname, _, lstr = args.select.rpartition(":")
        rows = [(fname, int(lstr), 0, "")]
    else:
        idx = load_index()
        hits = [r for r in idx if q in r[3].lower()]
        if args.grep:
            for path in sorted(DOC_DIR.glob("*.md")):
                if path.name in ("00-index.md", "sections.tsv"):
                    continue
                for n, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                    if q in ln.lower():
                        hits.append((path.name, n, 0, ln.strip()[:90]))
        if not hits:
            print(f"no heading match for {args.query!r}; try --grep or -s", file=sys.stderr)
            sys.exit(1)
        # keep the shallowest (most relevant) per file for the match list
        by_file: dict[str, tuple[int, int, str]] = {}  # level, line, heading
        for f, l, v, h in hits:
            cur = by_file.get(f)
            if cur is None or (v, l) < (cur[0], cur[1]):
                by_file[f] = (v, l, h)
        print("== matches (file:line  level  heading) ==")
        for f in sorted(by_file):
            v, l, h = by_file[f]
            print(f"  {f}:{l}  L{v}  {h}")
        rows = hits

    # print selected slices
    printed = 0
    for fname, start, level, heading in rows:
        path = DOC_DIR / fname
        if not path.exists():
            print(f"missing {path}", file=sys.stderr)
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if args.select:
            # find section end by scanning upward for the nearest heading <= level
            lv = None
            s = start
            for j in range(start - 1, 0, -1):
                stripped = lines[j - 1].lstrip()
                if stripped.startswith("#"):
                    lv = len(stripped) - len(stripped.lstrip("#"))
                    s = j
                    break
            end = section_span(lines, s, lv if lv else 1)
        else:
            end = section_span(lines, start, level if level else 1)
        if printed:
            print()
        print(f"## {fname}:{start}-{end-1}  (sed -n '{start},{end-1}p' {path.name})")
        body = lines[start - 1 : min(end - 1, start - 1 + args.max_lines)]
        for n, ln in enumerate(body, start=start):
            print(f"{n:>5} {ln}")
        if end - start > args.max_lines:
            print(f"... ({end - start - args.max_lines} more lines; rerun with sed or -s + --max-lines)")
        printed += 1
        if printed >= 5:
            print("\n(more matches omitted; use -s <file:line> to print one)")
            break


if __name__ == "__main__":
    main()
