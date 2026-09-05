---
title: "设备属性"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/attributes_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 设备属性

设备属性是指设备自身的一些状态特性，如设备的名称、设备打开关闭状态、设备的亮度及温度等。每个设备都有自己的属性，不同设备的属性一般不同，如电灯类设备的属性和插座类设备的属性不同。下表是一些常见设备的属性信息，其中每种设备都必须包含name属性和connectivity属性。

| 设备名称 | 属性信息 |
| --- | --- |
| 电灯类设备 | * name * connectivity * turnOnState * brightness * color |
| 插座类设备 | * name * connectivity * turnOnState |
| 空调类设备 | * name * connectivity * turnOnState * mode * temperature * targetTemperature * fanSpeed |
| 传感器类设备 | * name * connectivity * turnOnState * temperature * humidity |
| 可控湿度类设备 | * name * connectivity * turnOnState * humidity |
| 空气净化器类设备 | * name * connectivity * turnOnState * mode * fanSpeed * pm2.5 |
| 扫地机器人类设备 | * name * connectivity * turnOnState * pauseState * mode * suction * waterLevel * electricityCapacity * location |
| 跑步机类设备 | * name * connectivity * turnOnState * mode * speed * speed motionInfo |
| 智能床椅类设备 | * name * connectivity * turnOnState * mode |
| 浴霸类设备 | * name * connectivity * turnOnState * mode * targetTemperature * fanSpeed warmthLevel |

## 设备属性数据格式

设备属性的数据格式如下所示，每个属性都必须包含name,value,scale,timestampOfSample,uncertaintyInMilliseconds这5个字段，legalValue字段为可选字段。

```
"payload": {
    "attributes": [
        {
            "name": "name",
            "value": "温度传感器",
            "scale": "",
            "timestampOfSample": 1496741861,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "STRING"
        }
    ]
}
```

### 参数描述

| 参数名称 | 描述 | 类型 |
| --- | --- | --- |
| name | 属性名称，支持数字、字母和下划线，长度不能超过128个字符。 | string |
| value | 属性值，支持多种json类型。 | * Boolean：布尔类型 * Number：数值类型 * String：字符串类型 * Object：对象类型 |
| scale | 属性值的单位名称，支持数字、字母和下划线，长度不能超过128个字符。 常见的单位名称有温度单位摄氏温度（CELSIUS）和华氏温度（FAHRENHEIT）、百分比（%）、功率单位瓦特（%）、PM2.5含量的单位（ug/m3)等，如果属性值没有单位，该字段为空。 | string |
| timestampOfSample | 属性值取样的时间戳，单位是秒。 | int |
| uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。如打开厨房灯时，属性turnOnState变为ON，时间是time1，设备上报事件给技能，通知技能记录属性turnOnState变为ON，技能完成响应的操作的时间为time2（time2即属性值的取样时间），time2和time1之间的误差就是属性值取样的时间误差。 如果设备使用的是轮询时间间隔的取样方式，那么uncertaintyInMilliseconds就等于时间间隔。如温度传感器每1秒取样1次，那么uncertaintyInMilliseconds的值就是1000。 | int |
| legalValue | 属性取值的合法范围，是字符串类型。字符串中包含的值，可以是单个值："INTEGER"，表示合法值是整数；"DOUBLE"，表示合法值是浮点数；"STRING"，表示合法值是字符串；"BOOLEAN"，表示合法值是布尔值；"OBJECT"，表示合法值是json对象；可以是集合： "(A1, B1, C1, D1)"，表示值可以取这些字符串；也可以是数字范围："[from: to]"，表示合法值是处于对应的数值范围内。 | string |

## 常见的设备属性

