---
title: "发现设备"
source: "https://dueros.baidu.com/didp/doc/dueros-bot-platform/dbp-smart-home/protocol/discovery-message_markdown"
fetched_at: "2026-09-06 00:00 CST"
---

# 发现设备

发现设备消息用于查找用户可用的设备、可以使用的场景和设备分组信息，有DiscoverAppliancesRequest和DiscoverAppliancesResponse两个指令。DiscoverAppliancesRequest指令是发出查找设备请求，DiscoverAppliancesResponse指令回复查找到的设备。如果你的技能应用中的用户设备信息变更时,可以通过DuerOS提供的异步接口发送通知，触发用户设备信息同步到DuerOS。

## DiscoverAppliancesRequest

当用户查找设备时，DuerOS会将该消息发送给技能。另外，用户每次在DuerOS技能商店启用你的技能时，此消息会自动触发一次。

### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DiscoverAppliancesRequest |
| namespace | DuerOS.ConnectedHome.Discovery |

### Payload信息

| 属性 | 描述 | 是否必须 |
| --- | --- | --- |
| accessToken | 设备云端获取的access token。 | 是 |
| openUid | 被授权的百度账号开放ID，与设备云账号一一对应。设备云端需要将该字段与用户账号一一对应起来存储，主要用于后续的设备[状态同步](notification-message.md) | 是 |

### 应用举例

发现设备的时机有：

* 用户对小度说“发现设备”，在用户完成授权的基础上，会向技能发送DiscoverAppliancesRequest消息；
* 用户在小度APP登录三方账号完成技能授权后，会向技能发送DiscoverAppliancesRequest消息；
* 在用户完成三方账号授权的基础上，用户每次进入小度APP智能家居首页时，会向技能发送DiscoverAppliancesRequest消息。

消息示例如下：

```
{
    "header": {
        "namespace": "DuerOS.ConnectedHome.Discovery",
        "name": "DiscoverAppliancesRequest",
        "messageId": "6d6d6e14-8aee-473e-8c24-0d31ff9c17a2",
        "payloadVersion": "1"
    },
    "payload": {
        "accessToken": "[OAuth Token here]",
        "openUid": "27a7d83c2d3cfbad5d387cd35f3ca17b"
    }
}
```

## DiscoverAppliancesResponse

当DuerOS请求技能查找可用设备或可用场景时，技能会返回DiscoverAppliancesResponse消息。 如果查找到设备时，会返回设备的相关信息，包括actions、applianceTypes、additionalApplianceDetails、applianceId、friendlyDescription、friendlyName等属性信息。如果没有找到设备时，会返回空数组。

### Header信息

| 属性 | 取值 |
| --- | --- |
| name | DiscoverAppliancesResponse |
| namespace | DuerOS.ConnectedHome.Discovery |

### Payload信息

