# attributes-report（契约速查）


> 由 `make_contracts.py` 生成；原文：`../dbp-smart-home-protocol/attributes-report.md`

## 分组：ReportStateRequest

### ReportStateRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `appliance.attributeName` — 查询的属性名称，字符串类型，支持数字、字母和下划线，长度不能超过128个字符。  [必填]
- 原文：[attributes-report.md#reportstaterequest](attributes-report.md#reportstaterequest)

### ReportStateResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息，最多支持上报10个属性。  [必填]
  - `attribute.name` — 属性名称，支持数字、字母和下划线，长度不能超过128个字符。  [必填]
  - `attribute.value` — 属性值，支持多种json类型。  [必填]
  - `attribute.scale` — 属性值的单位名称，支持数字、字母和下划线，长度不能超过128个字符。  [必填]
  - `attribute.timestampOfSample` — 属性值取样的时间戳，单位是秒。  [必填]
  - `attribute.uncertaintyInMilliseconds` — 属性值取样的时间误差，单位是ms。如果设备使用的是轮询时间间隔的取样方式，那么uncertaintyInMilliseconds就等于时间…  [必填]
- 原文：[attributes-report.md#reportstateresponse](attributes-report.md#reportstateresponse)
