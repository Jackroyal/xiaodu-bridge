#!/usr/bin/env python3
"""Generate compact *payload-contract* files from the DuerOS protocol docs.

Original fetched Markdown under ``dbp-smart-home-protocol/`` is NEVER modified;
this writes derived, token-lean contracts into ``contracts/`` (scheme B/C):

- For every message-style heading (``*Request / *Response / *Confirmation /
  *Error``) it extracts the payload fields (name / required / short description)
  and drops the repeated boilerplate rows (accessToken / appliance) plus the
  bulky example JSON and prose.
- Output rows carry a pointer back to the original section.

Usage:  python3 reference/dueros/make_contracts.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOC_DIR = ROOT / "dbp-smart-home-protocol"
OUT_DIR = ROOT / "contracts"

# Pages that are pure prose / attribute reference (no parseable message set).
NARRATIVE = {
    "intro-protocol": "协议总览（Header/Payload 基本结构、命名空间）。属叙述性，直接查原文。",
    "attributes": "设备属性定义（name/type/scale/legalValue）。含大量示例，按属性名 grep 原文。",
    "sweeping-rebot-message": "扫地机器人：复用通用 发现/控制/查询/属性上报/错误 消息，仅约定设备能力。按主题查原文。",
}

MESSAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*(?:Request|Response|Confirmation|Error)(?:消息)?$")
COMMON_FIELDS = {
    "accessToken", "appliance", "appliance.applianceId",
    "appliance.additionalApplianceDetails",
}
DESC_LIMIT = 70


def parse_table_rows(block: list[str]) -> list[list[str]]:
    rows = []
    for raw in block:
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        # skip separator rows like | --- | --- |
        if all(re.fullmatch(r"[\s:|-]*", c or "") for c in cells):
            continue
        rows.append(cells)
    return rows


def collect_tables(lines: list[str]) -> list[tuple[int, list[list[str]]]]:
    """Return (start_line_index, rows) for each markdown table in lines."""
    tables = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip().startswith("|"):
            block = [lines[i]]
            j = i + 1
            while j < n and lines[j].strip().startswith("|"):
                block.append(lines[j])
                j += 1
            rows = parse_table_rows(block)
            if rows:
                tables.append((i, rows))
            i = j
        else:
            i += 1
    return tables


def message_direction(title: str) -> str:
    if title.endswith("Request"):
        return "DuerOS → 技能（请求）"
    if title.endswith("Confirmation") or title.endswith("Response"):
        return "技能 → DuerOS（响应/确认）"
    if title.endswith("Error"):
        return "技能 → DuerOS（错误）"
    return ""


def fmt_required(v: str) -> str:
    v = (v or "").strip()
    if v in ("是", "必须", "必填"):
        return "必填"
    if v in ("否", "可选", "否，可选"):
        return "可选"
    return v or ""


def shorten(desc: str) -> str:
    desc = re.sub(r"\s+", " ", desc or "").strip()
    return desc if len(desc) <= DESC_LIMIT else desc[: DESC_LIMIT - 1] + "…"


def section_region(lines: list[str], start_idx: int, level: int) -> tuple[int, int]:
    """Body of heading at start_idx: to next heading with level <= level."""
    for j in range(start_idx + 1, len(lines)):
        m = re.match(r"^(#{1,6})\s+", lines[j])
        if m and len(m.group(1)) <= level:
            return start_idx + 1, j
    return start_idx + 1, len(lines)


def heading_at(lines: list[str], idx: int) -> tuple[int, str] | None:
    m = re.match(r"^(#{1,6})\s+(.*)$", lines[idx])
    return (len(m.group(1)), m.group(2).strip()) if m else None


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = [
        "# DuerOS 协议契约索引（省 token 速查）\n",
        "",
        "> 由 `make_contracts.py` 自动生成，原始官方文档在 `../dbp-smart-home-protocol/`（未改动）。",
        "> 每条约含：方向 / 额外 Payload 字段（公共字段见下方约定）/ 原文指针。",
        "> 需要完整描述、示例 JSON、Header 细节时，点“原文”回查。",
        "",
        "## 公共 Payload 字段（所有消息通用）",
        "",
        "- `accessToken`：OAuth access token（必填）",
        "- `appliance`：设备对象，含 `applianceId`（必填）与 `additionalApplianceDetails`（可空）",
        "",
        "| 契约文件 | 覆盖内容 | 原文体积 |",
        "|---|---|---|",
    ]
    pairs = sorted(DOC_DIR.glob("*.md"))
    for path in pairs:
        slug = path.stem
        if slug in ("00-index", "sections"):
            continue
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        if slug in NARRATIVE:
            (OUT_DIR / f"{slug}.md").write_text(
                f"# {slug}（阅读指引）\n\n> 该页为叙述/属性型文档，无统一“消息→Payload”结构，未做契约抽取。\n\n{NARRATIVE[slug]}\n\n原文：`../dbp-smart-home-protocol/{slug}.md`（查找用 `lookup.py` 或 `sections.tsv`）\n",
                encoding="utf-8",
            )
            index.append(f"| `{slug}.md` | {NARRATIVE[slug].split('。')[0]}。 | 见原文 |")
            continue

        # locate message headings and their regions
        heads = []  # (level, title, idx)
        for idx, ln in enumerate(lines):
            h = heading_at(lines, idx)
            if h and MESSAGE_RE.match(h[1]):
                heads.append((h[0], re.sub(r"消息$", "", h[1]), idx))
        # skip parents whose body contains another detected message
        kept = []
        for level, title, idx in heads:
            s, e = section_region(lines, idx, level)
            if any(idx < oi < e for _, _, oi in heads if oi != idx):
                continue
            kept.append((level, title, idx, s, e))
        # open-heading stack for grouping labels
        out = [f"# {slug}（契约速查）\n", "", f"> 由 `make_contracts.py` 生成；原文：`../dbp-smart-home-protocol/{slug}.md`", ""]
        stack: list[tuple[int, str]] = []
        last_group = None
        for level, title, idx, s, e in kept:
            # sync grouping stack
            while stack and stack[-1][0] >= level:
                stack.pop()
            group = " / ".join(t for lv, t in stack)
            if group != last_group:
                out.append(f"## 分组：{group or title}")
                out.append("")
                last_group = group
            # find header(namespace) + payload tables in region
            body = lines[s:e]
            header_rows, payload_rows = [], []
            for _, rows in collect_tables(body):
                first = rows[0] if rows else []
                if len(first) >= 2 and first[0] in ("属性", "参数", "字段") and len(first) >= 3:
                    payload_rows = rows
                elif len(first) == 2 and any(r and r[0] in ("name", "namespace") for r in rows[1:]):
                    header_rows = rows
            ns = ""
            for r in header_rows[1:]:
                if r and r[0] == "namespace":
                    ns = r[1].strip()
            # drop common boilerplate rows; DuerOS payload keys are ASCII
            # identifiers, so rows whose first cell is not one (e.g. markdownify
            # wrapped a multi-paragraph description into a continuation row) are
            # artefacts and get dropped.
            extra = [
                r for r in payload_rows[1:]
                if r
                and r[0] not in COMMON_FIELDS
                and re.fullmatch(r"[A-Za-z][A-Za-z0-9._]*", r[0])
            ]
            out.append(f"### {title}")
            out.append("")
            out.append(f"- 方向：{message_direction(title)}")
            if ns:
                out.append(f"- namespace：`{ns}`")
            if extra:
                out.append("- 额外 Payload：")
                for r in extra:
                    fld = r[0]
                    req = fmt_required(r[2]) if len(r) > 2 else ""
                    desc = shorten(r[1]) if len(r) > 1 else ""
                    out.append(f"  - `{fld}` — {desc}  [{req}]")
            else:
                out.append("- 额外 Payload：无（仅公共字段 accessToken / appliance）")
            out.append(f"- 原文：[{slug}.md#{title.lower()}]({slug}.md#{title.lower()})")
            out.append("")
        (OUT_DIR / f"{slug}.md").write_text("\n".join(out), encoding="utf-8")
        index.append(f"| `{slug}.md` | {len(kept)} 条消息契约 | {path.stat().st_size//1024} KB |")

    (OUT_DIR / "00-index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print("contracts written to", OUT_DIR)


if __name__ == "__main__":
    main()