目前支持的属性有[name](#name属性)、[connectivity](#connectivity属性)、[brightness](#brightness属性)、[powerState](#powerstate属性)、[powerLevel](#powerlevel属性)、[temperature](#temperature属性)、[mode](#mode属性)、[humidity](#humidity属性)、[airQuality](#airquality属性)、[pm2.5](#pm25属性)、[co2](#co2属性)、[tovc](#tovc属性)、[formaldehyde](#formaldehyde属性)、[percentage](#percentage属性)、[color](#color属性)、[colorTemperatureInKelvin](#colortemperatureinkelvin属性)、[dateTime](#datetime属性)、[turnOnState](#turnonstate属性)、[pauseState](#pausestate属性)、[lockState](#lockstate属性)、[electricityCapacity](#electricitycapacity属性)、[oilCapacity](#oilcapacity属性)、[drivingDistance](#drivingdistance属性)、[fanSpeed](#fanspeed属性)、[speed](#speed属性)、[motionInfo](#motioninfo属性)、[channel](#channel属性)、[muteState](#mutestate属性)、[volume](#volume属性)、[suction](#suction属性)、[waterLevel](#waterlevel属性)、[location](#location属性)、[workState](#workstate属性)、[warmthLevel](#warmthlevel属性)。

### name属性

设备的名称属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值name。 |
| value | 属性值，是字符串类型。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "name",
    "value": "温度传感器",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "STRING"
}
```

**说明：**在同步时，属性name的值必须和[发现设备](discovery-message.md)时记录的friendlyName字段保持一致。

### connectivity属性

设备是否可达属性，指设备状态是否可控。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值connectivity。 |
| value | 属性值，是枚举类型。  * REACHABLE：表示设备状态可控。 * UNREACHABLE：表示设备状态不可控。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "connectivity",
    "value": "UNREACHABLE",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(UNREACHABLE, REACHABLE)"
}
```

**说明：**在同步时，属性connectivity的值必须和[发现设备](discovery-message.md)时记录的isReachable字段保持一致。

### brightness属性

设备的亮度属性，比如智能灯的亮度。

#### 参数使用说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值brightness。 |
| value | 属性值，double类型，取值范围是0~100，包括0和100。 |
| scale | 属性值的单位，取百分比(%)。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "brightness",
    "value": 50,
    "scale": "%",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0, 100]"
}
```

### powerState属性

设备通电状态的属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值powerState。 |
| value | 属性值，是枚举类型。  * ON：表示设备处于通电状态。 * OFF：表示设备处于断电状态。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "powerState",
    "value": "ON",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(ON, OFF)"
}
```

### powerLevel属性

设备的功率功率属性，比如电磁炉的功率是800w。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值powerLevel。 |
| value | 属性值，是整数类型。 |
| scale | 属性值的单位，是瓦特（W）。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "powerLevel",
    "value": 30,
    "scale": "W",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "INTEGER"
}
```

### temperature属性

设备对应的温度属性，可以指设备本身的温度、周围环境的温度、设备目标温度等等。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，包括以下名称：  * temperature：表示当前温度。 * targetTemperature：表示目标温度，比如空调设定的目标温度。 |
| value | 属性值，是double类型。 |
| scale | 属性单位，有CELSIUS（摄氏温度）和FAHRENHEIT（华氏温度）两种计量单位，默认使用CELSIUS。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "temperature",
    "value": 16,
    "scale": "CELSIUS",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[16, 31]"
}
```

### mode属性

设备控制模式属性，比如空气净化器的急速模式HIGHSPEED。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值mode。 |
| value | 属性值，是枚举类型。  * SLEEP：睡眠模式。 * HOME：在家模式。 * OUT：离家模式。 * AUTO：自动模式。 * MANUAL：手动模式。 * MUTE：静音模式。 * INTELLIGENT：智能模式。 * HIGHSPEED：急速模式。 * DUST：除尘模式。 * HCHO_FREE：除甲醛模式。 * customName：厂商自定义模式。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "mode",
    "value": "HIGHSPEED",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(SLEEP, HOME, OUT, AUTO, MANUAL, MUTE, INTELLIGENT, HIGHSPEED, DUST, HCHO_FREE)"
}
```

### humidity属性

湿度属性，比如传感器显示的当前空气的湿度。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值humidity。 |
| value | 属性值，浮点类型，取值范围是0~100，包括0和100。 |
| scale | 属性值的单位，是百分比（%）。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "humidity",
    "value": 22.9,
    "scale": "%",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0.0, 100.0]"
}
```

### airQuality属性

空气质量的属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值airQuality。 |
| value | 属性值，是枚举类型，包括以下取值：  * 优。 * 良。 * 差。 * 轻度污染。 * 中度污染。 * 重度污染。 * 严重污染。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "airQuality",
    "value": "良",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(优, 良, 差, 轻度污染, 中度污染, 重度污染, 严重污染)"
}
```

### pm2.5属性

该属性表示空气中PM2.5的含量。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值pm2.5。 |
| value | 属性值，浮点类型，取值范围为0~1000，包括0和1000。 |
| scale | 属性值的单位，是μg/m3。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "pm2.5",
    "value": 53.3,
    "scale": "μg/m3",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0.0, 1000.0]"
}
```

