"""Callbacks resource: verify and parse webhook payloads."""

from __future__ import annotations

import json
from typing import Any

from meowallet.exceptions import BadRequestError, CallbackVerificationError
from meowallet.models.callback import CallbackPayload
from meowallet.resources._base import BaseAsyncResource, BaseSyncResource

_VERIFY_PATH = "/api/v2/callback/verify"


def _to_bytes(payload: bytes | str | dict[str, Any]) -> bytes:
    """Convert payload to bytes for verification.

    The callback body must be sent verbatim to /api/v2/callback/verify.
    """
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, str):
        return payload.encode("utf-8")
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def _parse_payload(payload: bytes | str | dict[str, Any]) -> CallbackPayload:
    """Parse a callback payload into a typed model."""
    data = json.loads(payload) if isinstance(payload, (bytes, str)) else payload
    return CallbackPayload.model_validate(data)


def _is_verify_false(exc: BadRequestError) -> bool:
    """Check if a BadRequestError is the expected 'false' response from callback verify.

    The MEO Wallet API returns HTTP 400 with body "false" for invalid callbacks.
    This is NOT an error — it's the expected negative verification result.
    """
    body = exc.raw_body.strip()
    return body in (b"false", b'"false"')


class Callbacks(BaseSyncResource):
    """Synchronous callback verification and parsing."""

    def verify(self, payload: bytes | str | dict[str, Any]) -> bool:
        """Verify a callback payload against the MEO Wallet API.

        Sends the received payload to POST /api/v2/callback/verify.

        .. warning::
            For reliable verification, pass raw ``bytes`` or ``str`` exactly as
            received from the HTTP request. Passing a parsed ``dict`` re-serializes
            the JSON (potentially changing whitespace/key order), which may cause
            verification to fail if the API performs byte-level comparison.

        Args:
            payload: The callback body — prefer raw bytes from the HTTP request.

        Returns:
            True if the callback is valid, False otherwise.
        """
        raw = _to_bytes(payload)
        try:
            result = self._post(_VERIFY_PATH, raw_body=raw)
            return str(result) == "true"
        except BadRequestError as exc:
            if _is_verify_false(exc):
                return False
            raise

    def parse(self, payload: bytes | str | dict[str, Any]) -> CallbackPayload:
        """Parse a callback payload into a typed CallbackPayload model.

        Does NOT verify the payload. Use ``verify_and_parse`` for verified parsing.
        """
        return _parse_payload(payload)

    def verify_and_parse(self, payload: bytes | str | dict[str, Any]) -> CallbackPayload:
        """Verify a callback payload and parse it into a typed model.

        Raises CallbackVerificationError if verification fails.

        This is the recommended method for processing webhooks:
        1. Verify authenticity via the MEO Wallet API
        2. Parse into a typed model
        3. Process idempotently (callbacks may be retried for ~2 days)
        """
        if not self.verify(payload):
            raise CallbackVerificationError(
                "Callback payload failed verification against the MEO Wallet API."
            )
        return _parse_payload(payload)


class AsyncCallbacks(BaseAsyncResource):
    """Asynchronous callback verification and parsing."""

    async def verify(self, payload: bytes | str | dict[str, Any]) -> bool:
        """Verify a callback payload against the MEO Wallet API."""
        raw = _to_bytes(payload)
        try:
            result = await self._post(_VERIFY_PATH, raw_body=raw)
            return str(result) == "true"
        except BadRequestError as exc:
            if _is_verify_false(exc):
                return False
            raise

    def parse(self, payload: bytes | str | dict[str, Any]) -> CallbackPayload:
        """Parse a callback payload into a typed CallbackPayload model."""
        return _parse_payload(payload)

    async def verify_and_parse(self, payload: bytes | str | dict[str, Any]) -> CallbackPayload:
        """Verify a callback payload and parse it into a typed model."""
        if not await self.verify(payload):
            raise CallbackVerificationError(
                "Callback payload failed verification against the MEO Wallet API."
            )
        return _parse_payload(payload)
