---
title: "查询消息"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/query-message_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 查询消息(Query Message)

查询消息(Query Message)主要是通过智能家居设备查询空气质量、查询空气湿度、查询设备温度、查询设备状态等信息。目前支持以下查询消息。

* 查询空气质量
  + [GetAirQualityIndexRequest](#getairqualityindexrequest)
  + [GetAirQualityIndexResponse](#getairqualityindexresponse)
  + [GetAirPM25Request](#getairpm25request)
  + [GetAirPM25Response](#getairpm25response)
  + [GetAirPM10Request](#getairpm10request)
  + [GetAirPM10Response](#getairpm10response)
  + [GetCO2QuantityRequest](#getco2quantityrequest)
  + [GetCO2QuantityResponse](#getco2quantityresponse)
  + [GetHumidityRequest](#gethumidityrequest)
  + [GetHumidityResponse](#gethumidityresponse)
  + [GetTargetHumidityRequest](#gettargethumidityrequest)
  + [GetTargetHumidityResponse](#gettargethumidityresponse)
* 查询设备温度
  + [GetTemperatureReadingRequest](#gettemperaturereadingrequest)
  + [GetTemperatureReadingResponse](#gettemperaturereadingresponse)
  + [GetTargetTemperatureRequest](#gettargettemperaturerequest)
  + [GetTargetTemperatureResponse](#gettargettemperatureresponse)
* 查询设备运行参数
  + [GetRunningTimeRequest](#getrunningtimerequest)
  + [GetRunningTimeResponse](#getrunningtimeresponse)
  + [GetTimeLeftRequest](#gettimeleftrequest)
  + [GetTimeLeftResponse](#gettimeleftresponse)
  + [GetRunningStatusRequest](#getrunningstatusrequest)
  + [GetRunningStatusResponse](#getrunningstatusresponse)
  + [GetStateRequest](#getstaterequest)
  + [GetStateResponse](#getstateresponse)
  + [GetLocationRequest](#getlocationrequest)
  + [GetLocationResponse](#getlocationresponse)
* 查询电量
  + [GetElectricityCapacityRequest](#getelectricitycapacityrequest)
  + [GetElectricityCapacityResponse](#getelectricitycapacityresponse)
* 查询水质
  + [GetWaterQualityRequest](#getwaterqualityrequest)
  + [GetWaterQualityResponse](#getwaterqualityresponse)
* 查询风速
  + [GetFanSpeedRequest](#getfanspeedrequest)
  + [GetFanSpeedResponse](#getfanspeedresponse)
* 查询速度
  + [GetSpeedRequest](#getspeedrequest)
  + [GetSpeedResponse](#getspeedresponse)
* 查询运动信息
  + [GetMotionInfoRequest](#getmotioninforequest)
  + [GetMotionInfoResponse](#getmotioninforesponse)
* 查询开关状态
  + [GetTurnOnStateRequest](#getturnonstaterequest)
  + [GetTurnOnStateResponse](#getturnonstateresponse)

## 查询空气质量

### GetAirQualityIndexRequest

当用户发出查询空气质量的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetAirQualityIndexRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，空气净化器查一下空气质量”，DuerOS接收到用户意图后，向技能发送GetAirQualityIndexRequest消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetAirQualityIndexRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetAirQualityIndexResponse

当空气质量查询成功时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetAirQualityIndexResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| AQI | 空气质量。 | AQI和level必选其一 |
| level | 表示设备返回的空气质量等级描述 (优,良,差,轻度污染,中度污染,重度污染,严重污染) | AQI和level必选其一 |

#### 应用举例

技能查询到“空气净化器的空气质量为10”时，会向DuerOS发送GetAirQualityIndexResponse消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetAirQualityIndexResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "AQI": {
            "value": 10
        },
        "level":{
            "value":"轻度污染"
        }
    }
}
```

### GetAirPM25Request

当用户发出查询空气中PM2.5含量的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetAirPM25Request |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，空气净化器查一下PM2.5”，DuerOS接收到用户意图后，向技能发送GetAirPM25Request消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetAirPM25Request",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetAirPM25Response

当查询到空气中PM2.5含量成功时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetAirPM25Response |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| PM25 | 空气中PM2.5含量。 | 是 |
| PM25.value | 浮点型数值。 | 是 |
| PM25.scale | 单位微克每立方米（μg/m3）。 | 是 |

#### 应用举例

技能查询到“空气净化器的PM2.5为100”时，向DuerOS发送GetAirPM25Response消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetAirPM25Response",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "PM25": {
            "value": 100.0,
            "scale": 'μg/m3'
        }
    }
}
```

### GetAirPM10Request

当用户发出查询空气中PM10含量的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetAirPM10Request |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，空气净化器查一下PM10”，DuerOS接收到用户意图后，向技能发送GetAirPM10Request消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetAirPM10Request",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetAirPM10Response

当查询到空气中PM10含量成功时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetAirPM10Response |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| PM10 | 空气中PM10含量。 | 是 |
| PM10.value | 浮点型数值。 | 是 |
| PM10.scale | 单位微克每立方米（μg/m3）。 | 是 |

#### 应用举例

技能查询到“空气净化器的PM10为100”时，向DuerOS发送GetAirPM10Response消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetAirPM10Response",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "PM10": {
            "value": 100.0,
            "scale": 'μg/m3'
        }
    }
}
```

### GetCO2QuantityRequest

当用户发出查询空气中CO2含量的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetCO2QuantityRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，查一下新风机二氧化碳含量”，DuerOS接收到用户意图后，向技能发送GetCO2QuantityRequest消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetCO2QuantityRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetCO2QuantityResponse

当查询到空气中CO2含量成功时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetCO2QuantityResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| ppm | 空气中CO2的浓度信息。 | 是 |
| ppm.value | 空气中CO2的浓度数值，float类型。 | 是 |

#### 应用举例

技能查询到“新风机的CO2浓度为100.00”时，向DuerOS发送GetCO2QuantityResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetCO2QuantityResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "ppm": {
            "value": 100.00
        }
    }
}
```

### GetHumidityRequest

当用户发出查询空气湿度的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetHumidityRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，空气净化器查一下空气湿度”，DuerOS收到用户意图后，向技能发送GetHumidityRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetHumidityRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetHumidityResponse

当查询到湿度信息时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetHumidityResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息。 | 是 |

[humidity attribute定义](attributes.md#humidity属性)

#### 应用举例

技能查询到湿度成功时，向DuerOS发送GetHumidityResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetHumidityResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "humidity",
            "value": 50.1,
            "scale": "%",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "[0, 100]"
        }]
    }
}
```

### GetTargetHumidityRequest

当用户发出查询空气的目标湿度的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTargetHumidityRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，空气净化器查一下目标湿度”，DuerOS收到用户意图后，向技能发送GetTargetHumidityRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTargetHumidityRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetTargetHumidityResponse

当查询到湿度信息时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTargetHumidityResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息。 | 是 |

[humidity attribute定义](attributes.md#humidity属性)

#### 应用举例

技能查询到目标湿度成功时，向DuerOS发送GetTargetHumidityResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTargetHumidityResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {    
        "attributes": [{
            "name": "humidity",
            "value": 50.1,
            "scale": "%",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "[0, 100]"
        }]
    }
}
```

## 查询设备温度

### GetTemperatureReadingRequest

当用户发出查询当前设备温度的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTemperatureReadingRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| compartment | 当设备有不同的温度分区，需要根据分区进行温度查询。支持以下分区。  * freezer：冷冻室分区 * refrigerator：冷藏室分区 * variableTemperatureSpace：变温室分区 | 否 |

#### 应用举例

用户说“小度小度，热水器现在水温是多少度”。DuerOS了解到用户意图后，向技能发送GetTemperatureReadingRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

用户说“小度小度，冰箱冷藏室的温度是多少度”。DuerOS理解到用户意图后，向技能发送GetTemperatureReadingRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        },
        "compartment": "refrigerator"
    }
}
```

### GetTemperatureReadingResponse

当查询到设备温度时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTemperatureReadingResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| mode | 设备设置的模式。 | 是 |
| temperatureReading | 设备温度信息。 | 是 |
| temperatureReading.value | 温度值，是float类型。 | 是 |
| temperatureReading.scale | 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 否 |
| applianceResponseTimestamp | 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是标准ISO 8601格式，UTC时间，精度为1秒。RFC 3399变体是首选，但不允许使用负偏移。 | 否 |
| compartment | 当设备有不同的温度分区时，需要根据分区进行温度查询。支持以下分区。  * freezer：冷冻室分区 * refrigerator：冷藏室分区 * variableTemperatureSpace：变温室分区 | 否 |

#### 应用举例

技能查询到当前环境温度的时候，向DuerOS发送GetTemperatureReadingResponse消息，消息示例如下。

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
            "value": 60.0,
            "scale": "CELSIUS"
        },
        "applianceResponseTimestamp": "2017-08-12T11:20:50.52Z"
    }
}
```

技能查询到冰箱冷藏室当前温度为5度时，向DuerOS发送GetTemperatureReadingResponse消息，消息示例如下。

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
            "value": 5.0,
            "scale": "CELSIUS"
        },
        "applianceResponseTimestamp": "2017-08-12T11:20:50.52Z",
        "compartment": "refrigerator"
    }
}
```

### GetTargetTemperatureRequest

当用户想查询设备设定的目标温度的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTargetTemperatureRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| compartment | 当查询的设备有温度分区时，按温度分区查询。例如冰箱，分为  * 冷冻室：freezer * 冷藏室：refrigerator * 变温室：variableTemperatureSpace | 否 |

#### 应用举例

用户说“小度小度，空调设置的温度是多少度”，DuerOS理解到用户意图后，向技能发送GetTargetTemperatureRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        },
    }
}
```

用户说“小度小度，冰箱冷藏室设置多少度”。DuerOS理解到用户意图后，向技能发送GetTargetTemperatureRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        },
        "compartment": "refrigerator"
    }
}
```

### GetTargetTemperatureResponse

技能查询到设备设定的目标温度时，通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTargetTemperatureResponse |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| mode | 设备设置的模式。 | 是 |
| targetTemperature | 温度信息 | 否 |
| targetTemperature.value | 温度值，是浮点类型。 | 是 |
| targetTemperature.scale | 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 否 |
| coolingTargetTemperature | 制冷温度信息，在制冷加热的双模式下使用，一般与heatingTargetTemperature同时出现。 | 否 |
| coolingTargetTemperature.value | 温度值，是float类型。 | 是 |
| coolingTargetTemperature.scale | 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 否 |
| coolingTargetTemperature | 加热温度信息，在制冷加热可以同时开的双模式下使用，一般与coolingTargetTemperature同时出现。 | 否 |
| heatingTargetTemperature.value | 温度值，是浮点类型。 | 是 |
| heatingTargetTemperature.scale | 温度计量单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 | 否 |
| temperatureMode | 温控模式。 | 是 |
| temperatureMode.value | 温控模式。有以下七种模式：  * COOL：制冷模式。 * HEAT：制热模式。 * AUTO：自动模式。 * FAN：送风模式。 * DEHUMIDIFICATION：除湿模式。 * SLEEP：睡眠模式。 * CUSTOM：设备厂商特有模式。 | 是 |
| temperatureMode.friendlyName | 模式名称。 | 是 |
| applianceResponseTimestamp | 表示上次从目标设备检索到状态的时间。这表明了状态的新鲜度，这会影响DuerOS的响应。该值的精度是特定于设备的，可以由设备云预估。有效值是标准ISO 8601格式，UTC时间，精度为1秒。RFC 3399变体是首选，但不允许使用负偏移。 | 否 |
| compartment | 当查询的设备有温度分区时，按温度分区查询。例如冰箱，分为  * 冷冻室：freezer * 冷藏室：refrigerator * 变温室：variableTemperatureSpace | 否 |

#### 应用举例

技能查询到空调设置在26度时，向DuerOS发送GetTargetTemperatureResponse消息。消息示例如下。

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
            "value": 60.0,
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

技能查询到冰箱冷藏室设置在5度时，向DuerOS发送GetAirQualityIndexRequest消息。消息示例如下。

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
            "value": 5.0,
            "scale": "CELSIUS"
        },
        "applianceResponseTimestamp": "2017-08-12T11:20:50.52Z",
        "temperatureMode": {
            "value": "CUSTOM",
            "friendlyName": "Required device-specific mode name"
        }
        "compartment": "refrigerator"
    }
}
```

## 查询设备运行参数

### GetRunningTimeRequest

当用户发出查询设备运行时间的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetRunningTimeRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，查一下新风机运行时间”，DuerOS接收到用户意图后，向技能发送GetRunningTimeRequest消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetRunningTimeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetRunningTimeResponse

当查询设备运行时间成功时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetRunningTimeResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| totalTimeInSeconds | 设备总体运行时间信息。 | 是 |
| totalTimeInSeconds.value | 设备总体运行时间值，int类型，单位是秒。 | 是 |

#### 应用举例

技能查询到“新风机运行时间100秒”时，向DuerOS发送GetRunningTimeResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetRunningTimeResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "totalTimeInSeconds": {
            "value": 100
        }
    }
}
```

### GetTimeLeftRequest

当用户发出查询设备剩余运行时间的请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTimeLeftRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，查一下洗衣机还有多久洗完”，DuerOS接收到用户意图后，向技能发送GetTimeLeftRequest消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTimeLeftRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetTimeLeftResponse

当查询设备剩余运行时间成功时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTimeLeftResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| timeLeftInSeconds | 设备剩余运行时间信息。 | 是 |
| timeLeftInSeconds.value | 设备剩余运行时间值，int类型，单位是秒。 | 是 |

#### 应用举例

技能查询到“洗衣机的剩余运行时间是100秒时”，向DuerOS发送GetTimeLeftResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTimeLeftResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "timeLeftInSeconds": {
            "value": 100
        }
    }
}
```

### GetRunningStatusRequest

当用户发出查询设备运行状态请求时，DuerOS将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetRunningStatusRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，查一下洗衣机运行状态”，DuerOS接收到用户意图后，向技能发送GetRunningStatusRequest消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetRunningStatusRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetRunningStatusResponse

当查询设备运行状态成功时，技能通过该消息向DuerOS发送查询结果。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetRunningStatusResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| runningState | 设备当前运行状态对象信息。 | 是 |
| runningState.value | 设备当前运行状态值。 洗衣机支持以下状态。  * weighing：称重 * washing：洗涤 * rinsing：漂洗 * dehydration：脱水 * drying：烘干 * cooling：冷却(烘干后) * waterStay：留水(漂洗后) * windBlowing：吹风(烘干后) * finished：洗衣结束    风扇支持以下状态。  * working：已打开 * end：已关闭 | 是 |

#### 应用举例

技能查询到“洗衣机当前的运行状态是烘干时”，向DuerOS返回GetRunningStatusResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetRunningStatusResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "runningState": {
            "value": "drying" 
        }
    }
}
```

### GetStateRequest

当用户想了解设备状态时，DuerOS会该将消息发送给技能，比如想要了解扫地机器人当前状态(清扫中/充电中/回充中...)时，可以说，"小度小度, 扫地机器人在干吗?"， 这时技能会收到GetStateRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetStateRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，扫地机器人在干吗?”，DuerOS接收到用户意图后，向技能发送GetStateRequest消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetStateRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetStateResponse

当技能查询到设备当前状态时，需要给DuerOS返回该消息，告知用户当前扫地机器人的状态。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetStateResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息，最多支持上报10个属性。 | 是 |
| attribute.name | 属性名称，这里取"state"。 | 是 |
| attribute.value | 字符串，目前支持的属性值如下:  * CLEANING：清扫中 * CHARGING：充电中 * RECHARGING：回充中 * SLEEPING：休眠中 * STAND_BY：待命中 * REPORT_ERROR：报错 * SHUT_DOWN：关机 * REMOTE_CONTROLING：遥控中 * PAUSED：已暂停  。 | 是 |
| attribute.scale | 属性值的单位名称，这里是空串''。 | 是 |
| attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。 | 是 |

#### 应用举例

技能查询到“扫地机器人当前的运行状态是正在清扫时”，向DuerOS返回GetStateResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetStateResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "state",
            "value": "CLEANING",
            "scale": "",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10
        }]
    }
}
```

### GetLocationRequest

当用户想了解设备当前位置时，DuerOS会将该消息发送给技能，比如想要了解扫地机器人当前在哪个房间清扫时，可以说，"小度小度, 扫地机器人在哪儿呢?"， 这时技能会收到GetLocationRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetLocationRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，扫地机器人在哪儿呢?”，DuerOS接收到用户意图后，向技能发送GetLocationRequest消息。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetLocationRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetLocationResponse

当技能查询到设备当前位置时，需要给DuerOS返回该消息，告知用户当前扫地机器人的位置。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetLocationResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息，最多支持上报10个属性。 | 是 |
| attribute.name | 属性名称，这里取"location"。 | 是 |
| attribute.value | 字符串，目前支持的属性值如下:  * MASTER_BEDROOM：主卧 * SECOND_BEDROOM：次卧 * LIVING_ROOM：客厅 * KITCHEN：厨房 * STUDY：书房 * RESTAURANT：餐厅  。 | 是 |
| attribute.scale | 属性值的单位名称，这里是空串''。 | 是 |
| attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。 | 是 |

#### 应用举例

技能查询到“扫地机器人当前的位置在主卧”时，向DuerOS返回GetLocationResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetLocationResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "location",
            "value": "MASTER_BEDROOM",
            "scale": "",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10
        }]
    }
}
```

### GetElectricityCapacityRequest

当用户发出查询当前设备的电量信息的请求时，DuerOS收到请求后，向技能发送将GetElectricityCapacityRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetElectricityCapacityRequest |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，扫地机器人还有多少电”，DuerOS接收到用户请求后，向技能发送GetElectricityCapacityRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### GetElectricityCapacityResponse

当技能获取到当前设备的电量信息时，通过GetElectricityCapacityResponse消息将电量信息发送给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetElectricityCapacityResponse |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息，最多支持上报10个属性。 | 是 |
| attribute.name | 属性名称，这里取"electricityCapacity"。 | 是 |
| attribute.value | 浮点数。 | 是 |
| attribute.scale | 属性值的单位名称，这里是%。 | 是 |
| attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。 | 是 |

#### 应用举例

当技能查询到当前设备电量信息时，向DuerOS发送GetElectricityCapacityResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetElectricityCapacityResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "electricityCapacity",
                "value": "23",
                "scale": "%",
                "timestampOfSample": 1527514032,
                "uncertaintyInMilliseconds": 0
            }
        ]
    }
}
```

### GetWaterQualityRequest

当用户发出查询当前设备的水质的请求时，DuerOS收到请求后，向技能发送将GetWaterQualityRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetWaterQualityRequest |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，净水器水质怎么样”，DuerOS接收到用户请求后，向技能发送GetWaterQualityRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetWaterQualityRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### GetWaterQualityResponse

当技能获取到当前设备的电量信息时，通过GetWaterQualityResponse消息将电量信息发送给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Query |
| name | GetWaterQualityResponse |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| ppm | 水中含有各种污染物质的质量。 | 是 |
| ppm.value | 浮点型。 | 是 |
| ppm.scale | 单位名称，毫克每升或微克每升（ mg/L、ug/L）。 | 是 |

#### 应用举例

当技能查询到当前设备水质信息时，向DuerOS发送GetWaterQualityResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetWaterQualityResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "ppm":{
            "value": 10.0,
            "scale": "ug/L"
        }
    }
}
```

### GetFanSpeedRequest

当用户想了解设备当前风速时，DuerOS会将该消息发送给技能，比如想要了解风扇的当前风速时，可以说，"小度小度, 查询风扇的风速"， 这时技能会收到GetFanSpeedRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetFanSpeedRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，查询风扇的风速”，DuerOS接收到用户意图后，GetFanSpeedRequest。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetFanSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetFanSpeedResponse

当技能查询到设备当前风速时，需要给DuerOS返回该消息，告知用户当前设备最新的风速状态。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetFanSpeedResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息。 | 是 |
| attribute.name | 属性名称，取固定值"fanSpeed"。 | 是 |
| attribute.value | 属性值，整数或者string类型。 | 是 |
| attribute.scale | 属性值的单位，可以填空，单位默认为“档”。 | 是 |
| attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。 | 是 |
| attribute.legalValue | 属性值取值的合法范围。 | 是 |

[fanSpeed attribute定义](attributes.md#fanspeed属性)，为了兼容不存在整数档位的设备，添加了string类型支持。推荐优先使用整数类型的档位。

#### 应用举例

技能查询到“风扇风速为2”时，向DuerOS返回GetFanSpeedResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetFanSpeedResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "fanSpeed",
            "value": 2,
            "scale": "",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "[0, 10]"
        }]
    }
}
```

如果使用string类型档位，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetFanSpeedResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "fanSpeed",
            "value": "high",
            "scale": "",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "(min, low, middle, high, max, auto)"
        }]
    }
}
```

## 查询速度

### GetSpeedRequest

当用户想了解设备当前速度时，DuerOS会将该消息发送给技能，比如想要了解跑步机的当前速度时，可以说，"小度小度, 查询跑步机的速度"， 这时技能会收到GetSpeedRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetSpeedRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| speed | 速度信息。 | 是 |
| speed.value | 速度属性。current:当前, max:最大, min: 最小。 | 是 |

#### 应用举例

用户说“小度小度，跑步机当前速度是多少”，DuerOS接收到用户意图后，GetSpeedRequest。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        },
        "speed": {
            "value": "current"
        }
    }
}
```

### GetSpeedResponse

当技能查询到设备当前速度时，需要给DuerOS返回该消息，告知用户当前设备最新的速度状态。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetSpeedResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息。 | 是 |
| attribute.name | 属性名称，speed: 当前速度， maxSpeed: 最大速度， minSpeed: 最小速度。 | 是 |
| attribute.value | 属性值，整数或者string类型。 | 是 |
| attribute.scale | 属性值的单位，可以填空，当attribute.value为数值时，单位默认为（KM/H）目前支持的属性值如下:  * KM/H：千米每小时 * M/S：米每秒  。 当attribute.value是非数值，eg：“high”，scale为空。 | 是 |
| attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。 | 是 |
| attribute.legalValue | 属性值取值的合法范围。 | 是 |

[speed attribute定义](attributes.md#speed属性)，为了兼容不存在整数档位的设备，添加了string类型支持。推荐优先使用整数类型的档位。

#### 应用举例

技能查询到“跑步机速度为2公里每小时”时，向DuerOS返回GetSpeedResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetSpeedResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "speed",
            "value": 2,
            "scale": "KM/H",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "[0, 10]"
        }]
    }
}
```

如果使用string类型档位，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetSpeedResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "speed",
            "value": "high",
            "scale": "",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "(min, low, middle, high, max, auto)"
        }]
    }
}
```

## 查询运动信息

### GetMotionInfoRequest

当用户想了解跑步机跑了多长时间/多少公里/多少步时，DuerOS会将该消息发送给技能，比如想要了解在跑步机上跑了多久时，可以说，"小度小度, 我跑了多长时间"， 这时技能会收到GetMotionInfoRequest消息。
eg:我跑了多少米，我跑了多少步，我跑了多长时间，我消耗了多少卡路里。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetMotionInfoRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| motionInfo | 运动信息。 | 是 |
| motionInfo.type | 运动信息的类型。run:跑, walk: 走, consume: 消耗。 | 是 |
| motionInfo.metric | 运动信息的单位。howLong:时间, howFar: 距离, steps: 步长， calories： 卡路里。 | 是 |
| motionInfo.when | 运动信息的时间。today:今天, yesterday:昨天, theMonment:现在, theWeek:这周, theMonth:这个月。 | 是 |

#### 应用举例

用户说“小度小度，今天我跑了多长时间”，DuerOS接收到用户意图后，GetMotionInfoRequest。消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetMotionInfoRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        },
        "motionInfo": {
            "type": "run",
            "metric": "howLong",
            "when": "today"
        }
    }
}
```

### GetMotionInfoResponse

当技能查询到跑步机跑了多长时间/多少公里/多少步时，需要给DuerOS返回该消息，告知用户当前最新的运动信息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetMotionInfoResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息。 | 是 |
| attribute.name | 属性名称，取固定值"motionInfo"。 | 是 |
| attribute.value | 属性值，整数或者string类型。 | 是 |
| attribute.scale | 属性值的单位，可以填空，单位默认为(KM)。目前支持的属性值如下:  * KILOMETER：千米 * KM：千米 * METER：米 * STEP：步 * SECOND：秒 * MINUTE：分钟 * HOUR：小时 * CALORIES：卡路里  。 | 是 |
| attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。 | 是 |
| attribute.legalValue | 属性值取值的合法范围。 | 是 |

[motionInfo attribute定义](attributes.md#motioninfo属性)，为了兼容不存在整数档位的设备，添加了string类型支持。推荐优先使用整数类型的档位。

#### 应用举例

技能查询到“在跑步机上跑了2公里”时，向DuerOS返回GetMotionInfoResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetMotionInfoResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "motionInfo",
            "value": 2,
            "scale": "KM",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10,
            "legalValue": ""
        }]
    }
}
```

## 查询开关状态

### GetTurnOnStateRequest

当用户想了解设备开关状态时，DuerOS会该将消息发送给技能，比如想要了解灯的开关状态时，可以说，"小度小度, 台灯开了吗？"， 这时技能会收到GetTurnOnStateRequest消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTurnOnStateRequest |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，台灯开了吗？”，DuerOS接收到用户意图后，向技能发送GetTurnOnStateRequest消息。消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Ceiling Fan]"
        }
    }
}
```

### GetTurnOnStateResponse

当技能查询到设备开关状态时，需要给DuerOS返回该消息，告知用户设备的状态。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | GetTurnOnStateResponse |
| namespace | DuerOS.ConnectedHome.Query |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备的属性信息，最多支持上报10个属性。 | 是 |
| attribute.name | 属性名称，这里取"turnOnState"。 | 是 |
| attribute.value | 字符串，目前支持的属性值如下:  * ON：打开 * OFF：关闭  。 | 是 |
| attribute.scale | 属性值的单位名称，这里是空串''。 | 是 |
| attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。 | 是 |

#### 应用举例

技能查询到“扫地机器人当前的运行状态是正在清扫时”，向DuerOS返回GetTurnOnStateResponse消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Query",
        "name": "GetTurnOnStateResponse",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [{
            "name": "turnOnState",
            "value": "ON",
            "scale": "",
            "timestampOfSample":1496741861,
            "uncertaintyInMilliseconds": 10
        }]
    }
}
```
