---
title: "错误消息"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/error-message_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 错误消息(Error Message)

当DuerOS向技能发送设备请求信息时，请求信息中可能存在设备不支持或者超出设备使用范围等问题，此时技能会返回相应的错误类型和信息。技能不需要返回每个错误，仅返回错误对应的错误类型。本文列出了错误类型和详细信息。

* 用户故障类错误。

  + [ValueOutOfRangeError](#valueoutofrangeerror)
  + [TargetOfflineError](#targetofflineerror)
  + [BridgeOfflineError](#bridgeofflineerror)
* 设备故障类错误。

  + [DriverInternalError](#driverinternalerror)
  + [DependentServiceUnavailableError](#dependentserviceunavailableerror)
  + [NotSupportedInCurrentModeError](#notsupportedincurrentmodeerror)
  + [RateLimitExceededError](#ratelimitexceedederror)
  + [TargetBridgeConnectivityUnstableError](#targetbridgeconnectivityunstableerror)
  + [TargetFirmwareOutdatedError](#targetfirmwareoutdatederror)
  + [TargetBridgeFirmwareOutdatedError](#targetbridgefirmwareoutdatederror)
  + [TargetHardwareMalfunctionError](#targethardwaremalfunctionerror)
  + [TargetBridgeHardwareMalfunctionError](#targetbridgehardwaremalfunctionerror)
  + [TargetConnectivityUnstableError](#targetconnectivityunstableerror)
  + [TargetHardwareMalfunctionError](#targethardwaremalfunctionerror)
  + [UnableToGetValueError](#unabletogetvalueerror)
  + [UnableToSetValueError](#unabletosetvalueerror)
  + [UnwillingToSetValueError](#unwillingtosetvalueerror)
* 其他故障类错误。

  + [ExpiredAccessTokenError](#expiredaccesstokenerror)
  + [InvalidAccessTokenError](#invalidaccesstokenerror)
  + [UnsupportedTargetError](#unsupportedtargeterror)
  + [UnsupportedOperationError](#unsupportedoperationerror)
  + [UnsupportedTargetSettingError](#unsupportedtargetsettingerror)
  + [UnexpectedInformationReceivedError](#unexpectedinformationreceivederror)

**注意：**本文所列的错误信息不适用设备发现过程。

## 用户故障类错误(User Faults)

用户故障类错误指由于用户错误操作，导致请求失败的情况。

### ValueOutOfRangeError

当用户请求中对设备的设置参数超过设备支持的参数范围时，DuerOS就会收到该错误消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ValueOutOfRangeError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| minimumValue | 设备的允许设置参数的最小值，是64位双精度值类型。 | 是 |
| maximumValue | 设备的允许设置参数的最大值，是64位双精度值类型。 | 是 |

#### 应用举例

如用户想把空调温度设置为10度，但是空调的温度范围是17到30度，此时技能就会发送该消息给DuerOS，说明用户输入参数范围错误。消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":" ValueOutOfRangeError",
        "messageId":"697fe957-c842-4545-a159-8a8c75fbe5bd"，
        "payloadVersion":"1",
    },
    "payload":{
        "minimumValue":17.0,
        "maximumValue":30.0
    }
}
```

### TargetOfflineError

当技能检测到目标设备没有连接到设备云或者设备云不在线时，会给DuerOS发送TargetOfflineError消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TargetOfflineError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

TargetOfflineError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"TargetOfflineError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd"，
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### BridgeOfflineError

当技能检测到目标设备的家庭Hub或网桥没有连接到设备云或者设备云不在线时，会给DuerOS发送BridgeOfflineError消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | BridgeOfflineError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

BridgeOfflineError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"BridgeOfflineError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

## 设备故障类错误信息

设备故障类错误指由于设备硬件问题或者设备功能限制，导致用户请求无法完成的错误。

### DriverInternalError

当设备运行发生故障时，技能会发送DriverInternalError给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DriverInternalError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

DriverInternalError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"DriverInternalError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### DependentServiceUnavailableError

技能依赖的其他模块不可用，技能无法完成用户请求时，会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DependentServiceUnavailableError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| dependentServiceName | 技能依赖的其他模块服务名称，由数字、字母和空格组成，长度是256个字符。如果超过256个字符，后面的内容会被截断。 | 是 |

#### 应用举例

DependentServiceUnavailableError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"DependentServiceUnavailableError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
        "dependentServiceName":"Customer Credential Database"
    }
}
```

### TargetConnectivityUnstableError

当目标设备连接的云不稳定时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TargetConnectivityUnstableError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

TargetConnectivityUnstableError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"TargetConnectivityUnstableError ",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### TargetBridgeConnectivityUnstableError

当目标设备的家庭Hub或网桥的云连接不稳定时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TargetBridgeConnectivityUnstableError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

TargetBridgeConnectivityUnstableError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"TargetBridgeConnectivityUnstableError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### TargetFirmwareOutdatedError

当目标设备的固件版本太低时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TargetFirmwareOutdatedError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| minimumFirmwareVersion | 支持的最低的固件版本，版本长度不超过256个字符。 | 是 |
| currentFirmwareVersion | 当前固件版本，版本长度不超过256个字符。 | 是 |

#### 应用举例

TargetFirmwareOutdatedError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"TargetFirmwareOutdatedError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
        "minimumFirmwareVersion":"17",
        "currentFirmwareVersion":"6"
    }
}
```

### TargetBridgeFirmwareOutdatedError

当目标设备的家庭Hub或网桥的固件版本太低时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TargetBridgeFirmwareOutdatedError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| minimumFirmwareVersion | 支持的最低的固件版本，长度不超过256个字符。 | 是 |
| currentFirmwareVersion | 当前固件版本，长度不超过256个字符。 | 是 |

#### 应用举例

TargetBridgeFirmwareOutdatedError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"TargetBridgeFirmwareOutdatedError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
        "minimumFirmwareVersion":"17",
        "currentFirmwareVersion":"6"
    }
}
```

### TargetHardwareMalfunctionError

当目标设备出现硬件故障时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TargetHardwareMalfunctionError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

TargetHardwareMalfunctionError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"TargetHardwareMalfunctionError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### TargetBridgeHardwareMalfunctionError

当目标设备的家庭Hub或网桥出现硬件故障时，技能会向DuerOS发送该消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | TargetBridgeHardwareMalfunctionError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

TargetBridgeHardwareMalfunctionError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"TargetBridgeHardwareMalfunctionError",
        "messageId":"15a248f6-8ab5-433d-a3ac-73c358e0bebd",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### UnableToGetValueError

当技能无法在目标设备上获取指定值时，会发送该消息给DuerOS。DuerOS根据errorInfo.code值判断不同的故障。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnableToGetValueError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| errorInfo | 不能获取值时的错误信息。 | 是 |
| errorInfo.code | 错误代码。  * DEVICE_AJAR：由于设备没打开，无法获取指定的状态。 * DEVICE_BUSY：设备正忙。 * DEVICE_JAMMED：设备卡住。 * DEVICE_OVERHEATED：设备过热。 * HARDWARE_FAILURE：由于未确定的硬件故障，请求失败。 * LOW_BATTERY：设备的电池电量不足。 * NOT_CALIBRATED：设备未校准。 * DEVICE_MODEL_TOO_OLD：设备型号太旧。 * DEVICE_RESPONSE_TIMEOUT: 设备端响应超时 | 是 |
| errorInfo.Description | 设备的错误信息描述。 | 否 |

#### 应用举例

UnableToGetValueError消息示例如下。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"UnableToGetValueError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
        "errorInfo":{
            "code":"DEVICE_JAMMED",
            "description":"A custom description of the error.."
        }
    }
}
```

### UnableToSetValueError

当技能无法在目标设备上设置指定值时，会发送该消息给DuerOS。DuerOS根据errorInfo.code值判断不同的故障。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnableToSetValueError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| errorInfo | 不能设置时的错误信息。 | 是 |
| errorInfo.code | 通用错误代码。  * DEVICE_AJAR：由于设备没打开，无法获取指定的状态。 * DEVICE_BUSY：设备正忙。 * DEVICE_JAMMED：设备卡住。 * DEVICE_OVERHEATED：设备过热。 * HARDWARE_FAILURE：由于未确定的硬件故障，请求失败。 * LOW_BATTERY：设备的电池电量不足。 * NOT_CALIBRATED：设备未校准。 * MODE_NOT_SUPPORT_BOOKING：当前模式不支持预约计划哦，无法为您预约。 * MODE_NOT_SUPPORT_CANCEL：当前模式不支持取消。 * UNMODE_NOT_SUPPORT_CANCEL：当前设备不在该模式中，无法为您取消。 * WORKING_STATE_NOT_SUPPORT_RESET：当前设备已经在该模式中工作了，无法为您重复设置。 * OPEN_STATE_NOT_SUPPORT_RESET：已经打开了，无法为您重复设置。 * CLOSE_STATE_NOT_SUPPORT_RESET：已经关闭了，无法为您重复设置。 * BUSY_STATE_NOT_SUPPORT_RESET：当前设备正忙，无法为您设置。 * NOT_WORKING：当前设备没有在工作。 * UNABLE_TO_SET_MODE：当前设备不支持该模式。 * UNABLE_TO_MOVE_UP：当前无法继续升高了。 * UNABLE_TO_MOVE_DOWN：当前无法继续降低了。 * UNABLE_TO_REDUCE_FAN_SPEED：无法继续减小风量了。 * UNABLE_TO_INCREASE_FAN_SPEED：无法继续增大风量了。 * UNABLE_TO_SET_FAN_SPEED：当前设备不支持该档位的风量。 * UNABLE_TO_SET_COLOR：当前设备不支持这个颜色。 * ALREADY_STOPPED：当前设备已处于静止状态。 * UNABLE_TO_CONTROL_IN_MOTION：设备运动中，请稍后再试。 * DEVICE_MODEL_TOO_OLD：设备型号太旧。  蒸箱错误代码：  * NOT_IN_COOKING_MODE_SUPPORT_TIME_OR_TEMPERATE：当前设备不在烹饪模式中，无法为您设置温度或时间，请先设置调到烹饪模式。 * MODE_NOT_SUPPORT_TIME_OR_TEMPERATURE：当前模式中，不支持调节烹饪时间和温度。 * STEAM_BOT_WARN_INFO：您可以对我说，蒸箱打开普通蒸模式，然后开启烹饪。 * NO_WEB_BAKING_HUMIDITY_SET：只有加湿烤模式下才可以设置烹饪湿度，当前无法为您设置。 * BOOKING_NOT_SUPPORT_TIME_OR_TEMPERATURE：当前在预约计划中，不支持修改烹饪参数。  油烟机错误代码：  * ALREADY_RETRACTED：已经收回了，无法为您重复设置。 * UNABLE_TO_MOVE_UP_INSTEAD_RETRACT：当前无法继续升高了，您可以对我说，油烟机收回或油烟机下降。 * DEVICE_RESPONSE_TIMEOUT: 设备端响应超时 | 是 |
| errorInfo.Description | 设备的错误信息描述。 | 否 |

#### 应用举例

UnableToSetValueError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"UnableToSetValueError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
        "errorInfo":{
            "code":"DEVICE_JAMMED",
            "description":"A custom description of the error.."
        }
    }
}
```

### UnwillingToSetValueError

当技能获取到目标设备不接受某项功能的参数设置时，技能会发送该消息给DuerOS。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnwillingToSetValueError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| errorInfo | 错误对象。 | 是 |
| errorInfo.code | 错误代码。  * ThermostatIsOff：由于恒温器关闭，制造商不愿自动将其启动，因此被请求的操作被拒绝。 | 是 |
| errorInfo.Description | 设备的错误信息描述。 | 否 |

#### 应用举例

UnwillingToSetValueError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"UnwillingToSetValueError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
        "errorInfo":{
            "code":"ThermostatIsOff",
            "description":"The requested operation is unsafe because it requires changing the mode."
        }
    }
}
```

### RateLimitExceededError

当用户请求超出设备接受的最大请求数时，技能会发送该消息给DuerOS。如设备每小时只接收4次请求，如果用户发出第5次请求时，设备就会返回该错误消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | RateLimitExceededError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| errorInfo | 错误信息。 | 是 |
| rateLimit | 设备在指定的时间单位中接收的最大请求数，是int类型。 | 是 |
| timeUnit | 设备接收最大请求数rateLimit的时间单位，MINUTE，HOUR或DAY。 | 是 |

#### 应用举例

RateLimitExceededError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"RateLimitExceededError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
        "errorInfo":{
            "rateLimit":"10",
            "timeUnit":"HOUR"
        }
    }
}
```

### NotSupportedInCurrentModeError

当目标设备无法设置指定的模式时，技能会发送该消息给DuerOS，同时返回设备当前的模式信息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | NotSupportedInCurrentModeError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| errorInfo | 错误相关信息。 | 是 |
| currentDeviceMode | 设备当前模式的字符串。有AUTO，AWAY，COLOR，COOL，HEAT和OTHER。 | 是 |

#### 应用举例

NotSupportedInCurrentModeError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"NotSupportedInCurrentModeError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
        "errorInfo":{
            "currentDeviceMode":"COOL",
        }
    }
}
```

## 其他故障

### ExpiredAccessTokenError

该消息表示请求消息中access token过期，不能使用。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | ExpiredAccessTokenError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

ExpiredAccessTokenError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"ExpiredAccessTokenError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### InvalidAccessTokenError

该消息表示请求消息中access token信息无效，无效原因不包含过期。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | InvalidAccessTokenError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

InvalidAccessTokenError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"InvalidAccessTokenError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### UnsupportedTargetError

消息表示技能不支持目标设备。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnsupportedTargetError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

UnsupportedTargetError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"UnsupportedTargetError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### UnsupportedOperationError

该消息表示目标设备不支持请求的操作。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnsupportedOperationError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

UnsupportedOperationError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"UnsupportedOperationError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### UnsupportedTargetSettingError

该错误消息表示请求消息中设备操作在指定设备中不存在。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnsupportedTargetSettingError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

无。

#### 应用举例

UnsupportedTargetSettingError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"UnsupportedTargetSettingError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
    }
}
```

### UnexpectedInformationReceivedError

该消息表示由于请求消息中属性信息错误，导致技能无法处理请求消息。

#### Header信息

| 属性 | 取值 |
| --- | --- |
| name | UnexpectedInformationReceivedError |
| namespace | DuerOS.ConnectedHome.Control |

#### Payload信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| faultingParameter | 请求消息中错误的属性。 | 是 |

#### 应用举例

UnexpectedInformationReceivedError消息示例。

```
{
    "header":{
        "namespace":"DuerOS.ConnectedHome.Control",
        "name":"UnexpectedInformationReceivedError",
        "messageId":"917314cd-ca00-49ca-b75e-d6f65ac43503",
        "payloadVersion":"1"
    },
    "payload":{
        "faultingParameter": "value"
    }
}
```
