# Home Assistant Custom Integration: xiaodu bridge

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Hassfest](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hassfest.yml)
[![HACS Validation](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hacs.yml/badge.svg)](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hacs.yml)

让 Home Assistant 中的设备被小度音箱 / 小度 App 发现、查询与控制。

> **名称说明**：本集成的商店名称为 `xiaodu bridge`，domain 为 `xiaodu_bridge`
> （仓库也已更名为 `xiaodu-bridge`）。方向是 **Home Assistant → 小度**：HA 里的实体被
> 映射成 DuerOS 语义设备，交给小度音箱/App 控制。它与「把小度生态里的设备
> 反向导入 HA」类集成（例如 cookie 轮询 `xiaodu.baidu.com` 的方案）方向相反、
> 实现互不相关，两者可以同时安装、互不冲突（domain 不同）。

本集成作为 **DuerOS 智能家居 OAuth 服务端**运行：小度是 OAuth 客户端，集成通过
`/api/xiaodu` 与 `/api/xiaodu/service` 接收请求，把 HA 实体映射为 DuerOS 语义设备，
并签发仅限本集成使用的私有不透明 token；该 token 不能访问 Home Assistant API。

当前集成版本：**v0.9.6**。

## 功能

- **语义设备模型**：设备按 DuerOS 语义暴露，而不是拆成零散实体。浴霸、晾衣杆、
  扫地机、洗衣机有专用档案；灯、开关、风扇、空调、窗帘、媒体播放器、插座、
  温湿度传感器等使用通用能力合成。
- **配置流与选项流**：添加集成时配置 OAuth Client ID / Secret、botId、回调地址、
  公网地址；添加后按「设备 → 能力」选择要暴露的设备。
- **OAuth 2.0**：提供授权页与 Token 端点。Access Token 有效期 7 天，Refresh Token
  有效期 30 天，支持 `refresh_token` 续期。
- **Discovery / Query / Control**：兼容小度控制台模拟测试的 DCS multipart 与线上
  JSON 报文。
- **主动状态上报**：可控制设备状态变化时向小度发送 Change Report；纯只读传感器不上报。
- **房间分组**：可把 HA 区域同步为 DuerOS `discoveredGroups`。
- **定时开关**：支持 `timingTurnOn` / `timingTurnOff`，定时信息通过 HA Storage
  持久化，重启后自动恢复。
- **单一中枢设备**：设备注册表只保留一个「小度中枢」，桥接的 HA 设备不再重复
  出现在设备列表中。
- **设备集自动刷新**：新增/移除/改名实体、设备或区域后，设备集缓存自动失效重建，
  Discovery 始终按当前 HA 状态构建，新设备无需重启即可被小度发现。
- **温度单位归一化**：传感器温度按 HA 单位系统（`hass.config.units`）归一化
  上报（公制即统一摄氏度）；`unknown`/`unavailable` 等非数值读数不再上报 0.0。
- **独立灯设备**：浴霸、晾衣杆等复合设备的灯拆分为独立 `LIGHT` 设备，
  亮度/色温/颜色等能力按 HA 实体实际能力自动暴露。
- **空调温控加减**：温度与风速同时支持小度 App/语音的 `set*` 与
  `increment/decrement`；语音绝对设定 `SetTemperatureRequest` 按官方载荷键
  `targetTemperature` 解析（含 CELSIUS/FAHRENHEIT 归一）；空调风速按 HA climate
  的离散 `fan_mode` 档位（如 20/40/…/100/auto）映射，不再依赖不存在的 `percentage`。
- **空调模式上报**：hvac 模式优先取实体 state（兼容美的等不提供 `hvac_mode`
  属性的集成），避免制冷中的空调被小度识别为“未知模式”。

## 要求

- Home Assistant `2025.1.0` 或更高版本。
- 小度平台可以从公网访问 Home Assistant 端点。
- 建议使用有效 HTTPS 证书；下文示例使用 `https://ha.example.com`。
- 反向代理到 Home Assistant 时，示例后端端口使用 `8123`。

## 安装

### HACS（推荐）

