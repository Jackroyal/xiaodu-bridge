# Home Assistant Custom Integration: Xiaodu (DuerOS)

第一阶段骨架：一个可安装、可在 HA 界面添加的小度集成。已实现实体包含/排除
过滤；OAuth 与 DuerOS 协议尚未实现。目标是为后续「OAuth 授权 → DuerOS
发现/查询/控制」留出清晰边界。

## 目录结构

```text
.
├── custom_components/
│   └── xiaodu/
│       ├── __init__.py            # 集成入口：setup / unload
│       ├── config_flow.py         # 配置流（第一/二阶段入口）
│       ├── const.py               # 常量与阶段边界说明
│       ├── entity_filter.py       # 实体包含/排除过滤器（已实现并接入选项流）
│       ├── oauth_server.py        # OAuth2 授权/Token 端点（阶段 2，已实现）
│       ├── oauth_store.py         # 不透明 token 签发/持久化（最小权限）
│       ├── dueros/
│       │   ├── __init__.py        # 对外只暴露 handle_request
│       │   ├── constants.py       # 协议常量：namespace / 动作 / 错误码 / 设备类型
│       │   ├── adapters.py        # 域适配器注册表（每 HA 域一个适配器）
│       │   └── protocol.py        # 薄分发层：解析 header → 路由到适配器
│       ├── manifest.json
│       ├── strings.json           # 英文文案（UI 源）
│       └── translations/
│           └── zh-Hans.json       # 简体中文文案
├── tests/
│   ├── test_entity_filter.py      # 纯逻辑测试，无需 HA
│   ├── test_dueros_protocol.py    # DuerOS 协议纯逻辑测试（无需 HA）
│   ├── test_config_flow.py        # 配置流测试（需 HA 测试环境）
│   └── test_init.py               # setup/unload 测试（需 HA 测试环境）
├── pyproject.toml
└── README.md
```

## 阶段规划

- **阶段 1（完成）**：可安装骨架 + 配置流，能在 HA 中添加小度集成。
- **阶段 2（完成）**：实体包含/排除过滤已接入配置项选项流；小度智能家居
  技能走“小度当 OAuth 客户端、本集成当授权服务器”的模式：`oauth_server.py`
  提供 `/api/xiaodu/oauth/authorize` 授权页（复用 HA 登录流认证）与
  `/api/xiaodu/oauth/token` Token 端点。最小权限设计：签发给小度的是**本集成
  私有的不透明 token**（`oauth_store.py` 持久化存储），不是 HA 用户 token，
  无法用于 HA API；`/api/xiaodu` 端点只按 EntityFilter 暴露过滤后的实体。
- **阶段 3（完成）**：DuerOS discovery / query / action 已在 `dueros/` 实现，
  通过 HTTPS 端点 `/api/xiaodu/service`（WebService）接收小度请求，兼容小度
  控制台“模拟测试”的 DCS multipart 报文与线上纯 JSON 报文，校验 payload 中的
  access token 后将可控制实体映射为小度设备/能力；灯类设备支持开关、
  亮度、颜色与色温（`setColorTemperature` + `colorTemperatureInKelvin`，
  按设备 `supported_color_modes` 动态上报能力）。能力分两类：
  **控制能力**（power/brightness/colorTemperature/color/volume/channel/mute/
  fanSpeed/targetTemperature/mode/suction/pause…，映射小度动作）与**查询能力**
  （temperature/humidity，只读，映射小度查询/属性，可勾选）；能力按设备类型
  派生，只读能力跨实体聚合（温湿度计的温度/湿度分别路由到各自实体）。
  **多单元模型（v0.6.0）**：一台设备可暴露多个单元（实体），每个单元 = 小度
  侧一个设备，例如晾衣杆本体（`CLOTHES_RACK`，上升/下降/暂停）与晾衣杆灯
  （`LIGHT`）；指示灯/童锁等辅助实体自动排除。选项向导为 设备 → 单元 → 能力
  三级选择；默认单元保持设备名并沿用旧配置，其余单元默认关闭。
  **全量设备覆盖（v0.7.0）**：按小度官方协议逐台设备核对能力后补齐缺口——
  浴霸按官方 `YUBA` 类型暴露（`setMode` 取暖/吹风/换气/照明、
  `unSetMode`、`setTemperature` 设定温度、关浴霸 = 全功能关闭）；
  插座按官方 `SOCKET` 类型暴露；扫地机新增 `continue`（继续扫地）；
  所有带开关能力的设备支持小度定时开关（`timingTurnOn/timingTurnOff`，
  用 HA 自身的 `async_track_point_in_utc_time` 调度 + HA Storage 持久化，
  HA 重启后自动重新布防，不丢失）；电视/浴霸的 `*_is_on` 辅助开关、
  提示音/指示灯等辅助实体自动排除，避免多出无意义单元。
  可选「同步区域」
  （`sync_areas`）：发现时把 HA 的区域（房间）同步为小度
  `discoveredGroups`，分组名自动清洗（≤20 字符、去标点）。
