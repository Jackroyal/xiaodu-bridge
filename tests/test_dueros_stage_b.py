"""Stage-B pure-logic tests: per-device overrides (hidden / bindings / names /
mode) applied by the enhanced runtime path.

These mirror the user-facing advanced options: hiding an entity keeps it out of
profile matching / leftover / sensor aggregation; role bindings override the
auto-detection heuristics; appliance renames never change ``device_id``; and a
forced build shape (``mode``) narrows or falls back as specified.
"""

from tests._dueros_loader import load_enhanced

_, enhanced_mod = load_enhanced()
from xiaodu.dueros.device_config import (  # noqa: E402
    device_caps,
    merge_device_obj,
    serialize_caps,
)
from xiaodu.dueros.model import make_device_id  # noqa: E402
from xiaodu.dueros.profiles import (  # noqa: E402
    CLOTHES_RACK_PROFILE,
    SWEEPING_ROBOT_PROFILE,
    WASHING_MACHINE_PROFILE,
    YUBA_PROFILE,
)


class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}


def _device_of(*groups):
    table = {}
    for device_key, eids in groups:
        for eid in eids:
            table[eid] = device_key
    return lambda eid: table.get(eid)


_YUBA_STATES = [
    FakeState("light.yuba", "on", {"friendly_name": "浴室浴霸"}),
    FakeState("switch.heating", "on", {"friendly_name": "取暖"}),
    FakeState("switch.blow", "off", {"friendly_name": "吹风"}),
    FakeState("switch.ventilation", "off", {"friendly_name": "换气"}),
    FakeState("select.warmth_level", "select", {"friendly_name": "热度档位", "option": "暖风"}),
]


def _yuba_stable():
    return {
        "light.yuba": "yuba-light-uid",
        "switch.heating": "heat-uid",
        "switch.blow": "blow-uid",
        "switch.ventilation": "vent-uid",
        "select.warmth_level": "gear-uid",
    }


def _build(states, options=None, stable=None):
    return enhanced_mod.build_enhanced_device_set(
        states,
        {"devices": options} if options is not None else {},
        device_of=lambda eid: "yuba-dev",
        stable_id_of=(lambda eid: (stable or {}).get(eid)) if stable is not None else None,
    )


def _by_profile(es, profile_key):
    return [d for d in es.all() if d.profile_key == profile_key]


def test_no_override_enrolls_every_device_default_all():
    es = _build(_YUBA_STATES, None, stable=_yuba_stable())
    assert any(d.profile_key == "YUBA" for d in es.all())
    # The bathroom light is a leftover LIGHT appliance under default-all.
    assert any(d.profile_key == "light" for d in es.all())


def test_yuba_leftover_limited_to_light():
    # The bath heater's config/feature switches must not each surface as their
    # own SWITCH appliance (duplicate controls / NLU ambiguity): the YUBA
    # profile's ``leftover_domains`` allows only the light.
    states = _YUBA_STATES + [
        FakeState("switch.yuba_delay_stop", "off", {"friendly_name": "浴霸风暖 延时停止开关"}),
        FakeState("switch.yuba_plasma", "off", {"friendly_name": "杀菌 等离子开关"}),
        FakeState("switch.yuba_night_auto", "off", {"friendly_name": "自动化配置夜灯服务 自动化夜灯开关"}),
    ]
    es = _build(states, None, stable=_yuba_stable())
    assert sorted(d.profile_key for d in es.all()) == ["YUBA", "light"]
    primaries = {d.primary_entity_id for d in es.all()}
    assert "switch.yuba_delay_stop" not in primaries
    assert "switch.yuba_plasma" not in primaries
    assert "switch.yuba_night_auto" not in primaries


def test_empty_devices_dict_enrolls_nothing():
    es = _build(_YUBA_STATES, {}, stable=_yuba_stable())
    assert es.all() == []


# --- hidden ------------------------------------------------------------------

def test_hiding_yuba_light_falls_back_to_generic():
    # Removing the light means _matches_yuba no longer holds -> generic path.
    es = _build(
        _YUBA_STATES,
        {"yuba-dev": {"hidden": ["light.yuba"]}},
        stable=_yuba_stable(),
    )
    assert _by_profile(es, "YUBA") == []
    # The function switches surface as plain SWITCH appliances.
    assert any(d.profile_key == "switch" and d.primary_entity_id == "switch.heating"
               for d in es.all())


