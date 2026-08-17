"""Constants for the Xiaodu (DuerOS) integration."""

from __future__ import annotations

DOMAIN = "xiaodu"

# Config entry data / options keys
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_REDIRECT_URI = "redirect_uri"
CONF_PUBLIC_URL = "public_url"
# Xiaodu developer-console skill ID, needed for device-sync push notifications.
CONF_BOT_ID = "bot_id"

# Public endpoints served by this integration (paths relative to the base URL)
OAUTH_AUTHORIZE_PATH = "/api/xiaodu/oauth/authorize"
OAUTH_TOKEN_PATH = "/api/xiaodu/oauth/token"
DUEROS_API_PATH = "/api/xiaodu"
# Baidu console "模拟测试" sends DCS multipart to the /service path
DUEROS_SERVICE_PATH = "/api/xiaodu/service"

# DuerOS notification interface: notify DuerOS that a user's device set changed.
DUEROS_DEVICE_SYNC_URL = "https://xiaodu.baidu.com/saiya/smarthome/devicesync"

# OAuth2 server defaults
OAUTH_CODE_EXPIRE_SECONDS = 300
# Access tokens are sent with every DuerOS request; refresh tokens last
# longer and are rotated at the token endpoint.
OAUTH_ACCESS_TOKEN_EXPIRE_SECONDS = 7 * 24 * 60 * 60  # 7 days
OAUTH_REFRESH_TOKEN_EXPIRE_SECONDS = 30 * 24 * 60 * 60  # 30 days

# Runtime state keys (hass.data[DOMAIN])
DATA_TIMER_MANAGER = "timed_services"

# Capability-model device selection: device_key -> enabled caps.
# Legacy entity include/exclude keys below are still read for migration.
CONF_DEVICES = "devices"
CONF_CAPABILITIES = "capabilities"
CONF_DEVICE = "device"
CONF_UNITS = "units"
CONF_ENTITY_INCLUDE = "entity_include"
CONF_ENTITY_EXCLUDE = "entity_exclude"
CONF_SYNC_AREAS = "sync_areas"
