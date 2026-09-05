---
title: "智能家居协议简介"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/intro-protocol_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 智能家居协议

## 简介

智能家居协议是DuerOS与智能家居技能之间的通讯协议。通过这些协议您可以轻松的通过语音控制家里的智能设备，与设备进行交互。智能家居协议使用HTTPS传输，协议采用JSON消息格式。

## 认证

智能家居协议遵循OAuth2.0规范。
从DuerOS发送到技能的每个请求都包含OAuth的access token。
<https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-account-linking/account-linking_markdown>

## 协议

智能家居协议指令（directives）由Header和Payload两部分组成。

### Header信息

Header包含消息标识符、指令名称、命令空间和payload版本信息。

#### 消息格式

```
{
    "header": {        
        "namespace": "DuerOS.ConnectedHome.Discovery",
        "name": "DiscoverAppliancesRequest",
        "messageId": "6d6d6e14-8aee-473e-8c24-0d31ff9c17a2",
        "payloadVersion": "1"
    }
}
```

#### 属性说明

Header包含的属性及属性说明。

| 属性 | 属性说明 | 是否必须 |
| --- | --- | --- |
| namespace | 指令的类别。 目前支持的类别有：  * DuerOS.ConnectedHome.Discovery：发现设备指令。 * DuerOS.ConnectedHome.Control：控制设备指令。 * DuerOS.ConnectedHome.Query：查询设备指令。 | 是 |
| name | 指令的名称。 | 是 |
| messageId | 消息的唯一标识符，长度小于128个字符。messageId仅用于标识消息，无其他使用。建议使用随机生成的UUID作为messageId。 | 是 |
| payloadVersion | payload的版本号。 | 是 |

### Payload信息

Payload的内容与Header中的name值相关，不同类型的指令，其payload内容也不相同。
