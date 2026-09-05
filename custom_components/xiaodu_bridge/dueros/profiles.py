"""Concrete DuerOS device profiles.

A profile knows how to assemble the HA entities of one physical device into one
(or more) DuerOS appliances and which capabilities they expose. This is the
*documentation* of the long-term semantic model: complex devices (YUBA,
WASHING_MACHINE, ...) are described here declaratively (using ``dueros.composers``)
instead of with device-type ``if`` branches in the protocol layer.

Role auto-detection (``_match_role``) is a *suggestion* only — the user may bind
roles explicitly; it must never be the sole source of truth.
"""

from __future__ import annotations

from typing import Any

from .composers import (
    attribute_level_mapping,
    composite_power_mapping,
    mode_switches_mapping,
    pause_mapping,
    percentage_mapping,
    power_mapping,
    select_mapping,
    sensor_query_mapping,
    target_temperature_mapping,
)
from .constants import (
    ATTR_ELECTRICITY_CAPACITY,
    ATTR_FAN_SPEED,
    ATTR_MODE,
    ATTR_SUCTION,
    ATTR_WARMTH_LEVEL,
    ATTR_WATER_LEVEL,
    ATTR_WORK_STATE,
    ACTION_CONTINUE,
    ACTION_SET_SUCTION,
    ACTION_SET_WATER_LEVEL,
    ACTION_START_UP,
    ACTION_TURN_OFF,
    ACTION_TURN_ON,
    APPLIANCE_CLOTHES_RACK,
    APPLIANCE_SWEEPING_ROBOT,
    APPLIANCE_WASHING_MACHINE,
)
from .model import DeviceBuildContext, DuerDevice, DuerDeviceProfile, make_device_id


# --- role auto-detection ----------------------------------------------------

# Semantic role -> (markers to look for in entity id / friendly name). Kept loose
# on purpose: Xiaomi Home names a YUBA's functions ``*_heat`` / ``*_blow`` while
# other integrations name them 暖风 / 吹风 / 换气 / 照明.
"""Semantic-role -> matching rules for auto-detection.

Each rule is domain-aware and prefers entity-id markers over friendly-name
markers, so on a messy Mi Home device the *function switches* win over a
``暖风档位`` / ``风机档位`` select that merely mentions the same keyword.
``exclude`` drops auxiliary entities (indicator / night light / buzzer / fault).
Auto-detection is a suggestion only; explicit role bindings always win.
"""

_ROLE_RULES: dict[str, dict[str, Any]] = {
    # YUBA / 浴霸
    "heating": dict(
        domains=("switch",),
        entity_id_markers=("heating", "取暖", "暖风"),
        name_markers=("取暖", "暖风"),
    ),
    "blow": dict(
        domains=("switch",),
        entity_id_markers=("blow", "吹风"),
        name_markers=("吹风",),
    ),
    "ventilation": dict(
        domains=("switch",),
        entity_id_markers=("ventilation", "换气"),
        name_markers=("换气",),
    ),
    "light": dict(
        domains=("light",),
        entity_id_markers=("light",),
        name_markers=(),
        exclude=("indicator", "night", "夜灯", "指示灯"),
    ),
    "warmth_level": dict(
        domains=("select",),
        entity_id_markers=("heat_level", "warmth", "warmth_level"),
        name_markers=("暖风档位", "热度档位", "热度"),
    ),
    "fan_speed": dict(
        domains=("select",),
        entity_id_markers=("fan_level", "fan_speed"),
        name_markers=("风机档位", "风速"),
    ),
    "target_temperature": dict(
        domains=("number", "climate"),
        entity_id_markers=("target_temperature",),
        name_markers=("设定温度",),
    ),
    # 扫地机器人
    "robot": dict(domains=("vacuum",), entity_id_markers=("robot", "sweep", "vacuum"), name_markers=("扫地",)),
    "battery": dict(domains=("sensor",), entity_id_markers=("battery",), name_markers=("电量",)),
    # 晾衣架
    "cover": dict(domains=("cover",), entity_id_markers=("airer", "clothesrack", "clothes_rack"), name_markers=("晾衣",)),
    "dry": dict(domains=("switch", "select"), entity_id_markers=("dry",), name_markers=("烘干", "干燥")),
    "uv": dict(domains=("switch", "select"), entity_id_markers=("uv",), name_markers=("杀菌", "紫外")),
    # 洗衣机
    "power": dict(domains=("switch",), entity_id_markers=("power",), name_markers=("电源", "开关")),
    "wash_mode": dict(domains=("select",), entity_id_markers=("wash", "wash_mode"), name_markers=("程序", "洗涤", "洗衣")),
    "water_level": dict(domains=("select",), entity_id_markers=("water_level",), name_markers=("水位",)),
    "run_state": dict(domains=("sensor", "select"), entity_id_markers=("run_state",), name_markers=("运行状态",)),
    "time_left": dict(domains=("sensor",), entity_id_markers=("time_left", "time"), name_markers=("剩余时间",)),
}


