# DuerOS 协议契约索引（省 token 速查）


> 由 `make_contracts.py` 自动生成，原始官方文档在 `../dbp-smart-home-protocol/`（未改动）。
> 每条约含：方向 / 额外 Payload 字段（公共字段见下方约定）/ 原文指针。
> 需要完整描述、示例 JSON、Header 细节时，点“原文”回查。

## 公共 Payload 字段（所有消息通用）

- `accessToken`：OAuth access token（必填）
- `appliance`：设备对象，含 `applianceId`（必填）与 `additionalApplianceDetails`（可空）

| 契约文件 | 覆盖内容 | 原文体积 |
|---|---|---|
| `attributes-report.md` | 2 条消息契约 | 11 KB |
| `attributes.md` | 设备属性定义（name/type/scale/legalValue）。 | 见原文 |
| `control-message.md` | 108 条消息契约 | 181 KB |
| `discovery-message.md` | 2 条消息契约 | 17 KB |
| `error-message.md` | 22 条消息契约 | 21 KB |
| `intro-protocol.md` | 协议总览（Header/Payload 基本结构、命名空间）。 | 见原文 |
| `iov-message.md` | 30 条消息契约 | 64 KB |
| `notification-message.md` | 2 条消息契约 | 4 KB |
| `query-message.md` | 38 条消息契约 | 65 KB |
| `sweeping-rebot-message.md` | 扫地机器人：复用通用 发现/控制/查询/属性上报/错误 消息，仅约定设备能力。 | 见原文 |
