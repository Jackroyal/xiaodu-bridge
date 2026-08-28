# Home Assistant Custom Integration: xiaodu

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Hassfest](https://github.com/Jackroyal/ha-xiaodu/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Jackroyal/ha-xiaodu/actions/workflows/hassfest.yml)
[![HACS Validation](https://github.com/Jackroyal/ha-xiaodu/actions/workflows/hacs.yml/badge.svg)](https://github.com/Jackroyal/ha-xiaodu/actions/workflows/hacs.yml)

让 Home Assistant 中的设备被小度音箱 / 小度 App 发现、查询与控制。

本集成作为 **DuerOS 智能家居 OAuth 服务端**运行：小度是 OAuth 客户端，集成通过
`/api/xiaodu` 与 `/api/xiaodu/service` 接收请求，把 HA 实体映射为 DuerOS 语义设备，
并签发仅限本集成使用的私有不透明 token；该 token 不能访问 Home Assistant API。

当前集成版本：**v0.9.2**。

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
4. 搜索 **xiaodu**，或先添加本仓库为 Custom Repository：
   `https://github.com/Jackroyal/ha-xiaodu`，类别选择 **Integration**。
5. 下载后重启 Home Assistant。

> 小度为限定地区的平台，`hacs.json` 中已设置 `country: CN`：只有 HACS 的
> 国家/地区设置为 **China** 或 **All** 时才会显示本仓库。若未看到，可在
> **HACS → Settings → Country** 改为 **All**，或直接使用下面的手动安装方式。

### 手动安装

把仓库中的 `custom_components/ha_xiaodu` 目录复制到：

```text
/config/custom_components/ha_xiaodu
```

重启 Home Assistant 后，进入 **设置 → 设备与服务 → 添加集成**，搜索 **xiaodu**。

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
├── custom_components/ha_xiaodu/
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
└── tests/
```

## 本地开发

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
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
    custom_components.ha_xiaodu: debug
```

集成会记录 OAuth 与 WebService 请求的耗时、动作、结果和 HTTP 状态；不要把 token、
Client Secret 或用户设备 ID 发布到公开 issue。

## License

MIT
