# Home Assistant Custom Integration: Xiaodu (DuerOS)

项目仓库：<https://github.com/Jackroyal/ha-xiaodu>

小度智能家居自定义集成（当前版本 **v0.7.7**）：让 Home Assistant 中的设备可以被
小度音箱 / 小度 App 发现、查询与控制。架构为「小度当 OAuth 客户端、本集成当授权
服务器」：集成通过 `/api/xiaodu`、`/api/xiaodu/service` 接收小度智能家居请求，
把 HA 实体映射为小度设备/能力，并签发仅限本集成的私有不透明 token（最小权限，
token 无法用于 HA API）。

> **v0.7.7 兼容性修复**：适配 HA 2026.8+ 设备注册表中 HomeKit 桥设备的三元组
> 标识符 `(domain, object_id, key)`，避免 `_sync_device_registry` 解包
> `device.identifiers` 时抛 `ValueError: too many values to unpack` 导致集成启动失败。

## 功能现状

- **配置流添加/重配**：Client_Id / ClientSecret / botId / 回调地址 / 公网地址均可
  配置，添加后集成会直接展示需要回填到小度开发者后台的三个 URL。
- **OAuth 授权服务器**（`oauth_server.py`）：`/api/xiaodu/oauth/authorize` 授权页
  复用 HA 登录流认证，`/api/xiaodu/oauth/token` 签发/刷新 token；access token
  有效期 7 天、refresh token 30 天，小度侧用 `grant_type=refresh_token` 换新。
- **DuerOS 协议**（`dueros/`）：Discovery / Query / Action 三层分发，兼容小度控制台
  「模拟测试」的 DCS multipart 报文与线上纯 JSON 报文。
- **能力模型**：配置层为「设备 → 单元 → 能力」三级；控制能力（power/brightness/
  colorTemperature/color/volume/channel/mute/fanSpeed/targetTemperature/mode/
  suction/pause …）与只读查询能力（temperature/humidity，跨实体聚合）分开管理。
- **多单元设备**：一台 HA 设备可暴露多个单元（如晾衣杆本体 + 晾衣杆灯），每个单元
  在小度侧是一个设备；指示灯、提示音、`*_is_on` 等辅助实体自动排除。
- **全量设备覆盖**：浴霸（官方 `YUBA` 类型，`setMode`/`unSetMode`）、插座
  （`SOCKET`）、扫地机（含 `continue`）、灯、开关、风扇、空调、窗帘、媒体播放器、
  温湿度计等均按小度官方协议类型暴露。
- **定时开关**：支持小度定时（`timingTurnOn`/`timingTurnOff`），用 HA 自身的
  `async_track_point_in_utc_time` 调度 + HA Storage 持久化，HA 重启后自动重新布防。
- **区域同步（可选）**：`sync_areas` 开启后，发现时把 HA 区域（房间）同步为小度
  `discoveredGroups`（分组名 ≤20 字符、去标点）。
- **设备变更推送**：配置 botId 后，暴露设备变化时主动调用小度 devicesync 通知重新
  发现（`dueros_sync.py`），并支持实体状态变更上报（`state_report.py`）。
- **设备与服务页直达**：已同步设备会注册到集成条目名下（条目标题显示为
  「小度中枢」），在 **Settings → 设备与服务 → 小度中枢** 展开即可看到平铺的同步
  设备列表（带房间信息），无需进入选项流程即可总览；设备行三点菜单提供
  「单元与能力」单设备编辑入口（由前端模块注入核心组件菜单实现，非官方扩展口，
  详见 `www/` 文件头注释；若失效仍可通过「设备与能力」选项流程编辑）与官方
  「移除设备」（取消该设备同步，走 HA 官方 `async_remove_config_entry_device`
  钩子）、“禁用设备”项。

## 目录结构