def test_hidden_entity_stays_out_of_leftover():
    rack_states = [
        FakeState("cover.rack", "closed", {"friendly_name": "晾衣杆"}),
        FakeState("light.rack_light", "off", {"friendly_name": "晾衣杆 灯"}),
    ]
    es = enhanced_mod.build_enhanced_device_set(
        rack_states,
        {"devices": {"rack-dev": {"hidden": ["light.rack_light"]}}},
        device_of=lambda eid: "rack-dev",
        stable_id_of=lambda eid: {"cover.rack": "cuid", "light.rack_light": "luid"}.get(eid),
    )
    assert len(_by_profile(es, "CLOTHES_RACK")) == 1
    assert _by_profile(es, "light") == []


def test_hidden_entity_stays_out_of_sensor_aggregate():
    states = [
        FakeState("sensor.temp", "23", {"friendly_name": "温度", "device_class": "temperature", "unit_of_measurement": "°C"}),
        FakeState("sensor.hum", "50", {"friendly_name": "湿度", "device_class": "humidity", "unit_of_measurement": "%"}),
    ]
    es = enhanced_mod.build_enhanced_device_set(
        states,
        {"devices": {"sensor-dev": {"hidden": ["sensor.hum"]}}},
        device_of=lambda eid: "sensor-dev",
        stable_id_of=lambda eid: {"sensor.temp": "tu", "sensor.hum": "hu"}.get(eid),
    )
    sensors = _by_profile(es, "SENSOR")
    assert len(sensors) == 1
    keys = {c.key for c in sensors[0].capabilities}
    assert "temperature" in keys and "humidity" not in keys
    claimed = {b.entity_id for c in sensors[0].capabilities for b in c.bindings}
    assert "sensor.hum" not in claimed


# --- bindings ----------------------------------------------------------------

def test_binding_overrides_heuristic():
    # A physically-real switch that does NOT look like "heating" is bound to the
    # heating role explicitly; build_yuba must use it (no name/entity-id match).
    states = [
        FakeState("light.yuba", "on", {"friendly_name": "浴室浴霸"}),
        FakeState("switch.other_fn", "on", {"friendly_name": "浴室暖空调"}),
        FakeState("switch.heating", "off", {"friendly_name": "取暖"}),
        FakeState("switch.blow", "off", {"friendly_name": "吹风"}),
    ]
    es = _build(states, {"yuba-dev": {"bindings": {"heating": "switch.other_fn"}}})
    yuba = _by_profile(es, "YUBA")
    assert len(yuba) == 1
    power = next(c for c in yuba[0].capabilities if c.key == "power")
    bound = {b.entity_id for b in power.bindings}
    assert "switch.other_fn" in bound
    assert yuba[0].primary_entity_id == "switch.other_fn"


def test_role_candidates_only_in_domain_not_aux():
    entities = [
        {"id": "switch.h", "label": "取暖", "domain": "switch", "is_aux": False},
        {"id": "light.yuba", "label": "灯", "domain": "light", "is_aux": False},
        {"id": "switch.night", "label": "夜灯", "domain": "switch", "is_aux": True},
        {"id": "sensor.t", "label": "温度", "domain": "sensor", "is_aux": False},
    ]
    out = enhanced_mod.role_candidate_entities(entities, ("switch",))
    assert [e["id"] for e in out] == ["switch.h"]


def test_binding_to_hidden_entity_dropped_with_warning(caplog):
    # Binding the ``dry`` role to an entity that is also hidden must not build a
    # mapping on the hidden entity — it is gone from ctx.states, so the appliance
    # would be discovered but never reachable. The binding is dropped with a
    # warning and the dry heuristic simply finds no switch.
    rack_states = [
        FakeState("cover.rack", "closed", {"friendly_name": "晾衣杆"}),
        FakeState("switch.dry", "on", {"friendly_name": "烘干"}),
        FakeState("switch.uv", "off", {"friendly_name": "杀菌"}),
    ]
    with caplog.at_level("WARNING", logger="xiaodu.dueros.enhanced"):
        es = enhanced_mod.build_enhanced_device_set(
            rack_states,
            {
                "devices": {
                    "rack-dev": {
                        "bindings": {"dry": "switch.dry"},
                        "hidden": ["switch.dry"],
                    }
                }
            },
            device_of=lambda eid: "rack-dev",
            stable_id_of=lambda eid: {"cover.rack": "cuid", "switch.dry": "d-uid", "switch.uv": "u-uid"}.get(eid),
        )
    racks = _by_profile(es, "CLOTHES_RACK")
    assert len(racks) == 1
    claimed = {b.entity_id for c in racks[0].capabilities for b in c.bindings}
    assert "switch.dry" not in claimed
    # Only the still-present uv switch's mode is advertised (no DRYING).
    mode = next(c for c in racks[0].capabilities if c.key == "mode")
    assert mode.capability.attributes[0].legal == "(DISINFECT)"
    assert "dry" in caplog.text and "switch.dry" in caplog.text and "已被隐藏" in caplog.text


