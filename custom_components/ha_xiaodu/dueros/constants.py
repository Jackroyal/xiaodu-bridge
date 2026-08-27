"""Constants for the DuerOS Connected Home protocol.

Kept separate from ``custom_components.ha_xiaodu.const`` so the protocol layer
has no dependency on integration-level configuration keys.
"""

from __future__ import annotations

# Appliance version reported to Xiaodu (keep in sync with manifest.json).
APP_VERSION = "0.9.1"

# Request namespaces
NAMESPACE_DISCOVERY = "DuerOS.ConnectedHome.Discovery"
NAMESPACE_CONTROL = "DuerOS.ConnectedHome.Control"
NAMESPACE_QUERY = "DuerOS.ConnectedHome.Query"
NAMESPACE_UNBIND = "DuerOS.ConnectedHome.UnbindBot"

# Error names per the Xiaodu protocol spec
ERROR_INVALID_TOKEN = "InvalidAccessTokenError"
ERROR_DEVICE_NOT_FOUND = "DriverInternalError"
ERROR_OFFLINE = "TargetOfflineError"
ERROR_UNSUPPORTED = "NotSupportedInCurrentModeError"
ERROR_SERVICE = "DriverInternalError"

# Action names (header.name with the "Request" suffix stripped)
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
APPLIANCE_YUBA = "YUBA"

# ---------------------------------------------------------------------------
# Long-term semantic model vocabulary (additive; see dueros/architecture docs).
# These names mirror the official DuerOS protocol (attributes.md / control-message.md)
# and are the vocabulary the new ``dueros.model`` / ``dueros.composers`` use.
# ---------------------------------------------------------------------------

# Additional appliance types not yet exposed by the legacy adapters.
APPLIANCE_WASHING_MACHINE = "WASHING_MACHINE"
APPLIANCE_WATER_HEATER = "WATER_HEATER"
APPLIANCE_RANGE_HOOD = "RANGE_HOOD"
APPLIANCE_DEHUMIDIFIER = "DEHUMIDIFIER"
APPLIANCE_AIR_PURIFIER = "AIR_PURIFIER"
APPLIANCE_TREADMILL = "TREADMILL"
APPLIANCE_FISH_TANK = "FISH_TANK"
APPLIANCE_BED = "BED"

# Additional action names beyond the legacy set.
ACTION_SET_GEAR = "setGear"
ACTION_SET_WATER_LEVEL = "setWaterLevel"
ACTION_START_UP = "startUp"
ACTION_POWER = "setPower"
ACTION_INCREMENT_POWER = "incrementPower"
ACTION_DECREMENT_POWER = "decrementPower"
ACTION_INCREMENT_TEMPERATURE = "incrementTemperature"
ACTION_DECREMENT_TEMPERATURE = "decrementTemperature"
ACTION_INCREMENT_FAN_SPEED = "incrementFanSpeed"
ACTION_DECREMENT_FAN_SPEED = "decrementFanSpeed"
ACTION_INCREMENT_BRIGHTNESS = "incrementBrightnessPercentage"
ACTION_DECREMENT_BRIGHTNESS = "decrementBrightnessPercentage"
ACTION_SET_MIST = "setMist"
ACTION_INCREMENT_MIST = "incrementMist"
ACTION_DECREMENT_MIST = "decrementMist"

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
ATTR_LOCATION = "location"
ATTR_WORK_STATE = "workState"
ATTR_NAME = "name"
ATTR_CONNECTIVITY = "connectivity"