def _entity_text(state: Any) -> str:
    name = str((getattr(state, "attributes", None) or {}).get("friendly_name", ""))
    return f"{getattr(state, 'entity_id', '')} {name}".lower()


def _domain(state: Any) -> str:
    return getattr(state, "domain", "") or str(getattr(state, "entity_id", "")).split(".", 1)[0]


def _rule_matches(state: Any, role: str, *, by_id: bool) -> bool:
    rule = _ROLE_RULES.get(role)
    if rule is None:
        return False
    if rule.get("domains") and _domain(state) not in rule["domains"]:
        return False
    text = _entity_text(state)
    if any(marker in text for marker in rule.get("exclude", ())):
        return False
    eid = str(getattr(state, "entity_id", "")).lower()
    if by_id:
        return any(marker in eid for marker in rule.get("entity_id_markers", ()))
    return any(marker in text for marker in rule.get("name_markers", ()))


def match_role(state: Any, role: str) -> bool:
    """Return True when an entity looks like a semantic role (suggestion only)."""
    return _rule_matches(state, role, by_id=True) or _rule_matches(state, role, by_id=False)


def _suggest_role(ctx: DeviceBuildContext, role: str) -> str | None:
    """Resolve a role: explicit binding, then entity-id match, then name match."""
    if (explicit := ctx.entity_of(role)):
        return explicit
    for state in ctx.states:
        if _rule_matches(state, role, by_id=True):
            return getattr(state, "entity_id", "")
    for state in ctx.states:
        if _rule_matches(state, role, by_id=False):
            return getattr(state, "entity_id", "")
    return None


def _reachable(ctx: DeviceBuildContext, entity_ids: list[str]) -> bool:
    """A device is reachable unless its primary entity is ``unavailable``."""
    for eid in entity_ids:
        state = ctx.find_state(eid)
        if state is not None and getattr(state, "state", "") != "unavailable":
            return True
    return False


# --- profile auto-match (confident, used for the default path) -----------------

def _matches_yuba(states: Any) -> bool:
    """A bathroom heater has a light plus heating/blow/ventilation switches."""
    has_light = False
    has_fn = False
    for s in states:
        text = _entity_text(s)
        if any(x in text for x in ("indicator", "night", "夜灯", "指示灯")):
            continue
        if _domain(s) == "light":
            has_light = True
        if _domain(s) == "switch" and any(
            m in getattr(s, "entity_id", "").lower()
            for m in ("heating", "blow", "ventilation")
        ):
            has_fn = True
    return has_light and has_fn


def _matches_sweeping_robot(states: Any) -> bool:
    return any(_domain(s) == "vacuum" for s in states)


def _matches_clothes_rack(states: Any) -> bool:
    for s in states:
        if _domain(s) == "cover" and (
            any(m in getattr(s, "entity_id", "").lower() for m in ("airer", "clothesrack", "clothes_rack"))
            or "晾衣" in _entity_text(s)
        ):
            return True
    return False


