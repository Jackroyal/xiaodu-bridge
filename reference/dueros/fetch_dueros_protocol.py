#!/usr/bin/env python3
"""Fetch the DuerOS 智能家居协议 (dbp-smart-home/protocol) docs and convert to Markdown.

Usage:
    python3 reference/dueros/fetch_dueros_protocol.py

Output: Markdown files written next to this script under
    dbp-smart-home-protocol/<slug>.md   (plus 00-index.md)

Rules:
- Fetch only the 10 pages listed in PAGES (the official "智能家居协议" group).
- Extract only the article body (``div.resource-text.markdown-body``).
- Rewrite intra-group links (full URL / absolute path) to relative ``<slug>.md``
  files; GitHub-style slugify anchors so section links survive the conversion.
- Keep every other (external / out-of-group) URL absolute.
- Write a small YAML front-matter (title / source / fetched_at) on each file.
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE = "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol"
PAGES = [
    ("智能家居协议简介", "intro-protocol"),
    ("发现设备", "discovery-message"),
    ("控制消息", "control-message"),
    ("查询消息", "query-message"),
    ("通知消息", "notification-message"),
    ("错误消息", "error-message"),
    ("设备属性", "attributes"),
    ("设备属性上报", "attributes-report"),
    ("车载类设备协议", "iov-message"),
    ("扫地机器人协议", "sweeping-rebot-message"),
]
SLUGS = {slug for _, slug in PAGES}
OUT_DIR = Path(__file__).resolve().parent / "dbp-smart-home-protocol"


def slugify(text: str) -> str:
    """GitHub-flavoured anchor slug (lowercase, punctuation dropped, '-' for space)."""
    s = text.lower()
    s = re.sub(r"[^\w\u4e00-\u9fff-]", "", s, flags=re.UNICODE)
    s = s.replace("_", "-")
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    return s


def unescape_underscores(text: str) -> str:
    """Restore markdownify's "backslash-underscore" escapes back to plain "_" outside code fences.

    Intraword underscores (``AIR_CONDITION``) never start emphasis, so this is
    safe and keeps identifiers greppable. Content inside fenced code blocks is
    left untouched.
    """
    out = []
    in_code = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        elif not in_code:
            line = line.replace("\\_", "_")
        out.append(line)
    return "\n".join(out)


def clean_article(soup: BeautifulSoup) -> BeautifulSoup:
    """Keep the article body and strip self-link icon clutter."""
    node = soup.find("div", class_="resource-text markdown-body")
    if node is None:
        node = soup.find("div", class_="markdown-body")
    if node is None:
        raise RuntimeError("article container div.resource-text.markdown-body not found")
    # unwrap heading anchor-box wrappers, drop self-link icons
    for box in node.find_all("div", class_="anchor-box"):
        box.unwrap()
    for a in node.find_all("a", class_="anchor"):
        a.decompose()
    return node


def rewrite_links(node: BeautifulSoup) -> None:
    """Rewrite intra-group hrefs to relative md paths; keep others absolute."""
    for a in node.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("javascript:", "mailto:")):
            continue
        if href.startswith("#"):
            a["href"] = "#" + slugify(href[1:])
            continue
        # full or absolute-path link into the protocol group
        m = re.search(r"/protocol/([A-Za-z0-9-]+)_markdown(?:#([^#]*))?$", href)
        if m and m.group(1) in SLUGS:
            frag = m.group(2)
            target = f"{m.group(1)}.md"
            if frag:
                target += "#" + slugify(frag)
            a["href"] = target


def fetch(url: str) -> str:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text


def front_matter(title: str, slug: str, fetched: str) -> str:
    return (
        "---\n"
        f"title: \"{title}\"\n"
        f"source: \"{BASE}/{slug}_markdown\"\n"
        f"fetched_at: \"{fetched}\"\n"
        "---\n\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fetched = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    index = [
        "# DuerOS 智能家居协议（官方文档归档）\n",
        "",
        f"- 抓取时间：{fetched}",
        f"- 来源前缀：`{BASE}`",
        "- 链接约定：协议组内互链已改写为相对 `xxx.md` 路径，锚点为 GitHub 风格 slug；组外/外部链接保持绝对 URL。",
        "",
        "| # | 标题 | 本地文件 |",
        "|---|---|---|",
    ]
    for i, (title, slug) in enumerate(PAGES, start=1):
        url = f"{BASE}/{slug}_markdown"
        print(f"[{i}/{len(PAGES)}] fetching {slug} ...", flush=True)
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        node = clean_article(soup)
        rewrite_links(node)
        body_md = md(str(node), heading_style="ATX")
        body_md = unescape_underscores(body_md)
        # collapse 3+ blank lines
        body_md = re.sub(r"\n{3,}", "\n\n", body_md).strip() + "\n"
        out = OUT_DIR / f"{slug}.md"
        out.write_text(front_matter(title, slug, fetched) + body_md, encoding="utf-8")
        index.append(f"| {i} | {title} | `{slug}.md` |")
    (OUT_DIR / "00-index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print("done:", OUT_DIR)


if __name__ == "__main__":
    sys.exit(main())