### co2属性

该属性表示空气中CO2的浓度。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值co2。 |
| value | 属性值，整数类型。 |
| scale | 属性值的单位，是ppm。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "co2",
    "value": 1000,
    "scale": "ppm",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "INTEGER"
}
```

### tovc属性

该属性表示空气中总挥发性有机化合物的浓度。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值tovc。 |
| value | 属性值，double类型。 |
| scale | 属性值的单位，是mg/m3。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "tovc",
    "value": 0.003,
    "scale": "mg/m3",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "DOUBLE"
}
```

### formaldehyde属性

该属性表示空气中甲醛的浓度。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值formaldehyde。 |
| value | 属性值，double类型。 |
| scale | 属性值的单位，是mg/m3。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "formaldehyde",
    "value": 0.003,
    "scale": "mg/m3",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "DOUBLE"
}
```

### percentage属性

百分比属性，比如把窗帘关一半，百分比属性值是50%。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值percentage。 |
| value | 属性值，整数类型，取值范围为0~100，包括0和100。 |
| scale | 属性值的单位，是百分比（%）。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "percentage",
    "value": 30,
    "scale": "%",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0, 100]"
}
```

### color属性

设备的颜色，比如智能彩色灯泡，属性值是一个表示颜色的对象。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值color。 |
| value | 属性值，是对象类型。  * hue：表示颜色的色相，double类型，取值范围是0~360，包括0和360。 * saturation：表示颜色的饱和度，double类型，取值范围是0~1，包括0和1。 * brightness：表示颜色的明度，double类型，取值范围是0~1，包括0和1。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
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
```

### colorTemperatureInKelvin属性

设备的色温属性，比如可调白光的灯泡。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值colorTemperatureInKelvin。 |
| value | 属性值，整数类型，取值范围为1000~10000，包括1000和10000，根据设备自身范围设定。比较常见的色温值：   * 2200：暖色。 * 2700：明亮。 * 4000：白光。 * 5500：日光。 * 7000：冷白光。 |
| scale | 属性值的单位，是Kelvin（K）。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "colorTemperatureInKelvin",
    "value": 3000,
    "scale": "K",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[1000, 10000]"
}
```

### dateTime属性

日期和时间属性，比如电饭煲的定时做饭的时间。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值dateTime。 |
| value | 属性值，是字符串类型，有效值是标准ISO 8601格式，UTC时间，精度为1秒。RFC 3399变体是首选，但不允许使用负偏移。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "dateTime",
    "value": "2018-03-30T11:18:33Z",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "STRING"
}
```

### turnOnState属性

设备的开关状态属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值turnOnState。 |
| value | 属性值，是枚举类型，取值如下。   * ON：表示设备处于打开状态。 * OFF：表示设备处于关闭状态。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "turnOnState",
    "value": "ON",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(ON, OFF)"
}
```

### pauseState属性

设备的暂停属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值pauseState。 |
| value | 属性值，是布尔类型。   * true：表示设备处于暂停状态。 * false：表示设备未处于暂停状态。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "pauseState",
    "value": true,
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "BOOLEAN"
}
```

### lockState属性

锁的状态属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值lockState。 |
| value | 属性值，枚举类型，取值如下：   * LOCKED：表示设备处于锁状态。 * UNLOCKED：表示设备未处于锁状态。 * JAMMED：表示设备处于锁被卡状态，设备云无法知道设备锁状态。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "lockState",
    "value": "LOCKED",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(LOCKED, UNLOCKED, JAMMED)"
}
```

### electricityCapacity属性

设备电池的电量属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值electricityCapacity。 |
| value | 属性值，DOUBLE类型，取值范围是0~100，包括0和100。 |
| scale | 属性值的单位，是百分比取值（%）。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "electricityCapacity",
    "value": 20.5,
    "scale": "%",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0.0, 100.0]"
}
```

### oilCapacity属性

设备油箱的油量属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值oilCapacity。 |
| value | 属性值，DOUBLE类型，取值范围是0~100，包括0和100。 |
| scale | 属性值的单位，是百分比取值（%）。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "oilCapacity",
    "value": 32,
    "scale": "%",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0.0, 100.0]"
}
```