def _matches_washing_machine(states: Any) -> bool:
    for s in states:
        if _domain(s) == "select" and any(
            m in getattr(s, "entity_id", "").lower() for m in ("wash", "wash_mode")
        ):
            return True
    return False


# --- YUBA (浴霸) --------------------------------------------------------------

def build_yuba(ctx: DeviceBuildContext) -> list[DuerDevice]:
    """Assemble a bathroom heater into a single YUBA appliance.

    Roles:
      heating / blow / ventilation        -> used for ``power`` and ``mode``
      warmth_level                        -> ``warmthLevel`` via setGear
      fan_speed                           -> ``fanSpeed`` via setFanSpeed
      target_temperature                  -> ``targetTemperature`` via setTemperature

    The bathroom *light* is deliberately not claimed: DuerOS YUBA has no light
    actions (brightness/color), so the light surfaces through the leftover
    path as its own LIGHT appliance instead of being reduced to on/off.
    """
    heat = _suggest_role(ctx, "heating")
    blow = _suggest_role(ctx, "blow")
    vent = _suggest_role(ctx, "ventilation")
    gear = _suggest_role(ctx, "warmth_level")
    fan = _suggest_role(ctx, "fan_speed")
    temp = _suggest_role(ctx, "target_temperature")

    if not any((heat, blow, vent)):
        return []

    appliance_types = ("YUBA",)
    mappings = []

    # power: on when any function is on; off turns all functions off.
    switch_roles = [
        (eid, role)
        for eid, role in ((heat, "heating"), (blow, "blow"), (vent, "ventilation"))
        if eid
    ]
    primary = heat or blow or vent
    if switch_roles:
        mappings.append(
            composite_power_mapping(
                primary_entity_id=primary,
                domain="switch",
                switch_roles=switch_roles,
                appliance_types=appliance_types,
            )
        )

    # mode: N switch entities synthesise the active function. DuerOS addresses
    # a 浴霸's functions with *English* mode codes — confirmed from live
    # SetModeRequest traffic: 吹风=FAN, 换气=VENTILATION (取暖=HEAT, same
    # pattern) — so mode values / legalValue use codes, not Chinese labels.
    mode_elems = [
        (code, role, eid)
        for code, role, eid in (
            ("HEAT", "heating", heat),
            ("FAN", "blow", blow),
            ("VENTILATION", "ventilation", vent),
        )
        if eid
    ]
    if mode_elems:
        mappings.append(
            mode_switches_mapping(
                modes=mode_elems,
                appliance_types=appliance_types,
                exclusive=False,
            )
        )

    if gear:
        mappings.append(
            select_mapping(
                entity_id=gear,
                attribute_name=ATTR_WARMTH_LEVEL,
                capability_key="warmthLevel",
                appliance_types=appliance_types,
                set_action="setGear",
            )
        )
    if fan:
        mappings.append(
            select_mapping(
                entity_id=fan,
                attribute_name=ATTR_FAN_SPEED,
                capability_key="fanSpeed",
                appliance_types=appliance_types,
                set_action="setFanSpeed",
            )
        )
    if temp:
        mappings.append(
            target_temperature_mapping(entity_id=temp, appliance_types=appliance_types)
        )

    if not mappings:
        return []

    device_id = make_device_id("YUBA", ctx.ha_device_id)
    return [
        DuerDevice(
            device_id=device_id,
            friendly_name=ctx.device_name,
            profile_key="YUBA",
            primary_entity_id=primary,
            capabilities=tuple(mappings),
            is_reachable=_reachable(ctx, [eid for eid, _role in switch_roles] or [primary]),
            appliance_types=appliance_types,
        )
    ]


YUBA_PROFILE = DuerDeviceProfile(
    key="YUBA",
    appliance_types=("YUBA",),
    default_capabilities=("power", "mode", "warmthLevel", "fanSpeed", "targetTemperature"),
    build=build_yuba,
    matches=_matches_yuba,
)


# --- SWEEPING_ROBOT (扫地机器人) ----------------------------------------------

def _vacuum_on(state: Any) -> bool:
    """A vacuum is powered-on when it is not idle/docked/unavailable."""
    return getattr(state, "state", "") not in ("idle", "docked", "off", "unavailable")


