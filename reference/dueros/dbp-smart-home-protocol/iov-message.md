---
title: "车载类设备协议"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/iov-message_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 车载设备控制协议

车载设备控制协议是DuerOS与智能车载设备之间的通讯协议。通过这些协议您可以轻松的通过语音控制车载设备，与设备进行交互。车载协议使用HTTPS传输，协议采用JSON消息格式。

* [发现设备](#发现设备)
  + [DiscoverAppliancesRequest](#discoverappliancesrequest)
  + [DiscoverAppliancesResponse](#discoverappliancesresponse)
* [控制消息](#控制消息)
  + [打开关闭消息](#打开关闭消息)
    - [TurnOnRequest](#turnonrequest)
    - [TurnOnConfirmation](#turnonconfirmation)
    - [TurnOffRequest](#turnoffrequest)
    - [TurnOffConfirmation](#turnoffconfirmation)
  + [控制温度消息](#控制温度消息)
    - [IncrementTemperatureRequest](#incrementtemperaturerequest)
    - [IncrementTemperatureConfirmation](#incrementtemperatureconfirmation)
    - [DecrementTemperatureRequest](#decrementtemperaturerequest)
    - [DecrementTemperatureConfirmation](#decrementtemperatureconfirmation)
    - [SetTemperatureRequest](#settemperaturerequest)
    - [SetTemperatureConfirmation](#settemperatureconfirmation)
    - [HeatRequest](#heatrequest)
    - [HeatConfirmation](#heatconfirmation)
    - [CancelHeatRequest](#cancelheatrequest)
    - [CancelHeatConfirmation](#cancelheatconfirmation)
  + [控制电量消息](#控制电量消息)
    - [ChargeRequest](#chargerequest)
    - [ChargeConfirmation](#chargeconfirmation)
    - [DischargeRequest](#dischargerequest)
    - [DischargeConfirmation](#dischargeconfirmation)
* [查询消息](#查询消息)
  + [GetTurnOnStateRequest](#getturnonstaterequest)
  + [GetTurnOnStateResponse](#getturnonstateresponse)
  + [GetTemperatureReadingRequest](#gettemperaturereadingrequest)
  + [GetTemperatureReadingResponse](#gettemperaturereadingresponse)
  + [GetTargetTemperatureRequest](#gettargettemperaturerequest)
  + [GetTargetTemperatureResponse](#gettargettemperatureresponse)
  + [GetOilCapacityRequest](#getoilcapacityrequest)
  + [GetOilCapacityResponse](#getoilcapacityresponse)
  + [GetElectricityCapacityRequest](#getelectricitycapacityrequest)
  + [GetElectricityCapacityResponse](#getelectricitycapacityresponse)
* [错误消息](#错误消息)

## 发现设备

发现设备消息用于发现用户的车及车辆相关的车载设备，包含DiscoverAppliancesRequest和DiscoverAppliancesResponse两个指令。

### DiscoverAppliancesRequest

当用户查找设备或者当用户在小度之家技能商店启用技能并进行授权后，DuerOS向技能发送DiscoverAppliancesRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Discovery |
| name | DiscoverAppliancesRequest |

#### Payload信息

| 属性 | 描述 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| openUid | 被授权的百度账号开放ID，与设备云账号一一对应。 | 是 |

#### 应用举例

当用户说“小度小度，发现设备”，DuerOS收到用户请求后向技能发送DiscoverAppliancesRequest消息。消息示例如下。

```
{
    "header": { 
        "namespace": "DuerOS.ConnectedHome.Discovery",
        "name": "DiscoverAppliancesRequest",
        "messageId": "6d6d6e14-8aee-473e-8c24-0d31ff9c17a2",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "*OAuth Token here*",
        "openUid": "27a7d83c2d3cfbad5d387cd35f3ca17b"
    }
}
```

## DiscoverAppliancesResponse

当技能收到发现车载设备请求时，会通过DiscoverAppliancesResponse消息将发现的设备信息返回给DuerOS。

### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Discovery |
| name | DiscoverAppliancesResponse |

### Payload信息

#### 设备信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| discoveredAppliances | 客户关联设备云帐户的设备数组，允许接入的最大设备数量为300。当关联帐户下没有发现车载设备时，返回空数组。如果在发现设备过程中出现错误时，字段设置为null。 | 是 |
| discoveredAppliance.applianceTypes | 支持的车载设备类型。目前支持以下车载设备。  * VEHICLE_ENGINE：发动机类设备 * VEHICLE_LIGHT：车灯类设备 * VEHICLE_HORN：车喇叭类设备 * VEHICLE_ALARM：车载报警器类设备 * VEHICLE_AIR_CONDITION：车载空调类设备 * VEHICLE_DOOR：车门类设备 * VEHICLE_TRUNK：车后备箱类设备 * VEHICLE_TANK：油箱 * VEHICLE_BATTERY：车载电池类设备 * VEHICLE_WINDOW：车窗类设备 * VEHICLE_SKYLIGHT：天窗类设备 * VEHICLE_SEAT_HEATER：座椅加热器 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有车载设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母、数字和以下特殊字符：_ - = # ; : ? @ &。长度不能超过256个字符。 | 是 |
| discoveredAppliance.modelName | 设备型号名称，是字符串类型，长度不能超过128个字符。 | 是 |
| discoveredAppliance.version | 供应商提供的设备版本，是字符串类型，长度不能超过128个字符。 | 是 |
| discoveredAppliance.friendlyName | 用户用来识别车载设备的名称。 是字符串类型，不能包含特殊字符和标点符号，长度不能超过128个字符。 | 是 |
| discoveredAppliance.friendlyDescription | 车载设备相关的描述，描述内容需要提及设备厂商，使用场景及连接方式，长度不超过128个字符。 | 是 |
| discoveredAppliance.isReachable | 车载设备当前是否能够到达。  * true：设备在线可以被操控。 * false：设备不在线不能被操控。 | 是 |
| discoveredAppliance.actions | 车载设备支持的操作类型数组。合法的action包括：  * turnOn：打开 * turnOff：关闭 * heatTurnOn：加热 * heatTurnOff：停止加热 * chargeTurnOn：充电 * chargeTurnOff：停止充电 * incrementTemperature：升高温度 * decrementTemperature：降低温度 * setTemperature：设置温度 * getTemperatureReading：查询温度 * getTargetTemperature：查询目标温度 * getTurnOnState：查询设备打开状态 * getOilCapacity：查询油量信息 * getElectricityCapacity：查询电量信息 | 是 |
| discoveredAppliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| discoveredAppliance.manufacturerName | 设备厂商的名字。 | 是 |
| discoveredAppliance.attributes | 设备的属性信息。当设备没有属性信息时，协议中不需要传入该字段。每个设备允许同步的最大的属性数量是10。详细信息请参考[设备属性](attributes.md)及[设备属性上报](attributes-report.md)。 | 否，建议将设备属性上报给DuerOS，方便用户查询。 |
| discoveredAppliance.attribute.name | 属性名称，支持数字、字母和下划线，长度不能超过128个字符。 | 是 |
| discoveredAppliance.attribute.value | 属性值，支持多种json类型。 | 是 |
| discoveredAppliance.attribute.scale | 属性值的单位名称，支持数字、字母和下划线，长度不能超过128个字符。 | 是 |
| discoveredAppliance.attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| discoveredAppliance.attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。如果设备使用的是轮询时间间隔的取样方式，那么uncertaintyInMilliseconds就等于时间间隔。如温度传感器每1秒取样1次，那么uncertaintyInMilliseconds的值就是1000。 | 是 |

#### 分组信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| discoveredGroups | 与用户设备帐户相关联的分组对象的数组。如果没有发现与用户帐户关联的分组，返回空数组。如果在发生分组过程中出现错误，则返回null。允许最大的分组数量为10。 | 是 |
| discoveredGroups.groupName | 用来识别分组的名称，对应车的品牌名称，不应包含特殊字符或标点符号，长度不能超过20字符。 | 是 |
| discoveredGroups.groupType | 分组类型，默认类型为VEHICLE。 | 是 |
| discoveredGroups.applianceIds | 分组中包含设备ID的数组，要求设备ID必须是已经发现的设备的ID，否则会同步失败，每个分组设备ID数量不超过50。 | 是 |
| discoveredGroups.groupNotes | 分组备注信息，不能超过128个字符。 | 是 |
| discoveredGroups.additionalGroupDetails | 提供给技能使用的分组相关的附加信息的键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过2000字符。 | 是，内容可以为空 |

**说明：**

* 分组信息对应的是车品牌名称，一辆车对应一条分组记录。
* 分组信息字段applianceIds对应的设备id列表，必须是发现的车载设备id中的某一个。
* 如果没有发现车，分组信息和设备信息都为空。如果发现车但是没有发现车载设备，设备信息为空，分组信息不为空。

### 应用举例

当查找到车及对应车载设备时，技能向DuerOS发送DiscoverAppliancesResponse消息，消息示例如下。

```
{
　　"header": {
　　    "namespace": "DuerOS.ConnectedHome.Discovery",
　　    "name": "DiscoverAppliancesResponse",
　　    "messageId": "ff746d98-ab02-4c9e-9d0d-b44711658414",
　　    "payloadVersion": "1"
　　},
　　"payload": {
　　  　"discoveredAppliances": [
　　  　  　{
　　  　  　  　"actions": [
　　  　  　  　  　"turnOn",
　　  　  　  　  　"turnOff"
　　  　  　  　],
　　  　  　  　"applianceTypes": [
　　  　  　  　  　"VEHICLE_ENGINE"
　　  　  　  　],
　　  　  　  　"additionalApplianceDetails": {
　　  　  　  　  　"extraDetail1": "optionalDetailForSkillAdapterToReferenceThisDevice",
　　  　  　  　  　"extraDetail2": "There can be multiple entries",
　　  　  　  　  　"extraDetail3": "but they should only be used for reference purposes.",
　　  　  　  　  　"extraDetail4": "This is not a suitable place to maintain current device state"
　　  　  　  　},
　　  　  　  　"applianceId": "uniqueVehicleDeviceId",
　　  　  　  　"friendlyDescription": "展现给用户的详细介绍",
　　  　  　  　"friendlyName": "发动机",
　　  　  　  　"isReachable": "true",
　　  　  　  　"manufacturerName": "设备制造商的名称",
　　  　  　  　"modelName": "fancyVehicleEngine",
　　  　  　  　"version": "your software version number here.",
                "attributes": [
                    {
                        "name": "name",
            　　  　  　"value": "发动机",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 10
        　　  　  　}，
        　　  　  　{
            　　  　  　"name": "connectivity",
            　　  　  　"value": "UNREACHABLE",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 10
        　　  　  　}，
        　　  　  　{
            　　  　  　"name": "turnOnState",
            　　  　  　"value": "ON",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 0
        　　  　  　}
                ]
            },
　　  　  　{
　　  　  　  　"actions": [
　　  　  　  　  　"turnOn",
　　  　  　  　  　"turnOff"
　　  　  　  　],
　　  　  　  　"applianceTypes": [
　　  　  　  　  　"VEHICLE_LIGHT"
　　  　  　  　],
　　  　  　  　"additionalApplianceDetails": {
　　  　  　  　  　"extraDetail1": "optionalDetailForSkillAdapterToReferenceThisDevice",
　　  　  　  　  　"extraDetail2": "There can be multiple entries",
　　  　  　  　  　"extraDetail3": "but they should only be used for reference purposes.",
　　  　  　  　  　"extraDetail4": "This is not a suitable place to maintain current device state"
　　  　  　  　},
　　  　  　  　"applianceId": "uniqueVehicleDeviceId",
　　  　  　  　"friendlyDescription": "展现给用户的详细介绍",
　　  　  　  　"friendlyName": "车灯",
　　  　  　  　"isReachable": "true",
　　  　  　  　"manufacturerName": "设备制造商的名称",
　　  　  　  　"modelName": "fancyVehicleLight",
　　  　  　  　"version": "your software version number here.",
                "attributes": [
                    {
                        "name": "name",
            　　  　  　"value": "车灯",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 10
        　　  　  　}，
        　　  　  　{
            　　  　  　"name": "connectivity",
            　　  　  　"value": "UNREACHABLE",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 10
        　　  　  　}，
        　　  　  　{
            　　  　  　"name": "turnOnState",
            　　  　  　"value": "ON",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 0
        　　  　  　}，
        　　  　  　{
            　　  　  　"name": "brightness",
            　　  　  　"value": "50",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 100
        　　  　  　}
                ]
　　  　  　},
　　  　  　{
　　  　  　  　"actions": [
　　  　  　  　  　"turnOn",
　　  　  　  　  　"turnOff"
　　  　  　  　],
　　  　  　  　"applianceTypes": [
　　  　  　  　  　"VEHICLE_DOOR"
　　  　  　  　],
　　  　  　  　"additionalApplianceDetails": {
　　  　  　  　  　"extraDetail1": "optionalDetailForSkillAdapterToReferenceThisDevice",
　　  　  　  　  　"extraDetail2": "There can be multiple entries",
　　  　  　  　  　"extraDetail3": "but they should only be used for reference purposes.",
　　  　  　  　  　"extraDetail4": "This is not a suitable place to maintain current device state"
　　  　  　  　},
　　  　  　  　"applianceId": "uniqueVehicleDeviceId",
　　  　  　  　"friendlyDescription": "展现给用户的详细介绍",
　　  　  　  　"friendlyName": "车门",
　　  　  　  　"isReachable": "true",
　　  　  　  　"manufacturerName": "设备制造商的名称",
　　  　  　  　"modelName": "fancyVehicleDoor",
　　  　  　  　"version": "your software version number here.",
                "attributes": [
                    {
                        "name": "name",
            　　  　  　"value": "车门",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 10
        　　  　  　}，
        　　  　  　{
            　　  　  　"name": "connectivity",
            　　  　  　"value": "UNREACHABLE",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 10
        　　  　  　}，
        　　  　  　{
            　　  　  　"name": "turnOnState",
            　　  　  　"value": "OFF",
            　　  　  　"scale": "",
            　　  　  　"timestampOfSample": 1496741861,
            　　  　  　"uncertaintyInMilliseconds": 0
        　　  　  　}
                ]
　　  　  　}
　　  　],
　　    "discoveredGroups": [
            {
                "groupName": "汽车品牌A",
                "groupType": "VEHICLE",
                "applianceIds": [
                    "001",
                    "002",
                    "003"
                ],
                "groupNotes": "汽车品牌A001型号车",
                "additionalGroupDetails": {
                    "extraDetail1": "detail about the group",
                    "extraDetail2": "another detail about group",
                    "extraDetail3": "only be used for reference group."
                 }
            },
            {
                "groupName": "汽车品牌B",
                "groupType": "VEHICLE",
                "applianceIds": [
                    "004",
                    "005",
                    "006"
                ],
                "groupNotes": "汽车品牌B001型号车",
                "additionalGroupDetails": {
                    "extraDetail1": "detail about the group",
                    "extraDetail2": "another detail about group",
                    "extraDetail3": "only be used for reference group."
                }
            }
         ]
　　}
}
```

## 控制消息

控制消息(Control Message)是对车载设备进行控制的消息。按照车载设备的类型分为打开关闭设备的控制消息、温度设备的控制消息、电池设备的控制消息。

### 打开关闭消息

通过打开关闭消息可以实现对车载设备的打开和关闭控制，如打开关闭车门、打开关闭车窗等。

#### TurnOnRequest

当用户发出打开指定设备的请求时，DuerOS收到请求后，向技能发送TurnOnRequest消息，通知技能打开相应的设备。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | TurnOnRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

##### 应用举例

当用户说“小度小度，打开车门”，DuerOS收到用户请求后，向技能发送TurnOnRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TurnOnRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Vehicle Door ID]"
        }
    }
}
```

#### TurnOnConfirmation

当技能收到打开设备的指令时，会向DuerOS发送TurnOnConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | TurnOnConfirmation |

##### Payload信息

| 属性 | 取值 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

无。

##### 应用举例

当技能收到"打开车门"的请求时，向DuerOS发送TurnOnConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TurnOnConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

#### TurnOffRequest

当用户发出关闭设备的指令时，DuerOS收到请求后，向技能发送TurnOffRequest消息，通知技能关闭该设备。如关闭车门、关闭车窗等。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | TurnOffRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

##### 应用举例

当用户说“小度小度，把车门锁上”，DuerOS接收到用户请求后，向技能发送TurnOffRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TurnOffRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Vehicle Door ID]"
        }
    }
}
```

#### TurnOffConfirmation

当技能接收到关闭设备指令时，向DuerOS发送TurnOffConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | TurnOffConfirmation |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

##### 应用举例

当技能收到“把车门锁上”的请求时，向DuerOS发送TurnOffConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TurnOffConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### 控制温度消息

通过控制温度消息可以实现对车载设备的温度控制，包括设定设备温度、降低设备温度和调高设备温度。

#### IncrementTemperatureRequest

当用户发出调高设备温度的请求时，DuerOS收到请求后，向技能发送IncrementTemperatureRequest消息，通知技能调高设备温度。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | IncrementTemperatureRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备温度调高信息。 | 否，deltaValue为空表示用户没有指定温度调高的具体值 |
| deltaValue.value | 设备调高的温度值，是float类型。 | 当deltaValue存在时，该项必须存在 |
| deltaValue.scale | 温度计量单位。有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 当deltaValue存在时，该项必须存在。 |

##### 应用举例

用户说“小度小度，把车内温度调高一点”，DuerOS收到用户请求后，向技能发送IncrementTemperatureRequest消息，消息样例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementTemperatureRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue": {
            "value": 3.0,
            "scale": "CELSIUS"
        }
    }
}
```

#### IncrementTemperatureConfirmation

当技能收到调高设备温度的请求时，向DuerOS发送IncrementTemperatureConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | IncrementTemperatureConfirmation |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| mode | 设备温度变化后的设备模式。 | 否 |
| temperature | 设备温度变化后的设备温度，是double类型 | 是 |
| previousState | 设备温度变化前的设备状态。 | 是 |
| previousState.mode | 设备温度变化前的设备模式。 | 否 |
| previousState.temperature | 设备温度变化前的设备温度，是double类型。 | 是 |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

##### 应用举例

技能收到“把车内温度调高一点的请求”时，向DuerOS发送IncrementTemperatureConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "previousState": {
            "mode": {
                "value": "AUTO"
            },
            "temperature": {
                "value": 20.0
            }
        },
        "temperature": {
            "value": 23.0
        },
        "mode": {
            "value": "AUTO"
        },
        "attributes": []
    }
}
```

#### DecrementTemperatureRequest

当用户发出调低设备温度的指令时，DuerOS收到请求后，向技能发送DecrementTemperatureRequest消息，通知技能调低设备温度。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | DecrementTemperatureRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备温度调低信息。 | 否， deltaValue为空表示用户没有指定温度调低的具体值。 |
| deltaValue.value | 设备温度调低的温度值，是float类型。 | 当deltaValue存在时，该项必须存在。 |
| deltaValue.scale | 温度计量单位。有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 当deltaValue存在时，该项必须存在。 |

##### 应用举例

用户说“小度小度，把车内温度调低一点”，DuerOS收到用户请求时，会向技能发送DecrementTemperatureRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementTemperatureRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue": {
            "value": 3.0,
            "scale": "CELSIUS"
        }
    }
}
```

#### DecrementTemperatureConfirmation

当技能收到调低设备温度的指令时，向DuerOS发送DecrementTemperatureConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | DecrementTemperatureConfirmation |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| mode | 设备温度变化后的设备模式。 | 否 |
| temperature | 设备温度变化后的设备温度，是double类型。 | 是 |
| previousState | 设备温度变化前的状态。 | 是 |
| previousState.mode | 设备温度变化前的设备模式。 | 否 |
| previousState.temperature | 设备温度变化前的设备温度，是double类型。 | 是 |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

##### 应用举例

当技能收到“把车内温度调低一点”的指令时，会向DuerOS发送该DecrementTemperatureConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "previousState": {
            "mode": {
                "value": "AUTO"
            },
            "temperature": {
                "value": 23.0
            }
        },
        "temperature": {
            "value": 20.0
        },
        "mode": {
            "value": "AUTO"
        },
        "attributes": []
    }
}
```

#### SetTemperatureRequest

当用户发出设置设备温度的指令时，DuerOS向技能发送SetTemperatureRequest消息，通知技能对设备进行温度设置。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | SetTemperatureRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| targetTemperature | 设备设定的目标温度。 | 是 |
| targetTemperature.value | 设备设定的目标温度值。 | 是 |
| targetTemperature.scale | 温度计量单位。有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 是 |

##### 应用举例

用户说“小度小度，把车内空调温度设置为23度”，DuerOS接收用户的请求时，向技能发送SetTemperatureRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetTemperatureRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "targetTemperature": {
            "value": 23,
            "scale": "CELSIUS"
        },
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

#### SetTemperatureConfirmation

当技能收到设置设备温度的指令时，向DuerOS发送SetTemperatureConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | SetTemperatureConfirmation |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| mode | 温度设置成功后的设备模式。 | 否 |
| temperature | 温度设置成功后的设备温度，是double类型。 | 是 |
| previousState | 温度设置成功前的设备状态。 | 是 |
| previousState.mode | 温度设置成功前的设备模式。 | 否 |
| previousState.temperature | 温度设置成功前的设备温度，是double类型。 | 是 |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

##### 应用举例

当技能收到“把车内空调温度设置为23度”的指令时，向DuerOS发送SetTemperatureConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "previousState": {
            "mode": {
                "value": "AUTO"
            },
            "temperature": {
                "value": 25.0
            }
        },
        "temperature": {
            "value": 23.0
        },
        "mode": {
            "value": "AUTO"
        },
        "attributes": []
    }
}
```

#### HeatRequest

当用户发出加热设备的请求时，DuerOS收到请求后向技能发送HeatRequest消息，通知技能加热设备。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | HeatRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

##### 应用举例

用户说“小度小度，加热车座”，DuerOS接收到用户请求后，向技能发送HeatRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "HeatRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

#### HeatConfirmation

当技能收到加热设备的指令后，向DuerOS发送HeatConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | HeatConfirmation |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

##### 应用举例

当技能收到“加热车座”的指令后，向DuerOS发送HeatConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "HeatConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

#### CancelHeatRequest

当用户发出停止加热设备请求时，DuerOS收到请求后，向技能发送CancelHeatRequest消息，通知技能停止加热设备。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | CancelHeatRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

##### 应用举例

用户说“小度小度，停止加热车座”，DuerOS收到用户请求后，向技能发送CancelHeatRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "CancelHeatRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

#### CancelHeatConfirmation

当技能收到停止加热指令时，向DuerOS发送CancelHeatConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | CancelHeatConfirmation |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

##### 应用举例

当技能收到“停止加热车座”的消息后，向DuerOS发送CancelHeatConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "CancelHeatConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### 控制电量消息

通过控制电量消息可以实现对车载设备电量操作，如充电和停止充电操作。

#### ChargeRequest

当用户发出给设备充电的请求时，DuerOS收到请求后，向技能发送ChargeRequest消息，通知技能给设备充电。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | ChargeRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

##### 应用举例

用户说“小度小度，给车充电”，DuerOS接收到用户请求后，向技能发送ChargeRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ChargeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

#### ChargeConfirmation

当技能收到充电指令后，向DuerOS发送ChargeConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | ChargeConfirmation |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

##### 应用举例

当技能接收到“给车充电”指令后，向DuerOS发送ChargeConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ChargeConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

#### DischargeRequest

当用户发出停止给设备充电的请求时，DuerOS收到请求后，向技能发送DischargeRequest消息，通知技能停止给设备充电。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | DischargeRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

##### 应用举例

当用户说“小度小度，停止给车充电”，DuerOS接收到用户请求后，向技能发送DischargeRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DischargeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

#### DischargeConfirmation

当技能收到停止充电的指令后，向DuerOS发送DischargeConfirmation消息。

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | DischargeConfirmation |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

##### 应用举例

当技能收到“停止充电”的指令后，向DuerOS发送DischargeConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DischargeConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

## 查询消息

查询消息主要是通过指令查询车载设备的状态。目前支持查询车载设备的打开状态信息、查询车载设备的温度信息、查询车载设备的电量信息、查询设备的油量信息。

### GetTurnOnStateRequest

当用户发出查询当前设备打开状态的请求时，DuerOS收到用户请求后，向技能发送GetTurnOnStateRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetTurnOnStateRequest |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，车门打开了吗”，DuerOS接收到用户请求后，向技能发送GetTurnOnStateRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTurnOnStateRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### GetTurnOnStateResponse

当技能查询到设备打开状态信息时，通过GetTurnOnStateResponse消息将查询结果发送给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetTurnOnStateResponse |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| turnOn | 设备打开状态信息。 | 是 |
| turnOn.value | 设备打开状态取值，是bool类型。 | 是 |
| applianceResponseTimestamp | 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是标准ISO 8601格式，UTC时间，精度为1秒。RFC 3399变体是首选，但不允许使用负偏移。 | 否 |

#### 应用举例

当技能查询到当前车门处于打开状态时，向DuerOS发送GetTurnOnStateResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTurnOnStateResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "turnOn": {
            "value": "true",
        },
        "applianceResponseTimestamp": "2017-08-12T11:20:50.52Z"
    }
}
```

### GetTemperatureReadingRequest

当用户发出查询当前设备温度的请求时，DuerOS收到该请求后，向技能发送GetTemperatureReadingRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetTemperatureReadingRequest |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，车内现在多少度”，DuerOS接收到用户的请求后，向技能发送GetTemperatureReadingRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTemperatureReadingRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### GetTemperatureReadingResponse

当技能查询到设备温度时，通过GetTemperatureReadingResponse消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetTemperatureReadingResponse |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| mode | 设备设置的模式。 | 是 |
| temperatureReading | 设备温度信息。 | 是 |
| temperatureReading.value | 温度值，是float类型。 | 是 |
| temperatureReading.scale | 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 否 |
| applianceResponseTimestamp | 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是标准ISO 8601格式，UTC时间，精度为1秒。RFC 3399变体是首选，但不允许使用负偏移。 | 否 |

#### 应用举例

当技能查询到当前车内温度是26度时，向DuerOS发送GetTemperatureReadingResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTemperatureReadingResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "temperatureReading": {
            "value": 26.0,
            "scale": "CELSIUS"
        },
        "applianceResponseTimestamp": "2017-08-12T11:20:50.52Z"
    }
}
```

### GetTargetTemperatureRequest

当用户发出查询设备设定的目标温度的请求时，DuerOS收到请求后，向技能发送GetTargetTemperatureRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetTargetTemperatureRequest |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，车内空调设置的多少度”，DuerOS收到用户请求后，向技能发送GetTargetTemperatureRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTargetTemperatureRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### GetTargetTemperatureResponse

当技能查询到设备设定的目标温度时，通过GetTargetTemperatureResponse消息将查询结果发送给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | GetTargetTemperatureResponse |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| mode | 设备设置的模式。 | 是 |
| targetTemperature | 温度信息 | 否 |
| targetTemperature.value | 温度值，是float类型。 | 是 |
| targetTemperature.scale | 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 否 |
| coolingTargetTemperature | 制冷温度信息，在制冷加热的双模式下使用，一般与heatingTargetTemperature同时出现。 | 否 |
| coolingTargetTemperature.value | 温度值，是float类型。 | 是 |
| coolingTargetTemperature.scale | 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 否 |
| heatingTargetTemperature | 加热温度信息，在制冷加热可以同时开的双模式下使用，一般与coolingTargetTemperature同时出现。 | 否 |
| heatingTargetTemperature.value | 温度值，是float类型。 | 是 |
| heatingTargetTemperature.scale | 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 否 |
| temperatureMode | 温控模式。 | 是 |
| temperatureMode.value | 温控模式。有以下七种模式：  * COOL：制冷模式。 * HEAT：制热模式。 * AUTO：自动模式。 * FAN：送风模式。 * DEHUMIDIFICATION：除湿模式。 * SLEEP：睡眠模式。 * CUSTOM：设备厂商特有模式。 | 是 |
| temperatureMode.friendlyName | 模式名称。 | 是 |
| applianceResponseTimestamp | 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是标准ISO 8601格式，UTC时间，精度为1秒。RFC 3399变体是首选，但不允许使用负偏移。 | 否 |

#### 应用举例

当技能查询到空调温度设置在26度时，向DuerOS发送GetTargetTemperatureResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTargetTemperatureResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "targetTemperature": {
            "value": 26.0,
            "scale": "CELSIUS"
        },
        "applianceResponseTimestamp": "2017-08-12T11:20:50.52Z",
        "temperatureMode": {
            "value": "CUSTOM",
            "friendlyName": "Required device-specific mode name"
        }
    }
}
```

### GetOilCapacityRequest

当用户发出查询当前车辆油量的请求时，DuerOS收到请求后，向技能发送GetOilCapacityRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetOilCapacityRequest |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，车里还有多少油”，DuerOS接收到用户请求后，向技能发送GetOilCapacityRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetOilCapacityRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### GetOilCapacityResponse

当技能获取到当前车辆的油量信息时，通过GetOilCapacityResponse消息将油量信息发送给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetOilCapacityResponse |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| oilCapacity | 油量信息。 | 是 |
| oilCapacity.value | 油量值，是float类型。 | 是 |
| oilCapacity.scale | 油量计量单位L。 | 是 |
| drivingDistance | 可行驶距离信息。 | 是 |
| drivingDistance.value | 可行驶距离值，是float类型。 | 是 |
| drivingDistance.scala | 距离计量单位公里。 | 是 |
| applianceResponseTimestamp | 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是标准ISO 8601格式，UTC时间，精度为1秒。RFC 3399变体是首选，但不允许使用负偏移。 | 否 |

#### 应用举例

当技能获取到当前车辆的油量信息时，向DuerOS发送GetOilCapacityResponse消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetOilCapacityResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "oilCapacity": {
            "value": 5.0,
            "scale": "L",
        },
        "drivingDistance": {
            "value": 50.0,
            "scale": "公里",
        },
        "applianceResponseTimestamp": "2017-08-12T11:20:50.52Z"
    }
}
```

### GetElectricityCapacityRequest

当用户发出查询当前车辆的电量信息的请求时，DuerOS收到请求后，向技能发送将GetElectricityCapacityRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetElectricityCapacityRequest |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| pinCode | 控制密码，一般为4～8位有效数字。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，车里还有多少电”，DuerOS接收到用户请求后，向技能发送GetElectricityCapacityRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetElectricityCapacityRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "pinCode": "[control password here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### GetElectricityCapacityResponse

当技能获取到当前车辆的电量信息时，通过GetElectricityCapacityResponse消息将电量信息发送给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetElectricityCapacityResponse |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| electricityCapacity | 电量信息。 | 是 |
| electricityCapacity.value | 电量值，字符串, 比如20%。 | 是 |
| electricityCapacity.scale | 电量计量单位度。 | 是，内容可以为空。 |
| drivingDistance | 可行驶距离信息。 | 是 |
| drivingDistance.value | 可行驶距离值，是float类型。 | 是 |
| drivingDistance.scala | 距离计量单位公里。 | 是 |
| applianceResponseTimestamp | 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是标准ISO 8601格式，UTC时间，精度为1秒。RFC 3399变体是首选，但不允许使用负偏移。 | 否 |

#### 应用举例

当技能查询到当前车辆电量信息时，向DuerOS发送GetElectricityCapacityResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetElectricityCapacityResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "electricityCapacity": {
            "value": "20%",
            "scale": "",
        },
        "drivingDistance": {
            "value": 50.0,
            "scale": "公里",
        },
        "applianceResponseTimestamp": "2017-08-12T11:20:50.52Z"
    }
}
```

## 错误消息

当DuerOS向技能发送设备请求信息时，请求信息中可能存在设备不支持或者超出设备使用范围等情况，此时技能会返回相应的错误类型和信息。技能不需要返回每个错误，仅返回错误对应的错误类型。错误详细信息请参见[错误消息](error-message.md)章节。
