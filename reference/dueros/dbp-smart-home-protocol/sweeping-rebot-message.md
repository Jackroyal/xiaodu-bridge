---
title: "扫地机器人协议"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/sweeping-rebot-message_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 扫地机器人控制协议

扫地机器人控制协议是DuerOS与各型号扫地机器人设备之间的通讯协议。通过该协议您可以轻松的通过语音控制扫地机器人设备，与设备进行交互。协议使用HTTPS传输，采用JSON消息格式。
实现该协议后，购买了扫地机器人的客户可以这样通过语音这样控制扫地机器人，“小度小度，扫地机器人调为自动清扫模式”，然后扫地机器人就会调整为自动清扫模式。DuerOS赋能给扫地机器人后，顾客就可以通过语音这样来控制它：

* “打开扫地机器人”
* “关闭扫地机器人”
* “扫地机器人暂停”
* “扫地机器人继续扫地”
* “扫地机器人调为自动清扫/定点清扫/延边清扫/自动拖地/定点拖地/延边拖地/防打扰模式”
* “1分钟后扫地机器人自动清扫/自动拖地”
* “扫地机器人每天下午3点开始自动清扫”
* “我的扫地机器人扫到哪里了?”

实现该协议后，用户通过语音控制、App控制、手动控制扫地机器人后，可以通过App查看到扫地机器人状态，也可以通过语音查询扫地机器状态。
这篇文档会从发现设备、控制设备、查询设备、属性上报以及异常消息等方面，全面介绍扫地机器人接入时需要了解的内容。

