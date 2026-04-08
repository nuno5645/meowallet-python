"""Tests for the operations resource."""

import json

import httpx
import pytest

from tests.conftest import (
    OPERATION_LIST_RESPONSE,
    OPERATION_RESPONSE,
    REFUND_RESPONSE,
)


class TestOperationsSync:
    def test_list_operations(self, client, mock_api):
        mock_api.get("/api/v2/operations").mock(
            return_value=httpx.Response(200, json=OPERATION_LIST_RESPONSE)
        )
        result = client.operations.list(limit=10)
        assert result.total == 2
        assert len(result.elements) == 2
        assert result.elements[0].id == "op-uuid-001"

    def test_list_with_filters(self, client, mock_api):
        mock_api.get("/api/v2/operations").mock(
            return_value=httpx.Response(200, json={"total": 0, "elements": []})
        )
        client.operations.list(
            method="CC",
            type="PAYMENT",
            startdate="2025-01-01",
            enddate="2025-01-31",
            ext_invoiceid="INV-001",
            limit=5,
            offset=0,
        )
        request = mock_api.calls.last.request
        assert "method=CC" in str(request.url)
        assert "limit=5" in str(request.url)
        assert "ext_invoiceid=INV-001" in str(request.url)

    def test_list_omits_none_params(self, client, mock_api):
        mock_api.get("/api/v2/operations").mock(
            return_value=httpx.Response(200, json={"total": 0, "elements": []})
        )
        client.operations.list(method="CC")
        url = str(mock_api.calls.last.request.url)
        assert "number4" not in url
        assert "phone" not in url

    def test_get_operation(self, client, mock_api):
        mock_api.get("/api/v2/operations/op-uuid-001").mock(
            return_value=httpx.Response(200, json=OPERATION_RESPONSE)
        )
        op = client.operations.get("op-uuid-001")
        assert op.id == "op-uuid-001"
        assert op.status == "COMPLETED"
        assert op.method == "CC"
        assert op.card is not None
        assert op.card.last4 == "0027"

    def test_refund_full(self, client, mock_api):
        mock_api.post("/api/v2/operations/op-uuid-001/refund").mock(
            return_value=httpx.Response(200, json=REFUND_RESPONSE)
        )
        refund = client.operations.refund("op-uuid-001")
        assert refund.type == "REFUND"
        assert refund.parent == "op-uuid-001"

        body = json.loads(mock_api.calls.last.request.content)
        assert body["type"] == "full"

    def test_refund_partial(self, client, mock_api):
        mock_api.post("/api/v2/operations/op-uuid-001/refund").mock(
            return_value=httpx.Response(200, json=REFUND_RESPONSE)
        )
        client.operations.refund("op-uuid-001", type="partial", amount=5.0)
        body = json.loads(mock_api.calls.last.request.content)
        assert body["type"] == "partial"
        assert body["amount"] == 5.0

    def test_refund_with_model(self, client, mock_api):
        from meowallet import RefundRequest

        mock_api.post("/api/v2/operations/op-uuid-001/refund").mock(
            return_value=httpx.Response(200, json=REFUND_RESPONSE)
        )
        client.operations.refund("op-uuid-001", RefundRequest(type="full", notes="test"))
        body = json.loads(mock_api.calls.last.request.content)
        assert body["notes"] == "test"

    def test_refund_with_request_id(self, client, mock_api):
        mock_api.post("/api/v2/operations/op-uuid-001/refund").mock(
            return_value=httpx.Response(200, json=REFUND_RESPONSE)
        )
        client.operations.refund("op-uuid-001", request_id="uuid-idempotent")
        body = json.loads(mock_api.calls.last.request.content)
        assert body["request_id"] == "uuid-idempotent"


class TestOperationsAsync:
    @pytest.mark.asyncio
    async def test_list(self, async_client, mock_api):
        mock_api.get("/api/v2/operations").mock(
            return_value=httpx.Response(200, json=OPERATION_LIST_RESPONSE)
        )
        result = await async_client.operations.list()
        assert result.total == 2
        await async_client.close()

    @pytest.mark.asyncio
    async def test_refund(self, async_client, mock_api):
        mock_api.post("/api/v2/operations/op-uuid-001/refund").mock(
            return_value=httpx.Response(200, json=REFUND_RESPONSE)
        )
        refund = await async_client.operations.refund("op-uuid-001")
        assert refund.type == "REFUND"
        await async_client.close()
