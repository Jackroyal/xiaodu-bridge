"""DCS multipart envelope helpers (Baidu console simulator).

The smart-home skill's WebService receives two shapes of request:

- Production: a plain ``application/json`` body carrying the DuerOS
  smart-home directive (``DuerOS.ConnectedHome.*``) directly.

- Baidu console "模拟测试": the request is wrapped in a DCS
  ``multipart/form-data`` envelope. The actual smart-home directive is
  embedded as a JSON *string* at ``metadata.debug.bot.smarthome[0].request``
  and the gateway expects the response to be written back (as a JSON string)
  at ``metadata.debug.bot.smarthome[0].response``.

This module is deliberately dependency-free (no homeassistant imports) so the
envelope logic can be unit-tested standalone.
"""

from __future__ import annotations

import copy
import json
import re
from typing import Any

_METADATA_MARKER = b'name="metadata"'


def _parse_boundary(content_type: str) -> bytes | None:
    """Extract the multipart boundary from a Content-Type header."""
    match = re.search(r"boundary=([^;]+)", content_type, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip().strip('"').encode("utf-8")


def _split_parts(body: bytes, boundary: bytes) -> list[tuple[bytes, bytes]]:
    """Split a multipart body into (headers, content) byte pairs."""
    delimiter = b"--" + boundary
    parts: list[tuple[bytes, bytes]] = []
    for chunk in body.split(delimiter):
        chunk = chunk.strip(b"\r\n")
        if not chunk or chunk == b"--":
            continue
        sep = chunk.find(b"\r\n\r\n")
        if sep == -1:
            continue
        parts.append((chunk[:sep], chunk[sep + 4 :]))
    return parts


def _smarthome_request(metadata: dict[str, Any]) -> dict[str, Any] | None:
    """Return the nested smart-home directive, or None when absent."""
    try:
        smarthome = metadata["debug"]["bot"]["smarthome"]
    except (KeyError, TypeError):
        return None
    if not smarthome:
        return None
    entry = smarthome[0]
    raw = entry.get("request") if isinstance(entry, dict) else None
    if not raw:
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except (ValueError, TypeError):
        return None
    return data if isinstance(data, dict) else None


def parse_dcs_multipart(
    body: bytes, content_type: str
) -> dict[str, Any] | None:
    """Parse a DCS multipart body.

    Returns ``{"metadata": <dict>, "smarthome": <directive dict>}`` for the
    metadata part that carries a smart-home envelope, or ``None`` when the
    body is not a DCS envelope containing a smart-home request.
    """
    boundary = _parse_boundary(content_type)
    if boundary is None:
        return None
    for headers, content in _split_parts(body, boundary):
        if _METADATA_MARKER not in headers:
            continue
        try:
            metadata = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            continue
        if not isinstance(metadata, dict):
            continue
        smarthome = _smarthome_request(metadata)
        if smarthome is not None:
            return {"metadata": metadata, "smarthome": smarthome}
    return None


def fill_smarthome_response(metadata: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of the envelope with the smart-home response written back."""
    filled = copy.deepcopy(metadata)
    try:
        entry = filled["debug"]["bot"]["smarthome"][0]
        entry["response"] = json.dumps(response, ensure_ascii=False)
    except (KeyError, TypeError, IndexError):
        pass
    return filled