* [发现设备](#发现设备)
* [控制设备](#控制设备)
* [查询设备](#查询设备)
* [属性上报](#属性上报)
* [异常消息](#异常消息)

## 发现设备

发现设备消息用于发现用户帐号下所有的设备信息，当用户启用支持扫地机器人协议的技能并且在技能下绑定扫地机器人后，使用该协议可以将用户账号下的设备信息同步给DuerOS，让DuerOS找到该设备并执行控制和查询操作，包含[DiscoverAppliancesRequest](discovery-message.md#discoverappliancesrequest)和[DiscoverAppliancesResponse](discovery-message.md#discoverappliancesresponse)两个指令。
发现设备的协议介绍可以点击上方两个链接阅读详细内容。

### 应用举例

当查找到设备及相关场景或分组时，技能向DuerOS发送DiscoverAppliancesResponse消息，消息样例如下。

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
                    "turnOff",
                    "pause",
                    "continue",
                    "setSuction",
                    "setWaterLevel",
                    "chargeTurnOn",
                    "chargeTurnOff",
                    "setMovingDirection",
                    "setMode",
                    "timingSetMode",
                    "getElectricityCapacity",
                ],
                "applianceTypes": [
                    "SWEEPING_ROBOT"
                ],
                "additionalApplianceDetails": {
                    "extraDetail1": "optionalDetailForSkillAdapterToReferenceThisDevice",
                    "extraDetail2": "There can be multiple entries",
                    "extraDetail3": "but they should only be used for reference purposes",
                    "extraDetail4": "This is not a suitable place to maintain current device state"
                },
                "applianceId": "uniqueSweepingRobotId",
                "friendlyDescription": "展现给用户的详细介绍",
                "friendlyName": "扫地机器人",
                "isReachable": true,
                "manufacturerName": "设备制造商的名称",
                "modelName": "fancySweepingRobot",
                "version": "your software version number here.",
                "attributes": [
                    {
                        "name": "name",
                        "value": "扫地机器人",
                        "scale": "",
                        "timestampOfSample": 1526978456,
                        "uncertaintyInMilliseconds": 0
                    },
                    {
                        "name": "connectivity",
                        "value": "REACHABLE",
                        "scale": "",
                        "timestampOfSample": 1526978456,
                        "uncertaintyInMilliseconds": 0
                    },
                    {
                        "name": "turnOnState",
                        "value": "ON",
                        "scale": "",
                        "timestampOfSample": 1526978456,
                        "uncertaintyInMilliseconds": 10
                    },
                    {
                        "name": "pauseState",
                        "value": false,
                        "scale": "",
                        "timestampOfSample": 1526978456,
                        "uncertaintyInMilliseconds": 10
                    },
                    {
                        "name": "mode",
                        "value": "ANTI_DISTURB",
                        "scale": "",
                        "timestampOfSample": 1526978456,
                        "uncertaintyInMilliseconds": 10
                    },
                    {
                        "name": "suction",
                        "value": "standard",
                        "scale": "",
                        "timestampOfSample": 1526978456,
                        "uncertaintyInMilliseconds": 10
                    },
                    {
                        "name": "waterLevel",
                        "value": "MEDIUM",
                        "scale": "",
                        "timestampOfSample": 1526978456,
                        "uncertaintyInMilliseconds": 10
                    },
                    {
                        "name": "electricityCapacity",
                        "value": 23,
                        "scale": "%",
                        "timestampOfSample": 1526978456,
                        "uncertaintyInMilliseconds": 10
                    }
                ]
            },
        ],
        "discoveredGroups": []
    }
}
```

## 控制设备

| 操作 | 协议 |
| --- | --- |
| 打开扫地机器人 | [DuerOS.ConnectedHome.Control.TurnOnRequest](control-message.md#turnonrequest) |
| 关闭扫地机器人 | [DuerOS.ConnectedHome.Control.TurnOffRequest](control-message.md#turnoffrequest) |
| 暂停扫地机器人 | [DuerOS.ConnectedHome.Control.PauseRequest](control-message.md#pauserequest) |
| 扫地机器人继续扫地 | [DuerOS.ConnectedHome.Control.ContinueRequest](control-message.md#continuerequest) |
| 扫地机器人调成自动清扫模式 | [DuerOS.ConnectedHome.Control.SetModeRequest](control-message.md#setmoderequest) |
| 扫地机器人吸力调为标准档 | [DuerOS.ConnectedHome.Control.SetSuctionRequest](control-message.md#setsuctionrequest) |
| 扫地机器人水量调为高档 | [DuerOS.ConnectedHome.Control.SetWaterLevelRequest](control-message.md#setwaterlevelrequest) |
| 给扫地机器人充电 | [DuerOS.ConnectedHome.Control.ChargeRequest](control-message.md#chargerequest) |
| 扫地机器人前进 | [DuerOS.ConnectedHome.Control.SetDirectionRequest](control-message.md#setdirectionrequest) |
| 扫地机器人清扫主卧 | [DuerOS.ConnectedHome.Control.SetCleaningLocationRequest](control-message.md#setcleaninglocationrequest) |
| 1分钟后把扫地机器人调成自动清扫模式 | [DuerOS.ConnectedHome.Control.TimingSetModeRequest](control-message.md#timingsetmoderequest) |
| 扫地机器人动起来 | [DuerOS.ConnectedHome.Control.SetComplexActionsRequest](control-message.md#setcomplexactionsrequest) |

## 查询设备

| 操作 | 协议 |
| --- | --- |
| 查询扫地机器人的电量 | [DuerOS.ConnectedHome.Query.GetElectricityCapacityRequest](query-message.md#getelectricitycapacityrequest) |
| 查询扫地机器人状态 | [DuerOS.ConnectedHome.Query.GetStateRequest](query-message.md#getstaterequest) |
| 查询扫地机器人位置 | [DuerOS.ConnectedHome.Query.GetLocationRequest](query-message.md#getlocationrequest) |

## 属性上报

当手动操作扫地机器人、通过手机App控制扫地机器人或者通过语音控制扫地机器人时，会直接影响扫地机器人的状态, 比如水量档位、吸力档位等，为了让DuerOS能实时同步到扫地机器人的状态，需要在技能端捕获到属性发生变化的事件时，主动上报相应的属性信息，具体可以参考文档[设备属性上报](attributes-report.md)。

## 异常消息

在控制硬件过程中，可能会发生各种各样的异常，此时反馈的消息就不是确认消息，而是表达相应异常状态的消息，详见文档[错误消息](error-message.md)。