1. 确认已安装 [HACS](https://hacs.xyz)。
2. 打开 **HACS → Integrations**。
3. 选择 **Explore & Download Repositories**。
4. 搜索 **xiaodu bridge**，或先添加本仓库为 Custom Repository：
   `https://github.com/Jackroyal/xiaodu-bridge`，类别选择 **Integration**。
5. 下载后重启 Home Assistant。

> 小度为限定地区的平台，`hacs.json` 中已设置 `country: CN`：只有 HACS 的
> 国家/地区设置为 **China** 或 **All** 时才会显示本仓库。若未看到，可在
> **HACS → Settings → Country** 改为 **All**，或直接使用下面的手动安装方式。

### 手动安装

把仓库中的 `custom_components/xiaodu_bridge` 目录复制到：

```text
/config/custom_components/xiaodu_bridge
```

重启 Home Assistant 后，进入 **设置 → 设备与服务 → 添加集成**，搜索 **xiaodu bridge**。

## 配置集成

添加集成时填写与小度开发者后台一致的 OAuth 信息：

| 字段 | 说明 | 示例 |
|---|---|---|
| `client_id` | 自定义 OAuth Client ID | `dueros_xxx` |
| `client_secret` | 自定义随机 Client Secret | `<CLIENT_SECRET>` |
| `bot_id` | 小度技能 ID，用于设备变更推送 | `<BOT_ID>` |
| `redirect_uri` | 小度平台生成的 Callback URL | `https://xiaodu.baidu.com/...` |
| `public_url` | HA 的公网 HTTPS 基础地址 | `https://ha.example.com` |

确认页会展示需要填到小度开发者后台的地址：

```text
Authorize URL: https://ha.example.com/api/xiaodu/oauth/authorize
Token URL:     https://ha.example.com/api/xiaodu/oauth/token
WebService:    https://ha.example.com/api/xiaodu/service
Callback URL:  小度平台生成的 redirect_uri
```

如果 HA 使用非默认端口，请在 `public_url` 与反向代理中同步指定；本文示例端口为
`8123`。

## 公网 HTTPS 示例

```text
DuerOS
  ↓ HTTPS
https://ha.example.com
  ↓
反向代理 / HTTPS 终结
  ↓
Home Assistant :8123
  ↓
/api/xiaodu/*
```

反向代理需要保留标准转发头，并允许请求到达：

```text
/api/xiaodu/oauth/authorize
/api/xiaodu/oauth/token
/api/xiaodu/service
```

## 设备与能力

添加集成后，打开集成条目选择 **设备与能力**：

1. 中枢菜单提供设备列表、添加 / 移除设备、保存并完成。
2. 设备列表按「房间 · 设备名」展示，新增设备默认暴露全部可用能力。
3. 单个设备可选择能力；控制类设备的 `power` 强制开启，只读能力如
   `temperature` / `humidity` 可按需勾选。
4. `sync_areas` 开启后，HA 区域会作为小度房间分组同步。

## 目录结构

```text
.
├── .github/workflows/          # Hassfest 与 HACS 校验
├── custom_components/xiaodu_bridge/
│   ├── __init__.py             # 集成入口 / unload / 中枢设备注册
│   ├── config_flow.py          # 配置流与设备 → 能力选项流
│   ├── devices.py              # 设备、域与能力辅助
│   ├── oauth_server.py         # OAuth 端点与 DuerOS WebService 视图
│   ├── oauth_store.py          # 最小权限 token 存取
│   ├── timers.py               # 定时调度与持久化
│   ├── dueros_sync.py          # 设备变更推送
│   ├── state_report.py         # 语义设备状态上报
│   ├── dueros/                 # DuerOS 语义模型与协议实现
│   ├── manifest.json
│   ├── strings.json
│   └── translations/
├── hacs.json
├── pyproject.toml
├── reference/dueros/            # 小度官方协议归档 + 契约速查/检索（开发参考）
│   ├── dbp-smart-home-protocol/ # 官方协议原文（自动抓取，勿手改）
│   ├── contracts/               # 消息 → Payload 契约速查（自动生成）
│   ├── lookup.py                # 协议检索：契约优先，未命中回退原文切片
│   ├── verify_conversion.py     # 抓原文自检转换保真度
│   └── README.md
└── tests/
```

## 本地开发

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
```

### 协议参考（改动 DuerOS 协议前先读）

本地归档了小度官方「智能家居协议」全文与自动生成的契约速查（见 `reference/dueros/README.md`）。
改动 `xiaodu_bridge` 中任何 DuerOS 消息/字段/能力前，先用契约优先的检索定位，不要整篇读大文件：

```bash
python3 reference/dueros/lookup.py SetTemperature   # 契约速查 + 原文指针
python3 reference/dueros/lookup.py 空调 --grep       # 契约未覆盖时回退原文切片
```

仓库启用以下 GitHub Actions：

- Home Assistant **Hassfest** 校验。
- **HACS Integration** 校验。

## 日志

在 HA 配置中开启调试日志：

```yaml
logger:
  default: warning
  logs:
    custom_components.xiaodu_bridge: debug
```

集成会记录 OAuth 与 WebService 请求的耗时、动作、结果和 HTTP 状态；不要把 token、
Client Secret 或用户设备 ID 发布到公开 issue。

## License

MIT
