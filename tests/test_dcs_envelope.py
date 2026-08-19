"""Pure-logic tests for the DCS multipart envelope helpers (no HA runtime)."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_ENVELOPE = ROOT / "custom_components" / "ha_xiaodu" / "dueros" / "dcs_envelope.py"

spec = importlib.util.spec_from_file_location("dcs_envelope", _ENVELOPE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules["dcs_envelope"] = module
spec.loader.exec_module(module)

parse_dcs_multipart = module.parse_dcs_multipart
fill_smarthome_response = module.fill_smarthome_response

BOUNDARY = "___dueros_dcs_v1_boundary___"
CONTENT_TYPE = f"multipart/form-data; boundary={BOUNDARY}"

DISCOVERY_REQUEST = {
    "header": {
        "namespace": "DuerOS.ConnectedHome.Discovery",
        "name": "DiscoverAppliancesRequest",
        "messageId": "9ba724d577d344d8a0dbbe8c58ce26d5",
        "payloadVersion": "1",
    },
    "payload": {
        "accessToken": "test-access-token-0001",
        "openUid": "test-open-uid-0001",
    },
}


def _multipart(*parts):
    return (
        b"".join(
            f"--{BOUNDARY}\r\n{headers}\r\n\r\n".encode()
            + (body if isinstance(body, bytes) else body.encode())
            + b"\r\n"
            for headers, body in parts
        )
        + f"--{BOUNDARY}--\r\n".encode()
    )


def _dcs_envelope_body():
    """A realistic console-simulator envelope: TTS part + smarthome part."""
    speak_metadata = json.dumps(
        {
            "directive": {
                "header": {
                    "namespace": "ai.dueros.device_interface.voice_output",
                    "name": "Speak",
                    "messageId": "NmE4MWM3OThkNDQ4OTc0MTU=",
                },
                "payload": {
                    "token": "eyJib3RfaWQiOiJ1cyJ9",
                    "format": "AUDIO_MPEG",
                    "scene": "formal",
                    "url": "cid:11968",
                },
            }
        },
        ensure_ascii=False,
    )
    smarthome_metadata = json.dumps(
        {
            "debug": {
                "bot": {
                    "id": "ai.dueros.bot.smarthome",
                    "smarthome": [
                        {
                            "request": json.dumps(DISCOVERY_REQUEST),
                            "response": "",
                        }
                    ],
                    "request": None,
                    "response": None,
                }
            },
            "directive": {
                "header": {
                    "namespace": "ai.dueros.device_interface.system",
                    "name": "Nop",
                    "messageId": "NmE4MWM3OThkNDNkNTk5MzQ=",
                },
                "payload": {"time": 1786890136, "logid": "log-1"},
            },
        },
        ensure_ascii=False,
    )
    return _multipart(
        (
            'Content-Disposition: form-data; name="metadata"\r\n'
            "Content-Type: application/json; charset=utf-8",
            speak_metadata,
        ),
        (
            'Content-Type: application/octet-stream\r\n'
            'Content-Disposition: form-data; name="audio"\r\n'
            "Content-ID: <11968>",
            b"\x00\x01binary\xffaudio",
        ),
        (
            'Content-Disposition: form-data; name="metadata"\r\n'
            "Content-Type: application/json; charset=utf-8",
            smarthome_metadata,
        ),
    )


def test_parse_dcs_multipart_extracts_smarthome_request():
    envelope = parse_dcs_multipart(_dcs_envelope_body(), CONTENT_TYPE)
    assert envelope is not None
    assert envelope["smarthome"] == DISCOVERY_REQUEST
    assert "debug" in envelope["metadata"]


def test_fill_smarthome_response_writes_json_string():
    envelope = parse_dcs_multipart(_dcs_envelope_body(), CONTENT_TYPE)
    assert envelope is not None
    response = {
        "header": {
            "namespace": "DuerOS.ConnectedHome.Discovery",
            "name": "DiscoverAppliancesResponse",
            "messageId": "9ba724d577d344d8a0dbbe8c58ce26d5",
            "payloadVersion": "1",
        },
        "payload": {"discoveredAppliances": [], "discoveredGroups": []},
    }
    filled = fill_smarthome_response(envelope["metadata"], response)
    stored = filled["debug"]["bot"]["smarthome"][0]["response"]
    assert isinstance(stored, str)
    assert json.loads(stored) == response
    # The original metadata must not be mutated.
    assert envelope["metadata"]["debug"]["bot"]["smarthome"][0]["response"] == ""


def test_parse_dcs_multipart_none_for_non_smarthome_envelope():
    only_tts = _multipart(
        (
            'Content-Disposition: form-data; name="metadata"\r\n'
            "Content-Type: application/json; charset=utf-8",
            json.dumps({"directive": {"header": {"name": "Nop"}}}),
        )
    )
    assert parse_dcs_multipart(only_tts, CONTENT_TYPE) is None


def test_parse_dcs_multipart_none_for_plain_json_body():
    assert (
        parse_dcs_multipart(
            json.dumps(DISCOVERY_REQUEST).encode(), "application/json"
        )
        is None
    )


def test_parse_dcs_multipart_requires_boundary_param():
    # aiohttp's request.content_type strips the boundary parameter; the view
    # must pass the full Content-Type header instead.
    assert parse_dcs_multipart(_dcs_envelope_body(), "multipart/form-data") is None
