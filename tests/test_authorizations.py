"""Tests for the authorizations resource."""

import json

import httpx
import pytest

from tests.conftest import AUTHORIZATION_RESPONSE, CAPTURE_RESPONSE


class TestAuthorizationsSync:
    def test_list_authorizations(self, client, mock_api):
        mock_api.get("/api/v2/authorizations").mock(
            return_value=httpx.Response(
                200,
                json={
                    "total": 1,
                    "elements": [AUTHORIZATION_RESPONSE],
                },
            )
        )
        result = client.authorizations.list(method="CC", limit=10)
        assert result.total == 1
        assert result.elements[0].id == "auth-uuid-001"

    def test_list_with_date_filters(self, client, mock_api):
        mock_api.get("/api/v2/authorizations").mock(
            return_value=httpx.Response(200, json={"total": 0, "elements": []})
        )
        client.authorizations.list(startdate="2025-01-01", enddate="2025-12-31")
        url = str(mock_api.calls.last.request.url)
        assert "startdate=2025-01-01" in url
        assert "enddate=2025-12-31" in url

    def test_get_authorization(self, client, mock_api):
        mock_api.get("/api/v2/authorizations/auth-uuid-001").mock(
            return_value=httpx.Response(200, json=AUTHORIZATION_RESPONSE)
        )
        auth = client.authorizations.get("auth-uuid-001")
        assert auth.id == "auth-uuid-001"
        assert auth.type == "AUTH"
        assert auth.captures == []
        assert auth.releases == []

    def test_capture_full(self, client, mock_api):
        mock_api.post("/api/v2/authorizations/auth-uuid-001/capture").mock(
            return_value=httpx.Response(200, json=CAPTURE_RESPONSE)
        )
        op = client.authorizations.capture("auth-uuid-001")
        assert op.type == "CAPTURE"
        assert op.status == "COMPLETED"

    def test_capture_partial(self, client, mock_api):
        mock_api.post("/api/v2/authorizations/auth-uuid-001/capture").mock(
            return_value=httpx.Response(200, json=CAPTURE_RESPONSE)
        )
        client.authorizations.capture("auth-uuid-001", amount=25.0)
        body = json.loads(mock_api.calls.last.request.content)
        assert body["amount"] == 25.0

    def test_capture_with_model(self, client, mock_api):
        from meowallet import CaptureRequest

        mock_api.post("/api/v2/authorizations/auth-uuid-001/capture").mock(
            return_value=httpx.Response(200, json=CAPTURE_RESPONSE)
        )
        client.authorizations.capture(
            "auth-uuid-001",
            CaptureRequest(amount=10.0, ext_invoiceid="INV-001"),
        )
        body = json.loads(mock_api.calls.last.request.content)
        assert body["ext_invoiceid"] == "INV-001"

    def test_release_full(self, client, mock_api):
        release_response = {
            "id": "op-uuid-004",
            "type": "RELEASE",
            "status": "COMPLETED",
            "amount": 50.0,
        }
        mock_api.post("/api/v2/authorizations/auth-uuid-001/release").mock(
            return_value=httpx.Response(200, json=release_response)
        )
        op = client.authorizations.release("auth-uuid-001")
        assert op.type == "RELEASE"

    def test_release_partial(self, client, mock_api):
        release_response = {"id": "op-uuid-004", "type": "RELEASE", "status": "COMPLETED"}
        mock_api.post("/api/v2/authorizations/auth-uuid-001/release").mock(
            return_value=httpx.Response(200, json=release_response)
        )
        client.authorizations.release("auth-uuid-001", amount=20.0, notes="partial release")
        body = json.loads(mock_api.calls.last.request.content)
        assert body["amount"] == 20.0
        assert body["notes"] == "partial release"


class TestAuthorizationsAsync:
    @pytest.mark.asyncio
    async def test_capture(self, async_client, mock_api):
        mock_api.post("/api/v2/authorizations/auth-uuid-001/capture").mock(
            return_value=httpx.Response(200, json=CAPTURE_RESPONSE)
        )
        op = await async_client.authorizations.capture("auth-uuid-001", amount=25.0)
        assert op.type == "CAPTURE"
        await async_client.close()

    @pytest.mark.asyncio
    async def test_list(self, async_client, mock_api):
        mock_api.get("/api/v2/authorizations").mock(
            return_value=httpx.Response(200, json={"total": 0, "elements": []})
        )
        result = await async_client.authorizations.list()
        assert result.total == 0
        await async_client.close()
