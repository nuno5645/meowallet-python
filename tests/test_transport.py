"""Tests for HTTP transport layer."""

import httpx
import pytest
import respx

from meowallet.config import ClientConfig, RetryConfig
from meowallet.exceptions import InternalServerError, NotFoundError
from meowallet.transport import AsyncTransport, SyncTransport, _build_headers, _clean_params

TEST_KEY = "test_key_0000000000000000000000000000"


class TestBuildHeaders:
    def test_auth_header_format(self):
        cfg = ClientConfig(api_key=TEST_KEY)
        headers = _build_headers(cfg)
        assert headers["Authorization"] == f"WalletPT {TEST_KEY}"

    def test_content_type(self):
        cfg = ClientConfig(api_key=TEST_KEY)
        headers = _build_headers(cfg)
        assert headers["Content-Type"] == "application/json"

    def test_user_agent(self):
        cfg = ClientConfig(api_key=TEST_KEY)
        headers = _build_headers(cfg)
        assert "meowallet-python" in headers["User-Agent"]

    def test_extra_headers_merged(self):
        cfg = ClientConfig(api_key=TEST_KEY, extra_headers={"X-Custom": "value"})
        headers = _build_headers(cfg)
        assert headers["X-Custom"] == "value"


class TestCleanParams:
    def test_removes_none(self):
        assert _clean_params({"a": 1, "b": None, "c": "x"}) == {"a": 1, "c": "x"}

    def test_none_input(self):
        assert _clean_params(None) is None

    def test_all_none(self):
        assert _clean_params({"a": None}) == {}


class TestSyncTransportRequest:
    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_get_request(self, respx_mock):
        respx_mock.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"methods": ["CC", "MB"]})
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            result = transport.request("GET", "/api/v2/wallets/methods")
            assert result == {"methods": ["CC", "MB"]}
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_post_with_body(self, respx_mock):
        from meowallet.models.operation import RefundRequest

        respx_mock.post("/api/v2/operations/op1/refund").mock(
            return_value=httpx.Response(
                200,
                json={"id": "ref1", "type": "REFUND", "status": "COMPLETED"},
            )
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            from meowallet.models.operation import Operation

            result = transport.request(
                "POST",
                "/api/v2/operations/op1/refund",
                body=RefundRequest(type="full"),
                response_model=Operation,
            )
            assert result.id == "ref1"
            assert result.type == "REFUND"
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_callback_verify_true(self, respx_mock):
        respx_mock.post("/api/v2/callback/verify").mock(
            return_value=httpx.Response(200, text='"true"')
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            result = transport.request(
                "POST",
                "/api/v2/callback/verify",
                raw_body=b'{"operation_id": "op1"}',
            )
            assert result == "true"
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_204_returns_none(self, respx_mock):
        respx_mock.delete("/api/v2/checkout/chk1").mock(return_value=httpx.Response(204))
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            result = transport.request("DELETE", "/api/v2/checkout/chk1")
            assert result is None
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_malformed_json_raises_transport_error(self, respx_mock):
        """Truncated/invalid JSON on success should raise TransportError, not JSONDecodeError."""
        from meowallet.exceptions import TransportError as MeoTransportError
        from meowallet.models.operation import Operation

        respx_mock.get("/api/v2/operations/op1").mock(
            return_value=httpx.Response(200, content=b"<html>Bad Gateway</html>")
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            with pytest.raises(MeoTransportError, match="Failed to decode JSON"):
                transport.request("GET", "/api/v2/operations/op1", response_model=Operation)
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_invalid_model_raises_transport_error(self, respx_mock):
        """Valid JSON but wrong shape should raise TransportError, not ValidationError."""
        from meowallet.exceptions import TransportError as MeoTransportError
        from meowallet.models.operation import OperationList

        respx_mock.get("/api/v2/operations").mock(
            return_value=httpx.Response(200, json={"unexpected": "shape", "total": "not_a_number"})
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            with pytest.raises(MeoTransportError, match="Failed to parse response"):
                transport.request("GET", "/api/v2/operations", response_model=OperationList)
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_404_raises_not_found(self, respx_mock):
        respx_mock.get("/api/v2/checkout/bad").mock(
            return_value=httpx.Response(404, json={"code": 10004, "message": "Resource not found"})
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            with pytest.raises(NotFoundError) as exc_info:
                transport.request("GET", "/api/v2/checkout/bad")
            assert exc_info.value.status_code == 404
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_500_raises_internal_server_error(self, respx_mock):
        respx_mock.get("/api/v2/operations").mock(
            return_value=httpx.Response(500, json={"code": 19999, "message": "Internal Error"})
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            with pytest.raises(InternalServerError):
                transport.request("GET", "/api/v2/operations")
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_timeout_raises_transport_error(self, respx_mock):
        respx_mock.get("/api/v2/wallets/methods").mock(side_effect=httpx.ConnectTimeout("timeout"))
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            from meowallet.exceptions import TimeoutError as MeoTimeout

            with pytest.raises(MeoTimeout):
                transport.request("GET", "/api/v2/wallets/methods")
        finally:
            transport.close()

    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    def test_connection_error_raises_transport_error(self, respx_mock):
        respx_mock.get("/api/v2/wallets/methods").mock(
            side_effect=httpx.ConnectError("connection refused")
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = SyncTransport(cfg)
        try:
            from meowallet.exceptions import ConnectionError as MeoConnError

            with pytest.raises(MeoConnError):
                transport.request("GET", "/api/v2/wallets/methods")
        finally:
            transport.close()


class TestAsyncTransportRequest:
    @pytest.mark.asyncio
    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    async def test_get_request(self, respx_mock):
        respx_mock.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"methods": ["CC"]})
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = AsyncTransport(cfg)
        try:
            result = await transport.request("GET", "/api/v2/wallets/methods")
            assert result == {"methods": ["CC"]}
        finally:
            await transport.close()

    @pytest.mark.asyncio
    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    async def test_post_with_body(self, respx_mock):
        from meowallet.models.operation import Operation, RefundRequest

        respx_mock.post("/api/v2/operations/op1/refund").mock(
            return_value=httpx.Response(
                200, json={"id": "ref1", "type": "REFUND", "status": "COMPLETED"}
            )
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = AsyncTransport(cfg)
        try:
            result = await transport.request(
                "POST",
                "/api/v2/operations/op1/refund",
                body=RefundRequest(type="full"),
                response_model=Operation,
            )
            assert result.id == "ref1"
        finally:
            await transport.close()

    @pytest.mark.asyncio
    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    async def test_404_raises(self, respx_mock):
        respx_mock.get("/api/v2/checkout/bad").mock(
            return_value=httpx.Response(404, json={"code": 10004})
        )
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = AsyncTransport(cfg)
        try:
            with pytest.raises(NotFoundError):
                await transport.request("GET", "/api/v2/checkout/bad")
        finally:
            await transport.close()

    @pytest.mark.asyncio
    @respx.mock(base_url="https://services.sandbox.meowallet.pt")
    async def test_timeout_raises(self, respx_mock):
        respx_mock.get("/api/v2/wallets/methods").mock(side_effect=httpx.ConnectTimeout("timeout"))
        cfg = ClientConfig(api_key=TEST_KEY, retry=RetryConfig(max_retries=0))
        transport = AsyncTransport(cfg)
        try:
            from meowallet.exceptions import TimeoutError as MeoTimeout

            with pytest.raises(MeoTimeout):
                await transport.request("GET", "/api/v2/wallets/methods")
        finally:
            await transport.close()
