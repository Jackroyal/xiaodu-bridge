# discovery-message（契约速查）


> 由 `make_contracts.py` 生成；原文：`../dbp-smart-home-protocol/discovery-message.md`

## 分组：DiscoverAppliancesRequest

### DiscoverAppliancesRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Discovery`
- 额外 Payload：
  - `openUid` — 被授权的百度账号开放ID，与设备云账号一一对应。设备云端需要将该字段与用户账号一一对应起来存储，主要用于后续的设备[状态同步](notif…  [必填]
- 原文：[discovery-message.md#discoverappliancesrequest](discovery-message.md#discoverappliancesrequest)

### DiscoverAppliancesResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Discovery`
- 额外 Payload：
  - `discoveredGroups` — discoveredGroups 对象的数组，该对象包含可发现分组，与用户设备帐户相关联的。 如果没有与用户帐户关联的分组，此属性应包含一…  [必填]
  - `discoveredGroups.groupName` — 用户用来识别分组的名称, 不应包含特殊字符或标点符号，长度不超过20字符。  [必填]
  - `discoveredGroups.applianceIds` — 分组所包含设备ID的数组，要求设备ID必须是已经发现的设备中的ID，否则会同步失败，每个分组设备ID数量不超过50。  [必填]
  - `discoveredGroups.groupNotes` — 分组备注信息，不能超过128个字符。  [必填]
  - `discoveredGroups.additionalGroupDetails` — 提供给技能使用的分组相关的附加信息的键值对。该属性的内容不能超过2000字符。而且DuerOS也不了解或使用这些数据。  [是，但可以为空数组[]]
- 原文：[discovery-message.md#discoverappliancesresponse](discovery-message.md#discoverappliancesresponse)
