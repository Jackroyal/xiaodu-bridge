# Home Assistant Custom Integration: xiaodu bridge

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Hassfest](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hassfest.yml)
[![HACS Validation](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hacs.yml/badge.svg)](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hacs.yml)

> English: [README.en.md](README.en.md)

让 Home Assistant 中的设备被小度音箱 / 小度 App 发现、查询与控制。

> **名称说明**：本集成的商店名称为 `xiaodu bridge`，domain 为 `xiaodu_bridge`
> （仓库也已更名为 `xiaodu-bridge`）。方向是 **Home Assistant → 小度**：HA 里的实体被
> 映射成 DuerOS 语义设备，交给小度音箱/App 控制。它与「把小度生态里的设备
> 反向导入 HA」类集成（例如 cookie 轮询 `xiaodu.baidu.com` 的方案）方向相反、
> 实现互不相关，两者可以同时安装、互不冲突（domain 不同）。

本集成作为 **DuerOS 智能家居 OAuth 服务端**运行：小度是 OAuth 客户端，集成通过
`/api/xiaodu` 与 `/api/xiaodu/service` 接收请求，把 HA 实体映射为 DuerOS 语义设备，
并签发仅限本集成使用的私有不透明 token；该 token 不能访问 Home Assistant API。

当前集成版本：**v0.9.13**。

## 功能

- **语义设备模型**：设备按 DuerOS 语义暴露，而不是拆成零散实体。浴霸、晾衣杆、扫地机、洗衣机有专用档案；灯、开关、风扇、空调、窗帘、媒体播放器、插座、温湿度传感器等按通用能力合成。
- **配置流与选项流**：添加集成时配置 OAuth 凭证、botId、公网地址；添加后按「设备 → 能力」选择要暴露的设备，可对单个设备覆写：限制能力、隐藏实体、绑定语义角色、改展示名（不动 HA 实体名）。
- **OAuth 2.0 服务端**：提供授权页与 Token 端点；Access Token 7 天、Refresh Token 30 天，支持续期。签发的 token 仅限本集成使用，不能访问 HA API。
- **Discovery / Query / Control**：兼容小度控制台模拟测试的 DCS multipart 与线上 JSON 两种报文。
- **状态上报与定时**：可控设备状态变化时主动向小度发送 Change Report；支持 `timingTurnOn` / `timingTurnOff`，定时信息持久化，重启后自动恢复。
- **设备与房间管理**：HA 区域可同步为 DuerOS `discoveredGroups`；设备注册表只保留一个「小度中枢」，实体改名不会让小度侧设备重建，设备集变更自动刷新，新设备无需重启即可被发现。

## 最佳实践