## DuerOS 协议（阶段 3）

WebService 端点 `POST /api/xiaodu/service` 接收小度智能家居请求，按三层结构分发：
（小度后台的 **WebService** 字段填 `https://你的域名:端口/api/xiaodu/service`）

从 v0.4.0 起引入**能力模型**（平台无关，为多音箱扩展预留）：

```text
配置层：设备 + 能力勾选（power / brightness / colorTemperature / color，power 强制）
        │
        ▼
devices.py  XiaoduDeviceMap   # 按 device_id 归组实体、选主实体、派生能力集
        │
        ▼
dueros/protocol.py            # 小度平台层：能力 → DuerOS 动作/属性翻译
```

- 旧版「实体 include/exclude」选项会在读取时自动迁移为「设备 + 默认全能力」。
- 新增音箱（天猫精灵/小爱等）只需新写平台翻译层，复用 `devices.py` 的能力模型。

```text
oauth_server.XiaoduDuerOSServiceView  # 薄视图：解析纯 JSON 或 DCS multipart，校验 payload.accessToken、按 EntityFilter 过滤
        │
        ▼
dueros.protocol.handle_request      # 分发层：按 header.namespace 路由，拼装响应/错误信封
        │
        ▼
dueros.adapters.<Domain>Adapter     # 域适配器：设备类型 / 动作白名单 / 属性 / 服务调用映射
```

架构要点（区别于 HAVCS 的单体实现）：

- **适配器注册表**：每个 HA 域一个适配器类（`LightAdapter`、`SwitchAdapter`、
  `CoverAdapter`、`SensorAdapter` …），通过 `@register` 注册。协议分发层从不
  按域写 if/else，新增设备类型 = 新增一个适配器类 + 注册，不动分发层。
- **动作白名单**：每个适配器声明自己的 `actions`，控制请求只允许白名单内
  动作；任意 HA 服务从小度侧不可达（最小权限）。
- **协议常量集中**：namespace、错误码（`InvalidAccessTokenError` /
  `DriverInternalError` / `TargetOfflineError` / `NotSupportedInCurrentModeError`）、
  设备类型集中在 `dueros/constants.py`。
- **错误信封**：无效 token 返回 HTTP 401 `{"error":"ACCESS_TOKEN_INVALIDATE"}`
  （小度规范要求）；业务错误返回 HTTP 200 + `header.name` 为错误码 + 空 payload。
- **token 位置**：小度把 access token 放在 JSON 的 `payload.accessToken`，
  `Authorization: Bearer` 头保留作兼容回退。

当前支持的域：`light`（开关/亮度/颜色）、`switch`、`fan`、`climate`、
`media_player`（开关）、`cover`（turnOn→open_cover / turnOff→close_cover）、
`sensor`（仅温度/湿度类，按 `device_class` + 单位判断，电池等不会误报）。

### 如何新增一个设备域

在 `dueros/adapters.py` 中：

```python
@register
class LockAdapter(_PowerDeviceAdapter):
    domain = "lock"
    appliance_type = APPLIANCE_LOCK   # 在 constants.py 补充
    actions = (ACTION_TURN_ON, ACTION_TURN_OFF)  # 或自定义动作

    def service_call(self, state, action, payload):
        if action == ACTION_TURN_ON:
            return ("lock", "lock", {})
        if action == ACTION_TURN_OFF:
            return ("lock", "unlock", {})
        return None
```

### 本地调试

```bash
# 纯逻辑测试（无需 HA 运行时）
pytest tests/test_dueros_protocol.py
```

### 端到端调试（HAOS 已部署后）

```bash
# 1) 构造发现请求（token 用当前有效的 access token）
curl -sk -X POST https://ha.example.com:8663/api/xiaodu \
  -H 'Content-Type: application/json' \
  -d '{"header":{"namespace":"DuerOS.ConnectedHome.Discovery","name":"DiscoverAppliancesRequest","messageId":"dbg-1","payloadVersion":"1"},"payload":{"accessToken":"<ACCESS_TOKEN>"}}'

# 2) 控制（例如开灯）
curl -sk -X POST https://ha.example.com:8663/api/xiaodu \
  -H 'Content-Type: application/json' \
  -d '{"header":{"namespace":"DuerOS.ConnectedHome.Control","name":"TurnOnRequest","messageId":"dbg-2","payloadVersion":"1"},"payload":{"accessToken":"<ACCESS_TOKEN>","appliance":{"applianceId":"light.living"}}}'

# 3) token 过期后用 refresh token 换新（client_id/client_secret 在集成配置里）
curl -sk -X POST https://ha.example.com:8663/api/xiaodu/oauth/token \
  -d 'grant_type=refresh_token&client_id=dueros_xxx&client_secret=<SECRET>&refresh_token=<REFRESH>'
```