def test_binding_to_entity_gone_from_device_dropped_with_warning(caplog):
    # A binding pointing at an entity that is no longer on the device (renamed
    # or deleted) must be dropped rather than yielding an unreachable appliance.
    rack_states = [
        FakeState("cover.rack", "closed", {"friendly_name": "晾衣杆"}),
        FakeState("switch.dry", "on", {"friendly_name": "烘干"}),
    ]
    with caplog.at_level("WARNING", logger="xiaodu.dueros.enhanced"):
        es = enhanced_mod.build_enhanced_device_set(
            rack_states,
            {"devices": {"rack-dev": {"bindings": {"uv": "switch.uv"}}}},
            device_of=lambda eid: "rack-dev",
            stable_id_of=lambda eid: {"cover.rack": "cuid", "switch.dry": "d-uid"}.get(eid),
        )
    racks = _by_profile(es, "CLOTHES_RACK")
    assert len(racks) == 1
    claimed = {b.entity_id for c in racks[0].capabilities for b in c.bindings}
    assert "switch.uv" not in claimed
    mode = next(c for c in racks[0].capabilities if c.key == "mode")
    assert mode.capability.attributes[0].legal == "(DRYING)"
    assert "uv" in caplog.text and "switch.uv" in caplog.text and "改名或删除" in caplog.text


# --- profile role metadata ---------------------------------------------------

def test_profile_roles_and_role_domains_declared():
    assert YUBA_PROFILE.roles["heating"] == "取暖"
    assert YUBA_PROFILE.role_domains["heating"] == ("switch",)
    assert "target_temperature" in YUBA_PROFILE.roles
    for profile in (
        YUBA_PROFILE,
        SWEEPING_ROBOT_PROFILE,
        CLOTHES_RACK_PROFILE,
        WASHING_MACHINE_PROFILE,
    ):
        assert profile.roles, profile.key
        assert profile.role_domains, profile.key
        # Every declared role has an allowed-domain tuple and a label.
        assert set(profile.roles) == set(profile.role_domains), profile.key
    # Composite-power roles may only bind to "switch" (domain is hardcoded).
    assert "cover" in CLOTHES_RACK_PROFILE.role_domains


# --- names -------------------------------------------------------------------

def test_rename_keeps_device_id_and_overrides_friendly_name():
    names = {
        "YUBA": "主浴霸",
        "light:yuba-light-uid": "浴霸灯",
    }
    es = _build(_YUBA_STATES, {"yuba-dev": {"names": names}}, stable=_yuba_stable())
    yuba = _by_profile(es, "YUBA")[0]
    light = next(d for d in es.all() if d.profile_key == "light")
    assert yuba.friendly_name == "主浴霸"
    assert light.friendly_name == "浴霸灯"
    assert yuba.device_id == make_device_id("YUBA", "yuba-dev")
    assert light.device_id == make_device_id("light", "yuba-dev", "yuba-light-uid")


def test_same_appliance_key_across_auto_and_generic():
    # The same bathroom light maps to the same names key under auto (leftover)
    # and forced generic (whole group built by the generic builder).
    names = {"light:yuba-light-uid": "浴霸灯"}
    auto = _build(_YUBA_STATES, {"yuba-dev": {"names": names}}, stable=_yuba_stable())
    generic = _build(
        _YUBA_STATES,
        {"yuba-dev": {"names": names, "mode": "generic"}},
        stable=_yuba_stable(),
    )
    auto_light = next(d for d in auto.all() if d.profile_key == "light")
    generic_light = next(d for d in generic.all() if d.profile_key == "light")
    assert auto_light.friendly_name == "浴霸灯"
    assert generic_light.friendly_name == "浴霸灯"
    assert auto_light.device_id == generic_light.device_id


# --- mode --------------------------------------------------------------------

def test_generic_mode_splits_yuba_into_plain_appliances():
    es = _build(_YUBA_STATES, {"yuba-dev": {"mode": "generic"}}, stable=_yuba_stable())
    assert _by_profile(es, "YUBA") == []
    # The bathroom light becomes an independent LIGHT appliance.
    light = next(d for d in es.all() if d.profile_key == "light")
    assert light.primary_entity_id == "light.yuba"
    # The select (暖风档位) belongs to the YUBA aggregate only -> no SELECT/gear.
    assert not any(d.profile_key == "select" for d in es.all())