### drivingDistance属性

设备可行驶距离属性，比如车里的油可供车行使50.0公里。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值drivingDistance。 |
| value | 属性值，是DOUBLE类型。 |
| scale | 属性值的单位，是公里。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值可取的合法值。 |

#### 消息示例

```
{
    "name": "drivingDistance",
    "value": 50.0,
    "scale": "公里",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "DOUBLE"
}
```

### fanSpeed属性

设备风速值属性，比如把空调风速是2档。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值fanSpeed。 |
| value | 属性值，是整数类型，取值范围是0~10，包括0和10。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "fanSpeed",
    "value": 2,
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0, 10]"
}
```

### speed属性

设备速度值属性，比如跑步机当前速度多少。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，speed: 当前速度， maxSpeed: 最大速度， minSpeed: 最小速度。 |
| value | 属性值，是float类型。 |
| scale | 属性值的单位，该字段默认为（KM/H）。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "speed",
    "value": 2.0,
    "scale": "KM/H",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0, 10]"
}
```

### motionInfo属性

运动信息属性，比如在跑步机上跑了2公里。
eg: 我跑了多久，我跑了多少步，我跑了多少米/千米

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值motionInfo。 |
| value | 属性值，是float类型。 |
| scale | 属性值的单位，该字段默认为（KM）。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "motionInfo",
    "value": 2.0,
    "scale": "KM",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": ""
}
```

### channel属性

电视频道属性，比如电视3频道。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值channel。 |
| value | 属性值，是整数类型。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "channel",
    "value": 3,
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "INTEGER"
}
```

### muteState属性

发声设备当前的静音属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值muteState。 |
| value | 属性值，是布尔类型。  * true：表示设备处于静音状态。 * false：表示设备未处于静音状态。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "muteState",
    "value": true,
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "BOOLEAN"
}
```

### volume属性

设备的音量属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值volume。 |
| value | 属性值，是整数类型，取值范围为0~100，包括0和100。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "volume",
    "value": 50,
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "[0, 100]"
}
```

### suction属性

设备的吸力属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值suction。 |
| value | 属性值，枚举类型，取值如下：   * STANDARD：标准档。 * STRONG：强劲档。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "suction",
    "value": "STANDARD",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(STANDARD, STRONG)"
}
```

### waterLevel属性

设备的水量属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值waterLevel。 |
| value | 属性值，枚举类型，取值如下：   * LOW：低档。 * MEDIUM：中档。 * HIGH：高档。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "waterLevel",
    "value": "MEDIUM",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(LOW, MEDIUM, HIGH)"
}
```

### location属性

设备的位置属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值location。 |
| value | 属性值，字符串类型，比如：   * 客厅。 * 卧室。 * 书房。 * 其它。   属性值会直接拼接在话术中进行播报，或者在有屏端直接展现，需要提供能展示的明文。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "location",
    "value": "客厅",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "STRING"
}
```

### workState属性

设备的工作状态属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值workState。 |
| value | 属性值，枚举类型，取值如下：   * STOP：停止。 * START：开始。 * PAUSE：暂停。 * WORKING：工作中。 * WORK_NEARLY_FINISHED：即将完成。 * DONE：完成。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "workState",
    "value": "WORKING",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(STOP, START, PAUSE, WORKING, WORK_NEARLY_FINISHED, DONE)"
}
```

### warmthLevel属性

设备的暖度属性。

#### 参数说明

| 参数名称 | 参数说明 |
| --- | --- |
| name | 属性名称，取固定值warmthLevel。 |
| value | 属性值，枚举类型，取值如下：   * LOW：低档。 * MIDDLE：中档。 * HIGH：高档。 |
| scale | 属性值的单位，该字段为空。 |
| timestampOfSample | 属性值取样的时间戳。 |
| uncertaintyInMilliseconds | 属性值取样的时间误差。 |
| legalValue | 属性值取值的合法范围。 |

#### 消息示例

```
{
    "name": "warmthLevel",
    "value": "MIDDLE",
    "scale": "",
    "timestampOfSample": 1496741861,
    "uncertaintyInMilliseconds": 10,
    "legalValue": "(LOW, MIDDLE, HIGH)"
}
```

## 属性状态上报

为了方便DuerOS了解和管理设备，技能需要将设备的属性上报给DuerOS，具体的上报方式请参考[属性上报](attributes-report.md)。