小度开发者后台的「模拟测试 / 调试」会依次触发发现设备 → 查询 → 控制，
日志可在 HA 的 `ha core logs` 中按 `xiaodu` 过滤查看。

## 实体过滤

在集成条目的「选项」中可配置：

- **包含实体 / 排除实体（下拉选择）**：从 HA 现有实体中多选，直接加入规则。
- **包含通配符 / 排除通配符（手动输入）**：输入 `fnmatch` 模式，例如
  `light.*`、`switch.bedroom_*`，每行一个（也支持逗号分隔）。
- 下拉选中项与手动模式会合并保存；全部留空 = 暴露所有实体；排除优先于包含，
  模式匹配完整实体 ID。

## OAuth 授权（阶段 2）

首次添加集成时按提示创建百度开放平台凭据：

1. 在[百度开发者控制台](https://dueros.baidu.com/)创建应用，得到
   API Key（Client ID）与 Secret Key（Client Secret）。
2. 回调地址（redirect URI）填写 `https://my.home-assistant.io/redirect/oauth`
   （HA 2026.8 默认使用「My Home Assistant」回调，授权完成后会转发到你的
   实例）。如果你的 HA 未加载 `my` 组件，则以授权时生成的回调地址为准。
3. 在 HA 中 Add Integration → **Xiaodu**，填入 Client ID / Client Secret，
   随后跳转百度完成授权，授权成功后自动创建集成条目。

token 过期后由 `OAuth2Session` 自动刷新；刷新失败时可从集成条目触发重新授权
（reauth）。

## 安装到 HAOS

把 `custom_components/xiaodu` 整个目录复制到 HAOS 的配置目录：

```text
/config/custom_components/xiaodu
```

常用方式（任选其一）：

- **Samba 共享**：在 HAOS 加载项中安装 Samba Share，然后从电脑访问
  `\\<HAOS-IP>\config`（Windows）或 `smb://<HAOS-IP>/config`（macOS/Linux），
  将文件夹放入 `custom_components/`。
- **SSH 加载项**：安装并启用 Advanced SSH & Web Terminal，执行：
  `scp -r custom_components/xiaodu root@<HAOS-IP>:/config/custom_components/`。
- **Studio Code Server 加载项**：直接在 `/config` 文件树中粘贴。

复制完成后重启 HA（Settings → System → Restart，或 SSH 中
`ha core restart`）。然后在
**Settings → Devices & Services → Add Integration** 中搜索 **Xiaodu**，
按提示添加即可（第一阶段无额外表单字段，直接确认）。

## 本地测试

纯逻辑测试无需 HA：

```bash
pip install pytest
pytest tests/test_entity_filter.py
```

完整测试需要 Home Assistant 测试环境（用于配置流与 setup/unload）：

```bash
pip install -e ".[test]"
pytest
```

## 查看访问日志

集成内置了 INFO 级访问日志，每条小度与 HA 的交互记录一行（含 token 端点与
WebService 端点），通过 `ha core logs` 查看：

```bash
# 实时跟随小度的请求
ha core logs -f | grep "Xiaodu access"

# 最近 200 条
ha core logs -n 200 | grep "Xiaodu access"
```

日志字段：`kind`（dueros / token）、`messageId`、`namespace`、`name`（动作）、
`entity`（目标实体）、`result`（响应名或错误码）、`status`（HTTP 状态）、
`ms`（耗时）、`ip`（来源）、`xff`（转发来源）。

示例（成功发现）：

```text
INFO [custom_components.xiaodu.oauth_server]
Xiaodu access: kind=dueros messageId=... namespace=DuerOS.ConnectedHome.Discovery
name=DiscoverAppliancesRequest result=DiscoverAppliancesResponse status=200 ms=2.1 ip=...
```

需要在 `configuration.yaml` 中放开该组件的日志级别（已配置）：

```yaml
logger:
  default: warning
  logs:
    custom_components.xiaodu: info
```

想看到更细的请求分发日志（namespace/name 的 DEBUG 行），把 `info` 改为
`debug` 后重启即可；不需要时删掉这段 `logger:` 配置即可恢复默认。

## 部署后调试清单

1. 确认文件已就位：HAOS 上 `/config/custom_components/xiaodu/manifest.json`
   存在，且目录权限可读。
2. 重启后查看日志（Settings → System → Logs，或
   `/config/home-assistant.log`），确认没有 `xiaodu` 相关报错。
3. 在 Add Integration 中搜索「Xiaodu」并添加；成功后该集成会出现在
   Devices & Services 列表中。
4. 若搜索不到，检查 manifest 是否为合法 JSON，以及是否完成了 HA 重启。

> 部署到 HAOS 前请把 `manifest.json` 中的 `codeowners`、`documentation`、
> `issue_tracker` 占位链接替换为你的真实信息。