def build_sweeping_robot(ctx: DeviceBuildContext) -> list[DuerDevice]:
    robot = _suggest_role(ctx, "robot")
    battery = _suggest_role(ctx, "battery")
    if not robot:
        return []

    appliance_types = (APPLIANCE_SWEEPING_ROBOT,)
    mappings = [
        power_mapping(
            domain="vacuum",
            entity_id=robot,
            appliance_types=appliance_types,
            on_service="start",
            off_service="stop",
            actions=(ACTION_TURN_ON, ACTION_TURN_OFF),
            power_predicate=_vacuum_on,
        ),
        pause_mapping(entity_id=robot, appliance_types=appliance_types, domain="vacuum"),
        attribute_level_mapping(
            entity_id=robot,
            attribute_name=ATTR_SUCTION,
            capability_key="suction",
            appliance_types=appliance_types,
            set_action=ACTION_SET_SUCTION,
            service_domain="vacuum",
            service="set_fan_speed",
            data_key="fan_speed",
            payload_key="suction",
            read_attr="fan_speed",
        ),
    ]
    if battery:
        mappings.append(
            sensor_query_mapping(
                entity_id=battery,
                attribute_name=ATTR_ELECTRICITY_CAPACITY,
                capability_key="electricityCapacity",
                appliance_types=appliance_types,
                unit="%",
                legal="[0, 100]",
            )
        )

    return [
        DuerDevice(
            device_id=make_device_id("SWEEPING_ROBOT", ctx.ha_device_id),
            friendly_name=ctx.device_name,
            profile_key="SWEEPING_ROBOT",
            primary_entity_id=robot,
            capabilities=tuple(mappings),
            is_reachable=_reachable(ctx, [robot]),
            appliance_types=appliance_types,
        )
    ]


SWEEPING_ROBOT_PROFILE = DuerDeviceProfile(
    key="SWEEPING_ROBOT",
    appliance_types=(APPLIANCE_SWEEPING_ROBOT,),
    default_capabilities=("power", "pause", "suction", "electricityCapacity"),
    build=build_sweeping_robot,
    matches=_matches_sweeping_robot,
)


# --- CLOTHES_RACK (晾衣架) -----------------------------------------------------

def build_clothes_rack(ctx: DeviceBuildContext) -> list[DuerDevice]:
    cover = _suggest_role(ctx, "cover")
    dry = _suggest_role(ctx, "dry")
    uv = _suggest_role(ctx, "uv")
    if not cover:
        return []

    appliance_types = (APPLIANCE_CLOTHES_RACK,)
    mappings = [
        power_mapping(
            domain="cover",
            entity_id=cover,
            appliance_types=appliance_types,
            on_service="open_cover",
            off_service="close_cover",
        ),
        percentage_mapping(entity_id=cover, appliance_types=appliance_types),
        pause_mapping(entity_id=cover, appliance_types=appliance_types, domain="cover", include_continue=False),
    ]
    mode_elems = [
        (label, role, eid)
        for label, role, eid in (("烘干", "dry", dry), ("杀菌", "uv", uv))
        if eid
    ]
    if mode_elems:
        mappings.append(
            mode_switches_mapping(
                modes=mode_elems,
                appliance_types=appliance_types,
                exclusive=False,
            )
        )

    return [
        DuerDevice(
            device_id=make_device_id("CLOTHES_RACK", ctx.ha_device_id),
            friendly_name=ctx.device_name,
            profile_key="CLOTHES_RACK",
            primary_entity_id=cover,
            capabilities=tuple(mappings),
            is_reachable=_reachable(ctx, [cover]),
            appliance_types=appliance_types,
        )
    ]


CLOTHES_RACK_PROFILE = DuerDeviceProfile(
    key="CLOTHES_RACK",
    appliance_types=(APPLIANCE_CLOTHES_RACK,),
    default_capabilities=("power", "percentage", "pause", "mode"),
    build=build_clothes_rack,
    matches=_matches_clothes_rack,
)


