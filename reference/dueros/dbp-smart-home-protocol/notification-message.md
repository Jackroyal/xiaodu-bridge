---
title: "通知消息"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/notification-message_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 通知消息

## 设备信息同步消息

该接口为厂商通知DuerOS的接口，当技能涉及的用户设备信息发生变化时，如用户新增设备或减少设备，此时技能可以通过设备信息同步接口请求DuerOS进行设备信息同步。

### 请求消息说明

技能向DuerOS发送请求消息，请求DuerOS同步设备变更信息。

#### 接口地址

```
https://xiaodu.baidu.com/saiya/smarthome/devicesync
```

#### 请求方式

POST请求方式

#### 参数说明

| 参数名称 | 参数说明 | 类型 | 是否必需 |
| --- | --- | --- | --- |
| botId | 技能ID。 | string | 是 |
| logId | 技能本次请求logId。 | string | 是 |
| openUids | 需要同步的用户openUid信息，每次同步的openUid不超过5个。 | array | 是 |

#### Head说明

| 参数名称 | 取值 |
| --- | --- |
| Content-Type | application/json |

#### 请求示例

```
curl -v "https://xiaodu.baidu.com/saiya/smarthome/devicesync" -H 'Content-Type:application/json' -d
'{
    "botId":"123456xyz-123456-4c5d-345677xyz",
    "logId":"123456789",
    "openUids":[
        "17a7d83c2d3cfbad5d387cd35f3ca17b"
    ]
}'
```

### 返回说明

当技能发起设备信息同步请求后，DuerOS返回信息同步确认消息。

#### 参数说明

| 参数名称 | 描述 | 类型 | 是否必须 |
| --- | --- | --- | --- |
| status | 请求消息状态。0表示消息正常，非0表示消息异常。 | int | 是 |
| msg | 请求消息同步状态，可能出现以下情况。  * ok：表示至少一个openUid同步成功。 * openUid not more than 5：表示openUid信息超过5个。 * not support botId：表示技能ID不存在。 * sync failed：表示请求信息同步失败。 * param error：表示参数不合法。 | string | 是 |
| logid | 请求消息中的logid。 | string | 是 |
| data | 返回消息的数据信息。 | array | 是 |
| data.failed | 同步失败的openUid集合。 | array | 是 |
| data.succeed | 同步成功的openUid集合。 | array | 是 |

#### 返回示例

```
{
    "status": 0,
    "msg": "ok",
    "logid": "123456789",
    "data": {
        "failed": [],
        "succeed": [
            "17a7d83c2d3cfbad5d387cd35f3ca17b"
        ]
    }
}
```

## 技能解绑消息通知

该接口为DuerOS通知厂商的接口。当用户在技能商店解绑智能家居技能时，DuerOS会使用该协议通知到技能服务器，以便第三方智能家居服务提供商获取到用户的这一行为而做出相应的逻辑变化，比如，用户解绑技能后，当用户新增设备时，不再通知DuerOS。协议使用HTTPS传输，采用JSON消息格式。

### UnbindBotRequest

当用在技能商店解绑该技能时，DuerOS会将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnbindBotRequest |
| namespace | DuerOS.ConnectedHome.UnbindBot |

#### Payload信息

| 属性 | 描述 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |

#### 应用举例

当用户在技能商店解绑了该技能时, DuerOS向技能发送UnbindBot消息，消息样例如下

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.UnbindBot",
        "name": "UnbindBotRequest",
        "messageId": "6d6d6e14-8aee-473e-8c24-0d31ff9c17a2",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth Token here]"
    }
}
```

### UnbindBotResponse

当DuerOS通知技能用户解绑了该技能，技能会返回UnbindBotResponse消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnbindBotResponse |
| namespace | DuerOS.ConnectedHome.UnbindBot |

#### Payload信息

Payload信息为空，DuerOS只是通知技能用户在DuerOS技能商店解绑了该技能。

#### 应用举例

当DuerOS向技能发送了解绑消息后，技能回复DuerOS消息样例如下

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.UnbindBot",
        "name": "UnbindBotResponse",
        "messageId": "6d6d6e14-8aee-473e-8c24-0d31ff9c17a2",
        "payloadVersion": "1"
    },
    "payload": {
    }
}
```