def test_forced_profile_still_surfaces_leftover():
    es = _build(_YUBA_STATES, {"yuba-dev": {"mode": "YUBA"}}, stable=_yuba_stable())
    assert len(_by_profile(es, "YUBA")) == 1
    assert any(d.profile_key == "light" for d in es.all())


def _build_plain(options=None, states=None):
    states = states or [FakeState("light.bedroom", "off", {"friendly_name": "卧室灯"})]
    return enhanced_mod.build_enhanced_device_set(
        states,
        {"devices": options} if options is not None else {},
        device_of=lambda eid: "bedroom-dev",
        stable_id_of=lambda eid: {"light.bedroom": "b-uid"}.get(eid),
    )


def test_forced_profile_empty_without_binding_falls_back_to_generic():
    es = _build_plain({"bedroom-dev": {"mode": "YUBA"}})
    light = es.all()
    assert len(light) == 1
    assert light[0].profile_key == "light"
    assert light[0].device_id == make_device_id("light", "bedroom-dev", "b-uid")


def test_unregistered_profile_key_falls_back_to_auto():
    es = _build(_YUBA_STATES, {"yuba-dev": {"mode": "NOT_A_PROFILE"}}, stable=_yuba_stable())
    assert len(_by_profile(es, "YUBA")) == 1


def test_hidden_dropping_all_entities_enrolls_nothing_for_that_device():
    es = _build(
        _YUBA_STATES,
        {"yuba-dev": {"hidden": [s.entity_id for s in _YUBA_STATES]}},
        stable=_yuba_stable(),
    )
    assert es.all() == []


# --- A1: the advanced form renders under the forced / merged object ----------

def _detail(states, device_key, obj=None, stable=None):
    """Run the HA-free core of ``build_device_detail`` under ``obj``."""
    return enhanced_mod.build_device_detail_parts(
        states,
        device_key,
        obj,
        device_of=lambda eid: device_key,
        name_of=lambda key: None,
        stable_id_of=(lambda eid: (stable or {}).get(eid))
        if stable is not None
        else None,
    )


def test_forced_mode_detail_shows_profile_aggregate_when_auto_mismatches():
    # Two function switches but no bathroom light: auto never matches YUBA, yet
    # forcing YUBA with explicit role bindings must build the aggregate so the
    # form offers its role selects and aggregate rename box.
    states = [
        FakeState("switch.fn_a", "on", {"friendly_name": "功能甲"}),
        FakeState("switch.fn_b", "off", {"friendly_name": "功能乙"}),
    ]
    auto = _detail(states, "fn-dev")
    assert auto["matched_profile"] is None
    assert "YUBA" not in {a["appliance_key"] for a in auto["appliances"]}

    merged = merge_device_obj(
        None,
        {"mode": "YUBA", "bindings": {"heating": "switch.fn_a", "blow": "switch.fn_b"}},
    )
    forced = _detail(states, "fn-dev", merged)
    assert forced["matched_profile"] == "YUBA"
    assert "YUBA" in {a["appliance_key"] for a in forced["appliances"]}
    assert enhanced_mod.advanced_shape_key("YUBA", forced["matched_profile"]) == "YUBA"


def test_forced_mode_still_shapes_roles_when_build_is_empty():
    # The flagship scenario: auto detects nothing and the forced profile has not
    # been given a binding yet (so its build is empty). matched_profile is None,
    # but the shape must still resolve to the forced profile so the form renders
    # the role selects that let the user add the binding.
    states = [FakeState("switch.fn", "on", {"friendly_name": "功能"})]
    detail = _detail(states, "fn-dev", {"mode": "YUBA"})
    assert detail["matched_profile"] is None
    assert enhanced_mod.advanced_shape_key("YUBA", detail["matched_profile"]) == "YUBA"
    assert enhanced_mod.advanced_shape_key("auto", detail["matched_profile"]) is None


def test_advanced_shape_key_rules():
    assert enhanced_mod.advanced_shape_key("auto", "YUBA") == "YUBA"
    assert enhanced_mod.advanced_shape_key("auto", "light") is None
    assert enhanced_mod.advanced_shape_key("auto", None) is None
    assert enhanced_mod.advanced_shape_key("generic", "YUBA") is None
    assert enhanced_mod.advanced_shape_key("YUBA", None) == "YUBA"
    assert enhanced_mod.advanced_shape_key("", "CLOTHES_RACK") == "CLOTHES_RACK"


