#!/usr/bin/env python3
"""Build a heading -> (file, line) index over the converted DuerOS protocol docs.

Output: dbp-smart-home-protocol/sections.tsv  (tab-separated: file<TAB>line<TAB>level<TAB>heading)
"""
from __future__ import annotations
import re
from pathlib import Path

DOC_DIR = Path(__file__).resolve().parent / "dbp-smart-home-protocol"
OUT = DOC_DIR / "sections.tsv"

def main() -> None:
    rows = []
    for path in sorted(DOC_DIR.glob("*.md")):
        if path.name in ("sections.tsv", "00-index.md"):
            continue
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            m = re.match(r"^(#{1,6})\s+(.*)$", raw)
            if m:
                rows.append((path.name, lineno, len(m.group(1)), m.group(2).strip()))
    OUT.write_text("file\tline\tlevel\theading\n", encoding="utf-8")
    OUT.write_text("".join(f"{f}\t{l}\t{v}\t{h}\n" for f, l, v, h in rows), encoding="utf-8")
    print(f"indexed {len(rows)} headings -> {OUT} ({OUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
