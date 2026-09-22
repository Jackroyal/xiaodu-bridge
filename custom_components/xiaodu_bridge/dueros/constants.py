"""Constants for the DuerOS Connected Home protocol.

Kept separate from ``custom_components.xiaodu_bridge.const`` so the protocol layer
has no dependency on integration-level configuration keys.
"""

from __future__ import annotations

# Request namespaces
NAMESPACE_DISCOVERY = "DuerOS.ConnectedHome.Discovery"
NAMESPACE_CONTROL = "DuerOS.ConnectedHome.Control"
NAMESPACE_QUERY = "DuerOS.ConnectedHome.Query"
NAMESPACE_UNBIND = "DuerOS.ConnectedHome.UnbindBot"

# Error names per the Xiaodu protocol spec
ERROR_DEVICE_NOT_FOUND = "DriverInternalError"
ERROR_OFFLINE = "TargetOfflineError"
ERROR_UNSUPPORTED = "NotSupportedInCurrentModeError"
ERROR_SERVICE = "DriverInternalError"

# 每台设备最多同步的属性数量（discovery-message.md / attributes-report.md）
MAX_ATTRIBUTES_PER_APPLIANCE = 10

# Action names (header.name with the "Request" suffix stripped).
# NOTE: the discovery action list spells ``unSetMode`` while the Control request
# in the same contract is ``UnsetModeRequest``; the dispatcher matches action
# names case-insensitively so both spellings resolve to one action.
ACTION_TURN_ON = "turnOn"
ACTION_TURN_OFF = "turnOff"
ACTION_TIMING_TURN_ON = "timingTurnOn"
ACTION_TIMING_TURN_OFF = "timingTurnOff"
ACTION_PAUSE = "pause"
ACTION_CONTINUE = "continue"
ACTION_SET_BRIGHTNESS = "setBrightnessPercentage"
ACTION_SET_COLOR = "setColor"
ACTION_SET_COLOR_TEMPERATURE = "setColorTemperature"
ACTION_SET_VOLUME = "setVolume"
ACTION_SET_VOLUME_MUTE = "setVolumeMute"
ACTION_SET_TV_CHANNEL = "setTVChannel"
ACTION_SET_FAN_SPEED = "setFanSpeed"
ACTION_SET_TEMPERATURE = "setTemperature"
ACTION_SET_MODE = "setMode"
ACTION_UNSET_MODE = "unSetMode"
ACTION_SET_SUCTION = "setSuction"
ACTION_SET_HUMIDITY = "setHumidity"

# Appliance types exposed to Xiaodu
APPLIANCE_LIGHT = "LIGHT"
APPLIANCE_SWITCH = "SWITCH"
APPLIANCE_SOCKET = "SOCKET"
APPLIANCE_CURTAIN = "CURTAIN"
APPLIANCE_AIR_CONDITION = "AIR_CONDITION"
APPLIANCE_FAN = "FAN"
APPLIANCE_TV_SET = "TV_SET"
APPLIANCE_SENSOR = "SENSOR"
APPLIANCE_HUMIDIFIER = "HUMIDIFIER"
APPLIANCE_SWEEPING_ROBOT = "SWEEPING_ROBOT"
APPLIANCE_CLOTHES_RACK = "CLOTHES_RACK"

# ---------------------------------------------------------------------------
# Long-term semantic model vocabulary (additive; see dueros/architecture docs).
# These names mirror the official DuerOS protocol (attributes.md / control-message.md)
# and are the vocabulary the new ``dueros.model`` / ``dueros.composers`` use.
# ---------------------------------------------------------------------------

# Appliance types for composite profiles.
APPLIANCE_WASHING_MACHINE = "WASHING_MACHINE"

# Action names used by composite profiles.
ACTION_SET_GEAR = "setGear"
ACTION_SET_WATER_LEVEL = "setWaterLevel"
ACTION_START_UP = "startUp"
ACTION_INCREMENT_TEMPERATURE = "incrementTemperature"
ACTION_DECREMENT_TEMPERATURE = "decrementTemperature"
ACTION_INCREMENT_FAN_SPEED = "incrementFanSpeed"
ACTION_DECREMENT_FAN_SPEED = "decrementFanSpeed"

# Attribute names (match protocols/attributes.md). Used by ``DuerAttribute``.
ATTR_TURN_ON_STATE = "turnOnState"
ATTR_MODE = "mode"
ATTR_TARGET_TEMPERATURE = "targetTemperature"
ATTR_TEMPERATURE = "temperature"
ATTR_FAN_SPEED = "fanSpeed"
ATTR_WARMTH_LEVEL = "warmthLevel"
ATTR_SUCTION = "suction"
ATTR_WATER_LEVEL = "waterLevel"
ATTR_PAUSE_STATE = "pauseState"
ATTR_ELECTRICITY_CAPACITY = "electricityCapacity"
ATTR_BRIGHTNESS = "brightness"
ATTR_COLOR_TEMPERATURE = "colorTemperatureInKelvin"
ATTR_COLOR = "color"
ATTR_PERCENTAGE = "percentage"
ATTR_VOLUME = "volume"
ATTR_CHANNEL = "channel"
ATTR_MUTE_STATE = "muteState"
ATTR_HUMIDITY = "humidity"
ATTR_TARGET_HUMIDITY = "targetHumidity"
ATTR_WORK_STATE = "workState"
# 查询响应字段名（query-message.md 的 GetTimeLeftResponse 用它，不是属性名）
ATTR_TIME_LEFT_IN_SECONDS = "timeLeftInSeconds"

# --- 契约枚举（原文取值，勿按设备自造） ---------------------------------------
# attributes.md 的属性取值 / control-message.md 的请求取值。设备侧（HA 实体）的
# 选项目录由集成自己命名（低档/Weak/Standard…），由 composer 按这些枚举做双向解析。
WARMTH_LEVEL_VALUES = ("LOW", "MIDDLE", "HIGH")            # attributes.md warmthLevel
WATER_LEVEL_VALUES = ("LOW", "MEDIUM", "HIGH")             # attributes.md waterLevel
SUCTION_VALUES = ("STANDARD", "STRONG")                    # attributes.md suction
WORK_STATE_VALUES = (                                       # attributes.md workState
    "STOP",
    "START",
    "PAUSE",
    "WORKING",
    "WORK_NEARLY_FINISHED",
    "DONE",
)
WASHING_MODE_VALUES = (                                     # 模式表 WASHING_MACHINE
    "STANDARD",
    "DRY",
    "WASH_DRY",
    "FAST_WASH",
    "DOWN_JACKET",
)
# SetGearRequest.gear.value：档位刻度（AUTO / RANDOM 不在刻度上，见 composer）
GEAR_VALUES = (
    "MIN",
    "LOW",
    "MIDDLE_LOW",
    "MIDDLE",
    "MIDDLE_HIGH",
    "HIGH",
    "MAX",
)