#### 设备信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| discoveredAppliances | 以对象数组返回客户关联设备云帐户的设备、场景。如客户关联帐户没有设备、场景则返回空数组。如果在发现过程中出现错误，字段值设置为null, 用户允许接入的最大的设备数量是300。 | 是 |
| discoveredAppliance.applianceTypes | 支持的设备、场景类型。目前支持以下设备。  * LIGHT：电灯 * AIR_CONDITION：空调 * CURTAIN：窗帘 * CURT_SIMP：窗纱 * SOCKET：插座 * SWITCH：开关 * FRIDGE：冰箱 * WATER_PURIFIER：净水器 * HUMIDIFIER：加湿器 * DEHUMIDIFIER：除湿器 * INDUCTION_COOKER：电磁炉 * AIR_PURIFIER：空气净化器 * WASHING_MACHINE：洗衣机 * WATER_HEATER：热水器 * GAS_STOVE：燃气灶 * TV_SET：电视机 * OTT_BOX：网络盒子 * RANGE_HOOD：油烟机 * FAN：电风扇 * PROJECTOR：投影仪 * SWEEPING_ROBOT：扫地机器人 * KETTLE：热水壶 * MICROWAVE_OVEN：微波炉 * PRESSURE_COOKER：压力锅 * RICE_COOKER：电饭煲 * HIGH_SPEED_BLENDER：破壁机 * AIR_FRESHER：新风机 * CLOTHES_RACK：晾衣架 * OVEN：烤箱设备 * STEAM_OVEN：蒸烤箱 * STEAM_BOX：蒸箱 * HEATER：电暖器 * WINDOW_OPENER：开窗器 * WEBCAM：摄像头 * CAMERA：相机 * ROBOT：机器人 * PRINTER: 打印机 * WATER_COOLER：饮水机 * FISH_TANK：鱼缸 * WATERING_DEVICE：浇花器 * SET_TOP_BOX：机顶盒 * AROMATHERAPY_MACHINE：香薰机 * DVD：DVD * SHOE_CABINET：鞋柜 * WALKING_MACHINE：走步机 * TREADMILL：跑步机 * BED：床 * YUBA：浴霸 * SHOWER：花洒 * BATHTUB：浴缸 * DISINFECTION_CABINET：消毒柜 * DISHWASHER：洗碗机 * SOFA: 沙发品类 * DOOR_BELL：门铃 * ELEVATOR：电梯 * WEIGHT_SCALE：体重秤 * BODY_FAT_SCALE：体脂秤 * WALL_HUNG_GAS_BOILER：壁挂炉 * SCENE_TRIGGER：描述特定设备的组合场景，设备之间没有相互关联，无特定操作顺序。 例如“打开睡眠模式”包括关灯和锁上房门，但是关灯和锁上房门之间没有必然联系，可以先关灯然后锁上房门，也可以先锁上房门后关灯。 * ACTIVITY_TRIGGER：描述特定设备的组合场景。场景中的设备必须以指定顺序操作。如“观看优酷视频”场景中必须先打开电视机，然后打开HDMI1。 | 是 |
| discoveredAppliance.applianceId | 设备标识符。标识符在用户拥有的所有设备上必须是唯一的。此外，标识符需要在同一设备的多个发现请求之间保持一致，如发生变化，会被认为新设备。标识符可以包含任何字母或数字和以下特殊字符：_ - = # ; : ? @ &。标识符不能超过256个字符。 | 是 |
| discoveredAppliance.modelName | 设备型号名称，是字符串类型，长度不能超过128个字符。 | 是 |
| discoveredAppliance.version | 供应商提供的设备版本。是字符串类型，长度不能超过128个字符。 | 是 |
| discoveredAppliance.friendlyName | 用户用来识别设备的名称。 是字符串类型，不能包含特殊字符和标点符号，长度不能超过128个字符。 | 是 |
| discoveredAppliance.friendlyDescription | 设备相关的描述，描述内容提需要提及设备厂商，使用场景及连接方式，长度不超过128个字符。 | 是 |
| discoveredAppliance.isReachable | 设备当前是否能够到达。true表示设备当前可以到达，false表示当前设备不能到达。 | 是 |
| discoveredAppliance.actions | 设备支持的操作类型数组。详细情况请参见 [设备操作类型](#设备操作类型)。 | 是 |
| discoveredAppliance.additionalApplianceDetails | 提供给设备云使用，存放设备或场景相关的附加信息，是键值对。DuerOS不解析或使用这些数据。该属性的内容不能超过5000字节。 | 是，内容可以为空 |
| discoveredAppliance.manufacturerName | 设备厂商的名字。 | 是 |
| discoveredAppliance.attributes | 设备的属性信息。当设备没有属性信息时，协议中不需要传入该字段。每个设备允许同步的最大的属性数量是10。详细信息请参考[设备属性](attributes.md)及[设备属性上报](attributes-report.md)。 | 否，建议将设备属性上报给DuerOS，方便用户查询。 |
| discoveredAppliance.attribute.name | 属性名称，支持数字、字母和下划线，长度不能超过128个字符。 | 是 |
| discoveredAppliance.attribute.value | 属性值，支持多种json类型。 | 是 |
| discoveredAppliance.attribute.scale | 属性值的单位名称，支持数字、字母和下划线，长度不能超过128个字符。 | 是 |
| discoveredAppliance.attribute.timestampOfSample | 属性值取样的时间戳，单位是秒。 | 是 |
| discoveredAppliance.attribute.uncertaintyInMilliseconds | 属性值取样的时间误差，单位是ms。如果设备使用的是轮询时间间隔的取样方式，那么uncertaintyInMilliseconds就等于时间间隔。如温度传感器每1秒取样1次，那么uncertaintyInMilliseconds的值就是1000。 | 是 |

##### 设备操作类型

智能家居设备支持以下操作类型。

* turnOn：打开
* turnOff：关闭
* timingTurnOn：定时打开
* timingTurnOff：定时关闭
* pause：暂停
* continue：继续
* setColor：设置颜色
* setColorTemperature：设置灯光色温
* incrementColorTemperature：增高灯光色温
* decrementColorTemperature：降低灯光色温
* setBrightnessPercentage：设置灯光亮度
* incrementBrightnessPercentage：调亮灯光
* decrementBrightnessPercentage：调暗灯光
* setPower：设置功率
* incrementPower：增大功率
* decrementPower：减小功率
* incrementTemperature：升高温度
* decrementTemperature：降低温度
* setTemperature：设置温度
* incrementFanSpeed：增加风速
* decrementFanSpeed：减小风速
* setFanSpeed：设置风速
* setGear：设置档位
* setMode：设置模式
* unSetMode：取消设置的模式
* timingSetMode：定时设置模式
* timingUnsetMode：定时取消设置的模式
* incrementVolume：调高音量
* decrementVolume：调低音量
* setVolume：设置音量
* setVolumeMute：设置静音状态
* decrementTVChannel：上一个频道
* incrementTVChannel：下一个频道
* setTVChannel：设置频道
* returnTVChannel：返回上个频道
* chargeTurnOn：开始充电
* chargeTurnOff：停止充电
* getTurnOnState：查询开关状态
* getOilCapacity：查询油量
* getElectricityCapacity：查询电量
* setLockState：上锁/解锁
* getLockState：查询锁状态
* setSuction：设置吸力
* setWaterLevel：设置水量
* setCleaningLocation：设置清扫位置
* setComplexActions：执行自定义复杂动作
* setDirection：设置移动方向
* submitPrint：打印
* getAirPM25：查询PM2.5
* getAirPM10：查询PM10
* getCO2Quantity：查询二氧化碳含量
* getAirQualityIndex：查询空气质量
* getTemperature：查询温度（当前温度和目标温度）
* getTemperatureReading：查询当前温度
* getTargetTemperature：查询目标温度
* getHumidity：查询湿度
* getTargetHumidity：查询目标湿度
* getWaterQuality：查询水质
* getState：查询设备所有状态
* getTimeLeft：查询剩余时间
* getRunningStatus：查询运行状态
* getRunningTime：查询运行时间
* getLocation：查询设备所在位置
* setTimer：设备定时
* timingCancel：取消设备定时
* reset：设备复位
* incrementHeight：升高高度
* decrementHeight：降低高度
* setSwingAngle：设置摆风角度
* getFanSpeed：查询风速
* setHumidity：设置湿度模式
* incrementHumidity：增大湿度
* decrementHumidity：降低湿度
* incrementMist：增大雾量
* decrementMist：见效雾量
* setMist：设置雾量
* startUp：设备启动
* setFloor：设置电梯楼层
* decrementFloor：电梯按下
* incrementFloor：电梯按上
* incrementSpeed：增加速度
* decrementSpeed：降低速度
* setSpeed：设置速度
* getSpeed：获取速度
* getMotionInfo：获取跑步信息
* turnOnBurner：打开灶眼
* turnOffBurner：关闭灶眼
* timingTurnOnBurner：定时打开灶眼
* timingTurnOffBurner：定时关闭灶眼

#### 分组信息

| 属性 | 描述说明 | 是否必须 |
| --- | --- | --- |
| discoveredGroups | discoveredGroups 对象的数组，该对象包含可发现分组，与用户设备帐户相关联的。 如果没有与用户帐户关联的分组，此属性应包含一个空数组。 如果发生错误，该属性可以为空数组[]。阵列中允许的最大项目数量为10。 | 是 |
| discoveredGroups.groupName | 用户用来识别分组的名称, 不应包含特殊字符或标点符号，长度不超过20字符。 | 是 |
| discoveredGroups.applianceIds | 分组所包含设备ID的数组，要求设备ID必须是已经发现的设备中的ID，否则会同步失败，每个分组设备ID数量不超过50。 | 是 |
| discoveredGroups.groupNotes | 分组备注信息，不能超过128个字符。 | 是 |
| discoveredGroups.additionalGroupDetails | 提供给技能使用的分组相关的附加信息的键值对。该属性的内容不能超过2000字符。而且DuerOS也不了解或使用这些数据。 | 是，但可以为空数组[] |

**说明：**

* 如果没有找到设备或相关场景，此时返回的discoveredAppliances是一个空数组。如果查找设备过程中发生了错误，该字段值设置为null。
* 当applianceTypes=ACTIVITY_TRIGGER/SCENE_TRIGGER时，场景和模式不支持通过分组来控制，比如只支持“打开回家模式”，而不支持“打开客厅的回家模式”。
* 房间名称建议：主卧、次卧、客厅、卧室、餐厅、书房、厨房、洗手间、阳台、门口、浴室、衣帽间、客房、老人房、儿童房、婴儿房、保姆房、宠物房、影音室、娱乐室、工作间、杂物间、吧台、花园、楼上、楼下、玄关、一楼、二楼、三楼、四楼、楼梯、走廊、过道、办公室、温室、起居室、休息室、车库，同时，小度也支持自定义房间名称。

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
                    "setBrightnessPercentage"
                ],
                "applianceTypes": [
                    "LIGHT"
                ],
                "additionalApplianceDetails": {
                    "extraDetail1": "optionalDetailForSkillAdapterToReferenceThisDevice",
                    "extraDetail2": "There can be multiple entries",
                    "extraDetail3": "but they should only be used for reference purposes",
                    "extraDetail4": "This is not a suitable place to maintain current device state"
                },
                "applianceId": "uniqueLightDeviceId",
                "friendlyDescription": "展现给用户的详细介绍",
                "friendlyName": "灯",
                "isReachable": true,
                "manufacturerName": "设备制造商的名称",
                "modelName": "fancyLight",
                "version": "your software version number here.",
                "attributes": [
                    {
                        "name": "turnOnState",
                        "value": "ON",
                        "scale": "",
                        "timestampOfSample": 1496741861,
                        "uncertaintyInMilliseconds": 10
                    },
                    {
                        "name": "brightness",
                        "value": "50",
                        "scale": "",
                        "timestampOfSample": 1496741861,
                        "uncertaintyInMilliseconds": 100
                    },
                    {
                        "name": "connectivity",
                        "value": "REACHABLE",
                        "scale": "",
                        "timestampOfSample": 1496741861,
                        "uncertaintyInMilliseconds": 10
                    }
                ]
            },
            {
                "actions": [
                    "turnOn",
                    "turnOff"
                ],
                "applianceTypes": [
                    "CURTAIN"
                ],
                "additionalApplianceDetails": {
                    "extraDetail1": "optionalDetailForSkillAdapterToReferenceThisDevice",
                    "extraDetail2": "There can be multiple entries",
                    "extraDetail3": "but they should only be used for reference purposes",
                    "extraDetail4": "This is not a suitable place to maintain current device state"
                },
                "applianceId": "uniqueSwitchDeviceId",
                "friendlyDescription": "展现给用户的详细介绍",
                "friendlyName": "窗帘",
                "isReachable": true,
                "manufacturerName": "设备制造商的名称",
                "modelName": "fancyCurtain",
                "version": "your software version number here",
                "attributes": [
                    {
                        "name": "connectivity",
                        "value": "REACHABLE",
                        "scale": "",
                        "timestampOfSample": 1496741861,
                        "uncertaintyInMilliseconds": 10
                    },
                    {
                        "name": "turnOnState",
                        "value": "ON",
                        "scale": "",
                        "timestampOfSample": 1496741861,
                        "uncertaintyInMilliseconds": 10
                    }
                ]
            },
            {
                "actions": [
                    "turnOn"
                ],
                "applianceTypes": [
                    "SCENE_TRIGGER"
                ],
                "additionalApplianceDetails": {
                    "extraDetail1": "detail about the scene",
                    "extraDetail2": "another detail about scene",
                    "extraDetail3": "only be used for reference purposes"
                },
                "applianceId": "uniqueDeviceId",
                "friendlyDescription": "来自设备商的场景",
                "friendlyName": "回家",
                "isReachable": true,
                "manufacturerName": "yourManufacturerName",
                "modelName": "提供场景的设备型号",
                "version": "your software version number here",
                "attributes": []
            }
        ],
        "discoveredGroups": [
            {
                "groupName": "客厅",
                "applianceIds": [
                    "uniqueLightDeviceId1",
                    "uniqueLightDeviceId2",
                    "uniqueLightDeviceId3"
                ]
            },
            {
                "groupName": "卧室",
                "applianceIds": [
                    "uniqueLightDeviceId4",
                    "uniqueLightDeviceId5",
                    "uniqueLightDeviceId6"
                ]
            }
        ]
    }
}
```