```text
.
├── custom_components/ha_xiaodu/
│   ├── __init__.py            # 集成入口：setup / unload / 设备注册 / WS 命令
│   ├── config_flow.py         # 配置流 + 选项流（设备/单元/能力）
│   ├── const.py               # 常量与配置键（含旧配置迁移键）
│   ├── devices.py             # 设备映射：按 device_id 归组实体、选主实体、派生能力集
│   ├── entity_filter.py       # 旧版实体 include/exclude（读取时自动迁移）
│   ├── oauth_server.py        # OAuth2 授权/Token 端点 + DuerOS WebService 视图
│   ├── oauth_store.py         # 不透明 token 签发/持久化（最小权限）
│   ├── timers.py              # 小度定时开关调度（重启自动重新布防）
│   ├── dueros_sync.py         # 设备变更推送（devicesync）
│   ├── state_report.py        # 实体状态变更上报（change report）
│   ├── dueros/
│   │   ├── __init__.py        # 对外只暴露 handle_request
│   │   ├── constants.py       # 协议常量：namespace / 动作 / 错误码 / 设备类型
│   │   ├── adapters.py        # 域适配器注册表（每 HA 域一个适配器）
│   │   └── protocol.py        # 薄分发层：解析 header → 路由到适配器
│   ├── manifest.json
│   ├── strings.json           # 英文文案（UI 源）
│   └── translations/
│       └── zh-Hans.json       # 简体中文文案
│   └── www/
│       └── ha-xiaodu-device-config.js  # 设备行「单元与能力」菜单注入模块
├── tests/                     # 纯逻辑测试 + HA 测试环境测试
├── work/                      # 部署辅助脚本 / SSH 密钥（已 gitignore，不入库）
├── outputs/                   # 打包产物与部署记录（已 gitignore）
├── pyproject.toml
└── README.md
```

## 依赖组件与环境配置（HAOS 部署）

部署链路：

```text
公网 → 路由器（DDNS + 端口转发 443）
     → HAOS nginx add-on（TLS 443 终结，反代）
     → HA Core（server_port 8123，trusted proxy）
     → 小度集成端点 /api/xiaodu(/oauth/*, /service)
```

以下配置以通用示例（HAOS `192.168.1.10`、域名 `ha.example.com`）为例；
换成你自己的域名/IP/网段即可。

### 基础环境

| 组件 | 版本/值 | 说明 |
|---|---|---|
| HAOS | — | 本集成部署目标（示例 192.168.1.10） |
| Home Assistant Core | 2026.8.1 | manifest 要求 ≥ 2025.1.0 |
| 域名 | `ha.example.com` | Cloudflare DNS A 记录指向公网 IP |
| 路由器 | 华硕 ASUSWRT（192.168.1.1） | 端口转发 + DDNS |

### Add-on（HAOS 应用）

**NGINX Home Assistant SSL proxy**（`core_nginx_proxy`，4.5.1）— 公网 HTTPS 入口：

```yaml
domain: ha.example.com
certfile: fullchain.pem
keyfile: privkey.pem
hsts: max-age=31536000; includeSubDomains
client_max_body_size_megabytes: 1
cloudflare: false
customize:
  active: true
  default: nginx_proxy_default*.conf
  servers: nginx_proxy/*.conf
```

证书文件放在 `/ssl/`（由 Let's Encrypt add-on 生成），nginx 只读
`/ssl/fullchain.pem` 与 `/ssl/privkey.pem`。`customize.active = true` 后，add-on
会把 `/share/` 下匹配 `nginx_proxy_default*.conf` 的文件 include 进默认 443
server 块。本项目在 `/share/nginx_proxy_default_deny.conf` 里默认封禁所有路径、
仅放行小度需要的端点（OAuth + WebService），其余路径公网一律 404，内网不受影响：

```nginx
# /share/nginx_proxy_default_deny.conf（nginx add-on customize.default）
# 后端固定为 homeassistant.local.hass.io:<core port>，core port 为 8123

# 放行 OAuth 授权相关路径（authorize / token / 百度回调等均以 /auth/ 开头）
location ~ ^/auth/ {
    proxy_pass http://homeassistant.local.hass.io:8123;
    proxy_set_header Host $forward_host;
    proxy_set_header X-Forwarded-Host $forward_host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_redirect http:// https://;
    proxy_http_version 1.1;
}

# 放行小度集成端点（OAuth + WebService）
location ~ ^/api/xiaodu(/|$) {
    proxy_pass http://homeassistant.local.hass.io:8123;
    proxy_set_header Host $forward_host;
    proxy_set_header X-Forwarded-Host $forward_host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_redirect http:// https://;
    proxy_http_version 1.1;
}

# 默认：拒绝其余所有路径（404；想直接断开连接可改 return 444）
location ~ .* {
    return 404;
}
```

> 若 core port 不是 8123（例如 80），上面配置里的 `:8123` 与 HA 的
> `server_port` 要同步修改。

**Let's Encrypt**（`core_letsencrypt`，6.4.0）— 证书签发，DNS-01 校验：