def test_merge_device_obj_normalizes_and_overrides_whole_fields():
    assert merge_device_obj({"caps": ["power", "brightness"]}, None) == {
        "caps": ["power", "brightness"]
    }
    # An overlay replaces whole fields, so empty containers / ``auto`` clear a
    # stored advanced value instead of leaving a stale override behind.
    stored = {
        "caps": [],
        "bindings": {"heating": "switch.h"},
        "names": {"YUBA": "主浴霸"},
        "mode": "YUBA",
    }
    cleared = merge_device_obj(
        stored,
        {"mode": "auto", "hidden": [], "bindings": {}, "names": {}},
    )
    assert cleared["mode"] == "auto"
    assert cleared["bindings"] == {}
    assert cleared["names"] == {}
    assert cleared["hidden"] == []
    assert cleared["caps"] == []  # untouched by the overlay


# --- B2: caps serialization (all selected <=> default-all) -------------------

def test_serialize_caps_full_selection_is_default_all():
    full = ["power", "brightness", "colorTemperature", "color"]
    assert serialize_caps(full, full) == []
    # A re-saved all-selected default-all device stays default-all (dynamic),
    # never a pinned explicit full list.
    assert device_caps({"caps": serialize_caps(full, full)}) is None


def test_serialize_caps_strict_subset_keeps_power_implicit():
    full = ["power", "brightness", "color"]
    assert serialize_caps(full, ["power", "brightness"]) == ["brightness"]
    # ``power`` is implicit: the runtime exposes it even though it is not stored.
    assert device_caps({"caps": ["brightness"]}) == ["brightness"]


def test_serialize_caps_power_only_is_an_explicit_marker():
    # Unchecking every non-power capability must not collapse to default-all
    # (which would re-expose them); a power-only choice is stored as a marker.
    full = ["power", "brightness", "color"]
    assert serialize_caps(full, ["power"]) == ["power"]
    assert device_caps({"caps": ["power"]}) == ["power"]


def test_serialize_caps_consistent_with_device_caps_default_all():
    full = ["power", "mode"]
    assert serialize_caps(full, ["power", "mode"]) == []
    assert device_caps({"caps": []}) is None
    assert device_caps({"caps": serialize_caps(full, ["power", "mode"])}) is None
    assert serialize_caps(full, ["power", "mode", "temperature"]) == []  # unknown ignored
    assert device_caps({"caps": ["mode"]}) == ["mode"]


# --- B3: forced empty build warns and falls back even with bindings ----------

def test_forced_profile_empty_with_binding_warns_and_falls_back(caplog):
    # The binding (dry) does not satisfy the build-gating role (cover), so the
    # forced CLOTHES_RACK builds nothing. Bindings must not suppress the
    # warning / generic fallback.
    rack_states = [
        FakeState("switch.dry", "on", {"friendly_name": "烘干"}),
        FakeState("switch.uv", "off", {"friendly_name": "杀菌"}),
    ]
    with caplog.at_level("WARNING", logger="xiaodu.dueros.enhanced"):
        es = enhanced_mod.build_enhanced_device_set(
            rack_states,
            {
                "devices": {
                    "rack-dev": {
                        "mode": "CLOTHES_RACK",
                        "bindings": {"dry": "switch.dry"},
                    }
                }
            },
            device_of=lambda eid: "rack-dev",
            stable_id_of=lambda eid: {"switch.dry": "d-uid", "switch.uv": "u-uid"}.get(eid),
        )
    assert _by_profile(es, "CLOTHES_RACK") == []
    assert any(d.profile_key == "switch" for d in es.all())
    assert "强制形态" in caplog.text


# --- C: advanced-form readability helpers (display keys / plausible profiles) --

def _ent(entity_id, label, domain, is_aux=False):
    return {"id": entity_id, "label": label, "domain": domain, "is_aux": is_aux}


_ALL_PROFILES = (
    YUBA_PROFILE,
    SWEEPING_ROBOT_PROFILE,
    CLOTHES_RACK_PROFILE,
    WASHING_MACHINE_PROFILE,
)


def test_adv_field_map_uses_chinese_labels_for_dynamic_fields():
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖", "blow": "吹风"},
        [
            {"appliance_key": "YUBA", "label": "浴霸"},
            {"appliance_key": "light:yuba-light-uid", "label": "浴霸  灯"},
        ],
    )
    # Readable keys, no raw ``role:heating`` / ``name:light:...`` leak.
    assert field_map == {
        "取暖": ("role", "heating"),
        "吹风": ("role", "blow"),
        "浴霸": ("name", "YUBA"),
        "浴霸  灯": ("name", "light:yuba-light-uid"),
    }


