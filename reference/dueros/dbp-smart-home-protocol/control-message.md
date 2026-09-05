---
title: "控制消息"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/control-message_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 控制消息

控制消息(Control Message)是对智能家居设备进行控制的消息，技能应该根据自身IoT设备能力，来定义[IoT设备支持的操作-Action](discovery-message.md)，小度识别到用户控制意图后，再基于设备支持的操作，将对应的控制消息发送给设备云服务。

* [打开关闭设备](#打开关闭设备)
  + [TurnOnRequest](#turnonrequest)
  + [TurnOnConfirmation](#turnonconfirmation)
  + [TimingTurnOnRequest](#timingturnonrequest)
  + [TimingTurnOnConfirmation](#timingturnonconfirmation)
  + [TurnOffRequest](#turnoffrequest)
  + [TurnOffConfirmation](#turnoffconfirmation)
  + [TimingTurnOffRequest](#timingturnoffrequest)
  + [TimingTurnOffConfirmation](#timingturnoffconfirmation)
  + [PauseRequest](#pauserequest)
  + [PauseConfirmation](#pauseconfirmation)
  + [ContinueRequest](#continuerequest)
  + [ContinueConfirmation](#continueconfirmation)
  + [StartUpRequest](#startuprequest)
  + [StartUpConfirmation](#startupconfirmation)
* [可控灯光设备](#可控灯光设备)
  + [SetBrightnessPercentageRequest](#setbrightnesspercentagerequest)
  + [SetBrightnessPercentageConfirmation](#setbrightnesspercentageconfirmation)
  + [IncrementBrightnessPercentageRequest](#incrementbrightnesspercentagerequest)
  + [IncrementBrightnessPercentageConfirmation](#incrementbrightnesspercentageconfirmation)
  + [DecrementBrightnessPercentageRequest](#decrementbrightnesspercentagerequest)
  + [DecrementBrightnessPercentageConfirmation](#decrementbrightnesspercentageconfirmation)
  + [SetColorRequest](#setcolorrequest)
  + [SetColorConfirmation](#setcolorconfirmation)
  + [IncrementColorTemperatureRequest](#incrementcolortemperaturerequest)
  + [DecrementColorTemperatureRequest](#decrementcolortemperaturerequest)
  + [SetColorTemperatureRequest](#setcolortemperaturerequest)
* [可控温度设备](#可控温度设备)
  + [IncrementTemperatureRequest](#incrementtemperaturerequest)
  + [IncrementTemperatureConfirmation](#incrementtemperatureconfirmation)
  + [DecrementTemperatureRequest](#decrementtemperaturerequest)
  + [DecrementTemperatureConfirmation](#decrementtemperatureconfirmation)
  + [SetTemperatureRequest](#settemperaturerequest)
  + [SetTemperatureConfirmation](#settemperatureconfirmation)
* [可控风速设备](#可控风速设备)
  + [IncrementFanSpeedRequest](#incrementfanspeedrequest)
  + [IncrementFanSpeedConfirmation](#incrementfanspeedconfirmation)
  + [DecrementFanSpeedRequest](#decrementfanspeedrequest)
  + [DecrementFanSpeedConfirmation](#decrementfanspeedconfirmation)
  + [SetFanSpeedRequest](#setfanspeedrequest)
  + [SetFanSpeedConfirmation](#setfanspeedconfirmation)
* [可控速度设备](#可控速度设备)
  + [IncrementSpeedRequest](#incrementspeedrequest)
  + [IncrementSpeedConfirmation](#incrementspeedconfirmation)
  + [DecrementSpeedRequest](#decrementspeedrequest)
  + [DecrementSpeedConfirmation](#decrementspeedconfirmation)
  + [SetSpeedRequest](#setspeedrequest)
  + [SetSpeedConfirmation](#setspeedconfirmation)
* [设备模式设置](#设备模式设置)
  + [SetModeRequest](#setmoderequest)
  + [SetModeConfirmation](#setmodeconfirmation)
  + [UnsetModeRequest](#unsetmoderequest)
  + [UnsetModeConfirmation](#unsetmodeconfirmation)
  + [TimingSetModeRequest](#timingsetmoderequest)
  + [TimingSetModeConfirmation](#timingsetmodeconfirmation)
* [电视频道设置](#电视频道设置)
  + [IncrementTVChannelRequest](#incrementtvchannelrequest)
  + [IncrementTVChannelConfirmation](#incrementtvchannelconfirmation)
  + [DecrementTVChannelRequest](#decrementtvchannelrequest)
  + [DecrementTVChannelConfirmation](#decrementtvchannelconfirmation)
  + [SetTVChannelRequest](#settvchannelrequest)
  + [SetTVChannelConfirmation](#settvchannelconfirmation)
  + [ReturnTVChannelRequest](#returntvchannelrequest)
  + [ReturnTVChannelConfirmation](#returntvchannelconfirmation)
* [可控音量设备](#可控音量设备)
  + [IncrementVolumeRequest](#incrementvolumerequest)
  + [IncrementVolumeConfirmation](#incrementvolumeconfirmation)
  + [DecrementVolumeRequest](#decrementvolumerequest)
  + [DecrementVolumeConfirmation](#decrementvolumeconfirmation)
  + [SetVolumeRequest](#setvolumerequest)
  + [SetVolumeConfirmation](#setvolumeconfirmation)
  + [SetVolumeMuteRequest](#setvolumemuterequest)
  + [SetVolumeMuteConfirmation](#setvolumemuteconfirmation)
* [可锁定设备](#可锁定设备)
  + [SetLockStateRequest](#setlockstaterequest)
  + [SetLockStateConfirmation](#setlockstateconfirmation)
* [打印设备](#打印设备)
  + [SubmitPrintRequest](#submitprintrequest)
  + [SubmitPrintConfirmation](#submitprintconfirmation)
* [可控吸力设备](#可控吸力设备)
  + [SetSuctionRequest](#setsuctionrequest)
  + [SetSuctionConfirmation](#setsuctionconfirmation)
* [可控水量设备](#可控水量设备)
  + [SetWaterLevelRequest](#setwaterlevelrequest)
  + [SetWaterLevelConfirmation](#setwaterlevelconfirmation)
* [可控电量设备](#可控点量设备)
  + [ChargeRequest](#chargerequest)
  + [ChargeConfirmation](#chargeconfirmation)
  + [DischargeRequest](#dischargerequest)
  + [DischargeConfirmation](#dischargeconfirmation)
* [可控方向设备](#可控方向设备)
  + [SetDirectionRequest](#setdirectionrequest)
  + [SetDirectionConfirmation](#setdirectionconfirmation)
  + [SetCleaningLocationRequest](#setcleaninglocationrequest)
  + [SetCleaningLocationConfirmation](#setcleaninglocationconfirmation)
  + [SetComplexActionsRequest](#setcomplexactionsrequest)
  + [SetComplexActionsConfirmation](#setcomplexactionsconfirmation)
* [可控高度设备](#可控高度设备)
  + [IncrementHeightRequest](#incrementheightrequest)
  + [DecrementHeightRequest](#decrementheightrequest)
* [可控定时设备](#可控定时设备)
  + [SetTimerRequest](#settimerrequest)
  + [SetTimerConfirmation](#settimerconfirmation)
  + [TimingCancelRequest](#timingcancelrequest)
  + [TimingCancelConfirmation](#timingcancelconfirmation)
* [可复位设备](#可控复位设备)
  + [ResetRequset](#resetrequset)
  + [ResetConfirmation](#resetconfirmation)
* [可控楼层设备](#可控楼层设备)
  + [SetFloorRequest](#setfloorrequest)
  + [SetFloorConfirmation](#setfloorconfirmation)
  + [IncrementFloorRequest](#incrementfloorrequest)
  + [IncrementFloorConfirmation](#incrementfloorconfirmation)
  + [DecrementFloorRequest](#decrementfloorrequest)
  + [DecrementFloorConfirmation](#decrementfloorconfirmation)
* [可控湿度类设备](#可控湿度类设备)
  + [SetHumidityRequest](#sethumidityrequest)
  + [SetHumidityConfirmation](#sethumidityconfirmation)
* [可控挡位类设备](#可控挡位类设备)
  + [SetGearRequest](#setgearrequest)
  + [SetGearConfirmation](#setgearconfirmation)
* [可控水流类设备](#可控水流类设备)
  + [SetFlowRequest](#setflowrequest)
  + [SetFlowConfirmation](#setflowconfirmation)

## 打开关闭设备

打开关闭设备包括打开设备、定时打开设备、关闭设备、定时关闭设备、暂停设备等操作。

### TurnOnRequest

当用户想打开指定设备时，DuerOS会将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TurnOnRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，开灯”，DuerOS理解到用户意图后，向技能发送TurnOnRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Light]"
        }
    }
}
```

### TurnOnConfirmation

当请求的设备成功打开时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TurnOnConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 取值 | 是否必须 |
| --- | --- | --- |
| attributes | 设备控制后的状态或属性，支持返回多个，状态的定义一定是在[属性信息](attributes.md)列表中。注意不是控制前的状态，可以 |
| 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功打开时，技能向DuerOS发送TurnOnConfirmation消息，示例如下。

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
                "name": "turnOnState",
                "value": "ON",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(ON, OFF)"
            },
            {
                "name": "connectivity",
                "value": "REACHABLE",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(UNREACHABLE, REACHABLE)"
            }
        ]
    }
}
```

### TimingTurnOnRequest

当用户想在设定时间打开设备时，DuerOS会将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TimingTurnOnRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| timestamp | 表示设备定时设置的值，它指定一个数字，代表时间戳，单位是秒。 | 是 |

#### 应用举例

当用户说“小度小度，5分钟后开灯”，DuerOS理解用户意图后，会向技能发送TimingTurnOnRequest消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TimingTurnOnRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "timestamp": {
            "value": 1496741861
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### TimingTurnOnConfirmation

当请求设备在设定时间成功打开时，技能会将该消息发送给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TimingTurnOnConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当微波炉在设定时间5分钟打开时，技能会向DuerOS发送TimingTurnOnConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TimingTurnOnConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "turnOnState",
                "value": "ON",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(ON, OFF)"
            }
        ]
    }
}
```

### TurnOffRequest

当用户想关闭设备时，DuerOS会发送该消息给技能，通知技能关闭该设备。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TurnOffRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，帮我关闭电视”，DuerOS理解用户意图后，会向技能发送TurnOffRequest消息，示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### TurnOffConfirmation

当请求的设备成功关闭时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TurnOffConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功关闭时，技能会向DuerOS发送TurnOffConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TurnOffConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "turnOnState",
                "value": "OFF",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(ON, OFF)"
            }
        ]
    }
}
```

### TimingTurnOffRequest

当用户需要在设定的时间关闭设备时，DuerOS会向技能发送该消息，通知技能在设定时间关闭设备。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TimingTurnOffRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| timestamp | 表示设备定时设置的值，它指定一个数字，代表时间戳，单位是秒。 | 是 |

#### 应用举例

当用户说“小度小度，5分钟后关闭空调”，DuerOS理解用户意图后，会向技能发送TimingTurnOffRequest消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TimingTurnOffRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "timestamp": {
            "value": 1496741861
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### TimingTurnOffConfirmation

设备在设定时间成功关闭时，技能会将结果发送给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TimingTurnOffConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

烤箱在设定的30分钟关闭时，技能会向DuerOS发送TimingTurnOffConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TimingTurnOffConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "turnOnState",
                "value": "OFF",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(ON, OFF)"
            }
        ]
    }
}
```

### PauseRequest

当用户想暂停设备时，DuerOS会发送该消息给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | PauseRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，暂停窗帘”时，DuerOS了解用户意图后，会发送PauseRequest消息给技能。消息示例如下。

```
{
    "header": {    
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "PauseRequest",
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

### PauseConfirmation

设备成功暂停时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | PauseConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

洗衣机已经暂停，技能会向DuerOS发送PauseConfirmation消息，示例如下。

```
{
    "header": {        
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "PauseConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "pauseState",
                "value": true,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "BOOLEAN"
            }
        ]
    }
}
```

### ContinueRequest

当用户想设备继续之前的操作时，DuerOS会发送该消息给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ContinueRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，扫地机器人继续扫地”时，DuerOS了解用户意图后，会发送ContinueRequest消息给技能。消息示例如下。

```
{
    "header": {    
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ContinueRequest",
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

### ContinueConfirmation

设备成功接收指令并继续之前的操作时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ContinueConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

扫地机器人继续扫地后，技能会向DuerOS发送ContinueConfirmation消息，示例如下。

```
{
    "header": {        
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ContinueConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "pauseState",
                "value": false,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "BOOLEAN"
            }
        ]
    }
}
```

### StartUpRequest

当用户想启动指定设备时，DuerOS会将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | StartUpRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，启动洗衣机”，DuerOS理解到用户意图后，向技能发送StartUpRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "StartUpRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for Light]"
        }
    }
}
```

### StartUpConfirmation

当请求的设备成功启动时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | StartUpConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 取值 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当洗衣机成功启动时，技能向DuerOS发送StartUpConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "StartUpConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

## 可控灯光设备

可控灯光控制消息可以控制灯光的亮度、控制灯光的颜色。

### SetBrightnessPercentageRequest

当用户发出将灯光调到具体亮度值的请求时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetBrightnessPercentageRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| brightness | 灯光亮度的对象。 | 是 |
| brightness.value | 灯光亮度的百分比值，是double类型，取值范围为0～100。其中0表示灯在打开时的最小亮度，100表示灯的最大亮度。 | 是 |

#### 应用举例

当用户说“小度小度，将灯光亮度调到50%”时，DuerOS了解用户意图后，会发送SetBrightnessPercentageRequest消息给技能，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetBrightnessPercentageRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "brightness": {
            "value": 50.0
        }
    }
}
```

### SetBrightnessPercentageConfirmation

当灯光亮度设置成功后，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetBrightnessPercentageConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当灯光亮度设置成功时，技能会向DuerOS发送SetBrightnessPercentageConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetBrightnessPercentageConfirmation",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "brightness",
                "value": 50,
                "scale": "%",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        ]
    }
}
```

### IncrementBrightnessPercentageRequest

当用户需要将灯光调亮一点时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementBrightnessPercentageRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaPercentage | 亮度的百分比增量信息，包含value。 | 是 |
| deltaPercentage.value | 亮度增加的百分比值，是float类型，取值范围是0～100。 | 是 |

#### 应用举例

用户说“小度小度，把卧室的灯调亮一些”，DuerOS接收该意图时，发送IncrementBrightnessPercentageRequest消息给技能。示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementBrightnessPercentageRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaPercentage": {
            "value": 10.0
        }
    }
}
```

### IncrementBrightnessPercentageConfirmation

当灯光成功调亮时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementBrightnessPercentageConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

卧室灯光成功调亮时，技能会向DuerOS发送IncrementBrightnessPercentageConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementBrightnessPercentageConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "brightness",
                "value": 50,
                "scale": "%",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        ]
    }
}
```

### DecrementBrightnessPercentageRequest

当用户需要将灯光调暗时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementBrightnessPercentageRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaPercentage | 亮度的百分比减量信息。 | 是 |
| deltaPercentage.value | 亮度减少的百分比值，是float类型，取值范围是0～100。 | 是deltaPercentage的必须项。 |

#### 应用举例

用户说“小度小度，把卧室的灯调暗一点”，DuerOS接收到该意图时，会向技能发送DecrementBrightnessPercentageRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementBrightnessPercentageRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaPercentage": {
            "value": 10.0
        }
    }
}
```

### DecrementBrightnessPercentageConfirmation

当灯光亮度成功调暗时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementBrightnessPercentageConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

灯光亮度成功调暗时，技能会向DuerOS发送DecrementBrightnessPercentageConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementBrightnessPercentageConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "brightness",
                "value": 50,
                "scale": "%",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        ]
    }
}
```

### SetColorRequest

用户需要设置灯光颜色时，DuerOS会向技能发送该消息，通知技能调整灯光颜色。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetColorRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| color | 灯设置的颜色。包括[色相、饱和度、亮度（HSB）颜色模型](https://en.wikipedia.org/wiki/HSL_and_HSV)。 | 是 |
| color.hue | 灯光设置的色相，是double类型，取值范围为0.00〜360.00。 | 是 |
| color.saturation | 灯光设置饱和度，是double类型，取值范围为0.0000〜1.0000。 | 是 |
| color.brightness | 灯光设置的亮度，是double类型，取值范围为0.0000〜1.0000。 | 是 |

#### 应用举例

用户说：“小度小度，把卧室的灯设置为红色”，DuerOS了解到该意图时，会向技能发送SetColorRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetColorRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "color": {
            "hue": 350.5,
            "saturation": 0.7138,
            "brightness": 0.6524
        }
    }
}
```

### SetColorConfirmation

当灯光颜色成功设定时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetColorConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当卧室灯光成功调成红色时，技能会向DuerOS发送SetColorConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetColorConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "color",
                "value": {
                    "hue": 350.5,
                    "saturation": 0.7138,
                    "brightness": 0.6524
                },
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "OBJECT"
            }
        ]
    }
}
```

### IncrementColorTemperatureRequest

调高色温值，使灯光变冷，用户说:“小度小度，台灯增加冷色光”，DuerOS 了解到该意图时，会向技能发送IncrementColorTemperatureRequest消息，消息示例如下:

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementColorTemperatureRequest", 
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688", 
        "payloadVersion": "1"
    }, 
    "payload": {
        "accessToken": "[OAuth token here]", 
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]" 
        },
         "deltaPercentage": {
            "value": 10.0
        }
    } 
}
```

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementColorTemperatureRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaPercentage | 色温的百分比增量信息，包含value。 | 是 |
| deltaPercentage.value | 色温增加的百分比值，是float类型，取值范围是0～100。 | 是 |

### IncrementColorTemperatureConfirmation

灯光色温增高成功时，技能对DuerOS的请求响应IncrementColorTemperatureConfirmation消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementColorTemperatureConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。色温属性取值范围legalValue，根据设备实际范围上报。 |

#### 应用举例

消息示例如下：

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementColorTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "colorTemperatureInKelvin",
                "value": 3000,
                "scale": "K",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[1000, 10000]"
            }
        ]
    }
}
```

### DecrementColorTemperatureRequest

调低色温值，使灯光变暖，用户说:“小度小度，台灯增加暖色光”，DuerOS了解到该意图时，会向技能发送DecrementColorTemperatureRequest消息，消息示例如下:

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementColorTemperatureRequest", 
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688", 
        "payloadVersion": "1"
    }, 
    "payload": {
        "accessToken": "[OAuth token here]", 
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]" 
        },
        "deltaPercentage": {
            "value": 10.0
        }
    } 
}
```

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementColorTemperatureRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaPercentage | 色温的百分比减量信息，包含value。 | 是 |
| deltaPercentage.value | 色温减小的百分比值，是float类型，取值范围是0～100。 | 是 |

### DecrementColorTemperatureConfirmation

灯光色温降低成功时，技能对DuerOS的请求响应DecrementColorTemperatureConfirmation消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementColorTemperatureConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。色温属性取值范围legalValue，根据设备实际范围上报。 |

#### 应用举例

消息示例如下：

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementColorTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "colorTemperatureInKelvin",
                "value": 3000,
                "scale": "K",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[1000, 10000]"
            }
        ]
    }
}
```

### SetColorTemperatureRequest

用户说:“小度小度，把灯调成暖色光”，DuerOS了解到该意图时，会向技能发送SetColorTemperatureRequest消息，消息示例如下:

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetColorTemperatureRequest", 
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688", 
        "payloadVersion": "1"
    }, 
    "payload": {
        "accessToken": "[OAuth token here]", 
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]" 
        },
        "colorTemperatureInKelvin": 2800
    } 
}
```

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetColorTemperatureRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| colorTemperatureInKelvin | 色温值。 | 是 |

### SetColorTemperatureConfirmation

灯光色温调节成功时，技能对DuerOS的请求响应SetColorTemperatureConfirmation消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetColorTemperatureConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。色温属性取值范围legalValue，根据设备实际范围上报。 |

#### 应用举例

消息示例如下：

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetColorTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "colorTemperatureInKelvin",
                "value": 3000,
                "scale": "K",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[1000, 10000]"
            }
        ]
    }
}
```

## 可控温度设备

可控温度设备可以通过语音升高或者降低设备的温度，也可以设定设备的温度。

### IncrementTemperatureRequest

当用户需要把设备温度调高时，DuerOS会发送该消息给技能，通知技能调高设备温度。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementTemperatureRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备温度的增量信息。 | 否， 当值为空时表示用户没有指定调高的具体值 |
| deltaValue.value | 设备温度增量的具体值，是float类型。 | 当deltaValue存在时，该项必须存在。 |
| deltaValue.scale | 温度计量单位。有CELSIUS(摄氏温度)和FAHRENHEIT(华氏温度)两种计量单位，默认使用CELSIUS。 | 在deltaValue不为空时为是 |

#### 应用举例

用户说“小度小度，把卧室的温度调高一点”，DuerOS了解用户意图，会向技能发送IncrementTemperatureRequest消息，消息样例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue": {
            "value": 1.0,
            "scale": "CELSIUS"
        }
    }
}
```

### IncrementTemperatureConfirmation

设备温度成功调高时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementTemperatureConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，模式取值范围legalValue，根据设备支持的模式自行设定。 |

#### 应用举例

卧室温度调高成功时，技能会向DuerOS发送IncrementTemperatureConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "temperature",
                "value": 16,
                "scale": "CELSIUS",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[16, 31]"
            },
            {
                "name": "targetTemperature",
                "value": 20,
                "scale": "CELSIUS",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[16, 31]"
            },
            {
                "name": "mode",
                "value": "SLEEP",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, DEHUMIDIFICATION)"
            }
        ]
    }
}
```

### DecrementTemperatureRequest

当用户需要调低设备温度时，DuerOS会发送该消息给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementTemperatureRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备温度的减量信息。 | 否， 当值为空时表示用户没有指定调高的具体值 |
| deltaValue.value | 设备温度减量的具体值，是float类型。 | 当deltaValue存在时，该项必须存在。 |
| deltaValue.scale | 温度计量单位。有CELSIUS(摄氏温度)和FAHRENHEIT(华氏温度)两种计量单位，默认使用CELSIUS。 | 在deltaValue不为空时为是 |

#### 应用举例

用户说“小度小度，帮我把客厅温度调低一点”，DuerOS收到用户意图时，会向技能发送DecrementTemperatureRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue": {
            "value": 1.0,
            "scale": "CELSIUS"
        }
    }
}
```

### DecrementTemperatureConfirmation

当设备温度成功调低时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementTemperatureConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，模式取值范围legalValue，根据设备支持的模式自行设定。 |

#### 应用举例

当客厅温度调低成功时，技能会向DuerOS发送该DecrementTemperatureConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "temperature",
                "value": 16,
                "scale": "CELSIUS",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[16, 31]"
            },
            {
                "name": "targetTemperature",
                "value": 20,
                "scale": "CELSIUS",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[16, 31]"
            },
            {
                "name": "mode",
                "value": "SLEEP",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, DEHUMIDIFICATION)"
            }
        ]
    }
}
```

### SetTemperatureRequest

当用户需要设置设备温度时，DuerOS向技能发送该消息，通知技能调整温度。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetTemperatureRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| targetTemperature | 设备设定的目标温度。 | 是 |
| targetTemperature.value | 设备设定的目标温度值。 | 是 |
| targetTemperature.scale | 温度计量单位。有CELSIUS(摄氏温度)和FAHRENHEIT(华氏温度)两种计量单位，默认使用CELSIUS。 | 是 |

#### 应用举例

用户说“小度小度，把客厅温度设置为23度”，DuerOS了解用户意图，向技能发送SetTemperatureRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetTemperatureRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "targetTemperature": {
            "value": 23,
            "scale": "CELSIUS"
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### SetTemperatureConfirmation

当设备温度设置成功时，技能向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetTemperatureConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，模式取值范围legalValue，根据设备支持的模式自行设定。 |

#### 应用举例

当客厅温度成功设置成23度时，技能向DuerOS发送SetTemperatureConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetTemperatureConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "temperature",
                "value": 16,
                "scale": "CELSIUS",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[16, 31]"
            },
            {
                "name": "targetTemperature",
                "value": 20,
                "scale": "CELSIUS",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[16, 31]"
            },
            {
                "name": "mode",
                "value": "SLEEP",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, DEHUMIDIFICATION)"
            }
        ]
    }
}
```

## 可控风速设备

可控风速设备消息用于控制设备风速，常用的操作有增大设备风速、减小设备风速、设置设备风速、设置设备模式、取消设备模式等。

### IncrementFanSpeedRequest

用户需要加大设备的风速时，DuerOS会向技能发送该消息，通知技能加大风速。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementFanSpeedRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备风速的增量信息。 | 否 |
| deltaValue.value | 设备风速增量的具体值，是int类型。 | deltaValue对象的必须项 |

**说明**：若设备风速增加后的值超越了设备风速的最大值，此时会返回ValueOutOfRangeError错误信息。

#### 应用举例

用户说“小度小度，把空调的风速调大一些”，DuerOS了解用户意图后，向技能发送IncrementFanSpeedRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementFanSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue" : {
            "value" : 1
        }
    }
}
```

### IncrementFanSpeedConfirmation

设备风速增加成功时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementFanSpeedConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，风速取值范围legalValue，根据设备风速范围设定，模式也是一样。 |

#### 应用举例

当空调的风速变大时，技能向DuerOS发送IncrementFanSpeedConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementFanSpeedConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "fanSpeed",
                "value": 2,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 10]"
            },
            {
                "name": "mode",
                "value": "SLEEP",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, DEHUMIDIFICATION)"
            }
        ]
    }
}
```

### DecrementFanSpeedRequest

当用户需要减小设备风速时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementFanSpeedRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备风速的减量信息。 | 否 |
| deltaValue.value | 设备风速减量的具体值，是int类型。 | deltaValue对象的必须项 |

#### 应用举例

用户说“小度小度，把空调的风速调小一点”，DuerOS接收到用户意图后，向技能发送DecrementFanSpeedRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementFanSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue" : {
            "value" : 1
        }
    }
}
```

### DecrementFanSpeedConfirmation

当设备风速成功减小时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementFanSpeedConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，风速取值范围legalValue，根据设备风速范围设定，模式也是一样。 |

#### 应用举例

当空调风速调小后，技能向DuerOS发送DecrementFanSpeedConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementFanSpeedConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "fanSpeed",
                "value": 2,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 10]"
            },
            {
                "name": "mode",
                "value": "SLEEP",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, DEHUMIDIFICATION)"
            }
        ]
    }
}
```

### SetFanSpeedRequest

当用户需要设置设备的风速时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetFanSpeedRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| fanSpeed | 设备的风速对象，包含一个属性值value或者一个属性值level，取决于用户自然表达。 | 是 |
| fanSpeed.value | 设备的风速值，是int类型，取值范围是1～10。用户表达具体风速值时，会出该字段。 | 否 |
| fanSpeed.level | 设备的风速档位级别，是string类型，取值范围是(min、low、middle、high、max、auto))。用户表达风速级别时，会出该字段。 | 否 |

#### 应用举例

用户说“小度小度，把空调的风速设为2档”，DuerOS接收用户意图后，向技能发送SetFanSpeedRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetFanSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "fanSpeed": {
            "value": 2
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

用户说“小度小度，把空调的风速设为高速风”，DuerOS接收用户意图后，向技能发送SetFanSpeedRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetFanSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "fanSpeed": {
            "level": "high"
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### SetFanSpeedConfirmation

设备风速设定成功时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetFanSpeedConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，风速取值范围legalValue，根据设备风速范围设定，模式也是一样。 |

#### 应用举例

当空调风速设定为2档成功时，技能向DuerOS发送SetFanSpeedConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetFanSpeedConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "fanSpeed",
                "value": 2,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 10]"
            },
            {
                "name": "mode",
                "value": "SLEEP",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, DEHUMIDIFICATION)"
            }
        ]
    }
}
```

## 可控速度设备

可控速度设备消息用于控制设备速度，常用的操作有增大设备速度、减小设备速度、设置设备速度、设置设备模式、取消设备模式等。

### IncrementSpeedRequest

用户需要加大设备的速度时，DuerOS会向技能发送该消息，通知技能加大速度。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementSpeedRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备速度的增量信息。 | 否 |
| deltaValue.value | 设备速度增量的具体值, 小数点后保持2位的float。 | deltaValue对象的必须项 |

**说明**：若设备速度增加后的值超越了设备速度的最大值，此时会返回ValueOutOfRangeError错误信息。

#### 应用举例

用户说“小度小度，把跑步机的速度调大一些”，DuerOS了解用户意图后，向技能发送IncrementSpeedRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue" : {
            "value" : 1.00
        }
    }
}
```

### IncrementSpeedConfirmation

设备速度增加成功时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementSpeedConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，速度取值范围legalValue，根据设备速度范围自行定义。 |

#### 应用举例

当空调的速度变大时，技能向DuerOS发送IncrementSpeedConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementSpeedConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "speed",
                "value": 2.0,
                "scale": "KM/H",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 10]"
            }
        ]
    }
}
```

### DecrementSpeedRequest

当用户需要减小设备速度时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementSpeedRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备速度减量信息。 | 否 |
| deltaValue.value | 设备速度减量的具体值, 小数点后保持2位的float。 | deltaValue对象的必须项 |

#### 应用举例

用户说“小度小度，把跑步机的速度调小一点”，DuerOS接收到用户意图后，向技能发送DecrementSpeedRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue" : {
            "value" : 1.00
        }
    }
}
```

### DecrementSpeedConfirmation

当设备速度成功减小时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementSpeedConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，速度取值范围legalValue，根据设备速度范围自行定义。 |

#### 应用举例

当空调速度调小后，技能向DuerOS发送DecrementSpeedConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementSpeedConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "speed",
                "value": 2.0,
                "scale": "KM/H",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 10]"
            }
        ]
    }
}
```

### SetSpeedRequest

当用户需要设置设备的速度时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetSpeedRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| speed | 设备的速度对象，包含一个属性值value或者一个属性值level，取决于用户自然表达。 | 是 |
| speed.value | 设备的速度值, 小数点后保持2位的float。用户表达具体速度值时，会出该字段。 | 否 |
| speed.level | 设备的速度档位级别，是string类型，取值范围是(min、low、middle、high、max、auto))。用户表达速度级别时，会出该字段。 | 否 |

#### 应用举例

用户说“小度小度，把跑步机的速度设为2公里每小时”，DuerOS接收用户意图后，向技能发送SetSpeedRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "speed": {
            "value": 2.00
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

用户说“小度小度，把跑步机的速度设为高速”，DuerOS接收用户意图后，向技能发送SetSpeedRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetSpeedRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "speed": {
            "level": "high"
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### SetSpeedConfirmation

设备速度设定成功时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetSpeedConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，速度取值范围legalValue，根据设备速度范围自行定义。 |

#### 应用举例

当跑步机速度设定为2公里每小时成功时，技能向DuerOS发送SetSpeedConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetSpeedConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "speed",
                "value": 2.0,
                "scale": "KM/H",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 10]"
            }
        ]
    }
}
```

## 设备模式设置

### SetModeRequest

当用户需要设置设备的模式时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetModeRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| mode | 设备的模式信息。 | 是 |
| mode.value | 设备模式，详细信息请参见[设备模式表](#设备类型与模式表)。 | 是 |

#### 应用举例

用户说“小度小度，把空调调成制冷模式”，DuerOS理解用户意图后，向技能发送SetModeRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetModeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "mode": {
            "value": "COOL"
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### SetModeConfirmation

当设备的模式设置成功时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetModeConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。设备模式，请参考[设备模式表](#设备类型与模式表)，legalValue根据设备自身模式范围，自行设定。 |

#### 应用举例

设备模式设置成功时，技能向DuerOS发送SetModeConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetModeConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "mode",
                "value": "COOL",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, SLEEP)"
            }
        ]
    }
}
```

### UnsetModeRequest

当用户需要取消设置的模式时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnsetModeRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| mode | 设备的模式信息。 | 是 |
| mode.value | 设备模式，详细信息请参见[设备模式表](#设备类型与模式表)。 | 是 |

#### 应用举例

用户说“小度小度，取消空调制冷模式”时，DuerOS会发送UnsetModeRequest消息给技能，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "UnsetModeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "mode": {
            "value": "AUTO"
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### UnsetModeConfirmation

取消模式设置成功时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnsetModeConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。设备模式，请参考[设备模式表](#设备类型与模式表)，legalValue根据设备自身模式范围，自行设定。 |

#### 应用举例

取消模式设置成功时，技能会给DuerOS发送UnsetModeConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "UnsetModeConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "mode",
                "value": "COOL",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, SLEEP)"
            }
        ]
    }
}
```

### TimingSetModeRequest

当用户需要设备在设定的时间调整到指定模式时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TimingSetModeRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| mode | 设备的模式信息。 | 是 |
| mode.value | 设备模式，详细信息请参见[设备模式表](#设备类型与模式表)。 | 是 |

#### 应用举例

用户说“小度小度，1分钟后把空调调成制冷模式”，DuerOS了解用户意图后，会向技能发送TimingSetModeRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TimingSetModeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "mode": {
            "value": "COOL"
        },
        "timestamp": {
            "value": 60
        },
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### TimingSetModeConfirmation

当设备在设定的时间调整到指定的模式时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TimingSetModeConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。设备模式，请参考[设备模式表](#设备类型与模式表)，legalValue根据设备自身模式范围，自行设定。 |

#### 应用举例

当空调在1分钟后成功调成制冷模式时，技能向DuerOS发送TimingSetModeConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "TimingSetModeConfirmation",
        "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "mode",
                "value": "COOL",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(COOL, HEAT, AUTO, FAN, SLEEP)"
            }
        ]
    }
}
```

### 设备类型与模式表

不同设备类型，一般模式取值不同，根据自身设备，定义自身设备模式取值范围。另外，跨设备类型，模式名称可以通用，这里定义设备类型和模式的关系，便于理解和查找。

| 设备类型 | 设备模式 |
| --- | --- |
| LIGHT | * READING：阅读 * SLEEP：睡眠 * ALARM：报警 * NIGHT_LIGHT：夜灯 * ROMANTIC：浪漫 * SUNDOWN：日落 * SUNRISE：日出 * RELAX ：休闲/放松 * LIGHTING ：照明 * SUN ：太阳 * STAR ：星星 * ENERGY_SAVING：节能 * MOON：月亮 * JUDI：蹦迪 |
| AIR_CONDITION | * COOL：制冷 * HEAT：制热 * AUTO：自动 * FAN：送风 * DEHUMIDIFICATION：除湿 * SLEEP：睡眠 * CLEAN：净化 * NAI：负离子 * NO_WIND_FEELING: 无风感 * NO_UP_WIND_FEELING: 上无风感 * NO_DOWN_WIND_FEELING: 下无风感 * UP_DOWN_SWING: 上下摆风 * LEFT_RIGHT_SWING: 左右摆风 |
| AIR_PURIFIER | * SLEEP：睡眠 * HOME：回家 * OUT：离家 * AUTO：自动 * MANUAL：手动 * MUTE：静音 * INTELLIGENT：智能 * HIGHSPEED：急速 * DUST_REMOVE：除尘 * HCHO_FREE：除甲醛 * NAI：负离子 |
| INDUCTION_COOKER | * QUICK_FIRE：快速火 * SLOW：温火 * FRY：煎炸 * STEWING：蒸煮/炖煮 * SOUP：汤粥/煲汤 * HOT_POT：火锅 |
| SWEEPING_ROBOT | * RANDOM：随机 * AUTO：自动 * FOCUS：重点 * EDGE：沿边 * BOW：弓形 * SPIRAL：螺旋 * AUTO：自动(清扫/拖地) * FOCUS：定点(清扫/拖地) * ALONG_EDGE：延边(清扫/拖地) * ANTI_DISTURB：防打扰 * 蛇形：S_STYLE * Z形：Z_STYLE * 精细：FINE * 回充：CHARGE * 安静：QUIET * 标准：STANDARD * 强力：POWERFUL * MAX：MAX |
| AIR_HEATER | * HIGH_HEAT：高热 * LOW_HEAT：低热 * COOL：冷风 |
| MICROWAVE_OVEN | * MICROWAVE：微波 * BARBECUE：烧烤 * THAW：解冻 |
| OVEN | * FERMENTATION：发酵 * DOUBLE_TUBE：双管 * THAW：解冻 |
| FAN | * NIGHT：夜间 * SWING：摆动/摆风 * SINGLE：单人 * MULTI：多人 * SPURT：喷射 * SPREAD：扩散 * QUIET：安静 * NORMAL：正常风速/适中风速/一般风速 * POWERFUL：强效 * MUTE：静音风速 * NATURAL：自然风速 * BABY：无感风速/轻微风速 * COMFORTABLE：舒适风速 * FEEL：人感风速 |
| RICE_COOKER | * HOTTING：加热/热饭/再加热 * INSULATED：保温 * SOUP：煮粥/煲汤/杂粮粥 * FAST_SOUP：快速粥 * STEWING：蒸煮/炖煮/美味蒸 * NORMAL_RICE：蒸米饭 * MIXED_RICE：杂粮饭 * SMALL_RICE：小米饭 * GERMINATED_RICE：发芽饭 |
| AIR_FRESHER | * NORMAL：普通模式 * AUTO：自动模式 * SLEEP：睡眠模式 * HEAT：加热模式 |
| WASHING_MACHINE | * STANDARD：标准 * DRY：干洗 * WASH_DRY：洗烘 * FAST_WASH：快洗 * DOWN_JACKET：羽绒服 |
| RANGE_HOOD | * HIGH：高速 * MIDDLE：中速 * LOW：低速 * STIR_FRY：爆炒 |
| FRIDGE | * INTELLIGENT：智能 * FAST_FREEZE：速冻 * FAST_COOL：速冷 * MANUAL：手动设定 * ICE_DRINK：冰饮功能 * HOLIDY：假日 |
| WATER_PURIFIER | * CLEAN：冲洗 * ADD_WATER：取水 * SMALL_CUP：小杯 * MIDDLE_CUP：中杯 * BIG_CUP：大杯 * NORMAL：常温 * BOILING：开水 * TEA：泡茶 * MILK：冲奶 |
| CLOTHES_RACK | * DRYING：烘干 * AIR_DRY：风干 * DISINFECT：消毒 |
| SOFA | * READING：阅读(读书，看书) * MUSIC：音乐(听音乐) * LIE：躺姿(平躺，躺下) * SIT：坐姿(坐下) |
| BED | * ZERO_GREVITY：零重力 * CINEMA：影院 * READING：阅读 * SLEEP：睡眠 |
| SHOE_CABINET | * DEODORIZATION：除臭 * STERILIZATION：杀菌 * AIR_DRY：风干 * DRYING：烘干 * AUTO：自动 * CUSTOM：自定义 |
| WALL_HUNG_GAS_BOILER | * SPRING：春季 * SUMMER：夏季 * AUTUMN：秋季 * WINTER：冬季 * ADVANCED：高级 |

## 电视频道设置

### IncrementTVChannelRequest

用户需要观看下一个电视频道，DuerOS会向技能发送该消息，通知技能设置电视到下一个频道。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementTVChannelRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，电视调到下一个台”，DuerOS了解用户意图后，会向技能发送IncrementTVChannelRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementTVChannelRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        }
    }
}
```

### IncrementTVChannelConfirmation

当电视成功调整到下一频道时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementTVChannelConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功调整下一台时，技能向DuerOS发送IncrementTVChannelConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementTVChannelConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### DecrementTVChannelRequest

用户需要观看上一个电视频道，DuerOS会向技能发送该消息，通知技能设置电视到上一个频道。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementTVChannelRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，电视调到上一个台”，DuerOS了解用户意图后，会向技能发送DecrementTVChannelRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementTVChannelRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        }
    }
}
```

### DecrementTVChannelConfirmation

当电视成功调整上一个频道时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementTVChannelConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功调整上一台时，技能向DuerOS发送DecrementTVChannelConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementTVChannelConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### ReturnTVChannelRequest

用户需要返回之前电视频道，DuerOS会向技能发送该消息，通知技能设置电视返回上一个观看频道。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ReturnTVChannelRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，电视返回上一个台”，DuerOS了解用户意图后，会向技能发送ReturnTVChannelRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ReturnTVChannelRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        }
    }
}
```

### ReturnTVChannelConfirmation

当请求的电视成功返回上一台时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ReturnTVChannelConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功返回上一台时，技能向DuerOS发送ReturnTVChannelConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ReturnTVChannelConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### SetTVChannelRequest

用户需要观看某一电视频道，DuerOS会向技能发送该消息，通知技能设置电视调整到该频道。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetTVChannelRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备电视频道变化信息。 | 否， 当值为空时表示用户没有指定频道信息 |
| deltaValue.value | 设备频道变化值，int类型或者string类型。当是int类型时, 表示数字频道；当是字符串时，表示频度名称，比如湖南卫视、中央一套等。 | 当deltaValue存在时，该项必须存在。 |

#### 应用举例

用户说“小度小度，电视调到3频道”，DuerOS了解用户意图后，会向技能发送SetTVChannelRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetTVChannelRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "deltaValue": {
            "value": 3 
        }
    }
}
```

### SetTVChannelConfirmation

当请求的电视成功设置频道，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetTVChannelConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功调整到3频道时，技能向DuerOS发送SetTVChannelConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetTVChannelConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

## 可控音量设备

### IncrementVolumeRequest

用户需要增大设备音量，DuerOS会向技能发送该消息，通知技能设置设备增大音量。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementVolumeRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备音量增量信息，为空时表示用户没有指定音量调节的具体值。 | 否 |
| deltaValue.value | 设备增大音量值，是int类型。音量范围0-100 | 当deltaValue存在时，该项必须存在。 |

#### 应用举例

用户说“小度小度，电视音量大点”，DuerOS了解用户意图后，会向技能发送IncrementVolumeRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementVolumeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "deltaValue": {
            "value": 2 
        }
    }
}
```

### IncrementVolumeConfirmation

当请求的设备成功调大音量，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementVolumeConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功调调大音量，技能向DuerOS发送IncrementVolumeConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementVolumeConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "volume",
                "value": 50,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        ]
    }
}
```

### DecrementVolumeRequest

用户需要减小设备音量，DuerOS会向技能发送该消息，通知技能设置设备减小音量。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementVolumeRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备音量减量信息。 | 否， 当值为空时表示用户没有指定音量调小的具体值 |
| deltaValue.value | 设备减小音量值，是int类型。音量范围0-100 | 当deltaValue存在时，该项必须存在。 |

#### 应用举例

用户说“小度小度，电视音量小点”，DuerOS了解用户意图后，会向技能发送DecrementVolumeRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementVolumeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "deltaValue": {
            "value": 2 
        }
    }
}
```

### DecrementVolumeConfirmation

当请求的设备成功减小音量，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementVolumeConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功调小音量，技能向DuerOS发送DecrementVolumeConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementVolumeConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "volume",
                "value": 50,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        ]
    }
}
```

### SetVolumeRequest

当用户需要设置设备的音量时，DuerOS会向技能发送该消息，通知技能设置设备的音量。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetVolumeRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备音量变化信息。 | 否， 当值为空时表示用户没有指定音量调小的具体值 |
| deltaValue.value | 设备音量变化值，是int类型。音量范围0-100 | 当deltaValue存在时，该项必须存在。 |

#### 应用举例

用户说“小度小度，电视音量调到30”，DuerOS了解用户意图后，会向技能发送SetVolumeRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetVolumeRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "deltaValue": {
            "value":  30 
        }
    }
}
```

### SetVolumeConfirmation

当设备成功设置音量后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetVolumeConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视音量调到30时，技能向DuerOS发送SetVolumeConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetVolumeConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "volume",
                "value": 50,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        ]
    }
}
```

### SetVolumeMuteRequest

当用户需要对设备进行静音或取消静音操作时，DuerOS会向技能发送该消息，通知技能设置设备的静音状态。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetVolumeMuteRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 设备静音开关的变化信息。 | 是 |
| deltaValue.value | 设备静音状态，枚举类型，取值为如下。  * on：将设备设置为静音状态。 * off：取消设备的静音。 | 是 |

#### 应用举例

用户说“小度小度，将电视静音”，DuerOS了解用户意图后，会向技能发送SetVolumeMuteRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetVolumeMuteRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "deltaValue": {
            "value":  "on" 
        }
    }
}
```

### SetVolumeMuteConfirmation

当设备成功的设置静音状态时，如静音或取消静音，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetVolumeMuteConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电视成功调整到静音时，技能向DuerOS发送SetVolumeMuteConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetVolumeMuteConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "muteState",
                "value": true,
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "BOOLEAN"
            }
        ]
    }
}
```

## 可锁定设备

### SetLockStateRequest

当用户发出对设备进行锁定或解除锁定操作的请求时，包括童锁的锁定和解除锁定的操作，DuerOS会向技能发送该消息，通知技能设置设备的锁定状态。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetLockStateRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| lockState | 设备当前锁定状态，枚举类型，取值如下。  * LOCKED：设备处于锁定状态。 * UNLOCKED：设备处于解锁状态。 | 是 |

#### 应用举例

用户说“小度小度，冰箱按键锁定”，DuerOS了解用户意图后，会向技能发送SetLockStateRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetLockStateRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "lockState":"LOCKED"
    }
}
```

### SetLockStateConfirmation

当设置设备锁定状态成功时，如设置锁定或解除锁定操作成功，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetLockStateConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| lockState | 设备锁定状态信息。 | 是 |
| lockState.value | 设备当前锁定状态，枚举类型，取值如下。  * LOCKED：设备处于锁定状态。 * UNLOCKED：设备处于解锁状态。 | 是 |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当冰箱按键成功锁定时，技能向DuerOS发送SetLockStateConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetLockStateConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "lockState",
                "value": "LOCKED",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(LOCKED, UNLOCKED, JAMMED)"
            }
        ]
    }
}
```

## 打印设备

### SubmitPrintRequest

当用户需要进行打印时，DuerOS会向技能发送该消息，通知技能开始打印操作。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SubmitPrintRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| fileSourceUrl | 打印资源的地址。支持打印资源的格式为".doc"、".docx"、".rtf"、".xls"、".xlsx"、".ppt"、".pptx"、".jpeg"、".jpg"、".png"、".gif"、".bmp"、".txt"、".html"、".pdf"。 | 是 |
| fileName | 打印文件的名称。 | 否 |
| mediaSize | 打印纸张的尺寸大小。支持以下规格：  * IsoA3_420x297mm：表示使用A3规格的纸张打印。 * IsoA4_210x297mm：表示使用A4规格的纸张打印，默认使用IsoA4_210x297mm。 * IsoA5_148x210mm：表示使用A5规格的纸张打印。 | 否 |
| color | 是否使用彩色打印，布尔类型。  * true：表示使用彩色打印。 * false：表示使用黑白打印，默认使用false。 | 否 |
| copies | 打印份数，默认是1。 | 否 |

#### 应用举例

用户说“小度小度，把这张图打印一份”，DuerOS了解用户意图后，会向技能发SubmitPrintRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SubmitPrintRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "fileSourceUrl": "http://www.234.cn/uploadfile/image/20140410111022_9402.jpg",
        "fileName": "小鸭子",
        "mediaSize": "IsoA4_210x297mm",
        "color": false,
        "copies": 1
    }
}
```

### SubmitPrintConfirmation

当提交打印任务成功时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SubmitPrintConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| jobId | 本次任务提交完成后的jobId，后续获取任务状态时将使用该值。 | 是 |

#### 应用举例

当提交打印任务成功时，技能会发送该消息给DuerOS，示例如下。

#### Header信息

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SubmitPrintConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "jobId": "print_job_20180512_232221_000"
    }
}
```

### SetSuctionRequest

当用户需要设置设备的吸力时，比如调整扫地机器人吸力，DuerOS会向技能发送该消息，通知技能设置设备的吸力。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetSuctionRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| suction | 设备吸力大小信息。 | 是 |
| suction.value | 吸力设置值的列表，目前支持的值有:  * "STANDARD" * "STRONG" | 是 |

#### 应用举例

用户说“小度小度，扫地机器人吸力调为强劲档”，DuerOS了解用户意图后，会向技能发送SetSuctionRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetSuctionRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "suction": {
            "value": "STRONG"
        }
    }
}
```

### SetSuctionConfirmation

当设备成功设置吸力后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetSuctionConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当扫地机器人吸力调为强劲档时，技能向DuerOS发送SetVolumeConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetSuctionConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### SetWaterLevelRequest

当用户需要设置设备的水量时，比如调整扫地机器人水量，DuerOS会向技能发送该消息，通知技能设置设备的水量。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetWaterLevelRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| waterLevel | 设备水量大小信息。 | 是 |
| waterLevel.value | 吸力设置值的列表，目前支持的值有:  * "HIGH" * "MEDIUM" * "LOW" | 是 |

#### 应用举例

用户说“小度小度，扫地机器人水量调为中档”，DuerOS了解用户意图后，会向技能发送SetWaterLevelRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetWaterLevelRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "waterLevel": {
            "value": "MEDIUM"
        }
    }
}
```

### SetWaterLevelConfirmation

当设备成功设置水量后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetWaterLevelConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当扫地机器人水量调为中档时，技能向DuerOS发送SetWaterLevelConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetWaterLevelConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "waterLevel",
                "value": "MEDIUM",
                "scale": "",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(LOW, MEDIUM, HIGH)"
            }
        ]
    }
}
```

### ChargeRequest

当用户需要给设备充电时时，比如给扫地机器人充电，DuerOS会向技能发送该消息，通知技能给设备充电。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ChargeRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，扫地机器人充电”，DuerOS了解用户意图后，会向技能发送ChargeRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        }
    }
}
```

### ChargeConfirmation

当给设备充电指令成功发送并执行后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ChargeConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当扫地机器人执行充电指令时，技能向DuerOS发送ChargeConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ChargeConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "electricityCapacity",
                "value": 20.5,
                "scale": "%",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0.0, 100.0]"
            }
        ]
    }
}
```

### DischargeRequest

当用户发出停止给设备充电的请求时，DuerOS收到请求后，向技能发送DischargeRequest消息，通知技能停止给设备充电。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | DischargeRequest |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象。包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，扫地机停止充电”，DuerOS接收到用户请求后，向技能发送DischargeRequest消息，消息示例如下。

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
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### DischargeConfirmation

当技能收到停止充电的指令后，向DuerOS发送DischargeConfirmation消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| namespace | DuerOS.ConnectedHome.Control |
| name | DischargeConfirmation |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

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
        "attributes": [
            {
                "name": "electricityCapacity",
                "value": 20.5,
                "scale": "%",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0.0, 100.0]"
            }
        ]
    }
}
```

### SetDirectionRequest

当用户需要设置设备移动方向时，比如扫地机器人前进，DuerOS会向技能发送该消息，通知技能设置设备的移动方向。

### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetDirectionRequest |
| namespace | DuerOS.ConnectedHome.Control |

### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| direction | 设备移动方向信息。 | 是 |
| direction.value | 方向设置值的列表，目前支持的值有:  * FORWARD：向前 * BACKWARD：向后 * LEFT：向左 * RIGHT：向右 * CLOCKWISE：顺时针转 * COUNTERCLOCKWISE：逆时针转 | 是 |
| direction.type | 方向类型，目前支持的值有:  * MOVE：移动 * BLOW：吹风 * SWING：摇摆 | 否 |

#### 应用举例

用户说“小度小度，扫地机器人前进”，DuerOS了解用户意图后，会向技能发送SetDirectionRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetDirectionRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "direction": {
            "value": "FORWARD",
            "type": ["MOVE"],
        }
    }
}
```

### SetDirectionConfirmation

当设备开始按照指定方向移动后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetDirectionConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当扫地机器人开始前进后，技能向DuerOS发送SetDirectionConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetDirectionConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### SetCleaningLocationRequest

当用户需要设置设备清扫位置时，比如扫地机器人清扫主卧，DuerOS会向技能发送该消息，通知技能设置扫地机器人的清扫位置。

### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetCleaningLocationRequestRequest |
| namespace | DuerOS.ConnectedHome.Control |

### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| location | 位置，目前支持的值有:  * MASTER_BEDROOM：主卧 * SECOND_BEDROOM：次卧 * LIVING_ROOM：客厅 * KITCHEN：厨房 * STUDY：书房 * RESTAURANT：餐厅 | 是 |

#### 应用举例

用户说“小度小度，扫地机器人清扫主卧”，DuerOS了解用户意图后，会向技能发送SetCleaningLocationRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetCleaningLocationRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
        "location": "MASTER_BEDROOM"
    }
}
```

### SetCleaningLocationConfirmation

当扫地机器人开始前往指定的房间清扫后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetCleaningLocationConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当扫地机器人开始前往对应的房间进行清扫后，技能向DuerOS发送SetCleaningLocationConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetCleaningLocationConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### SetComplexActionsRequest

当用户需要给设备定制比较复杂的动作，比如, 用户想让设备做出比较好玩的动作, 比如让扫地机器人做出复杂的运动路线, 同时也播放同节奏的音乐, 这时就可以对音箱说, "小度小度, 扫地机器人动起来"。
如果针对其它设备想要实现该协议时, 具体设备的反应, 由设备云技能自己自定义, 完全可以发挥更多的想象力, 做出更多好玩的功能。

### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetComplexActionsRequest |
| namespace | DuerOS.ConnectedHome.Control |

### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，扫地机器人动起来”，DuerOS了解用户意图后，会向技能发送SetComplexActionsRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetComplexActionsRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for TV]"
        },
    }
}
```

### SetComplexActionsConfirmation

当扫地机器人开始响应用户请求后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetDirectionConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当扫地机器人执行负责动作后，技能向DuerOS发送SetComplexActionsConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetComplexActionsConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### IncrementHeightRequest

当用户需要升高设备时，比如自动晾衣架升起，DuerOS会向技能发送该消息，通知技能升高设备。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementHeightRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| deltaValue | 按照距离和百分比进行调节的增量信息，包含value和scale。 | 否 |
| deltaValue.value | 按照距离和百分比调节增量的具体值。 | 否 |
| deltaValue.scale | 按照距离调节时增量的单位, 如果是按照百分比调节的，则该项不存在，按照距离调节时，单位为米（METER）或者英尺（FOOT） | 否 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，晾衣架调高50厘米”，DuerOS了解用户意图后，会向技能发送IncrementHeightRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementHeightRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "deltaValue": {
            "value": "0.5",
            "scale": "METER"
        },
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### IncrementHeightConfirmation

当设备升高后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementHeightConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当晾衣架升高后，技能向DuerOS发送IncrementHeightConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementHeightConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### DecrementHeightRequest

当用户需要降低设备高度时，比如自动晾衣架下降，DuerOS会向技能发送该消息，通知技能降低设备高度。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementHeightRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| deltaValue | 按照距离和百分比进行调节的减量信息，包含value和scale。 | 否 |
| deltaValue.value | 按照距离和百分比调节减量的值。 | 否 |
| deltaValue.scale | 按照距离调节时减量的单位, 如果是按照百分比调节的，则该项不存在，按照距离调节时，单位为米（METER）或者英尺（FOOT）。 | 否 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

用户说“小度小度，晾衣架高度下降”，DuerOS了解用户意图后，会向技能发送DecrementHeightRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementHeightRequest",
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

用户说“小度小度，晾衣架高度下降50厘米”，DuerOS了解用户意图后，会向技能发送DecrementHeightRequest消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementHeightRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "deltaValue": {
            "value": "0.5",
            "scale": "METER"
        },
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        }
    }
}
```

### DecrementHeightConfirmation

当设备下降后，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementHeightConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当晾衣架下降后，技能向DuerOS发送DecrementHeightConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementHeightConfirmation",
        "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```

### SetTimerRequest

当用户想给指定设备定时的时候，DuerOS会将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetTimerRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| timeInterval | 定时时长，单位为秒 | 是 |

#### 应用举例

当用户说“小度小度，电饭煲定时15分钟”，DuerOS理解到用户意图后，向技能发送SetTimerRequest消息，消息示例如下。

```
{
     "header": {
         "namespace": "DuerOS.ConnectedHome.Control",
         "name": "SetTimerRequest",
         "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
         "payloadVersion": "1"
     },
     "payload": {
         "accessToken": "[OAuth token here]",
         "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for RICE COOKER]",
         }
         "timeInterval": "900"
     }
}
```

### SetTimerConfirmation

当请求的设备定时成功时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetTimerConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 取值 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电饭煲定时成功时，技能向DuerOS发送SetTimerConfirmation消息，示例如下。

```
{
     "header": {
         "namespace": "DuerOS.ConnectedHome.Control",
         "name": "SetTimerConfirmation",
         "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
         "payloadVersion": "1"
     },
     "payload": {
         "attributes": []
     }
}
```

### TimingCancelRequest

当用户想取消设备的定时任务的时候，DuerOS会将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TimingCancelRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，取消电饭煲定时任务”，DuerOS理解到用户意图后，向技能发送TimingCancelRequest消息，消息示例如下。

```
{
     "header": {
         "namespace": "DuerOS.ConnectedHome.Control",
         "name": "TimingCancelRequest",
         "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
         "payloadVersion": "1"
     },
     "payload": {
         "accessToken": "[OAuth token here]",
         "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for RICE COOKER]",
         }
     }
}
```

### TimingCancelConfirmation

当请求的设备取消定时任务成功时，技能需要发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TimingCancelConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 取值 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当电饭煲取消定时成功时，技能向DuerOS发送TimingCancelConfirmation消息，示例如下。

```
{
     "header": {
         "namespace": "DuerOS.ConnectedHome.Control",
         "name": "TimingCancelConfirmation",
         "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
         "payloadVersion": "1"
     },
     "payload": {
         "attributes": []
     }
}
```

### ResetRequest

当用户想让设备复位的时候，DuerOS会将该消息发送给技能。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ResetRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |

#### 应用举例

当用户说“小度小度，沙发复位”，DuerOS理解到用户意图后，向技能发送Request消息，消息示例如下。

```
{
     "header": {
         "namespace": "DuerOS.ConnectedHome.Control",
         "name": "ResetRequest",
         "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
         "payloadVersion": "1"
     },
     "payload": {
         "accessToken": "[OAuth token here]",
         "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID for SOFA]",
         }
     }
}
```

### ResetConfirmation

当请求的设备复位成功时，技能需要发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ResetConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 取值 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当沙发复位成功时，技能向DuerOS发送ResetConfirmation消息，示例如下。

```
{
     "header": {
         "namespace": "DuerOS.ConnectedHome.Control",
         "name": "ResetConfirmation",
         "messageId": "26fa11a8-accb-4f66-a272-8b1ff7abd722",
         "payloadVersion": "1"
     },
     "payload": {
         "attributes": []
     }
}
```

## 可控楼层设备

可控楼层设备可以控制电梯的楼层，电梯场景分为梯内和梯外，需要厂家根据部署的情况自己区分。

### SetFloorRequest

当用户发出将电梯调到具体的楼层时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetFloorRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| floor | 电梯楼层的对象。 | 是 |
| floor.value | 电梯楼层设置的值，是int类型，取值范围为-1000～1000。其中-1000表示电梯在运行时的最低楼层，1000表示电梯的最高楼层。 | 是 |

#### 应用举例

当用户说“小度小度，将电梯调到1楼时，DuerOS了解用户意图后，会发送SetFloorRequest消息给技能，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetFloorRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "floor": {
            "value": 1
        }
    }
}
```

### SetFloorConfirmation

当电梯楼层设置成功后，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetFloorConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| floor | 电梯楼层设置后的对象。 | 是 |
| floor.value | 电梯楼层设置的值，是int类型，取值范围为-1000～1000。其中-1000表示电梯在运行时的最低楼层，1000表示电梯的最高楼层。 | 是 |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当楼层设置成功时，技能会向DuerOS发送SetFloorConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetFloorConfirmation",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "floor": {
            "value": 1
        },
        "attributes": []
    }
}
```

### IncrementFloorRequest

当用户发出增加电梯具体的楼层时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementFloorRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaFloor | 电梯楼层增量信息。 | 是 |
| deltaFloor.value | 电梯楼层增量的值，是int类型，取值范围为0～1000。其中0表示电梯在运行时的增加的最低值，1000表示增加的最高值。 | 是 |

#### 应用举例

当用户说“小度小度，上楼”时，DuerOS了解用户意图后，会发送IncrementFloorRequest消息给技能，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementFloorRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaFloor": {
            "value": 0
        }
    }
}
```

### IncrementFloorConfirmation

当电梯楼层增加成功后，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | IncrementFloorConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| floor | 电梯楼层设置后的对象。 | 是 |
| floor.value | 电梯楼层设置的值，是int类型，取值范围为-1000～1000。其中-1000表示电梯在运行时的最低楼层，1000表示电梯的最高楼层。 | 是 |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当楼层设置成功时，技能会向DuerOS发送IncrementFloorConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "IncrementFloorConfirmation",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "floor": {
           "value": 3
        },
        "attributes": []
    }
}
```

### DecrementFloorRequest

当用户发出减少电梯具体的楼层时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementFloorRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaFloor | 电梯楼层的减量信息。 | 是 |
| deltaFloor.value | 电梯楼层减量的值，是int类型，取值范围为0～1000。其中0表示电梯在运行时减少的最低值，1000表示电梯减少的最高值。 | 是 |

#### 应用举例

当用户说“小度小度，下楼“，DuerOS了解用户意图后，会发送DecrementFloorRequest消息给技能，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementFloorRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaFloor": {
            "value": 0
        }
    }
}
```

### DecrementFloorConfirmation

当电梯楼层设置成功后，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DecrementFloorConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| floor | 电梯楼层设置后的对象。 | 是 |
| floor.value | 电梯楼层设置的值，是int类型，取值范围为-1000～1000。其中-1000表示电梯在运行时的最低楼层，1000表示电梯的最高楼层。 | 是 |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当楼层设置成功时，技能会向DuerOS发送DecrementFloorConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "DecrementFloorConfirmation",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "floor": {
           "value": 1
        },
        "attributes": []
    }
}
```

## 可控湿度类设备

可控湿度设备可以控制设备的湿度。

### SetHumidityRequest

当用户发出将可控可控湿度设备调到具体的湿度值时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetHumidityRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| deltaValue | 按照百分比进行调节的数值变化信息，包含value和scale。 | 是 |
| deltaValue.value | 湿度百分比变化值，是double类型，取值范围为0～100。其中0表示设备的最小湿度，100表示最大湿度。 | 是 |
| deltaValue.scale | 湿度的调节单位，默认为 % 。 | 是 |

#### 应用举例

当用户说“小度小度，加湿器湿度设置为10，DuerOS了解用户意图后，会发送SetHumidityRequest消息给技能，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetHumidityRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "deltaValue": {
            "value": 10,
            "scale": "%"
        }
    }
}
```

### SetHumidityConfirmation

当可控湿度类设备湿度设置成功后，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetHumidityConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当可控湿度设备设置成功时，技能会向DuerOS发送SetHumidityConfirmation消息，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetHumidityConfirmation",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": [
            {
                "name": "humidity",
                "value": 22.9,
                "scale": "%",
                "timestampOfSample": 1496741861,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0.0, 100.0]"
            }
        ]
    }
}
```

## 可控挡位类设备

可控挡位设备可以控制设备的挡位。

### SetGearRequest

当用户发出将可控挡位设备调到具体的挡位值时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetGearRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| gear | 调节对象，包含value和scale。 | 是 |
| gear.value | 挡位值，是string类型，取值范围为(MIN, LOW, MIDDLE_LOW, MIDDLE, MIDDLE_HIGH, HIGH, MAX, AUTO, RANDOM) | 是 |
| gear.scale | 挡位的调节单位,默认为‘挡‘ | 是 |

#### 应用举例

本指令是弱意图指令，当用户说“小度小度，热水器设置为中挡”，DuerOS了解用户意图后，会发送SetGearRequest消息给技能，消息示例如下。技能在收到此请求时，需要根据设备类型映射到特定属性，比如热水器的挡位设置映射到temperature属性。新增浴霸的挡位设置映射到warmthLevel暖度属性。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetGearRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "gear": {
            "value": "MIDDLE",
            "scale": "挡"
        }
    }
}
```

### SetGearConfirmation

挡位设置是弱意图，当挡位设置成功后，技能会向DuerOS发送该消息，或者技能向DuerOS发送对应属性的消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetGearConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当挡位设置成功时，技能会向DuerOS发送SetGearConfirmation消息或对应属性的消息。例如“取暖器中挡”，技能将挡位映射到temperature属性，技能也可以返回SetGearConfirmation消息。SetGearConfirmation消息示例如下。新增浴霸的挡位设置映射到warmthLevel属性，需要返回warmthLevel属性。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"SetGearConfirmation",
        "messageId":"01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion":"1"
    },
    "payload":{
        "attributes":[]
    }
}
```

## 可控水流类设备

可控水流设备可以控制设备的水流。

### SetFlowRequest

当用户发出将可控水流设备调到具体状态时，DuerOS会向技能发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetFlowRequest |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| appliance | 设备操作的具体对象，包括applianceId和additionalApplianceDetails。 | 是 |
| appliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| appliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| flow | 调节对象，包含action、select、control。 | 是 |
| flow.action | 操作值，是string类型，取值范围为(POUR_WATER,FILL_WATER)。POUR_WATER：出水、排水；FILL_WATER：加水、注水。 | 是 |
| flow.select | 选取设备值，是string类型，取值范围(TOP,HANDLE_HELD,UNDER)。TOP：顶部；HANDLE_HELD：手持；UNDER：底部。 | 否 |
| flow.control | 水流状态控制，是string类型，取值范围(START,STOP)。START：开始、启动；STOP：停止。 | 否 |

#### 应用举例

当用户说“小度小度，手持花洒排水”，DuerOS了解用户意图后，会发送SetFlowRequest消息给技能，消息示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetFlowRequest",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth token here]",
        "appliance": {
            "additionalApplianceDetails": {},
            "applianceId": "[Device ID]"
        },
        "flow": {
            "action": "POUR_WATER",
            "select": "HANDLE_HELD"
        }
    }
}
```

### SetFlowConfirmation

当水流设置成功后，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | SetFowConfirmation |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| attributes | 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。 | 否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。 |

#### 应用举例

当水流控制完成后，技能向DuerOS发送SetFowConfirmation消息，示例如下。

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "SetFowConfirmation",
        "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
        "payloadVersion": "1"
    },
    "payload": {
        "attributes": []
    }
}
```