```yaml
certfile: fullchain.pem
keyfile: privkey.pem
challenge: dns
dns:
  provider: dns-cloudflare
  cloudflare_api_token: <CLOUDFLARE_API_TOKEN>   # 不要提交到仓库
domains:
  - ha.example.com
email: <通知邮箱>
```

采用 DNS 校验（Cloudflare API token），**无需开放 80 端口**；证书输出到
`/ssl/`。token / 邮箱等凭据请勿写入任何版本控制文件。

**Terminal & SSH**（`core_ssh`）— 部署与排障入口：`scp` 上传集成、
`ha core logs` 查看日志。**File editor**（`core_configurator`）可选，用于界面编辑
`/config` 文件。**HACS**（或 Get HACS add-on）用于安装第三方自定义集成。

### 路由器配置（ASUSWRT）

浏览器打开 `http://192.168.1.1` → **WAN → 虚拟服务器/端口转发**：

- 外部 443（TCP）→ 内部 IP `192.168.1.10`，内部端口 `443`（与 external_url、
  证书完全一致，最干净）；
- 可选：外部 80（TCP）→ `192.168.1.10:80`（HTTP 访问/重定向）。

**WAN → DDNS**：公网 IP 固定则无需动作；动态 IP 需保证 A 记录
`ha.example.com → 公网 IP` 及时更新（华硕自带 DDNS 仅支持 asuscomm.com，
Cloudflare 可用自定义 DDNS 或单独脚本）。若改用其他域名，nginx 的 `domain`、
证书与 HA 的 `external_url` 需同步更换。

### HA 核心配置

`/config/configuration.yaml`：

```yaml
# Loads default set of integrations. Do not remove.
default_config:

frontend:
  themes: !include_dir_merge_named themes

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

logger:
  default: warning
  logs:
    custom_components.ha_xiaodu: info   # 需要分发细节时改为 debug
```

**http 配置**（HA 2026.8 起存储在 `/config/.storage/http`，`configuration.yaml`
里的 `http:` 块会被忽略；修改走 WebSocket `http/config/configure` +
`http/config/promote`）：

```json
{
  "server_port": 8123,
  "use_x_forwarded_for": true,
  "trusted_proxies": ["172.30.32.0/23"],
  "cors_allowed_origins": ["https://cast.home-assistant.io"],
  "login_attempts_threshold": -1,
  "ip_ban_enabled": true,
  "use_x_frame_options": true,
  "ssl_profile": "modern"
}
```

`external_url = https://ha.example.com`（Settings → System → Network，或
`config/core/update`）。

要点：

- `trusted_proxies` 必须覆盖 nginx add-on 所在 Docker 网段（示例
  `172.30.32.0/23`，以你的实际网段为准）；否则带 `X-Forwarded-For` 的反代请求
  会被 HA 直接拒绝（400，日志关键字 `homeassistant.components.http.forwarded`）。
- `server_port` 必须与 nginx 反代后端一致（8123）。
- 修改 http 配置会触发 HA 重启，固化前先确认 active 正常。

### 小米 Home（xiaomi_home）

米家官方 HA 集成（`XiaoMi/ha_xiaomi_home`，当前部署 v0.4.7），负责把米家设备
（Wi-Fi / BLE / 中枢网关等）接入 HA：

- **安装**：HACS（或手动复制到 `/config/custom_components/xiaomi_home`），
  依赖 `construct`、`paho-mqtt`、`numpy`、`cryptography`、`psutil`。
- **配置**：Settings → Devices & Services → Add Integration → **Xiaomi Home**，
  用小米账号登录（Mi Login），授权后设备自动出现在 HA 中。
- **与本集成的关系**：小度暴露的是 **HA 实体**，实体来源可以是 xiaomi_home
  （米家）、`midea_ac_lan`（美的）或任何其他集成；小米设备接入后，在小度集成
  的「选项」里勾选要暴露的设备/能力即可，二者之间没有额外桥接配置。

### 其他可选集成

- **HACS**：第三方集成管理（xiaomi_home、midea_ac_lan 等均通过它安装/升级）。
- **midea_ac_lan**：美的空调局域网控制，提供 `climate` 域实体，小度侧按空调
  （`targetTemperature`/`mode`）暴露。

## 小度集成配置

### 添加集成时填写

在 **Settings → Devices & Services → Add Integration → Xiaodu** 中填写：

