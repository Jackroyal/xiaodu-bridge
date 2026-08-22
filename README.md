# Home Assistant Custom Integration: Xiaodu

项目仓库：<https://github.com/Jackroyal/ha-xiaodu>

小度智能家居自定义集成，让 Home Assistant 中的设备可以被小度音箱 / 小度 App 发现、查询与控制。

## 安装

### HACS

本项目按 HACS Custom Integration 规范组织。将仓库加入 HACS 的自定义仓库后，类别选择 **Integration**，即可安装。

安装后重启 Home Assistant，在 **设置 → 设备与服务 → 添加集成** 中搜索 **Xiaodu**。

> 正式提交 HACS Default 后，用户无需再手动添加自定义仓库。

### 手动安装

将仓库中的 `custom_components/ha_xiaodu` 目录复制到 Home Assistant 的 `config/custom_components/` 下，然后重启 Home Assistant。

## 配置

集成提供：

- Client_Id / ClientSecret / botId / 回调地址 / 公网地址配置流。
- OAuth 授权服务器：`/api/xiaodu/oauth/authorize` 与 `/api/xiaodu/oauth/token`。
- DuerOS WebService：`/api/xiaodu/service`。
- Discovery / Query / Action / ReportState 等智能家居协议处理。
- 「设备 → 单元 → 能力」三级设备暴露配置，可手动选择同步设备、单元和能力。
- 小度设备变更主动同步及状态变化上报。
- 小度定时开关与 HA Storage 持久化。
- 可选的 HA 区域同步到小度。

## 公网 HTTPS

小度平台需要从公网访问集成端点。推荐使用自己的域名和有效 HTTPS 证书，并将公网 HTTPS 请求反向代理到 Home Assistant。

典型链路：

```text
小度平台
   ↓ HTTPS
公网域名
   ↓
路由器 / NGINX / 其他反向代理
   ↓
Home Assistant :8123
   ↓
/api/xiaodu/*
```

不要把 ClientSecret、OAuth token、HA 长期访问令牌等敏感信息提交到 Git 仓库。

## 开发

项目包含 pytest 测试以及 Home Assistant 自定义组件测试依赖。仓库启用了：

- Home Assistant Hassfest 校验
- HACS integration 校验

本地测试：

```bash
python -m pytest
```

## 目录结构

```text
custom_components/ha_xiaodu/
├── __init__.py
├── config_flow.py
├── const.py
├── devices.py
├── entity_filter.py
├── oauth_server.py
├── oauth_store.py
├── timers.py
├── dueros_sync.py
├── state_report.py
├── dueros/
├── translations/
├── strings.json
├── manifest.json
└── www/

tests/
pyproject.toml
hacs.json
```

## 版本

当前版本：**v0.7.9**。

## License

License information will be added before publication to HACS Default.
