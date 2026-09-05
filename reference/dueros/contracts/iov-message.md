# iov-message（契约速查）


> 由 `make_contracts.py` 生成；原文：`../dbp-smart-home-protocol/iov-message.md`

## 分组：DiscoverAppliancesRequest

### DiscoverAppliancesRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Discovery`
- 额外 Payload：
  - `openUid` — 被授权的百度账号开放ID，与设备云账号一一对应。  [必填]
- 原文：[iov-message.md#discoverappliancesrequest](iov-message.md#discoverappliancesrequest)

### DiscoverAppliancesResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Discovery`
- 额外 Payload：
  - `discoveredGroups` — 与用户设备帐户相关联的分组对象的数组。如果没有发现与用户帐户关联的分组，返回空数组。如果在发生分组过程中出现错误，则返回null。允许最大…  [必填]
  - `discoveredGroups.groupName` — 用来识别分组的名称，对应车的品牌名称，不应包含特殊字符或标点符号，长度不能超过20字符。  [必填]
  - `discoveredGroups.groupType` — 分组类型，默认类型为VEHICLE。  [必填]
  - `discoveredGroups.applianceIds` — 分组中包含设备ID的数组，要求设备ID必须是已经发现的设备的ID，否则会同步失败，每个分组设备ID数量不超过50。  [必填]
  - `discoveredGroups.groupNotes` — 分组备注信息，不能超过128个字符。  [必填]
  - `discoveredGroups.additionalGroupDetails` — 提供给技能使用的分组相关的附加信息的键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过2000字符。  [是，内容可以为空]
- 原文：[iov-message.md#discoverappliancesresponse](iov-message.md#discoverappliancesresponse)

### TurnOnRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#turnonrequest](iov-message.md#turnonrequest)

### TurnOnConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#turnonconfirmation](iov-message.md#turnonconfirmation)

### TurnOffRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#turnoffrequest](iov-message.md#turnoffrequest)

### TurnOffConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#turnoffconfirmation](iov-message.md#turnoffconfirmation)

### IncrementTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
  - `deltaValue` — 设备温度调高信息。  [否，deltaValue为空表示用户没有指定温度调高的具体值]
  - `deltaValue.value` — 设备调高的温度值，是float类型。  [当deltaValue存在时，该项必须存在]
  - `deltaValue.scale` — 温度计量单位。有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [当deltaValue存在时，该项必须存在。]
- 原文：[iov-message.md#incrementtemperaturerequest](iov-message.md#incrementtemperaturerequest)

### IncrementTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `mode` — 设备温度变化后的设备模式。  [可选]
  - `temperature` — 设备温度变化后的设备温度，是double类型  [必填]
  - `previousState` — 设备温度变化前的设备状态。  [必填]
  - `previousState.mode` — 设备温度变化前的设备模式。  [可选]
  - `previousState.temperature` — 设备温度变化前的设备温度，是double类型。  [必填]
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#incrementtemperatureconfirmation](iov-message.md#incrementtemperatureconfirmation)

### DecrementTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
  - `deltaValue` — 设备温度调低信息。  [否， deltaValue为空表示用户没有指定温度调低的具体值。]
  - `deltaValue.value` — 设备温度调低的温度值，是float类型。  [当deltaValue存在时，该项必须存在。]
  - `deltaValue.scale` — 温度计量单位。有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [当deltaValue存在时，该项必须存在。]
- 原文：[iov-message.md#decrementtemperaturerequest](iov-message.md#decrementtemperaturerequest)

### DecrementTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `mode` — 设备温度变化后的设备模式。  [可选]
  - `temperature` — 设备温度变化后的设备温度，是double类型。  [必填]
  - `previousState` — 设备温度变化前的状态。  [必填]
  - `previousState.mode` — 设备温度变化前的设备模式。  [可选]
  - `previousState.temperature` — 设备温度变化前的设备温度，是double类型。  [必填]
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#decrementtemperatureconfirmation](iov-message.md#decrementtemperatureconfirmation)

### SetTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
  - `targetTemperature` — 设备设定的目标温度。  [必填]
  - `targetTemperature.value` — 设备设定的目标温度值。  [必填]
  - `targetTemperature.scale` — 温度计量单位。有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [必填]
- 原文：[iov-message.md#settemperaturerequest](iov-message.md#settemperaturerequest)

### SetTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `mode` — 温度设置成功后的设备模式。  [可选]
  - `temperature` — 温度设置成功后的设备温度，是double类型。  [必填]
  - `previousState` — 温度设置成功前的设备状态。  [必填]
  - `previousState.mode` — 温度设置成功前的设备模式。  [可选]
  - `previousState.temperature` — 温度设置成功前的设备温度，是double类型。  [必填]
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#settemperatureconfirmation](iov-message.md#settemperatureconfirmation)

### HeatRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#heatrequest](iov-message.md#heatrequest)

### HeatConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#heatconfirmation](iov-message.md#heatconfirmation)

### CancelHeatRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#cancelheatrequest](iov-message.md#cancelheatrequest)

### CancelHeatConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#cancelheatconfirmation](iov-message.md#cancelheatconfirmation)

### ChargeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#chargerequest](iov-message.md#chargerequest)

### ChargeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#chargeconfirmation](iov-message.md#chargeconfirmation)

### DischargeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#dischargerequest](iov-message.md#dischargerequest)

### DischargeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[iov-message.md#dischargeconfirmation](iov-message.md#dischargeconfirmation)

### GetTurnOnStateRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#getturnonstaterequest](iov-message.md#getturnonstaterequest)

### GetTurnOnStateResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `turnOn` — 设备打开状态信息。  [必填]
  - `turnOn.value` — 设备打开状态取值，是bool类型。  [必填]
  - `applianceResponseTimestamp` — 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是…  [可选]
- 原文：[iov-message.md#getturnonstateresponse](iov-message.md#getturnonstateresponse)

### GetTemperatureReadingRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#gettemperaturereadingrequest](iov-message.md#gettemperaturereadingrequest)

### GetTemperatureReadingResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `mode` — 设备设置的模式。  [必填]
  - `temperatureReading` — 设备温度信息。  [必填]
  - `temperatureReading.value` — 温度值，是float类型。  [必填]
  - `temperatureReading.scale` — 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [可选]
  - `applianceResponseTimestamp` — 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是…  [可选]
- 原文：[iov-message.md#gettemperaturereadingresponse](iov-message.md#gettemperaturereadingresponse)

### GetTargetTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#gettargettemperaturerequest](iov-message.md#gettargettemperaturerequest)

### GetTargetTemperatureResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `mode` — 设备设置的模式。  [必填]
  - `targetTemperature` — 温度信息  [可选]
  - `targetTemperature.value` — 温度值，是float类型。  [必填]
  - `targetTemperature.scale` — 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [可选]
  - `coolingTargetTemperature` — 制冷温度信息，在制冷加热的双模式下使用，一般与heatingTargetTemperature同时出现。  [可选]
  - `coolingTargetTemperature.value` — 温度值，是float类型。  [必填]
  - `coolingTargetTemperature.scale` — 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [可选]
  - `heatingTargetTemperature` — 加热温度信息，在制冷加热可以同时开的双模式下使用，一般与coolingTargetTemperature同时出现。  [可选]
  - `heatingTargetTemperature.value` — 温度值，是float类型。  [必填]
  - `heatingTargetTemperature.scale` — 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [可选]
  - `temperatureMode` — 温控模式。  [必填]
  - `temperatureMode.value` — 温控模式。有以下七种模式： * COOL：制冷模式。 * HEAT：制热模式。 * AUTO：自动模式。 * FAN：送风模式。 * DE…  [必填]
  - `temperatureMode.friendlyName` — 模式名称。  [必填]
  - `applianceResponseTimestamp` — 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是…  [可选]
- 原文：[iov-message.md#gettargettemperatureresponse](iov-message.md#gettargettemperatureresponse)

### GetOilCapacityRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#getoilcapacityrequest](iov-message.md#getoilcapacityrequest)

### GetOilCapacityResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `oilCapacity` — 油量信息。  [必填]
  - `oilCapacity.value` — 油量值，是float类型。  [必填]
  - `oilCapacity.scale` — 油量计量单位L。  [必填]
  - `drivingDistance` — 可行驶距离信息。  [必填]
  - `drivingDistance.value` — 可行驶距离值，是float类型。  [必填]
  - `drivingDistance.scala` — 距离计量单位公里。  [必填]
  - `applianceResponseTimestamp` — 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是…  [可选]
- 原文：[iov-message.md#getoilcapacityresponse](iov-message.md#getoilcapacityresponse)

### GetElectricityCapacityRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `pinCode` — 控制密码，一般为4～8位有效数字。  [必填]
- 原文：[iov-message.md#getelectricitycapacityrequest](iov-message.md#getelectricitycapacityrequest)

### GetElectricityCapacityResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `electricityCapacity` — 电量信息。  [必填]
  - `electricityCapacity.value` — 电量值，字符串, 比如20%。  [必填]
  - `electricityCapacity.scale` — 电量计量单位度。  [是，内容可以为空。]
  - `drivingDistance` — 可行驶距离信息。  [必填]
  - `drivingDistance.value` — 可行驶距离值，是float类型。  [必填]
  - `drivingDistance.scala` — 距离计量单位公里。  [必填]
  - `applianceResponseTimestamp` — 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是…  [可选]
- 原文：[iov-message.md#getelectricitycapacityresponse](iov-message.md#getelectricitycapacityresponse)
