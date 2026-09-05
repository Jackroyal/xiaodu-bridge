---
title: "设备属性上报"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/attributes-report_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 设备属性上报

在设备正常运行过程中，DuerOS不会感知到设备的属性。只有当技能上报设备属性给DuerOS时，DuerOS才会记录存储设备属性。在以下三种情况下，技能会上报设备属性信息。

* 发现设备时，在返回消息[DiscoverAppliancesResponse](discovery-message.md#discoverappliancesresponse)中上报设备所有的属性信息。
* 当用户下发智能家居[控制请求](control-message.md)消息，技能成功处理请求消息时，会在confirmation消息中返回发生变化的属性信息。
* 当用户没有通过发送DuerOS[控制消息](control-message.md)，而是使用手动或其他方式对设备进行操作来修改属性信息时，技能主动上报设备属性信息。

## 发现设备时上报设备属性

当用户查找设备或者在技能商店中启用技能时，DuerOS会向技能发送DiscoverAppliancesRequest请求。当技能收到请求时，将设备属性信息通过消息[DiscoverAppliancesResponse](discovery-message.md#discoverappliancesresponse)上报给DuerOS。

在[DiscoverAppliancesResponse](discovery-message.md#discoverappliancesresponse)消息中携带了属性的所有信息，包括name、value、scale、timestampOfSample、uncertaintyInMilliseconds。具体的上报方式请参照[DiscoverAppliancesResponse](discovery-message.md#discoverappliancesresponse)消息。

**说明：**

* 如果设备的某个属性在发现设备过程中，没有上报给DuerOS，后续在技能主动上报该属性或控制消息中上报该属性，DuerOS会新增该属性。

## 控制消息中上报设备属性

当用户通过语音控制设备，如用户说“打开厨房灯”，DuerOS收到用户请求时，会向技能发送控制请求消息，技能执行完相应的指令后会向DuerOS发送confirmation信息并上报设备属性信息。如成功打开厨房灯时技能会发送TurnOnConfirmation信息，并上报厨房灯的属性信息。

### 示例1

用户请求打开厨房灯，当厨房灯成功打开时，技能会发送TurnOnConfirmation消息，并在消息中上报name、brightness、turnOnState属性信息。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TurnOnConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "name",
                "value": "电灯",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10
            }，
            {
                "name": "brightness",
                "value": "50",
                "scale": "%",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10
            }，
            {
                "name": "turnOnState",
                "value": "ON",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10
            }
        ]
    }
}
```

### 示例2

在车载场景中，当技能收到“把车内温度调低一点”的指令时，会向DuerOS发送该DecrementTemperatureConfirmation消息，并上报temperature属性信息。

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
        "attributes": [
            {
                "name": "temperature",
                "value": 20.0,
                "scale": "CELSIUS",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10
            }
        ]
    }
}
```

**说明**

* 技能在控制消息中上报设备属性时，可以上报变化的属性信息，也可以上报设备所有的属性信息。如示例1中，打开厨房灯时，厨房灯的brightness和turnOnState属性发生变化，厨房灯的name属性没有变化，此时可以仅上报brightness和turnOnState属性，也可以上报name属性。建议至少将变化的属性信息上报给DuerOS。

## 技能主动上报设备属性

当用户手动操作设备或者通过第三方app修改设备状态，如手动关闭厨房灯，手动切换电风扇模式，使用第三方app修改设备名称等，这些情况下DuerOS不会感知到设备属性变化，需要设备云主动上报设备属性。

技能主动向DuerOS发送请求消息，请求DuerOS同步设备属性信息。DuerOS收到请求后向技能发送ReportStateRequest消息，请求技能上报相应的属性信息，技能收到请求后，将向DuerOS发送ReportStateResponse消息，上报属性信息。

### 主动上报请求消息

当用户手动操作设备或者通过第三方app修改设备状态时，技能会主动上报属性信息，发送上报请求消息。

#### 接口地址

