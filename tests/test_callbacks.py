"""Tests for callback verification and parsing."""

import json

import httpx
import pytest

from meowallet.exceptions import CallbackVerificationError
from tests.conftest import CALLBACK_PAYLOAD


class TestCallbacksSync:
    def test_verify_valid(self, client, mock_api):
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"true"')
        )
        assert client.callbacks.verify(CALLBACK_PAYLOAD) is True

    def test_verify_invalid_200_false(self, client, mock_api):
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"false"')
        )
        assert client.callbacks.verify(CALLBACK_PAYLOAD) is False

    def test_verify_invalid_400_false(self, client, mock_api):
        """Real API returns 400 with body 'false' for invalid callbacks."""
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(400, text="false")
        )
        assert client.callbacks.verify(CALLBACK_PAYLOAD) is False

    def test_verify_sends_bytes_verbatim(self, client, mock_api):
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"true"')
        )
        raw = b'{"operation_id":"op-001","event":"COMPLETED"}'
        client.callbacks.verify(raw)
        # Verify the raw bytes were sent as-is
        assert mock_api.calls.last.request.content == raw

    def test_verify_accepts_string(self, client, mock_api):
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"true"')
        )
        assert client.callbacks.verify('{"event": "COMPLETED"}') is True

    def test_parse(self, client):
        payload = client.callbacks.parse(CALLBACK_PAYLOAD)
        assert payload.operation_id == "op-uuid-001"
        assert payload.event == "COMPLETED"
        assert payload.amount == 10.0
        assert payload.user == 99999

    def test_parse_from_bytes(self, client):
        raw = json.dumps(CALLBACK_PAYLOAD).encode()
        payload = client.callbacks.parse(raw)
        assert payload.operation_id == "op-uuid-001"

    def test_parse_from_string(self, client):
        raw = json.dumps(CALLBACK_PAYLOAD)
        payload = client.callbacks.parse(raw)
        assert payload.operation_id == "op-uuid-001"

    def test_verify_and_parse_success(self, client, mock_api):
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"true"')
        )
        payload = client.callbacks.verify_and_parse(CALLBACK_PAYLOAD)
        assert payload.operation_id == "op-uuid-001"
        assert payload.event == "COMPLETED"

    def test_verify_and_parse_failure(self, client, mock_api):
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"false"')
        )
        with pytest.raises(CallbackVerificationError):
            client.callbacks.verify_and_parse(CALLBACK_PAYLOAD)


class TestCallbacksAsync:
    @pytest.mark.asyncio
    async def test_verify_valid(self, async_client, mock_api):
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"true"')
        )
        assert await async_client.callbacks.verify(CALLBACK_PAYLOAD) is True
        await async_client.close()

    @pytest.mark.asyncio
    async def test_verify_and_parse(self, async_client, mock_api):
        mock_api.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"true"')
        )
        payload = await async_client.callbacks.verify_and_parse(CALLBACK_PAYLOAD)
        assert payload.event == "COMPLETED"
        await async_client.close()

    @pytest.mark.asyncio
    async def test_parse_sync_on_async_client(self, async_client):
        """parse() is synchronous even on the async client."""
        payload = async_client.callbacks.parse(CALLBACK_PAYLOAD)
        assert payload.operation_id == "op-uuid-001"
        await async_client.close()
