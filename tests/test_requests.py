"""Tests for the requests (idempotency) resource."""

import httpx
import pytest

from meowallet.exceptions import NotFoundError


class TestRequestsSync:
    def test_get_request_status(self, client, mock_api):
        mock_api.get("/api/v2/requests/uuid-123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "href": "/api/v2/operations/op-uuid-001",
                    "status": "COMPLETED",
                    "method": "GET",
                },
            )
        )
        status = client.requests.get("uuid-123")
        assert status.status == "COMPLETED"
        assert status.href == "/api/v2/operations/op-uuid-001"

    def test_get_request_not_found(self, client, mock_api):
        mock_api.get("/api/v2/requests/unknown-uuid").mock(
            return_value=httpx.Response(
                404,
                json={
                    "code": 10004,
                    "message": "Resource not found",
                },
            )
        )
        with pytest.raises(NotFoundError):
            client.requests.get("unknown-uuid")


class TestRequestsAsync:
    @pytest.mark.asyncio
    async def test_get_request_status(self, async_client, mock_api):
        mock_api.get("/api/v2/requests/uuid-456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "href": "/api/v2/operations/op-002",
                    "status": "COMPLETED",
                    "method": "POST",
                },
            )
        )
        status = await async_client.requests.get("uuid-456")
        assert status.status == "COMPLETED"
        await async_client.close()