| 字段 | 含义 | 示例 |
|---|---|---|
| `client_id` | OAuth Client_Id（**由你自定义**，与小度后台一致） | `dueros_xxx` |
| `client_secret` | OAuth ClientSecret（由你自定义，随机字符串） | `<随机串>` |
| `bot_id` | 小度技能 ID（开发者后台「基础信息」页），用于设备变更推送 | `12345678` |
| `redirect_uri` | 回调地址（小度平台生成的 Callback URL） | `https://xiaodu.baidu.com/...` |
| `public_url` | 公网基础地址（与 external_url 一致） | `https://ha.example.com` |

确认页会展示需要回填到小度开发者后台技能配置的 URL：

```text
授权地址 Authorize URL:  https://<public_url>/api/xiaodu/oauth/authorize
Token 地址 Token URL:    https://<public_url>/api/xiaodu/oauth/token
WebService:              https://<public_url>/api/xiaodu/service
回调地址 Callback URL:    小度平台生成的那一个（即 redirect_uri）
```

客户端凭据由你自己定义（例如 `dueros_xxx` + 一串随机字符串），只要与小度后台
OAuth 配置里填的一致即可，不需要在百度开放平台单独创建应用。

### 选项流：中枢 → 平台 → 设备（单元/能力）

添加完成后在集成条目 → **设备与能力（选项）** 中配置，菜单结构为：

1. **中枢**（首层菜单）：展开平台列表 / 添加移除设备 / 保存并完成。
2. **平台列表**：当前为「小度（N 台设备）」；后续扩展天猫精灵等平台时与它并列。
3. **平台 → 设备列表**：已同步设备的平铺列表（行标签「房间 · 设备名」，标注
   （新增）/（已配置）），点击任意设备进入该设备的 **单元 → 能力** 编辑；
   「返回上一级」逐层返回。
4. **添加 / 移除设备**：多选列表（房间前缀便于筛选）；新设备默认同步其默认单元的
   全部能力，已保存的设备保留原设置。
5. **sync_areas（开关）**：把 HA 区域（房间）同步为小度 `discoveredGroups`。

每台设备可配置多个 **单元（unit）**（每个单元在小度侧是一个设备；默认单元保持
设备名，其余单元默认关闭）与 **能力（capabilities）**（`power` 强制开启；只读
能力如 temperature/humidity 可勾选；新单元默认全选）。

旧版「实体 include/exclude」选项会在读取时自动迁移为「设备 + 默认全能力」，
无需手动处理。

## DuerOS 协议

WebService 端点 `POST /api/xiaodu/service`（小度后台 WebService 字段填写
`https://<public_url>/api/xiaodu/service`）接收小度智能家居请求，按三层结构分发：

```text
配置层：设备 + 单元 + 能力勾选（power 强制）
        │
        ▼
devices.py  XiaoduDeviceMap   # 按 device_id 归组实体、选主实体、派生能力集
        │
        ▼
dueros/protocol.py            # 小度平台层：能力 → DuerOS 动作/属性翻译
```

新增音箱（天猫精灵/小爱等）只需新写平台翻译层，复用 `devices.py` 的能力模型。

```text
oauth_server.XiaoduDuerOSServiceView  # 薄视图：解析纯 JSON 或 DCS multipart，
                                      # 校验 payload.accessToken、按暴露配置过滤
        │
        ▼
dueros.protocol.handle_request      # 分发层：按 header.namespace 路由，
                                    # 拼装响应/错误信封
        │
        ▼
dueros.adapters.<Domain>Adapter     # 域适配器：设备类型 / 动作白名单 /
                                    # 属性 / 服务调用映射
```

架构要点：

- **适配器注册表**：每个 HA 域一个适配器类（`LightAdapter`、`SwitchAdapter`、
  `CoverAdapter`、`SensorAdapter` …），通过 `@register` 注册；新增设备类型 =
  新增一个适配器类 + 注册，不动分发层。
- **动作白名单**：每个适配器声明自己的 `actions`，控制请求只允许白名单内动作，
  任意 HA 服务从小度侧不可达（最小权限）。
- **协议常量集中**：namespace、错误码（`InvalidAccessTokenError` /
  `DriverInternalError` / `TargetOfflineError` / `NotSupportedInCurrentModeError`）、
  设备类型集中在 `dueros/constants.py`。
- **错误信封**：无效 token 返回 HTTP 401 `{"error":"ACCESS_TOKEN_INVALIDATE"}`
  （小度规范要求）；业务错误返回 HTTP 200 + `header.name` 为错误码 + 空 payload。
