# error-message（契约速查）


> 由 `make_contracts.py` 生成；原文：`../dbp-smart-home-protocol/error-message.md`

## 分组：ValueOutOfRangeError

### ValueOutOfRangeError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `minimumValue` — 设备的允许设置参数的最小值，是64位双精度值类型。  [必填]
  - `maximumValue` — 设备的允许设置参数的最大值，是64位双精度值类型。  [必填]
- 原文：[error-message.md#valueoutofrangeerror](error-message.md#valueoutofrangeerror)

### TargetOfflineError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#targetofflineerror](error-message.md#targetofflineerror)

### BridgeOfflineError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#bridgeofflineerror](error-message.md#bridgeofflineerror)

### DriverInternalError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#driverinternalerror](error-message.md#driverinternalerror)

### DependentServiceUnavailableError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `dependentServiceName` — 技能依赖的其他模块服务名称，由数字、字母和空格组成，长度是256个字符。如果超过256个字符，后面的内容会被截断。  [必填]
- 原文：[error-message.md#dependentserviceunavailableerror](error-message.md#dependentserviceunavailableerror)

### TargetConnectivityUnstableError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#targetconnectivityunstableerror](error-message.md#targetconnectivityunstableerror)

### TargetBridgeConnectivityUnstableError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#targetbridgeconnectivityunstableerror](error-message.md#targetbridgeconnectivityunstableerror)

### TargetFirmwareOutdatedError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `minimumFirmwareVersion` — 支持的最低的固件版本，版本长度不超过256个字符。  [必填]
  - `currentFirmwareVersion` — 当前固件版本，版本长度不超过256个字符。  [必填]
- 原文：[error-message.md#targetfirmwareoutdatederror](error-message.md#targetfirmwareoutdatederror)

### TargetBridgeFirmwareOutdatedError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `minimumFirmwareVersion` — 支持的最低的固件版本，长度不超过256个字符。  [必填]
  - `currentFirmwareVersion` — 当前固件版本，长度不超过256个字符。  [必填]
- 原文：[error-message.md#targetbridgefirmwareoutdatederror](error-message.md#targetbridgefirmwareoutdatederror)

### TargetHardwareMalfunctionError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#targethardwaremalfunctionerror](error-message.md#targethardwaremalfunctionerror)

### TargetBridgeHardwareMalfunctionError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#targetbridgehardwaremalfunctionerror](error-message.md#targetbridgehardwaremalfunctionerror)

### UnableToGetValueError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `errorInfo` — 不能获取值时的错误信息。  [必填]
  - `errorInfo.code` — 错误代码。 * DEVICE_AJAR：由于设备没打开，无法获取指定的状态。 * DEVICE_BUSY：设备正忙。 * DEVICE_J…  [必填]
  - `errorInfo.Description` — 设备的错误信息描述。  [可选]
- 原文：[error-message.md#unabletogetvalueerror](error-message.md#unabletogetvalueerror)

### UnableToSetValueError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `errorInfo` — 不能设置时的错误信息。  [必填]
  - `errorInfo.code` — 通用错误代码。 * DEVICE_AJAR：由于设备没打开，无法获取指定的状态。 * DEVICE_BUSY：设备正忙。 * DEVICE…  [必填]
  - `errorInfo.Description` — 设备的错误信息描述。  [可选]
- 原文：[error-message.md#unabletosetvalueerror](error-message.md#unabletosetvalueerror)

### UnwillingToSetValueError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `errorInfo` — 错误对象。  [必填]
  - `errorInfo.code` — 错误代码。 * ThermostatIsOff：由于恒温器关闭，制造商不愿自动将其启动，因此被请求的操作被拒绝。  [必填]
  - `errorInfo.Description` — 设备的错误信息描述。  [可选]
- 原文：[error-message.md#unwillingtosetvalueerror](error-message.md#unwillingtosetvalueerror)

### RateLimitExceededError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `errorInfo` — 错误信息。  [必填]
  - `rateLimit` — 设备在指定的时间单位中接收的最大请求数，是int类型。  [必填]
  - `timeUnit` — 设备接收最大请求数rateLimit的时间单位，MINUTE，HOUR或DAY。  [必填]
- 原文：[error-message.md#ratelimitexceedederror](error-message.md#ratelimitexceedederror)

### NotSupportedInCurrentModeError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `errorInfo` — 错误相关信息。  [必填]
  - `currentDeviceMode` — 设备当前模式的字符串。有AUTO，AWAY，COLOR，COOL，HEAT和OTHER。  [必填]
- 原文：[error-message.md#notsupportedincurrentmodeerror](error-message.md#notsupportedincurrentmodeerror)

### ExpiredAccessTokenError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#expiredaccesstokenerror](error-message.md#expiredaccesstokenerror)

### InvalidAccessTokenError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#invalidaccesstokenerror](error-message.md#invalidaccesstokenerror)

### UnsupportedTargetError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#unsupportedtargeterror](error-message.md#unsupportedtargeterror)

### UnsupportedOperationError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#unsupportedoperationerror](error-message.md#unsupportedoperationerror)

### UnsupportedTargetSettingError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[error-message.md#unsupportedtargetsettingerror](error-message.md#unsupportedtargetsettingerror)

### UnexpectedInformationReceivedError

- 方向：技能 → DuerOS（错误）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `faultingParameter` — 请求消息中错误的属性。  [必填]
- 原文：[error-message.md#unexpectedinformationreceivederror](error-message.md#unexpectedinformationreceivederror)