# --- WASHING_MACHINE (洗衣机) --------------------------------------------------

def build_washing_machine(ctx: DeviceBuildContext) -> list[DuerDevice]:
    power_entity = _suggest_role(ctx, "power")
    wash_mode = _suggest_role(ctx, "wash_mode")
    water_level = _suggest_role(ctx, "water_level")
    temp = _suggest_role(ctx, "target_temperature")
    run_state = _suggest_role(ctx, "run_state")
    time_left = _suggest_role(ctx, "time_left")

    # Need at least a power switch or a wash-program selector to identify the machine.
    if not (power_entity or wash_mode):
        return []

    appliance_types = (APPLIANCE_WASHING_MACHINE,)
    mappings: list[Any] = []
    if power_entity:
        mappings.append(
            power_mapping(
                domain="switch",
                entity_id=power_entity,
                appliance_types=appliance_types,
                actions=(ACTION_TURN_ON, ACTION_TURN_OFF, ACTION_START_UP),
                action_calls={ACTION_START_UP: ("switch", "turn_on", {})},
            )
        )
    if wash_mode:
        mappings.append(
            select_mapping(
                entity_id=wash_mode,
                attribute_name=ATTR_MODE,
                capability_key="mode",
                appliance_types=appliance_types,
                set_action="setMode",
                select_domain="select",
            )
        )
    if water_level:
        mappings.append(
            select_mapping(
                entity_id=water_level,
                attribute_name=ATTR_WATER_LEVEL,
                capability_key="waterLevel",
                appliance_types=appliance_types,
                set_action=ACTION_SET_WATER_LEVEL,
                select_domain="select",
            )
        )
    if temp:
        mappings.append(
            target_temperature_mapping(entity_id=temp, appliance_types=appliance_types)
        )
    if run_state:
        mappings.append(
            sensor_query_mapping(
                entity_id=run_state,
                attribute_name=ATTR_WORK_STATE,
                capability_key="workState",
                appliance_types=appliance_types,
            )
        )
    if time_left:
        mappings.append(
            sensor_query_mapping(
                entity_id=time_left,
                attribute_name="timeLeft",
                capability_key="timeLeft",
                appliance_types=appliance_types,
                unit="min",
            )
        )

    primary = power_entity or wash_mode
    return [
        DuerDevice(
            device_id=make_device_id("WASHING_MACHINE", ctx.ha_device_id),
            friendly_name=ctx.device_name,
            profile_key="WASHING_MACHINE",
            primary_entity_id=primary,
            capabilities=tuple(mappings),
            is_reachable=_reachable(ctx, [primary]),
            appliance_types=appliance_types,
        )
    ]


WASHING_MACHINE_PROFILE = DuerDeviceProfile(
    key="WASHING_MACHINE",
    appliance_types=(APPLIANCE_WASHING_MACHINE,),
    default_capabilities=("power", "mode", "waterLevel", "targetTemperature", "workState", "timeLeft"),
    build=build_washing_machine,
    matches=_matches_washing_machine,
)


# --- registration ------------------------------------------------------------

def register_default_profiles(registry: Any) -> tuple[DuerDeviceProfile, ...]:
    """Register the built-in device profiles and return them."""
    registry.register_profile(YUBA_PROFILE)
    registry.register_profile(SWEEPING_ROBOT_PROFILE)
    registry.register_profile(CLOTHES_RACK_PROFILE)
    registry.register_profile(WASHING_MACHINE_PROFILE)
    return (YUBA_PROFILE, SWEEPING_ROBOT_PROFILE, CLOTHES_RACK_PROFILE, WASHING_MACHINE_PROFILE)


__all__ = [
    "YUBA_PROFILE",
    "SWEEPING_ROBOT_PROFILE",
    "CLOTHES_RACK_PROFILE",
    "WASHING_MACHINE_PROFILE",
    "build_yuba",
    "build_sweeping_robot",
    "build_clothes_rack",
    "build_washing_machine",
    "match_role",
    "register_default_profiles",
]
