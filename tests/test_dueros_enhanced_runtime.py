"""Pure-logic tests for the enhanced (device-center) runtime path.

Exercises routing in ``protocol.handle_request`` when an ``EnhancedDeviceSet`` is
present in ``hass.data``: discovery / control / query all resolve against the
semantic model (the legacy per-entity path is removed).
"""

import asyncio

from tests._dueros_loader import load_enhanced

protocol, enhanced_mod = load_enhanced()

NAMESPACE_DISCOVERY = protocol.NAMESPACE_DISCOVERY
NAMESPACE_CONTROL = protocol.NAMESPACE_CONTROL
NAMESPACE_QUERY = protocol.NAMESPACE_QUERY
DOMAIN = protocol.DOMAIN
DATA_ENHANCED_DEVICES = protocol.DATA_ENHANCED_DEVICES

class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}

class FakeStates:
    def __init__(self, states):
        self._states = {s.entity_id: s for s in states}
    def async_all(self):
        return list(self._states.values())
    def get(self, entity_id):
        return self._states.get(entity_id)

class FakeServices:
    def __init__(self, hass):
        self._hass = hass
    async def async_call(self, domain, service, data, blocking=True):
        self._hass.service_calls.append((domain, service, data))

class FakeHass:
    def __init__(self, states):
        self.states = FakeStates(states)
        self.service_calls = []
        self.services = FakeServices(self)
        self.data = {}

def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)

def _header(ns, name):
    return {"namespace": ns, "name": name, "messageId": "msg-1", "payloadVersion": "1"}

def _request(ns, name, payload):
    return {"header": _header(ns, name), "payload": payload}

_YUBA = [
    FakeState("light.yuba", "on", {"friendly_name": "浴室浴霸"}),
    FakeState("switch.heating", "on", {"friendly_name": "取暖"}),
    FakeState("switch.blow", "off", {"friendly_name": "吹风"}),
    FakeState("switch.ventilation", "off", {"friendly_name": "换气"}),
    FakeState("select.warmth_level", "select", {"friendly_name": "热度档位", "option": "暖风"}),
]

def _states():
    return list(_YUBA) + [FakeState("light.bedroom", "off", {"friendly_name": "卧室灯"})]

def _device_of():
    yuba_ids = {s.entity_id for s in _YUBA}
    def fn(eid):
        return "yuba-device" if eid in yuba_ids else None
    return fn

def _hass_with_enhanced():
    states = _states()
    hass = FakeHass(states)
    options = {}  # default path: auto-detect profiles (no feature flag)
    enhanced = enhanced_mod.build_enhanced_device_set(
        states, options, device_of=_device_of(), name_of=lambda k: {"yuba-device": "浴室浴霸"}.get(k)
    )
    assert enhanced
    hass.data = {DOMAIN: {DATA_ENHANCED_DEVICES: enhanced}}
    return hass

def _yuba_device(hass):
    """Return the enrolled YUBA DuerDevice (there may be other devices too)."""
    for d in hass.data[DOMAIN][DATA_ENHANCED_DEVICES].all():
        if d.profile_key == "YUBA":
            return d
    raise AssertionError("no YUBA device in enhanced set")

def test_discovery_merges_enhanced_and_skips_legacy_yuba():
    hass = _hass_with_enhanced()
    resp = run(protocol.handle_request(hass, None, _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {})))
    appliances = resp["payload"]["discoveredAppliances"]
    ids = {a["applianceId"] for a in appliances}
    # enhanced yuba present (hash id) ...
    enhanced_yuba = [a for a in appliances if a["modelName"] == "YUBA" and a["applianceId"].startswith("dueros-")]
    assert enhanced_yuba
    # ... and the legacy entity-id yuba function switches are NOT re-emitted
    # (no duplicate); the bathroom light is its own separate LIGHT device.
    assert "switch.heating" not in ids
    light_app = [a for a in appliances if a["applianceTypes"] == ["LIGHT"] and a["applianceId"] == "light.yuba"]
    assert light_app
    # legacy non-yuba device still present.
    assert "light.bedroom" in ids
    # enhanced yuba advertises the YUBA action set.
    assert "setGear" in enhanced_yuba[0]["actions"]
    assert enhanced_yuba[0]["applianceTypes"] == ["YUBA"]

def test_control_turn_off_fans_out_to_enhanced_yuba():
    hass = _hass_with_enhanced()
    device = _yuba_device(hass)
    req = _request(NAMESPACE_CONTROL, "TurnOffRequest", {"appliance": {"applianceId": device.device_id}})
    resp = run(protocol.handle_request(hass, None, req))
    assert resp["header"]["name"] == "TurnOffConfirmation"
    # heating is on -> turned off; the light is a separate device and must
    # NOT be switched off together with the YUBA functions.
    calls = [(d, s) for d, s, _ in hass.service_calls]
    assert ("switch", "turn_off") in calls
    assert ("light", "turn_off") not in calls

def test_control_set_mode_targets_function_switch():
    hass = _hass_with_enhanced()
    device = _yuba_device(hass)
    req = _request(NAMESPACE_CONTROL, "SetModeRequest", {
        "appliance": {"applianceId": device.device_id},
        "mode": {"value": "吹风"},
    })
    resp = run(protocol.handle_request(hass, None, req))
    assert resp["header"]["name"] == "SetModeConfirmation"
    assert ("switch", "turn_on") in [(d, s) for d, s, _ in hass.service_calls]
    # The turn_on should target switch.blow.
    blow_call = [data for d, s, data in hass.service_calls if data.get("entity_id") == "switch.blow"]
    assert blow_call

def test_query_get_state_returns_attributes():
    hass = _hass_with_enhanced()
    device = _yuba_device(hass)
    req = _request(NAMESPACE_QUERY, "GetState", {"appliance": {"applianceId": device.device_id}})
    resp = run(protocol.handle_request(hass, None, req))
    attrs = resp["payload"]["attributes"]
    names = {a["name"] for a in attrs}
    assert "turnOnState" in names
    assert "mode" in names
    assert "warmthLevel" in names

def test_auto_detect_and_default_light_enrolled():
    # Default path: every device is enrolled (no feature flag).
    states = _states()
    enhanced = enhanced_mod.build_enhanced_device_set(states, {}, device_of=_device_of())
    assert enhanced
    assert any(d.profile_key == "YUBA" for d in enhanced.all())
    # A plain light device (no profile) is now ALSO enrolled through the
    # generic builder (device_id == entity_id), not left to a legacy path.
    light_only = [
        FakeState("light.yeelink_cn_751118878_bslamp2_s_2_light", "off", {"friendly_name": "床头灯"}),
    ]
    es2 = enhanced_mod.build_enhanced_device_set(light_only, {}, device_of=lambda eid: eid)
    assert es2
    dev = es2.all()[0]
    assert dev.device_id == "light.yeelink_cn_751118878_bslamp2_s_2_light"
    assert dev.profile_key == "light"
    assert "turnOn" in dev.actions()
    # Discovery (enhanced-only) still emits the plain light.
    hass = FakeHass(states)
    hass.data = {DOMAIN: {DATA_ENHANCED_DEVICES: enhanced}}
    resp = run(protocol.handle_request(hass, None, _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {})))
    ids = {a["applianceId"] for a in resp["payload"]["discoveredAppliances"]}
    assert "light.bedroom" in ids
