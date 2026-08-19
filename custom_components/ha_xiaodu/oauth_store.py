"""OAuth2 code/token store for the Xiaodu integration.

Tokens issued to the Xiaodu skill are opaque random strings owned by this
integration, NOT Home Assistant user tokens. The DuerOS endpoint (phase 3)
validates requests against this store and only exposes entities allowed by
the entry's EntityFilter, so even a leaked token cannot be used against the
Home Assistant API with user-level permissions (least privilege).

Token lifecycle: access tokens last 7 days (sent with every DuerOS request);
refresh tokens last 30 days and are rotated at the token endpoint.
"""

from __future__ import annotations

import secrets
import time
from typing import Any

from .const import (
    OAUTH_ACCESS_TOKEN_EXPIRE_SECONDS,
    OAUTH_CODE_EXPIRE_SECONDS,
    OAUTH_REFRESH_TOKEN_EXPIRE_SECONDS,
)


class XiaoduOAuthStore:
    """Manage authorization codes and opaque access/refresh tokens."""

    def __init__(self) -> None:
        self._codes: dict[str, dict[str, Any]] = {}
        self._tokens: dict[str, dict[str, Any]] = {}
        self._refresh: dict[str, str] = {}
        # HA user_id -> Baidu openUid (device-sync targets, cleaned on unbind).
        self._open_uids: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Authorization codes (short-lived, kept in memory only)
    # ------------------------------------------------------------------

    def issue_code(
        self, client_id: str, redirect_uri: str, user_id: str | None = None
    ) -> str:
        """Issue a single-use authorization code."""
        code = secrets.token_urlsafe(32)
        self._codes[code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "user_id": user_id,
            "expires_at": time.time() + OAUTH_CODE_EXPIRE_SECONDS,
        }
        return code

    def consume_code(self, code: str) -> dict[str, Any] | None:
        """Consume (and delete) an authorization code."""
        record = self._codes.pop(code, None)
        if record is None or record["expires_at"] <= time.time():
            return None
        return record

    # ------------------------------------------------------------------
    # Opaque access / refresh tokens (persisted across restarts)
    # ------------------------------------------------------------------

    def issue_token(
        self, client_id: str, user_id: str | None = None
    ) -> tuple[str, str]:
        """Issue a new access/refresh token pair."""
        self._purge()
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        now = time.time()
        self._tokens[access_token] = {
            "client_id": client_id,
            "user_id": user_id,
            "created_at": now,
            "refresh_token": refresh_token,
            "access_expires_at": now + OAUTH_ACCESS_TOKEN_EXPIRE_SECONDS,
            "refresh_expires_at": now + OAUTH_REFRESH_TOKEN_EXPIRE_SECONDS,
        }
        self._refresh[refresh_token] = access_token
        return access_token, refresh_token

    def rotate_token(self, refresh_token: str) -> tuple[str, str] | None:
        """Rotate a refresh token into a fresh token pair."""
        self._purge()
        access_token = self._refresh.pop(refresh_token, None)
        if access_token is None:
            return None
        record = self._tokens.pop(access_token, None)
        if record is None or record["refresh_expires_at"] <= time.time():
            return None
        return self.issue_token(record["client_id"], record.get("user_id"))

    def validate_token(self, access_token: str) -> bool:
        """Return True when the access token is still valid."""
        now = time.time()
        record = self._tokens.get(access_token)
        return record is not None and record["access_expires_at"] > now

    def revoke(self, access_token: str) -> None:
        """Revoke an access token and its refresh token (skill unbind)."""
        record = self._tokens.pop(access_token, None)
        if record is not None:
            self._refresh.pop(record.get("refresh_token"), None)

    def user_id_for_token(self, access_token: str) -> str | None:
        """Return the HA user the token was issued to, if any."""
        record = self._tokens.get(access_token)
        return record.get("user_id") if record else None

    def record_open_uid(self, user_id: str | None, open_uid: str) -> bool:
        """Associate a Baidu openUid with an HA user.

        Returns True when the mapping changed (and should be persisted).
        """
        key = user_id or f"anon-{open_uid}"
        if self._open_uids.get(key) == open_uid:
            return False
        self._open_uids[key] = open_uid
        return True

    def remove_open_uid(self, user_id: str | None) -> bool:
        """Forget the openUid bound to an HA user (skill unbind)."""
        key = user_id or ""
        return self._open_uids.pop(key, None) is not None

    def open_uids(self) -> list[str]:
        """Return the known Baidu openUids (sorted, deduped, for device sync)."""
        return sorted(set(self._open_uids.values()))

    def _purge(self) -> None:
        """Drop expired codes and fully-expired token pairs."""
        now = time.time()
        expired_codes = [k for k, v in self._codes.items() if v["expires_at"] <= now]
        for key in expired_codes:
            self._codes.pop(key, None)
        expired_tokens = [
            k for k, v in self._tokens.items() if v["refresh_expires_at"] <= now
        ]
        for key in expired_tokens:
            record = self._tokens.pop(key)
            self._refresh.pop(record["refresh_token"], None)

    # ------------------------------------------------------------------
    # Persistence (tokens only)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize tokens for storage."""
        return {
            "tokens": self._tokens,
            "refresh": self._refresh,
            "open_uids": dict(self._open_uids),
        }

    def load_dict(self, data: dict[str, Any] | None) -> None:
        """Load serialized tokens."""
        if not data:
            return
        self._tokens = {
            key: dict(value) for key, value in data.get("tokens", {}).items()
        }
        self._refresh = dict(data.get("refresh", {}))
        raw = data.get("open_uids") or {}
        if isinstance(raw, dict):
            self._open_uids = {str(key): str(value) for key, value in raw.items()}
        else:
            # Legacy list format: no user association.
            self._open_uids = {f"anon-{value}": str(value) for value in raw}
