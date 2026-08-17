"""Constants for the DuerOS Connected Home protocol.

Kept separate from ``custom_components.xiaodu.const`` so the protocol layer
has no dependency on integration-level configuration keys.
"""

from __future__ import annotations

# Appliance version reported to Xiaodu (keep in sync with manifest.json).
APP_VERSION = "0.7.6"

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