def test_adv_field_map_restores_submitted_values_onto_canonical_keys():
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖", "blow": "吹风"},
        [{"appliance_key": "YUBA", "label": "浴霸"}],
    )
    user_input = {"取暖": "switch.fn_a", "吹风": "__auto__", "浴霸": "主浴霸"}
    bindings = {
        key: user_input[dk]
        for dk, (kind, key) in field_map.items()
        if kind == "role" and user_input[dk] and user_input[dk] != "__auto__"
    }
    names = {
        key: user_input[dk]
        for dk, (kind, key) in field_map.items()
        if kind == "name" and user_input[dk] and user_input[dk] != "浴霸"
    }
    assert bindings == {"heating": "switch.fn_a"}
    assert names == {"YUBA": "主浴霸"}


def test_adv_field_map_disambiguates_duplicate_appliance_labels():
    field_map = enhanced_mod.adv_field_map(
        {"cover": "晾衣杆主体"},
        [
            {"appliance_key": "CLOTHES_RACK", "label": "晾衣杆"},
            {"appliance_key": "cover:rack-uid", "label": "晾衣杆"},
            {"appliance_key": "light:rack-uid", "label": "晾衣杆 灯"},
        ],
    )
    assert len(field_map) == 4
    assert field_map["晾衣杆"] == ("name", "CLOTHES_RACK")
    assert field_map["晾衣杆（2）"] == ("name", "cover:rack-uid")
    assert field_map["晾衣杆 灯"] == ("name", "light:rack-uid")
    assert field_map["晾衣杆主体"] == ("role", "cover")


def test_adv_field_map_disambiguates_role_appliance_label_collision():
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖"},
        [{"appliance_key": "YUBA", "label": "取暖"}],
    )
    assert field_map["取暖"] == ("role", "heating")
    assert field_map["取暖（2）"] == ("name", "YUBA")


def test_role_binding_specs_lists_every_role_with_empty_candidates_when_unbound():
    # Every declared role of a forced profile is rendered, even when this device
    # has no in-domain candidate (a clothes-rack dry/uv without their switches
    # still shows the role picker with only 自动识别 — hiding roles without a
    # candidate was the previous regression).
    bare = [_ent("cover.rack", "晾衣杆", "cover")]
    specs = enhanced_mod.role_binding_specs(CLOTHES_RACK_PROFILE, bare)
    assert set(specs) == {"cover", "dry", "uv"}
    assert [e["id"] for e in specs["cover"]] == ["cover.rack"]
    assert specs["dry"] == []
    assert specs["uv"] == []


def test_role_binding_specs_in_domain_switch_adds_candidate_aux_excluded():
    bare = [_ent("cover.rack", "晾衣杆", "cover")]
    with_dry = bare + [_ent("switch.dry", "烘干", "switch")]
    specs = enhanced_mod.role_binding_specs(CLOTHES_RACK_PROFILE, with_dry)
    assert set(specs) == {"cover", "dry", "uv"}
    # dry and uv share the switch/select domains, so both may bind the same
    # in-domain switch.
    assert [e["id"] for e in specs["dry"]] == ["switch.dry"]
    assert [e["id"] for e in specs["uv"]] == ["switch.dry"]

    # An aux-only switch never counts as a candidate.
    aux_only = bare + [_ent("switch.uv", "杀菌", "switch", is_aux=True)]
    specs2 = enhanced_mod.role_binding_specs(CLOTHES_RACK_PROFILE, aux_only)
    assert specs2["uv"] == []


def test_role_binding_specs_yuba_lists_all_six_roles_no_hiding():
    yuba = [
        _ent("switch.heating", "取暖", "switch"),
        _ent("light.yuba", "浴霸 灯", "light"),
    ]
    specs = enhanced_mod.role_binding_specs(YUBA_PROFILE, yuba)
    # 取暖/吹风/换气/暖风档位/风速档位/设定温度 are all present — nothing hidden.
    assert set(specs) == {
        "heating",
        "blow",
        "ventilation",
        "warmth_level",
        "fan_speed",
        "target_temperature",
    }
    assert [e["id"] for e in specs["heating"]] == ["switch.heating"]
    # warmth_level / fan_speed need select|fan; target_temperature needs
    # climate|number — none present, so the role stays but offers no candidate.
    assert specs["warmth_level"] == []
    assert specs["fan_speed"] == []
    assert specs["target_temperature"] == []