- **token 位置**：小度把 access token 放在 JSON 的 `payload.accessToken`，
  `Authorization: Bearer` 头保留作兼容回退。

当前支持的域：`light`（开关/亮度/颜色/色温）、`switch`、`fan`、`climate`、
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

## 本地调试

```bash
# 纯逻辑测试（无需 HA 运行时）
pytest tests/test_dueros_protocol.py
```

## 端到端调试（HAOS 已部署后）

```bash
# 1) 构造发现请求（token 用当前有效的 access token）
curl -sk -X POST https://ha.example.com/api/xiaodu \
  -H 'Content-Type: application/json' \
  -d '{"header":{"namespace":"DuerOS.ConnectedHome.Discovery","name":"DiscoverAppliancesRequest","messageId":"dbg-1","payloadVersion":"1"},"payload":{"accessToken":"<ACCESS_TOKEN>"}}'

# 2) 控制（例如开灯）
curl -sk -X POST https://ha.example.com/api/xiaodu \
  -H 'Content-Type: application/json' \
  -d '{"header":{"namespace":"DuerOS.ConnectedHome.Control","name":"TurnOnRequest","messageId":"dbg-2","payloadVersion":"1"},"payload":{"accessToken":"<ACCESS_TOKEN>","appliance":{"applianceId":"light.living"}}}'

# 3) token 过期后用 refresh token 换新（client_id/client_secret 在集成配置里）
curl -sk -X POST https://ha.example.com/api/xiaodu/oauth/token \
  -d 'grant_type=refresh_token&client_id=dueros_xxx&client_secret=<SECRET>&refresh_token=<REFRESH>'
```

公网入口若不是 443，URL 需带上端口，且与集成配置里的 `public_url` 保持一致。
小度开发者后台的「模拟测试 / 调试」会依次触发发现设备 → 查询 → 控制，日志可在
HA 的 `ha core logs` 中按 `xiaodu` 过滤查看。

## 安装到 HAOS

把 `custom_components/ha_xiaodu` 整个目录复制到 HAOS 的配置目录：

```text
/config/custom_components/ha_xiaodu
```

常用方式（任选其一）：

- **Terminal & SSH 加载项**（推荐）：`scp -r custom_components/ha_xiaodu root@<HAOS-IP>:/config/custom_components/`。
- **Samba Share**：从电脑访问 `\\<HAOS-IP>\config`（Windows）或
  `smb://<HAOS-IP>/config`（macOS/Linux），将文件夹放入 `custom_components/`。
- **File editor / Studio Code Server**：直接在 `/config` 文件树中粘贴。

复制完成后重启 HA（Settings → System → Restart，或 SSH 中
`ha core restart`），然后在 **Settings → Devices & Services → Add Integration**
中搜索 **Xiaodu**，按上文「小度集成配置」填写。

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

集成内置 INFO 级访问日志，每条小度与 HA 的交互记录一行（含 token 端点与
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
INFO [custom_components.ha_xiaodu.oauth_server]
Xiaodu access: kind=dueros messageId=... namespace=DuerOS.ConnectedHome.Discovery
name=DiscoverAppliancesRequest result=DiscoverAppliancesResponse status=200 ms=2.1 ip=...
```

日志级别在 `configuration.yaml` 中配置（见上文 HA 核心配置）；想看到更细的请求
分发日志（namespace/name 的 DEBUG 行），把 `custom_components.ha_xiaodu` 的级别
改为 `debug` 后重启即可。

## 部署后调试清单

1. 确认文件已就位：HAOS 上 `/config/custom_components/ha_xiaodu/manifest.json`
   存在，且目录权限可读。
2. 重启后查看日志（Settings → System → Logs，或 `/config/home-assistant.log`），
   确认没有 `xiaodu` 相关报错。
3. 在 Add Integration 中搜索「Xiaodu」并添加；成功后该集成会出现在
   Devices & Services 列表中。
4. 若搜索不到，检查 manifest 是否为合法 JSON，以及是否完成了 HA 重启。
5. 公网回调不通时，依次检查：路由器 443 转发、nginx add-on `domain` 与证书、
   HA `external_url`、`trusted_proxies` 网段、core port（80）是否一致。
6. 外网访问被 400 拒绝时，看日志关键字 `homeassistant.components.http.forwarded`，
   通常是把 `X-Forwarded-For` 来源网段加进 `trusted_proxies`。
