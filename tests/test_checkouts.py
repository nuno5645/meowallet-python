"""Tests for the checkouts resource."""

import json

import httpx
import pytest

from tests.conftest import CHECKOUT_RESPONSE


class TestCheckoutsSync:
    def test_create_payment_with_kwargs(self, client, mock_api):
        mock_api.post("/api/v2/checkout").mock(
            return_value=httpx.Response(201, json=CHECKOUT_RESPONSE)
        )
        checkout = client.checkouts.create_payment(
            amount=10.0,
            currency="EUR",
            items=[{"name": "Test Item", "qt": 1}],
            url_confirm="https://example.com/confirm",
            url_cancel="https://example.com/cancel",
        )
        assert checkout.id == "chk-uuid-001"
        assert checkout.url_redirect == "https://wallet.pt/checkout/chk-uuid-001"
        assert checkout.payment is not None
        assert checkout.payment.status == "NEW"

        # Verify request body structure
        request = mock_api.calls.last.request
        body = json.loads(request.content)
        assert "payment" in body
        assert body["payment"]["amount"] == 10.0
        assert body["url_confirm"] == "https://example.com/confirm"

    def test_create_payment_with_model(self, client, mock_api):
        from meowallet import PaymentBody

        mock_api.post("/api/v2/checkout").mock(
            return_value=httpx.Response(201, json=CHECKOUT_RESPONSE)
        )
        body = PaymentBody(amount=10.0, currency="EUR")
        checkout = client.checkouts.create_payment(
            body,
            url_confirm="https://example.com/confirm",
            url_cancel="https://example.com/cancel",
        )
        assert checkout.id == "chk-uuid-001"

    def test_create_authorization(self, client, mock_api):
        auth_response = {
            "id": "chk-uuid-002",
            "url_redirect": "https://wallet.pt/checkout/chk-uuid-002",
            "authorization": {
                "id": "auth-op-001",
                "amount": 50.0,
                "type": "AUTH",
                "status": "NEW",
            },
        }
        mock_api.post("/api/v2/checkout").mock(
            return_value=httpx.Response(201, json=auth_response)
        )
        checkout = client.checkouts.create_authorization(
            amount=50.0,
            currency="EUR",
            url_confirm="https://example.com/confirm",
            url_cancel="https://example.com/cancel",
        )
        assert checkout.authorization is not None
        assert checkout.authorization.type == "AUTH"

        body = json.loads(mock_api.calls.last.request.content)
        assert "authorization" in body
        assert "payment" not in body

    def test_get_checkout(self, client, mock_api):
        mock_api.get("/api/v2/checkout/chk-uuid-001").mock(
            return_value=httpx.Response(200, json=CHECKOUT_RESPONSE)
        )
        checkout = client.checkouts.get("chk-uuid-001")
        assert checkout.id == "chk-uuid-001"

    def test_delete_checkout(self, client, mock_api):
        mock_api.delete("/api/v2/checkout/chk-uuid-001").mock(return_value=httpx.Response(204))
        result = client.checkouts.delete("chk-uuid-001")
        assert result is None

    def test_create_payment_both_model_and_kwargs_raises(self, client):
        from meowallet import PaymentBody

        with pytest.raises(TypeError, match="not both"):
            client.checkouts.create_payment(
                PaymentBody(amount=10.0),
                amount=10.0,
                url_confirm="https://example.com/confirm",
                url_cancel="https://example.com/cancel",
            )

    def test_exclude_payment_methods(self, client, mock_api):
        mock_api.post("/api/v2/checkout").mock(
            return_value=httpx.Response(201, json=CHECKOUT_RESPONSE)
        )
        client.checkouts.create_payment(
            amount=10.0,
            currency="EUR",
            url_confirm="https://example.com/confirm",
            url_cancel="https://example.com/cancel",
            exclude=["MB", "WALLET"],
        )
        body = json.loads(mock_api.calls.last.request.content)
        assert body["exclude"] == ["MB", "WALLET"]


class TestCheckoutsAsync:
    @pytest.mark.asyncio
    async def test_create_payment(self, async_client, mock_api):
        mock_api.post("/api/v2/checkout").mock(
            return_value=httpx.Response(201, json=CHECKOUT_RESPONSE)
        )
        checkout = await async_client.checkouts.create_payment(
            amount=10.0,
            currency="EUR",
            url_confirm="https://example.com/confirm",
            url_cancel="https://example.com/cancel",
        )
        assert checkout.id == "chk-uuid-001"
        await async_client.close()

    @pytest.mark.asyncio
    async def test_get_checkout(self, async_client, mock_api):
        mock_api.get("/api/v2/checkout/chk-uuid-001").mock(
            return_value=httpx.Response(200, json=CHECKOUT_RESPONSE)
        )
        checkout = await async_client.checkouts.get("chk-uuid-001")
        assert checkout.id == "chk-uuid-001"
        await async_client.close()