- 《[HA 折腾记：从米家、美的到小度和 HomeKit](https://mp.weixin.qq.com/s/vCMu2KMSknTfMnio1MwWNA)》——一篇实际部署记录：
  家里的米家 / Sonoff / 美的设备接进 HA，再交给小度与 HomeKit 的完整链路。

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

## 支持的设备、属性与能力

本集成把 HA 实体映射为 DuerOS 语义设备，分「专用档案」与「通用能力合成」两类。

### 设备类型

**专用档案（复合设备）** —— 一个物理设备合成一个或多个 DuerOS appliance：

| 设备 | DuerOS 类型 | 合成能力 |
|---|---|---|
| 浴霸 | `YUBA` | 开关（取暖 / 吹风 / 换气）、模式（`HEAT` / `FAN` / `VENTILATION`）、暖风档位、风速、目标温度 |
| 晾衣架 | `CLOTHES_RACK` | 开关（升降）、位置、暂停、模式（`DRYING` / `DISINFECT`） |
| 扫地机器人 | `SWEEPING_ROBOT` | 开关、暂停、吸力、电量 |
| 洗衣机 | `WASHING_MACHINE` | 电源（开 / 关 / 启动）、洗涤模式、水位、目标温度、运行状态、剩余时间 |

浴霸、晾衣架的灯不并入复合设备（DuerOS 无对应动作），而是拆分为独立的 `LIGHT`
设备，亮度 / 色温 / 颜色按实体实际能力自动暴露。

**通用能力合成** —— 按 HA 实体域映射：

| HA 域 | DuerOS 类型 | 能力 |
|---|---|---|
| `light` | `LIGHT` | 开关、亮度、色温、颜色 |
| `switch` | `SWITCH` | 开关 |
| 插座（`plug` / 名称含「插座」） | `SOCKET` | 开关 |
| `fan` | `FAN` | 开关、风速 |
| `climate` | `AIR_CONDITION` | 开关、目标温度、模式、风速 |
| `cover` | `CURTAIN` | 开关、位置、暂停 |
| `media_player` | `TV_SET` | 开关、音量、静音、频道 |
| `humidifier` | `HUMIDIFIER` | 开关、目标湿度、模式 |
| `sensor` | `SENSOR` | 温度、湿度（只读） |

> `vacuum` 域由「扫地机器人」档案接管。指示 / 童锁 / 夜灯 / 故障等状态实体
> （`indicator`、`child_lock`、`night_light`、`fault` 等）不会暴露给音箱。

### 能力清单

| 能力 key | 中文 | 类型 | DuerOS 属性 |
|---|---|---|---|
| `power` | 开关 | 控制 | `turnOnState` |
| `brightness` | 亮度 | 控制 | `brightness` |
| `colorTemperature` | 色温 | 控制 | `colorTemperatureInKelvin` |
| `color` | 颜色 | 控制 | `color` |
| `volume` | 音量 | 控制 | `volume` |
| `mute` | 静音 | 控制 | `muteState` |
| `channel` | 频道 | 控制 | `channel` |
| `fanSpeed` | 风速 | 控制 | `fanSpeed` |
| `targetTemperature` | 目标温度 | 控制 | `targetTemperature` |
| `targetHumidity` | 目标湿度 | 控制 | `targetHumidity` |
| `mode` | 模式 | 控制 | `mode` |
| `percentage` | 位置 | 控制 | `percentage` |
| `suction` | 吸力 | 控制 | `suction` |
| `waterLevel` | 水量 / 水位 | 控制 | `waterLevel` |
| `pause` | 暂停 | 控制 | `pauseState` |
| `continue` | 继续 | 控制 | — |
| `temperature` | 温度 | 只读 | `temperature` |
| `humidity` | 湿度 | 只读 | `humidity` |
| `warmthLevel` | 暖风档位 | 控制 | `warmthLevel`（请求字段 `gear`） |
| `electricityCapacity` | 电量 | 只读 | `electricityCapacity` |
| `workState` | 运行状态 | 只读 | `workState` |
| `timeLeft` | 剩余时间 | 只读 | `timeLeftInSeconds` |

控制类能力映射为 DuerOS 动作（`turnOn` / `turnOff` / `set*` / `increment*` /
`decrement*` / `pause` / `continue` / `timingTurnOn` / `timingTurnOff` 等）；只读
能力仅作为属性，供 Query 查询。传感器温度按 HA 单位系统归一化上报（公制即统一
摄氏度）；`unknown` / `unavailable` 等非数值读数不产生属性。

`suction` / `waterLevel` / `warmthLevel` / `mode` 这类取值是**契约枚举**的能力，
按实体自身的候选值双向解析：先比对同名值，再按别名关键词（标准 / 强力 / 低 / 中 /
高 / 快洗 …）匹配，有序档位最后按位置换算；解析不到时控制返回“不支持”，读取则
不上报该属性（不会把厂商自己的档位名当成契约取值报给小度）。别名表在
`dueros/profiles.py` 顶部，集成换了措辞改那里即可。

两处例外：`mode` 属性按契约允许 `customName`（厂商自定义模式），认不出的模式名照
原样上报与下发，`legalValue` 用实体自己的候选值；风速（`fanSpeed`）读回的是 1~10
档位刻度上的**整数**位置，与写入用的是同一刻度。每台设备最多同步 10 个属性（协议
上限），Discovery / 控制确认 / 查询共用同一个构造，按名去重且基线属性（`name` /
`connectivity`）优先。

`select` 类实体的当前档位取自实体 **state**（HA 的 select 不提供 `option` 属性），
所以暖风档位 / 风机档位这类能力会真正上报当前档位，而不是空值。

## 配置设备与能力

添加集成后，打开集成条目选择 **设备与能力**：

1. 中枢菜单提供设备列表、添加 / 移除设备、保存并完成。
2. 设备列表按「房间 · 设备名」展示，新增设备默认暴露全部可用能力。
3. 单个设备可选择能力；控制类设备的 `power` 强制开启，只读能力如
   `temperature` / `humidity` 可按需勾选。
4. `sync_areas` 开启后，HA 区域会作为小度房间分组同步。

## 目录结构

```text
.
├── .github/workflows/          # Hassfest、HACS 与 Tests 校验
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

改动 `xiaodu_bridge` 中任何 DuerOS 消息 / 字段 / 能力前，**先查小度官方「智能家居协议」的
Payload 契约再动代码**——不要凭属性名或直觉推断载荷键（历史上有过把属性名当载荷键用，
导致语音指令一律回落「不支持」的教训）。

该协议文档为小度官方资料，**不随本仓库分发**。开发者需自行从官方文档站获取，或使用本地的
两级检索工具（契约速查优先，未命中再回退原文切片）：

```bash
python3 <协议归档>/lookup.py SetTemperature   # 契约速查 + 原文指针
python3 <协议归档>/lookup.py 空调 --grep       # 契约未覆盖时回退原文切片
```

用法与两级工作流见归档目录内的 `README.md`。

仓库启用以下 GitHub Actions：

- Home Assistant **Hassfest** 校验。
- **HACS Integration** 校验。
- **Tests**：pytest 单元/集成测试、ruff 静态检查、manifest ↔ pyproject 版本一致性校验。

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
