# DuerOS 智能家居协议 — 本地参考（两级 · 省 token 工作流）

本目录是从小度官方「智能家居协议」文档抓取的**只读原文档案 + 自动生成的契约速查**，
供开发 `xiaodu_bridge` 时按需查阅。官方来源与抓取时间见各文件 front-matter / `00-index.md`。

## 两级结构（B+C）

1. **第一级：契约速查（`contracts/`，日常开发首选）**
   - 由 `make_contracts.py` 从原文自动抽取，每条约：方向 / namespace / 额外 Payload 字段(必填) / 原文指针。
   - 公共字段（`accessToken`、`appliance`）在 `contracts/00-index.md` 统一说明，不再逐条重复。
   - 10 篇原文约 418KB → 契约约 104KB（`control-message.md` 185KB → 53KB）。
2. **第二级：原文档案（`dbp-smart-home-protocol/`，有歧义/需要示例 JSON 时回查）**
   - 完整描述、Header 结构、示例 JSON、逐字说明都在这里，**保持原始抓取内容不变**。

## 推荐工作流（对开发/Agent 都适用）

```bash
# ① 查消息（默认命中契约，输出几行速查 + 原文指针）
python3 reference/dueros/lookup.py SetTemperature

# ② 契约没覆盖（属性/叙述页）→ 回退原文标题索引或全文搜索
python3 reference/dueros/lookup.py 空调 --grep

# ③ 需要某节完整原文 → 按指针精确切片，禁止整篇读
sed -n '1606,1654p' reference/dueros/dbp-smart-home-protocol/control-message.md

# ④ 浏览某页有哪些内容（只 grep，别 cat）
grep -E 'control-message' reference/dueros/dbp-smart-home-protocol/sections.tsv
```

## 文件说明

| 路径 | 作用 |
|---|---|
| `contracts/00-index.md` | 契约总索引 + 公共字段约定 |
| `contracts/<page>.md` | 每页消息 → Payload 契约（自动生成，勿手改） |
| `dbp-smart-home-protocol/00-index.md` | 原文 10 页清单 + 抓取时间 + 链接约定 |
| `dbp-smart-home-protocol/sections.tsv` | 原文全部 1006 个标题 → 文件:行号（只 grep） |
| `dbp-smart-home-protocol/<page>.md` | 原文档案（未改动，按需 sed 切片） |
| `lookup.py` | 首选入口：先命中契约，未命中回退原文切片 |
| `make_index.py` | 重新生成 `sections.tsv`（原文变化后跑） |
| `make_contracts.py` | 重新生成 `contracts/`（原文变化后跑） |
| `verify_conversion.py` | 抓原文自检转换保真度（结构/文本/转义/代码围栏），干净则退出码 0 |
| `fetch_dueros_protocol.py` | 重新抓取官方原文并转换（重抓后跑上面两个） |

## 维护顺序（官方文档更新时）

```bash
python3 reference/dueros/fetch_dueros_protocol.py   # 重抓原文（覆盖 dbp-smart-home-protocol/*.md）
python3 reference/dueros/make_index.py              # 重建标题索引
python3 reference/dueros/make_contracts.py          # 重建契约
python3 reference/dueros/verify_conversion.py       # 自检：应输出 OK 且退出码 0
```

## 链接与锚点约定

- 协议组内互链已改写为相对 `xxx.md` 路径，锚点为 GitHub 风格 slug。
- 组外/外部链接保留绝对 URL。

## 已知取舍

- markdownify 会把表格里嵌套列表压成行内 ` * … * ` 形式；个别多段落单元格在 md 里错行，
  `make_contracts.py` 已按“payload 键必为 ASCII 标识符”规则剔除这类伪行。
- 锚点为 GitHub slug：GitHub / VS Code / Typora / Obsidian 均可跳转。
