"""Tests for the login-flow schema serializer.

Home Assistant 2026.9 replaced the ``voluptuous-serialize`` dependency with
``probatio``; the authorize page must keep rendering login/MFA fields on both
lineages, and must never fail the page when neither serializer is importable.
"""

from types import SimpleNamespace

from custom_components.xiaodu_bridge import oauth_server


def test_schema_fields_none():
    assert oauth_server._schema_fields(None) == []


def test_schema_fields_prefers_probatio(monkeypatch):
    calls = []

    def to_field_list(schema):
        calls.append(schema)
        return [{"name": "username", "type": "string", "required": True}]

    monkeypatch.setattr(oauth_server, "probatio", SimpleNamespace(to_field_list=to_field_list))
    # The legacy serializer must not be touched when probatio is available.
    monkeypatch.setattr(
        oauth_server,
        "voluptuous_serialize",
        SimpleNamespace(convert=lambda schema: [{"name": "wrong"}]),
    )

    assert oauth_server._schema_fields(object()) == [
        {"name": "username", "type": "string", "required": True}
    ]
    assert len(calls) == 1


def test_schema_fields_falls_back_to_voluptuous_serialize(monkeypatch):
    monkeypatch.setattr(oauth_server, "probatio", None)
    monkeypatch.setattr(
        oauth_server,
        "voluptuous_serialize",
        SimpleNamespace(convert=lambda schema: [{"name": "password", "type": "string"}]),
    )

    assert oauth_server._schema_fields(object()) == [
        {"name": "password", "type": "string"}
    ]


def test_schema_fields_without_any_serializer(monkeypatch):
    monkeypatch.setattr(oauth_server, "probatio", None)
    monkeypatch.setattr(oauth_server, "voluptuous_serialize", None)

    assert oauth_server._schema_fields(object()) == []


def test_schema_fields_swallows_serializer_errors(monkeypatch):
    def boom(schema):
        raise ValueError("bad schema")

    monkeypatch.setattr(oauth_server, "probatio", SimpleNamespace(to_field_list=boom))

    assert oauth_server._schema_fields(object()) == []