def test_role_binding_specs_yuba_target_temperature_binds_number_from_whole_group():
    # A YUBA whose 设定温度 is a ``number`` setting (never exposed standalone)
    # must still be bindable: role candidates draw from the whole HA group.
    yuba = [
        _ent("switch.heating", "取暖", "switch"),
        _ent("light.yuba", "浴霸 灯", "light"),
        _ent("number.target_temp", "设定温度", "number"),
    ]
    specs = enhanced_mod.role_binding_specs(YUBA_PROFILE, yuba)
    assert [e["id"] for e in specs["target_temperature"]] == ["number.target_temp"]
    assert specs["warmth_level"] == []
    assert specs["fan_speed"] == []


def test_adv_field_map_reverse_tables_key_canonical_names():
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖", "blow": "吹风"},
        [
            {"appliance_key": "YUBA", "label": "浴霸"},
            {"appliance_key": "light:yuba-light-uid", "label": "浴霸  灯"},
        ],
    )
    # Reverse tables key by role name / appliance_key (not the raw display).
    assert field_map.role_to_display == {"heating": "取暖", "blow": "吹风"}
    assert field_map.appliance_to_display == {
        "YUBA": "浴霸",
        "light:yuba-light-uid": "浴霸  灯",
    }
    # Reverse tables stay consistent with the forward rows.
    for display, (kind, key) in field_map.items():
        if kind == "role":
            assert field_map.role_to_display[key] == display
        else:
            assert field_map.appliance_to_display[key] == display


def test_adv_field_map_reverse_tables_use_disambiguated_keys():
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖"},
        [{"appliance_key": "YUBA", "label": "取暖"}],
    )
    assert field_map.role_to_display == {"heating": "取暖"}
    assert field_map.appliance_to_display == {"YUBA": "取暖（2）"}


def test_adv_field_map_yuba_all_six_roles_in_reverse_map():
    field_map = enhanced_mod.adv_field_map(YUBA_PROFILE.roles, [])
    assert set(field_map.role_to_display) == {
        "heating",
        "blow",
        "ventilation",
        "warmth_level",
        "fan_speed",
        "target_temperature",
    }
    assert field_map.role_to_display["warmth_level"] == "暖风档位"
    assert field_map.role_to_display["fan_speed"] == "风速档位"
    assert field_map.role_to_display["target_temperature"] == "设定温度"


def test_detail_all_entities_includes_non_exposable_role_sources():
    # Role-binding sources must be the *whole* device group: a ``select``
    # (暖风档位) and a ``number`` (设定温度) are never exposed standalone, so they
    # must not appear in the hidden/``entities`` list, yet the advanced form has
    # to offer them for the warmth_level / target_temperature role pickers.
    yuba = [
        FakeState("light.yuba", "on", {"friendly_name": "浴室浴霸"}),
        FakeState("switch.heating", "on", {"friendly_name": "取暖"}),
        FakeState("switch.blow", "off", {"friendly_name": "吹风"}),
        FakeState("switch.ventilation", "off", {"friendly_name": "换气"}),
        FakeState("select.warmth_level", "3", {"friendly_name": "暖风档位"}),
        FakeState("number.target_temp", "26", {"friendly_name": "设定温度"}),
    ]
    detail = _detail(yuba, "yuba-dev", {"mode": "YUBA"})
    ids = {e["id"] for e in detail["all_entities"]}
    assert {"select.warmth_level", "number.target_temp"} <= ids
    exposed = {e["domain"] for e in detail["entities"]}
    assert "select" not in exposed and "number" not in exposed
    # And the whole-group source really lets the YUBA roles bind them.
    specs = enhanced_mod.role_binding_specs(YUBA_PROFILE, detail["all_entities"])
    assert [e["id"] for e in specs["warmth_level"]] == ["select.warmth_level"]
    assert [e["id"] for e in specs["target_temperature"]] == ["number.target_temp"]



# --- D: section-nested advanced submit restore (device_advanced sections) ----

