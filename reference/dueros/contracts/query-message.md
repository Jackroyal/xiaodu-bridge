# query-message（契约速查）


> 由 `make_contracts.py` 生成；原文：`../dbp-smart-home-protocol/query-message.md`

## 分组：GetAirQualityIndexRequest

### GetAirQualityIndexRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getairqualityindexrequest](query-message.md#getairqualityindexrequest)

### GetAirQualityIndexResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `AQI` — 空气质量。  [AQI和level必选其一]
  - `level` — 表示设备返回的空气质量等级描述 (优,良,差,轻度污染,中度污染,重度污染,严重污染)  [AQI和level必选其一]
- 原文：[query-message.md#getairqualityindexresponse](query-message.md#getairqualityindexresponse)

### GetAirPM25Request

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getairpm25request](query-message.md#getairpm25request)

### GetAirPM25Response

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `PM25` — 空气中PM2.5含量。  [必填]
  - `PM25.value` — 浮点型数值。  [必填]
  - `PM25.scale` — 单位微克每立方米（μg/m3）。  [必填]
- 原文：[query-message.md#getairpm25response](query-message.md#getairpm25response)

### GetAirPM10Request

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getairpm10request](query-message.md#getairpm10request)

### GetAirPM10Response

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `PM10` — 空气中PM10含量。  [必填]
  - `PM10.value` — 浮点型数值。  [必填]
  - `PM10.scale` — 单位微克每立方米（μg/m3）。  [必填]
- 原文：[query-message.md#getairpm10response](query-message.md#getairpm10response)

### GetCO2QuantityRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getco2quantityrequest](query-message.md#getco2quantityrequest)

### GetCO2QuantityResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `ppm` — 空气中CO2的浓度信息。  [必填]
  - `ppm.value` — 空气中CO2的浓度数值，float类型。  [必填]
- 原文：[query-message.md#getco2quantityresponse](query-message.md#getco2quantityresponse)

### GetHumidityRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#gethumidityrequest](query-message.md#gethumidityrequest)

### GetHumidityResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息。  [必填]
- 原文：[query-message.md#gethumidityresponse](query-message.md#gethumidityresponse)

### GetTargetHumidityRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#gettargethumidityrequest](query-message.md#gettargethumidityrequest)

### GetTargetHumidityResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息。  [必填]
- 原文：[query-message.md#gettargethumidityresponse](query-message.md#gettargethumidityresponse)

### GetTemperatureReadingRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `compartment` — 当设备有不同的温度分区，需要根据分区进行温度查询。支持以下分区。 * freezer：冷冻室分区 * refrigerator：冷藏室分区…  [可选]
- 原文：[query-message.md#gettemperaturereadingrequest](query-message.md#gettemperaturereadingrequest)

### GetTemperatureReadingResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `mode` — 设备设置的模式。  [必填]
  - `temperatureReading` — 设备温度信息。  [必填]
  - `temperatureReading.value` — 温度值，是float类型。  [必填]
  - `temperatureReading.scale` — 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [可选]
  - `applianceResponseTimestamp` — 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是…  [可选]
  - `compartment` — 当设备有不同的温度分区时，需要根据分区进行温度查询。支持以下分区。 * freezer：冷冻室分区 * refrigerator：冷藏室分…  [可选]
- 原文：[query-message.md#gettemperaturereadingresponse](query-message.md#gettemperaturereadingresponse)

### GetTargetTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `compartment` — 当查询的设备有温度分区时，按温度分区查询。例如冰箱，分为 * 冷冻室：freezer * 冷藏室：refrigerator * 变温室：v…  [可选]
- 原文：[query-message.md#gettargettemperaturerequest](query-message.md#gettargettemperaturerequest)

### GetTargetTemperatureResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `mode` — 设备设置的模式。  [必填]
  - `targetTemperature` — 温度信息  [可选]
  - `targetTemperature.value` — 温度值，是浮点类型。  [必填]
  - `targetTemperature.scale` — 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [可选]
  - `coolingTargetTemperature` — 制冷温度信息，在制冷加热的双模式下使用，一般与heatingTargetTemperature同时出现。  [可选]
  - `coolingTargetTemperature.value` — 温度值，是float类型。  [必填]
  - `coolingTargetTemperature.scale` — 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [可选]
  - `coolingTargetTemperature` — 加热温度信息，在制冷加热可以同时开的双模式下使用，一般与coolingTargetTemperature同时出现。  [可选]
  - `heatingTargetTemperature.value` — 温度值，是浮点类型。  [必填]
  - `heatingTargetTemperature.scale` — 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。  [可选]
  - `temperatureMode` — 温控模式。  [必填]
  - `temperatureMode.value` — 温控模式。有以下七种模式： * COOL：制冷模式。 * HEAT：制热模式。 * AUTO：自动模式。 * FAN：送风模式。 * DE…  [必填]
  - `temperatureMode.friendlyName` — 模式名称。  [必填]
  - `applianceResponseTimestamp` — 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是…  [可选]
  - `compartment` — 当查询的设备有温度分区时，按温度分区查询。例如冰箱，分为 * 冷冻室：freezer * 冷藏室：refrigerator * 变温室：v…  [可选]
- 原文：[query-message.md#gettargettemperatureresponse](query-message.md#gettargettemperatureresponse)

### GetRunningTimeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getrunningtimerequest](query-message.md#getrunningtimerequest)

### GetRunningTimeResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `totalTimeInSeconds` — 设备总体运行时间信息。  [必填]
  - `totalTimeInSeconds.value` — 设备总体运行时间值，int类型，单位是秒。  [必填]
- 原文：[query-message.md#getrunningtimeresponse](query-message.md#getrunningtimeresponse)

### GetTimeLeftRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#gettimeleftrequest](query-message.md#gettimeleftrequest)

### GetTimeLeftResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `timeLeftInSeconds` — 设备剩余运行时间信息。  [必填]
  - `timeLeftInSeconds.value` — 设备剩余运行时间值，int类型，单位是秒。  [必填]
- 原文：[query-message.md#gettimeleftresponse](query-message.md#gettimeleftresponse)

### GetRunningStatusRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getrunningstatusrequest](query-message.md#getrunningstatusrequest)

### GetRunningStatusResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `runningState` — 设备当前运行状态对象信息。  [必填]
  - `runningState.value` — 设备当前运行状态值。 洗衣机支持以下状态。 * weighing：称重 * washing：洗涤 * rinsing：漂洗 * dehyd…  [必填]
- 原文：[query-message.md#getrunningstatusresponse](query-message.md#getrunningstatusresponse)

### GetStateRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getstaterequest](query-message.md#getstaterequest)

### GetStateResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息，最多支持上报10个属性。  [必填]
  - `attribute.name` — 属性名称，这里取"state"。  [必填]
  - `attribute.value` — 字符串，目前支持的属性值如下: * CLEANING：清扫中 * CHARGING：充电中 * RECHARGING：回充中 * SLEE…  [必填]
  - `attribute.scale` — 属性值的单位名称，这里是空串''。  [必填]
  - `attribute.timestampOfSample` — 属性值取样的时间戳，单位是秒。  [必填]
  - `attribute.uncertaintyInMilliseconds` — 属性值取样的时间误差，单位是ms。  [必填]
- 原文：[query-message.md#getstateresponse](query-message.md#getstateresponse)

### GetLocationRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getlocationrequest](query-message.md#getlocationrequest)

### GetLocationResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息，最多支持上报10个属性。  [必填]
  - `attribute.name` — 属性名称，这里取"location"。  [必填]
  - `attribute.value` — 字符串，目前支持的属性值如下: * MASTER_BEDROOM：主卧 * SECOND_BEDROOM：次卧 * LIVING_ROOM…  [必填]
  - `attribute.scale` — 属性值的单位名称，这里是空串''。  [必填]
  - `attribute.timestampOfSample` — 属性值取样的时间戳，单位是秒。  [必填]
  - `attribute.uncertaintyInMilliseconds` — 属性值取样的时间误差，单位是ms。  [必填]
- 原文：[query-message.md#getlocationresponse](query-message.md#getlocationresponse)

### GetElectricityCapacityRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getelectricitycapacityrequest](query-message.md#getelectricitycapacityrequest)

### GetElectricityCapacityResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息，最多支持上报10个属性。  [必填]
  - `attribute.name` — 属性名称，这里取"electricityCapacity"。  [必填]
  - `attribute.value` — 浮点数。  [必填]
  - `attribute.scale` — 属性值的单位名称，这里是%。  [必填]
  - `attribute.timestampOfSample` — 属性值取样的时间戳，单位是秒。  [必填]
  - `attribute.uncertaintyInMilliseconds` — 属性值取样的时间误差，单位是ms。  [必填]
- 原文：[query-message.md#getelectricitycapacityresponse](query-message.md#getelectricitycapacityresponse)

### GetWaterQualityRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getwaterqualityrequest](query-message.md#getwaterqualityrequest)

### GetWaterQualityResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `ppm` — 水中含有各种污染物质的质量。  [必填]
  - `ppm.value` — 浮点型。  [必填]
  - `ppm.scale` — 单位名称，毫克每升或微克每升（ mg/L、ug/L）。  [必填]
- 原文：[query-message.md#getwaterqualityresponse](query-message.md#getwaterqualityresponse)

### GetFanSpeedRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getfanspeedrequest](query-message.md#getfanspeedrequest)

### GetFanSpeedResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息。  [必填]
  - `attribute.name` — 属性名称，取固定值"fanSpeed"。  [必填]
  - `attribute.value` — 属性值，整数或者string类型。  [必填]
  - `attribute.scale` — 属性值的单位，可以填空，单位默认为“档”。  [必填]
  - `attribute.timestampOfSample` — 属性值取样的时间戳，单位是秒。  [必填]
  - `attribute.uncertaintyInMilliseconds` — 属性值取样的时间误差，单位是ms。  [必填]
  - `attribute.legalValue` — 属性值取值的合法范围。  [必填]
- 原文：[query-message.md#getfanspeedresponse](query-message.md#getfanspeedresponse)

### GetSpeedRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `speed` — 速度信息。  [必填]
  - `speed.value` — 速度属性。current:当前, max:最大, min: 最小。  [必填]
- 原文：[query-message.md#getspeedrequest](query-message.md#getspeedrequest)

### GetSpeedResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息。  [必填]
  - `attribute.name` — 属性名称，speed: 当前速度， maxSpeed: 最大速度， minSpeed: 最小速度。  [必填]
  - `attribute.value` — 属性值，整数或者string类型。  [必填]
  - `attribute.scale` — 属性值的单位，可以填空，当attribute.value为数值时，单位默认为（KM/H）目前支持的属性值如下: * KM/H：千米每小时 …  [必填]
  - `attribute.timestampOfSample` — 属性值取样的时间戳，单位是秒。  [必填]
  - `attribute.uncertaintyInMilliseconds` — 属性值取样的时间误差，单位是ms。  [必填]
  - `attribute.legalValue` — 属性值取值的合法范围。  [必填]
- 原文：[query-message.md#getspeedresponse](query-message.md#getspeedresponse)

### GetMotionInfoRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `motionInfo` — 运动信息。  [必填]
  - `motionInfo.type` — 运动信息的类型。run:跑, walk: 走, consume: 消耗。  [必填]
  - `motionInfo.metric` — 运动信息的单位。howLong:时间, howFar: 距离, steps: 步长， calories： 卡路里。  [必填]
  - `motionInfo.when` — 运动信息的时间。today:今天, yesterday:昨天, theMonment:现在, theWeek:这周, theMonth:这…  [必填]
- 原文：[query-message.md#getmotioninforequest](query-message.md#getmotioninforequest)

### GetMotionInfoResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息。  [必填]
  - `attribute.name` — 属性名称，取固定值"motionInfo"。  [必填]
  - `attribute.value` — 属性值，整数或者string类型。  [必填]
  - `attribute.scale` — 属性值的单位，可以填空，单位默认为(KM)。目前支持的属性值如下: * KILOMETER：千米 * KM：千米 * METER：米 * …  [必填]
  - `attribute.timestampOfSample` — 属性值取样的时间戳，单位是秒。  [必填]
  - `attribute.uncertaintyInMilliseconds` — 属性值取样的时间误差，单位是ms。  [必填]
  - `attribute.legalValue` — 属性值取值的合法范围。  [必填]
- 原文：[query-message.md#getmotioninforesponse](query-message.md#getmotioninforesponse)

### GetTurnOnStateRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[query-message.md#getturnonstaterequest](query-message.md#getturnonstaterequest)

### GetTurnOnStateResponse

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Query`
- 额外 Payload：
  - `attributes` — 设备的属性信息，最多支持上报10个属性。  [必填]
  - `attribute.name` — 属性名称，这里取"turnOnState"。  [必填]
  - `attribute.value` — 字符串，目前支持的属性值如下: * ON：打开 * OFF：关闭 。  [必填]
  - `attribute.scale` — 属性值的单位名称，这里是空串''。  [必填]
  - `attribute.timestampOfSample` — 属性值取样的时间戳，单位是秒。  [必填]
  - `attribute.uncertaintyInMilliseconds` — 属性值取样的时间误差，单位是ms。  [必填]
- 原文：[query-message.md#getturnonstateresponse](query-message.md#getturnonstateresponse)