```
https://xiaodu.baidu.com/saiya/smarthome/changereport
```

#### 请求方式

POST请求方式。

#### Head说明

| 参数名称 | 取值 |
| --- | --- |
| Content-Type | application/json |

#### 参数信息

##### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | ChangeReportRequest |

##### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| botId | 设备云技能ID。 | 是 |
| openUid | 用户被授权的百度账号开放ID，与设备云账号一一对应。 | 是 |
| appliance | 上报的设备对象，包括applianceId和attributeName。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.attributeName | 设备的属性名称，每次仅请求上报一个属性。 | 是 |

#### 请求示例

```
curl -v "https://xiaodu.baidu.com/saiya/smarthome/changereport" -H 'Content-Type:application/json' -d
'{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ChangeReportRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "botId": "5385e18b-619a-abcd-ed10-33a7d69780a6",
        "openUid": "27a7d83c2d3cfbad5d387cd35f3ca17b",
        "appliance": {
            "applianceId": "[Device ID for Light]",
            "attributeName": "powerState"
        }
    }
}'
```

**说明**

* 这里主动上报的属性，属性值是通过ReportStateRequest查询到的，所以需要在ReportStateRequest协议实现中支持上对于上报属性的查询。

### 请求返回消息

当技能主动发起上报属性请求后，DuerOS返回确认信息。

#### 参数说明

| 参数名称 | 描述 | 类型 | 是否必须 |
| --- | --- | --- | --- |
| status | 消息状态。0表示已经完成属性上报，非0表示消息异常。 | int | 是 |
| msg | 消息提示信息。当状态码为0时，提示更新的属性记录数。当状态码非0时，返回对应的错误消息。 | string | 是 |
| messageId | 请求消息中的messageId信息。 | string | 是 |
| data | 返回消息的数据信息。 | array | 是 |
| data.updated_attribute_num | 同步属性的数量。 | int | 是 |

#### 返回示例

```
{
    “status”: 0, 
    "msg": "update 3 attributes", 
    "messageId": "请求消息中的messageId", 
    "data": {
        "updated_attribute_num": 3
    }
}
```

### ReportStateRequest消息

当DuerOS收到技能主动上报设备属性的请求时，会向技能发送ReportStateRequest消息，请求技能上报属性的完整信息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ReportStateRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| appliance.attributeName | 查询的属性名称，字符串类型，支持数字、字母和下划线，长度不能超过128个字符。 | 是 |

#### 应用举例

当手动将关上厨房灯时，厨房灯的属性发生变化，技能主动向DuerOS发送请求，DuerOS收到请求后，向技能发送ReportStateRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "ReportStateRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Light ]"
            "attributeName": "turnOnState"
        }
    }
}
```

### ReportStateResponse消息

当技能收到ReportStateRequest请求消息时，会主动上报请求消息中属性的完整信息，并向技能发送ReportStateResponse消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ReportStateResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息，最多支持上报10个属性。 | 是 |
| attribute.name | 属性名称，支持数字、字母和下划线，长度不能超过128个字符。 | 是 |
| attribute.value | 属性值，支持多种json类型。 | 是 |
| attribute.scale | 属性值的单位名称，支持数字、字母和下划线，长度不能超过128个字符。 | 是 |
| attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。如果设备使用的是轮询时间间隔的取样方式，那么uncertaintyInMilliseconds就等于时间间隔。如温度传感器每1秒取样1次，那么uncertaintyInMilliseconds的值就是1000。 | 是 |

#### 应用举例

技能获取到厨房灯的turnOnState属性时，向DuerOS发送ReportStateResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "ReportStateResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "turnOnState",
                "value": "OFF",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 0
            }
        ]
    }
}
```

**说明**

* 技能主动上报属性时，在[主动上报请求消息](#主动上报请求消息)中每次仅请求上报一个属性，在[ReportStateResponse](#reportstateresponse消息)消息中除了返回请求的属性外，还可以返回设备的其他属性信息，最多支持返回10个属性信息。
