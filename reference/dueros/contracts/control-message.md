# control-message（契约速查）


> 由 `make_contracts.py` 生成；原文：`../dbp-smart-home-protocol/control-message.md`

## 分组：TurnOnRequest

### TurnOnRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#turnonrequest](control-message.md#turnonrequest)

### TurnOnConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备控制后的状态或属性，支持返回多个，状态的定义一定是在[属性信息](attributes.md)列表中。注意不是控制前的状态，可以  []
- 原文：[control-message.md#turnonconfirmation](control-message.md#turnonconfirmation)

### TimingTurnOnRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `timestamp` — 表示设备定时设置的值，它指定一个数字，代表时间戳，单位是秒。  [必填]
- 原文：[control-message.md#timingturnonrequest](control-message.md#timingturnonrequest)

### TimingTurnOnConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#timingturnonconfirmation](control-message.md#timingturnonconfirmation)

### TurnOffRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#turnoffrequest](control-message.md#turnoffrequest)

### TurnOffConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#turnoffconfirmation](control-message.md#turnoffconfirmation)

### TimingTurnOffRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `timestamp` — 表示设备定时设置的值，它指定一个数字，代表时间戳，单位是秒。  [必填]
- 原文：[control-message.md#timingturnoffrequest](control-message.md#timingturnoffrequest)

### TimingTurnOffConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#timingturnoffconfirmation](control-message.md#timingturnoffconfirmation)

### PauseRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#pauserequest](control-message.md#pauserequest)

### PauseConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#pauseconfirmation](control-message.md#pauseconfirmation)

### ContinueRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#continuerequest](control-message.md#continuerequest)

### ContinueConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#continueconfirmation](control-message.md#continueconfirmation)

### StartUpRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#startuprequest](control-message.md#startuprequest)

### StartUpConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#startupconfirmation](control-message.md#startupconfirmation)

### SetBrightnessPercentageRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `brightness` — 灯光亮度的对象。  [必填]
  - `brightness.value` — 灯光亮度的百分比值，是double类型，取值范围为0～100。其中0表示灯在打开时的最小亮度，100表示灯的最大亮度。  [必填]
- 原文：[control-message.md#setbrightnesspercentagerequest](control-message.md#setbrightnesspercentagerequest)

### SetBrightnessPercentageConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setbrightnesspercentageconfirmation](control-message.md#setbrightnesspercentageconfirmation)

### IncrementBrightnessPercentageRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaPercentage` — 亮度的百分比增量信息，包含value。  [必填]
  - `deltaPercentage.value` — 亮度增加的百分比值，是float类型，取值范围是0～100。  [必填]
- 原文：[control-message.md#incrementbrightnesspercentagerequest](control-message.md#incrementbrightnesspercentagerequest)

### IncrementBrightnessPercentageConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#incrementbrightnesspercentageconfirmation](control-message.md#incrementbrightnesspercentageconfirmation)

### DecrementBrightnessPercentageRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaPercentage` — 亮度的百分比减量信息。  [必填]
  - `deltaPercentage.value` — 亮度减少的百分比值，是float类型，取值范围是0～100。  [是deltaPercentage的必须项。]
- 原文：[control-message.md#decrementbrightnesspercentagerequest](control-message.md#decrementbrightnesspercentagerequest)

### DecrementBrightnessPercentageConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#decrementbrightnesspercentageconfirmation](control-message.md#decrementbrightnesspercentageconfirmation)

### SetColorRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `color` — 灯设置的颜色。包括[色相、饱和度、亮度（HSB）颜色模型](https://en.wikipedia.org/wiki/HSL_and_H…  [必填]
  - `color.hue` — 灯光设置的色相，是double类型，取值范围为0.00〜360.00。  [必填]
  - `color.saturation` — 灯光设置饱和度，是double类型，取值范围为0.0000〜1.0000。  [必填]
  - `color.brightness` — 灯光设置的亮度，是double类型，取值范围为0.0000〜1.0000。  [必填]
- 原文：[control-message.md#setcolorrequest](control-message.md#setcolorrequest)

### SetColorConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setcolorconfirmation](control-message.md#setcolorconfirmation)

### IncrementColorTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaPercentage` — 色温的百分比增量信息，包含value。  [必填]
  - `deltaPercentage.value` — 色温增加的百分比值，是float类型，取值范围是0～100。  [必填]
- 原文：[control-message.md#incrementcolortemperaturerequest](control-message.md#incrementcolortemperaturerequest)

### IncrementColorTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。色温属性取值范围legalValue，根据设备实际范围上报。]
- 原文：[control-message.md#incrementcolortemperatureconfirmation](control-message.md#incrementcolortemperatureconfirmation)

### DecrementColorTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaPercentage` — 色温的百分比减量信息，包含value。  [必填]
  - `deltaPercentage.value` — 色温减小的百分比值，是float类型，取值范围是0～100。  [必填]
- 原文：[control-message.md#decrementcolortemperaturerequest](control-message.md#decrementcolortemperaturerequest)

### DecrementColorTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。色温属性取值范围legalValue，根据设备实际范围上报。]
- 原文：[control-message.md#decrementcolortemperatureconfirmation](control-message.md#decrementcolortemperatureconfirmation)

### SetColorTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `colorTemperatureInKelvin` — 色温值。  [必填]
- 原文：[control-message.md#setcolortemperaturerequest](control-message.md#setcolortemperaturerequest)

### SetColorTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。色温属性取值范围legalValue，根据设备实际范围上报。]
- 原文：[control-message.md#setcolortemperatureconfirmation](control-message.md#setcolortemperatureconfirmation)

### IncrementTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备温度的增量信息。  [否， 当值为空时表示用户没有指定调高的具体值]
  - `deltaValue.value` — 设备温度增量的具体值，是float类型。  [当deltaValue存在时，该项必须存在。]
  - `deltaValue.scale` — 温度计量单位。有CELSIUS(摄氏温度)和FAHRENHEIT(华氏温度)两种计量单位，默认使用CELSIUS。  [在deltaValue不为空时为是]
- 原文：[control-message.md#incrementtemperaturerequest](control-message.md#incrementtemperaturerequest)

### IncrementTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，模式取值范围legalValue，根据设备支持的模式自行设定。]
- 原文：[control-message.md#incrementtemperatureconfirmation](control-message.md#incrementtemperatureconfirmation)

### DecrementTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备温度的减量信息。  [否， 当值为空时表示用户没有指定调高的具体值]
  - `deltaValue.value` — 设备温度减量的具体值，是float类型。  [当deltaValue存在时，该项必须存在。]
  - `deltaValue.scale` — 温度计量单位。有CELSIUS(摄氏温度)和FAHRENHEIT(华氏温度)两种计量单位，默认使用CELSIUS。  [在deltaValue不为空时为是]
- 原文：[control-message.md#decrementtemperaturerequest](control-message.md#decrementtemperaturerequest)

### DecrementTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，模式取值范围legalValue，根据设备支持的模式自行设定。]
- 原文：[control-message.md#decrementtemperatureconfirmation](control-message.md#decrementtemperatureconfirmation)

### SetTemperatureRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `targetTemperature` — 设备设定的目标温度。  [必填]
  - `targetTemperature.value` — 设备设定的目标温度值。  [必填]
  - `targetTemperature.scale` — 温度计量单位。有CELSIUS(摄氏温度)和FAHRENHEIT(华氏温度)两种计量单位，默认使用CELSIUS。  [必填]
- 原文：[control-message.md#settemperaturerequest](control-message.md#settemperaturerequest)

### SetTemperatureConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，模式取值范围legalValue，根据设备支持的模式自行设定。]
- 原文：[control-message.md#settemperatureconfirmation](control-message.md#settemperatureconfirmation)

### IncrementFanSpeedRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备风速的增量信息。  [可选]
  - `deltaValue.value` — 设备风速增量的具体值，是int类型。  [deltaValue对象的必须项]
- 原文：[control-message.md#incrementfanspeedrequest](control-message.md#incrementfanspeedrequest)

### IncrementFanSpeedConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，风速取值范围legalValue，根据设备风速范围设定，模式也是一样。]
- 原文：[control-message.md#incrementfanspeedconfirmation](control-message.md#incrementfanspeedconfirmation)

### DecrementFanSpeedRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备风速的减量信息。  [可选]
  - `deltaValue.value` — 设备风速减量的具体值，是int类型。  [deltaValue对象的必须项]
- 原文：[control-message.md#decrementfanspeedrequest](control-message.md#decrementfanspeedrequest)

### DecrementFanSpeedConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，风速取值范围legalValue，根据设备风速范围设定，模式也是一样。]
- 原文：[control-message.md#decrementfanspeedconfirmation](control-message.md#decrementfanspeedconfirmation)

### SetFanSpeedRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `fanSpeed` — 设备的风速对象，包含一个属性值value或者一个属性值level，取决于用户自然表达。  [必填]
  - `fanSpeed.value` — 设备的风速值，是int类型，取值范围是1～10。用户表达具体风速值时，会出该字段。  [可选]
  - `fanSpeed.level` — 设备的风速档位级别，是string类型，取值范围是(min、low、middle、high、max、auto))。用户表达风速级别时，会出…  [可选]
- 原文：[control-message.md#setfanspeedrequest](control-message.md#setfanspeedrequest)

### SetFanSpeedConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，风速取值范围legalValue，根据设备风速范围设定，模式也是一样。]
- 原文：[control-message.md#setfanspeedconfirmation](control-message.md#setfanspeedconfirmation)

### IncrementSpeedRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备速度的增量信息。  [可选]
  - `deltaValue.value` — 设备速度增量的具体值, 小数点后保持2位的float。  [deltaValue对象的必须项]
- 原文：[control-message.md#incrementspeedrequest](control-message.md#incrementspeedrequest)

### IncrementSpeedConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，速度取值范围legalValue，根据设备速度范围自行定义。]
- 原文：[control-message.md#incrementspeedconfirmation](control-message.md#incrementspeedconfirmation)

### DecrementSpeedRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备速度减量信息。  [可选]
  - `deltaValue.value` — 设备速度减量的具体值, 小数点后保持2位的float。  [deltaValue对象的必须项]
- 原文：[control-message.md#decrementspeedrequest](control-message.md#decrementspeedrequest)

### DecrementSpeedConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，速度取值范围legalValue，根据设备速度范围自行定义。]
- 原文：[control-message.md#decrementspeedconfirmation](control-message.md#decrementspeedconfirmation)

### SetSpeedRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `speed` — 设备的速度对象，包含一个属性值value或者一个属性值level，取决于用户自然表达。  [必填]
  - `speed.value` — 设备的速度值, 小数点后保持2位的float。用户表达具体速度值时，会出该字段。  [可选]
  - `speed.level` — 设备的速度档位级别，是string类型，取值范围是(min、low、middle、high、max、auto))。用户表达速度级别时，会出…  [可选]
- 原文：[control-message.md#setspeedrequest](control-message.md#setspeedrequest)

### SetSpeedConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。其中，速度取值范围legalValue，根据设备速度范围自行定义。]
- 原文：[control-message.md#setspeedconfirmation](control-message.md#setspeedconfirmation)

### SetModeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `mode` — 设备的模式信息。  [必填]
  - `mode.value` — 设备模式，详细信息请参见[设备模式表](#设备类型与模式表)。  [必填]
- 原文：[control-message.md#setmoderequest](control-message.md#setmoderequest)

### SetModeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。设备模式，请参考[设备模式表](#设备类型与模式表)，legalValue根据设备自身模式范围，自行设定。]
- 原文：[control-message.md#setmodeconfirmation](control-message.md#setmodeconfirmation)

### UnsetModeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `mode` — 设备的模式信息。  [必填]
  - `mode.value` — 设备模式，详细信息请参见[设备模式表](#设备类型与模式表)。  [必填]
- 原文：[control-message.md#unsetmoderequest](control-message.md#unsetmoderequest)

### UnsetModeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。设备模式，请参考[设备模式表](#设备类型与模式表)，legalValue根据设备自身模式范围，自行设定。]
- 原文：[control-message.md#unsetmodeconfirmation](control-message.md#unsetmodeconfirmation)

### TimingSetModeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `mode` — 设备的模式信息。  [必填]
  - `mode.value` — 设备模式，详细信息请参见[设备模式表](#设备类型与模式表)。  [必填]
- 原文：[control-message.md#timingsetmoderequest](control-message.md#timingsetmoderequest)

### TimingSetModeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。设备模式，请参考[设备模式表](#设备类型与模式表)，legalValue根据设备自身模式范围，自行设定。]
- 原文：[control-message.md#timingsetmodeconfirmation](control-message.md#timingsetmodeconfirmation)

### IncrementTVChannelRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#incrementtvchannelrequest](control-message.md#incrementtvchannelrequest)

### IncrementTVChannelConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#incrementtvchannelconfirmation](control-message.md#incrementtvchannelconfirmation)

### DecrementTVChannelRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#decrementtvchannelrequest](control-message.md#decrementtvchannelrequest)

### DecrementTVChannelConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#decrementtvchannelconfirmation](control-message.md#decrementtvchannelconfirmation)

### ReturnTVChannelRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#returntvchannelrequest](control-message.md#returntvchannelrequest)

### ReturnTVChannelConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#returntvchannelconfirmation](control-message.md#returntvchannelconfirmation)

### SetTVChannelRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备电视频道变化信息。  [否， 当值为空时表示用户没有指定频道信息]
  - `deltaValue.value` — 设备频道变化值，int类型或者string类型。当是int类型时, 表示数字频道；当是字符串时，表示频度名称，比如湖南卫视、中央一套等。  [当deltaValue存在时，该项必须存在。]
- 原文：[control-message.md#settvchannelrequest](control-message.md#settvchannelrequest)

### SetTVChannelConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#settvchannelconfirmation](control-message.md#settvchannelconfirmation)

### IncrementVolumeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备音量增量信息，为空时表示用户没有指定音量调节的具体值。  [可选]
  - `deltaValue.value` — 设备增大音量值，是int类型。音量范围0-100  [当deltaValue存在时，该项必须存在。]
- 原文：[control-message.md#incrementvolumerequest](control-message.md#incrementvolumerequest)

### IncrementVolumeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#incrementvolumeconfirmation](control-message.md#incrementvolumeconfirmation)

### DecrementVolumeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备音量减量信息。  [否， 当值为空时表示用户没有指定音量调小的具体值]
  - `deltaValue.value` — 设备减小音量值，是int类型。音量范围0-100  [当deltaValue存在时，该项必须存在。]
- 原文：[control-message.md#decrementvolumerequest](control-message.md#decrementvolumerequest)

### DecrementVolumeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#decrementvolumeconfirmation](control-message.md#decrementvolumeconfirmation)

### SetVolumeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备音量变化信息。  [否， 当值为空时表示用户没有指定音量调小的具体值]
  - `deltaValue.value` — 设备音量变化值，是int类型。音量范围0-100  [当deltaValue存在时，该项必须存在。]
- 原文：[control-message.md#setvolumerequest](control-message.md#setvolumerequest)

### SetVolumeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setvolumeconfirmation](control-message.md#setvolumeconfirmation)

### SetVolumeMuteRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 设备静音开关的变化信息。  [必填]
  - `deltaValue.value` — 设备静音状态，枚举类型，取值为如下。 * on：将设备设置为静音状态。 * off：取消设备的静音。  [必填]
- 原文：[control-message.md#setvolumemuterequest](control-message.md#setvolumemuterequest)

### SetVolumeMuteConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setvolumemuteconfirmation](control-message.md#setvolumemuteconfirmation)

### SetLockStateRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `lockState` — 设备当前锁定状态，枚举类型，取值如下。 * LOCKED：设备处于锁定状态。 * UNLOCKED：设备处于解锁状态。  [必填]
- 原文：[control-message.md#setlockstaterequest](control-message.md#setlockstaterequest)

### SetLockStateConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `lockState` — 设备锁定状态信息。  [必填]
  - `lockState.value` — 设备当前锁定状态，枚举类型，取值如下。 * LOCKED：设备处于锁定状态。 * UNLOCKED：设备处于解锁状态。  [必填]
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setlockstateconfirmation](control-message.md#setlockstateconfirmation)

### SubmitPrintRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `fileSourceUrl` — 打印资源的地址。支持打印资源的格式为".doc"、".docx"、".rtf"、".xls"、".xlsx"、".ppt"、".pptx"…  [必填]
  - `fileName` — 打印文件的名称。  [可选]
  - `mediaSize` — 打印纸张的尺寸大小。支持以下规格： * IsoA3_420x297mm：表示使用A3规格的纸张打印。 * IsoA4_210x297mm：…  [可选]
  - `color` — 是否使用彩色打印，布尔类型。 * true：表示使用彩色打印。 * false：表示使用黑白打印，默认使用false。  [可选]
  - `copies` — 打印份数，默认是1。  [可选]
- 原文：[control-message.md#submitprintrequest](control-message.md#submitprintrequest)

### SubmitPrintConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `jobId` — 本次任务提交完成后的jobId，后续获取任务状态时将使用该值。  [必填]
- 原文：[control-message.md#submitprintconfirmation](control-message.md#submitprintconfirmation)

### SetSuctionRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `suction` — 设备吸力大小信息。  [必填]
  - `suction.value` — 吸力设置值的列表，目前支持的值有: * "STANDARD" * "STRONG"  [必填]
- 原文：[control-message.md#setsuctionrequest](control-message.md#setsuctionrequest)

### SetSuctionConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setsuctionconfirmation](control-message.md#setsuctionconfirmation)

### SetWaterLevelRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `waterLevel` — 设备水量大小信息。  [必填]
  - `waterLevel.value` — 吸力设置值的列表，目前支持的值有: * "HIGH" * "MEDIUM" * "LOW"  [必填]
- 原文：[control-message.md#setwaterlevelrequest](control-message.md#setwaterlevelrequest)

### SetWaterLevelConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setwaterlevelconfirmation](control-message.md#setwaterlevelconfirmation)

### ChargeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#chargerequest](control-message.md#chargerequest)

### ChargeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#chargeconfirmation](control-message.md#chargeconfirmation)

### DischargeRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#dischargerequest](control-message.md#dischargerequest)

### DischargeConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#dischargeconfirmation](control-message.md#dischargeconfirmation)

### SetDirectionRequest

- 方向：DuerOS → 技能（请求）
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#setdirectionrequest](control-message.md#setdirectionrequest)

### SetDirectionConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setdirectionconfirmation](control-message.md#setdirectionconfirmation)

### SetCleaningLocationRequest

- 方向：DuerOS → 技能（请求）
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#setcleaninglocationrequest](control-message.md#setcleaninglocationrequest)

### SetCleaningLocationConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setcleaninglocationconfirmation](control-message.md#setcleaninglocationconfirmation)

### SetComplexActionsRequest

- 方向：DuerOS → 技能（请求）
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#setcomplexactionsrequest](control-message.md#setcomplexactionsrequest)

### SetComplexActionsConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setcomplexactionsconfirmation](control-message.md#setcomplexactionsconfirmation)

### IncrementHeightRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 按照距离和百分比进行调节的增量信息，包含value和scale。  [可选]
  - `deltaValue.value` — 按照距离和百分比调节增量的具体值。  [可选]
  - `deltaValue.scale` — 按照距离调节时增量的单位, 如果是按照百分比调节的，则该项不存在，按照距离调节时，单位为米（METER）或者英尺（FOOT）  [可选]
- 原文：[control-message.md#incrementheightrequest](control-message.md#incrementheightrequest)

### IncrementHeightConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#incrementheightconfirmation](control-message.md#incrementheightconfirmation)

### DecrementHeightRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 按照距离和百分比进行调节的减量信息，包含value和scale。  [可选]
  - `deltaValue.value` — 按照距离和百分比调节减量的值。  [可选]
  - `deltaValue.scale` — 按照距离调节时减量的单位, 如果是按照百分比调节的，则该项不存在，按照距离调节时，单位为米（METER）或者英尺（FOOT）。  [可选]
- 原文：[control-message.md#decrementheightrequest](control-message.md#decrementheightrequest)

### DecrementHeightConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#decrementheightconfirmation](control-message.md#decrementheightconfirmation)

### SetTimerRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `timeInterval` — 定时时长，单位为秒  [必填]
- 原文：[control-message.md#settimerrequest](control-message.md#settimerrequest)

### SetTimerConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#settimerconfirmation](control-message.md#settimerconfirmation)

### TimingCancelRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#timingcancelrequest](control-message.md#timingcancelrequest)

### TimingCancelConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#timingcancelconfirmation](control-message.md#timingcancelconfirmation)

### ResetRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：无（仅公共字段 accessToken / appliance）
- 原文：[control-message.md#resetrequest](control-message.md#resetrequest)

### ResetConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#resetconfirmation](control-message.md#resetconfirmation)

### SetFloorRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `floor` — 电梯楼层的对象。  [必填]
  - `floor.value` — 电梯楼层设置的值，是int类型，取值范围为-1000～1000。其中-1000表示电梯在运行时的最低楼层，1000表示电梯的最高楼层。  [必填]
- 原文：[control-message.md#setfloorrequest](control-message.md#setfloorrequest)

### SetFloorConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `floor` — 电梯楼层设置后的对象。  [必填]
  - `floor.value` — 电梯楼层设置的值，是int类型，取值范围为-1000～1000。其中-1000表示电梯在运行时的最低楼层，1000表示电梯的最高楼层。  [必填]
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setfloorconfirmation](control-message.md#setfloorconfirmation)

### IncrementFloorRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaFloor` — 电梯楼层增量信息。  [必填]
  - `deltaFloor.value` — 电梯楼层增量的值，是int类型，取值范围为0～1000。其中0表示电梯在运行时的增加的最低值，1000表示增加的最高值。  [必填]
- 原文：[control-message.md#incrementfloorrequest](control-message.md#incrementfloorrequest)

### IncrementFloorConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `floor` — 电梯楼层设置后的对象。  [必填]
  - `floor.value` — 电梯楼层设置的值，是int类型，取值范围为-1000～1000。其中-1000表示电梯在运行时的最低楼层，1000表示电梯的最高楼层。  [必填]
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#incrementfloorconfirmation](control-message.md#incrementfloorconfirmation)

### DecrementFloorRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaFloor` — 电梯楼层的减量信息。  [必填]
  - `deltaFloor.value` — 电梯楼层减量的值，是int类型，取值范围为0～1000。其中0表示电梯在运行时减少的最低值，1000表示电梯减少的最高值。  [必填]
- 原文：[control-message.md#decrementfloorrequest](control-message.md#decrementfloorrequest)

### DecrementFloorConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `floor` — 电梯楼层设置后的对象。  [必填]
  - `floor.value` — 电梯楼层设置的值，是int类型，取值范围为-1000～1000。其中-1000表示电梯在运行时的最低楼层，1000表示电梯的最高楼层。  [必填]
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#decrementfloorconfirmation](control-message.md#decrementfloorconfirmation)

### SetHumidityRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `deltaValue` — 按照百分比进行调节的数值变化信息，包含value和scale。  [必填]
  - `deltaValue.value` — 湿度百分比变化值，是double类型，取值范围为0～100。其中0表示设备的最小湿度，100表示最大湿度。  [必填]
  - `deltaValue.scale` — 湿度的调节单位，默认为 % 。  [必填]
- 原文：[control-message.md#sethumidityrequest](control-message.md#sethumidityrequest)

### SetHumidityConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#sethumidityconfirmation](control-message.md#sethumidityconfirmation)

### SetGearRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `gear` — 调节对象，包含value和scale。  [必填]
  - `gear.value` — 挡位值，是string类型，取值范围为(MIN, LOW, MIDDLE_LOW, MIDDLE, MIDDLE_HIGH, HIGH, …  [必填]
  - `gear.scale` — 挡位的调节单位,默认为‘挡‘  [必填]
- 原文：[control-message.md#setgearrequest](control-message.md#setgearrequest)

### SetGearConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setgearconfirmation](control-message.md#setgearconfirmation)

### SetFlowRequest

- 方向：DuerOS → 技能（请求）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `flow` — 调节对象，包含action、select、control。  [必填]
  - `flow.action` — 操作值，是string类型，取值范围为(POUR_WATER,FILL_WATER)。POUR_WATER：出水、排水；FILL_WATE…  [必填]
  - `flow.select` — 选取设备值，是string类型，取值范围(TOP,HANDLE_HELD,UNDER)。TOP：顶部；HANDLE_HELD：手持；UND…  [可选]
  - `flow.control` — 水流状态控制，是string类型，取值范围(START,STOP)。START：开始、启动；STOP：停止。  [可选]
- 原文：[control-message.md#setflowrequest](control-message.md#setflowrequest)

### SetFlowConfirmation

- 方向：技能 → DuerOS（响应/确认）
- namespace：`DuerOS.ConnectedHome.Control`
- 额外 Payload：
  - `attributes` — 设备属性信息，支持上报一个或多个属性信息。请查看[属性信息](attributes.md)，了解设备的属性和上报方式。  [否，当设备属性信息发生变化时，建议将属性变更信息上报给DuerOS。]
- 原文：[control-message.md#setflowconfirmation](control-message.md#setflowconfirmation)
