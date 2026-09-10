# Home Assistant Custom Integration: xiaodu bridge

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Hassfest](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hassfest.yml/badge.svg)](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hassfest.yml)
[![HACS Validation](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hacs.yml/badge.svg)](https://github.com/Jackroyal/xiaodu-bridge/actions/workflows/hacs.yml)

> 中文文档见 [README.md](README.md) · English below.

Let the Xiaodu speaker / Xiaodu App discover, query, and control devices in Home Assistant.

> **Naming**: the integration's store name is `xiaodu bridge`, its domain is
> `xiaodu_bridge` (the repository was also renamed to `xiaodu-bridge`). The direction
> is **Home Assistant → Xiaodu**: HA entities are mapped into DuerOS semantic devices
> and handed to the Xiaodu speaker/App. This is the opposite of integrations that
> "import Xiaodu-ecosystem devices back into HA" (e.g. the cookie-polling
> `xiaodu.baidu.com` approach); the two are unrelated and can be installed side by side
> (different domains).

This integration runs as a **DuerOS smart-home OAuth server**: Xiaodu is the OAuth
client, and the integration receives requests via `/api/xiaodu` and
`/api/xiaodu/service`, maps HA entities to DuerOS semantic devices, and issues a
private opaque token scoped to this integration; that token cannot access the
Home Assistant API.

Current version: **v0.9.9**.

## Features

- **Semantic device model**: devices are exposed as DuerOS semantics rather than split
  into loose entities. Bathroom heaters (yuba), clothes airers, robot vacuums, and
  washing machines have dedicated profiles; lights, switches, fans, climate, covers,
  media players, sockets, and temperature/humidity sensors are synthesized from generic
  capabilities.
- **Config flow and options flow**: configure OAuth Client ID / Secret, botId, callback
  URL, and public URL when adding the integration; afterwards select which devices to
  expose via "device → capability".
- **Per-device advanced overrides**: configure each device individually — limit exposed
  capabilities, hide entities (not exposed to Xiaodu, and not participating in role
  detection/aggregation), bind a semantic role to a specific entity (overriding
  auto-detection), force "split as single devices" or a specific device type (with
  automatic fallback when it cannot be built), and rename a Xiaodu device's display
  name independently (without affecting the HA entity name). Legacy flat / per-entity
  capability configs are migrated automatically on read.
- **OAuth 2.0**: provides an authorization page and a token endpoint. Access tokens last
  7 days, refresh tokens 30 days, with `refresh_token` renewal.
- **Discovery / Query / Control**: compatible with both the Xiaodu console mock-testing
  DCS multipart and the production JSON messages.
- **Proactive state reporting**: sends a Change Report to Xiaodu when controllable
  device state changes; read-only sensors do not report.
- **Room grouping**: syncs HA areas as DuerOS `discoveredGroups`.
- **Timed on/off**: supports `timingTurnOn` / `timingTurnOff`, persisted via HA Storage
  and restored after restart.
- **Single hub device**: the device registry keeps a single "Xiaodu hub"; bridged HA
  devices are not duplicated in the device list.
- **Automatic device-set refresh**: after adding/removing/renaming entities, devices, or
  areas, the cached device set is invalidated and rebuilt; Discovery always reflects the
  current HA state, so new devices are discoverable without a restart.
- **Temperature unit normalization**: sensor temperature is normalized to HA's unit
  system (`hass.config.units`) before reporting (metric = Celsius); non-numeric readings
  such as `unknown`/`unavailable` are no longer reported as 0.0.
- **Independent light devices**: the light on composite devices (bathroom heater, clothes
  airer) is split into a separate `LIGHT` device; brightness/color-temperature/color are
  exposed based on the entity's actual capabilities.
- **Climate temperature increments**: temperature and fan speed support both `set*` and
  `increment/decrement` from the Xiaodu App/voice; the absolute `SetTemperatureRequest`
  is parsed from the official payload key `targetTemperature` (with CELSIUS/FAHRENHEIT
  normalization); AC fan speed maps to HA climate's discrete `fan_mode` steps (e.g.
  20/40/…/100/auto) instead of a nonexistent `percentage`.