def test_restore_bindings_names_reads_role_and_name_fields_from_sections():
    # The device_advanced form puts the role/rename widgets inside their
    # sections; submitted values arrive nested (``user_input[<section>][<展示键>]``)
    # while the Chinese display keys are still the ones ``adv_field_map`` issues.
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖", "blow": "吹风"},
        [{"appliance_key": "YUBA", "label": "浴霸"}],
    )
    defaults = {"YUBA": "浴霸"}
    user_input = {
        "capabilities": {"capabilities": ["power"]},  # unrelated section ignored
        "role_bindings": {"取暖": "switch.fn_a", "吹风": "__auto__"},
        "device_names": {"浴霸": "主浴霸"},
    }
    bindings, names = enhanced_mod.restore_bindings_and_names(
        user_input, field_map, default_labels=defaults
    )
    assert bindings == {"heating": "switch.fn_a"}
    assert names == {"YUBA": "主浴霸"}


def test_restore_bindings_names_clears_reset_or_blank_values():
    # A role left on 自动识别 / a rename left blank (or equal to the appliance
    # default label) drops out — the caller replaces the whole stored field, so
    # this is what removes a stale override on save.
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖"},
        [{"appliance_key": "YUBA", "label": "浴霸"}],
    )
    defaults = {"YUBA": "浴霸"}
    reset = {
        "role_bindings": {"取暖": "__auto__"},
        "device_names": {"浴霸": ""},
    }
    bindings, names = enhanced_mod.restore_bindings_and_names(
        reset, field_map, default_labels=defaults
    )
    assert bindings == {}
    assert names == {}

    kept_default = {"role_bindings": {}, "device_names": {"浴霸": "浴霸"}}
    _, names = enhanced_mod.restore_bindings_and_names(
        kept_default, field_map, default_labels=defaults
    )
    assert names == {}


def test_restore_bindings_names_section_omitted_restores_nothing():
    # A shape rendered with no role/rename widgets never submits those sections;
    # both dicts come back empty so the whole-field replace clears any stale
    # override from an earlier shape.
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖"},
        [{"appliance_key": "YUBA", "label": "浴霸"}],
    )
    user_input = {"capabilities": {"capabilities": ["power"]}}
    bindings, names = enhanced_mod.restore_bindings_and_names(
        user_input, field_map, default_labels={"YUBA": "浴霸"}
    )
    assert bindings == {}
    assert names == {}


def test_restore_bindings_names_section_keys_are_parameterized():
    # The helper reads from whatever section keys the caller uses, so the flow
    # and its tests stay decoupled from the exact slugs (translation paths
    # ``.options.step.device_advanced.sections.<key>``).
    field_map = enhanced_mod.adv_field_map(
        {"cover": "晾衣杆主体"},
        [{"appliance_key": "CLOTHES_RACK", "label": "晾衣杆"}],
    )
    user_input = {"角色": {"晾衣杆主体": "cover.rack"}, "改名": {"晾衣杆": "主晾衣杆"}}
    bindings, names = enhanced_mod.restore_bindings_and_names(
        user_input,
        field_map,
        default_labels={"CLOTHES_RACK": "晾衣杆"},
        roles_section="角色",
        names_section="改名",
    )
    assert bindings == {"cover": "cover.rack"}
    assert names == {"CLOTHES_RACK": "主晾衣杆"}


def test_restore_bindings_names_default_sections_match_strings_keys():
    # Default section slugs are role_bindings / device_names — the same keys the
    # flow and strings.json ``sections`` block use; guard them so a rename here
    # cannot silently drift from the config-flow constants.
    field_map = enhanced_mod.adv_field_map(
        {"heating": "取暖"},
        [{"appliance_key": "YUBA", "label": "浴霸"}],
    )
    user_input = {
        "role_bindings": {"取暖": "switch.fn_a"},
        "device_names": {"浴霸": "主浴霸"},
    }
    bindings, names = enhanced_mod.restore_bindings_and_names(
        user_input, field_map, default_labels={"YUBA": "浴霸"}
    )
    assert bindings == {"heating": "switch.fn_a"}
    assert names == {"YUBA": "主浴霸"}


def test_profile_roles_resolve_from_shared_role_meta():
    """Every profile role/label/domain comes from the single ROLE_META table."""
    from xiaodu.dueros.profiles import ROLE_META  # noqa: PLC0415

    for profile in (
        YUBA_PROFILE,
        SWEEPING_ROBOT_PROFILE,
        CLOTHES_RACK_PROFILE,
        WASHING_MACHINE_PROFILE,
    ):
        assert set(profile.roles) == set(profile.role_domains), profile.key
        for role, label in profile.roles.items():
            assert role in ROLE_META, (profile.key, role)
            assert ROLE_META[role]["label"] == label, (profile.key, role)
        for role, domains in profile.role_domains.items():
            assert ROLE_META[role]["domains"] == domains, (profile.key, role)