- **Climate mode reporting**: hvac mode prefers the entity state (compatible with
  integrations like Midea that don't provide an `hvac_mode` attribute), avoiding a
  cooling AC being reported as "unknown mode".
- **Stable device identity**: generic/standalone entity DuerOS appliance IDs are anchored
  to HA device and entity unique IDs, so renaming an entity in HA keeps the Xiaodu-side
  device identity stable (no delete-and-recreate); orphaned entities without a device
  keep their original behavior.

## Requirements

- Home Assistant `2025.1.0` or newer.
- The Xiaodu platform must be able to reach the Home Assistant endpoint from the public
  internet.
- A valid HTTPS certificate is recommended; the examples below use `https://ha.example.com`.
- When reverse-proxying to Home Assistant, the example backend port is `8123`.

## Installation

### HACS (recommended)

1. Make sure [HACS](https://hacs.xyz) is installed.
2. Open **HACS → Integrations**.
3. Select **Explore & Download Repositories**.
4. Search for **xiaodu bridge**, or add this repository as a Custom Repository first:
   `https://github.com/Jackroyal/xiaodu-bridge`, category **Integration**.
5. Restart Home Assistant after downloading.

> Xiaodu is a region-limited platform, and `hacs.json` sets `country: CN`: this
> repository only appears when HACS's country/region is set to **China** or **All**. If
> you don't see it, change **HACS → Settings → Country** to **All**, or use the manual
> installation below.

### Manual installation

Copy the `custom_components/xiaodu_bridge` directory from this repository into:

```text
/config/custom_components/xiaodu_bridge
```

Restart Home Assistant, then go to **Settings → Devices & Services → Add Integration**
and search for **xiaodu bridge**.

## Configuration

When adding the integration, fill in the OAuth information matching the Xiaodu developer
console:

| Field | Description | Example |
|---|---|---|
| `client_id` | Custom OAuth Client ID | `dueros_xxx` |
| `client_secret` | Custom random Client Secret | `<CLIENT_SECRET>` |
| `bot_id` | Xiaodu skill ID, used for device change push | `<BOT_ID>` |
| `redirect_uri` | Callback URL generated by the Xiaodu platform | `https://xiaodu.baidu.com/...` |
| `public_url` | Public HTTPS base URL of HA | `https://ha.example.com` |

The confirmation page shows the addresses to enter in the Xiaodu developer console:

```text
Authorize URL: https://ha.example.com/api/xiaodu/oauth/authorize
Token URL:     https://ha.example.com/api/xiaodu/oauth/token
WebService:    https://ha.example.com/api/xiaodu/service
Callback URL:  redirect_uri generated by the Xiaodu platform
```

If HA uses a non-default port, specify it consistently in `public_url` and the reverse
proxy; the examples here use port `8123`.

## Public HTTPS example

```text
DuerOS
  ↓ HTTPS
https://ha.example.com
  ↓
Reverse proxy / HTTPS termination
  ↓
Home Assistant :8123
  ↓
/api/xiaodu/*
```

The reverse proxy must preserve the standard forwarding headers and allow requests to
reach:

```text
/api/xiaodu/oauth/authorize
/api/xiaodu/oauth/token
/api/xiaodu/service
```

## Supported devices, attributes and capabilities

This integration maps HA entities into DuerOS semantic devices, in two ways: dedicated
profiles and generic capability synthesis.

### Device types

**Dedicated profiles (composite devices)** — one physical device is synthesized into one
or more DuerOS appliances:

| Device | DuerOS type | Synthesized capabilities |
|---|---|---|
| Bathroom heater (yuba) | `YUBA` | Power (heating / blow / ventilation), mode (`HEAT` / `FAN` / `VENTILATION`), warmth level, fan speed, target temperature |
| Clothes airer | `CLOTHES_RACK` | Power (up / down), position, pause, mode (`DRYING` / `DISINFECT`) |
| Robot vacuum | `SWEEPING_ROBOT` | Power, pause, suction, battery level |
| Washing machine | `WASHING_MACHINE` | Power (on / off / start), wash program, water level, target temperature, run state, time left |

The light on a bathroom heater or clothes airer is not merged into the composite device
(DuerOS has no corresponding action); it is split into a separate `LIGHT` device, with
brightness / color temperature / color exposed according to the entity's actual
capabilities.

**Generic capability synthesis** — mapped by HA entity domain:

| HA domain | DuerOS type | Capabilities |
|---|---|---|
| `light` | `LIGHT` | Power, brightness, color temperature, color |
| `switch` | `SWITCH` | Power |
| Socket (`plug` / name contains "插座") | `SOCKET` | Power |
| `fan` | `FAN` | Power, fan speed |
| `climate` | `AIR_CONDITION` | Power, target temperature, mode, fan speed |
| `cover` | `CURTAIN` | Power, position, pause |
| `media_player` | `TV_SET` | Power, volume, mute, channel |
| `humidifier` | `HUMIDIFIER` | Power, target humidity, mode |
| `sensor` | `SENSOR` | Temperature, humidity (read-only) |

> The `vacuum` domain is handled by the "robot vacuum" profile. Status/safety entities
> such as indicators, child locks, night lights, and fault flags (`indicator`,
> `child_lock`, `night_light`, `fault`, …) are never exposed to the speaker.

### Capabilities

| Capability key | Label | Type | DuerOS attribute |
|---|---|---|---|
| `power` | Power | Control | `turnOnState` |
| `brightness` | Brightness | Control | `brightness` |
| `colorTemperature` | Color temperature | Control | `colorTemperatureInKelvin` |
| `color` | Color | Control | `color` |
| `volume` | Volume | Control | `volume` |
| `mute` | Mute | Control | `muteState` |
| `channel` | Channel | Control | `channel` |
| `fanSpeed` | Fan speed | Control | `fanSpeed` |
| `targetTemperature` | Target temperature | Control | `targetTemperature` |
| `targetHumidity` | Target humidity | Control | `targetHumidity` |
| `mode` | Mode | Control | `mode` |
| `percentage` | Position | Control | `percentage` |
| `suction` | Suction | Control | `suction` |
| `waterLevel` | Water level | Control | `waterLevel` |
| `pause` | Pause | Control | `pauseState` |
| `continue` | Continue | Control | — |
| `temperature` | Temperature | Read-only | `temperature` |
| `humidity` | Humidity | Read-only | `humidity` |
| `warmthLevel` | Warmth level | Control | `warmthLevel` |
| `electricityCapacity` | Battery level | Read-only | `electricityCapacity` |
| `workState` | Run state | Read-only | `workState` |
| `timeLeft` | Time left | Read-only | `timeLeft` |

Control capabilities map to DuerOS actions (`turnOn` / `turnOff` / `set*` / `increment*`
/ `decrement*` / `pause` / `continue` / `timingTurnOn` / `timingTurnOff`, …); read-only
capabilities surface only as attributes for Query. Sensor temperature is normalized to
HA's unit system before reporting (metric = Celsius); non-numeric readings such as
`unknown` / `unavailable` produce no attribute.

## Configuring devices and capabilities

After adding the integration, open the integration entry and select **设备与能力**
(Devices & capabilities):

1. The hub menu provides the device list, add / remove device, and save & finish.
2. The device list shows "room · device name"; newly added devices expose all available
   capabilities by default.
3. Each device can select capabilities; `power` is force-enabled for controllable
   devices, while read-only capabilities such as `temperature` / `humidity` can be
   toggled as desired.
4. When `sync_areas` is enabled, HA areas are synced as Xiaodu room groups.

## Directory structure

```text
.
├── .github/workflows/          # Hassfest, HACS and Tests validation
├── custom_components/xiaodu_bridge/
│   ├── __init__.py             # integration entry / unload / hub device registration
│   ├── config_flow.py          # config flow and device → capability options flow
│   ├── devices.py              # device, domain and capability helpers
│   ├── oauth_server.py         # OAuth endpoints and DuerOS WebService views
│   ├── oauth_store.py          # least-privilege token storage
│   ├── timers.py               # timed scheduling and persistence
│   ├── dueros_sync.py          # device change push
│   ├── state_report.py         # semantic device state reporting
│   ├── dueros/                 # DuerOS semantic model and protocol implementation
│   ├── manifest.json
│   ├── strings.json
│   └── translations/
├── hacs.json
├── pyproject.toml
├── reference/dueros/            # Xiaodu official protocol archive + contract lookup (dev reference)
│   ├── dbp-smart-home-protocol/ # official protocol source (auto-fetched, do not edit)
│   ├── contracts/               # message → payload contract lookup (auto-generated)
│   ├── lookup.py                # protocol lookup: contract-first, fallback to source slices
│   ├── verify_conversion.py     # fetch source and self-check conversion fidelity
│   └── README.md
└── tests/
```

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest
```

### Protocol reference (read before changing the DuerOS protocol)

The repository locally archives the official Xiaodu "smart home protocol" full text plus
auto-generated contract lookups (see `reference/dueros/README.md`). Before changing any
DuerOS message/field/capability in `xiaodu_bridge`, locate it with the contract-first
lookup instead of reading large files wholesale:

```bash
python3 reference/dueros/lookup.py SetTemperature   # contract lookup + source pointer
python3 reference/dueros/lookup.py 空调 --grep       # fall back to source slices when not covered by contracts
```

The repository enables the following GitHub Actions:

- Home Assistant **Hassfest** validation.
- **HACS Integration** validation.
- **Tests**: pytest unit/integration tests, ruff static checks, and manifest ↔ pyproject version-sync validation.

## Logging

Enable debug logging in the HA configuration:

```yaml
logger:
  default: warning
  logs:
    custom_components.xiaodu_bridge: debug
```

The integration logs the duration, action, result, and HTTP status of OAuth and
WebService requests; do not publish tokens, Client Secrets, or user device IDs to public
issues.

## License

MIT
