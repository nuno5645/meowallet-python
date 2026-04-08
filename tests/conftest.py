"""Shared test fixtures."""

from __future__ import annotations

import pytest
import respx

from meowallet import AsyncMeoWalletClient, Environment, MeoWalletClient, RetryConfig

TEST_API_KEY = "test_key_0000000000000000000000000000"
SANDBOX_URL = "https://services.sandbox.meowallet.pt"

NO_RETRY = RetryConfig(max_retries=0)


@pytest.fixture
def mock_api():
    """respx mock router scoped to the sandbox base URL."""
    with respx.mock(base_url=SANDBOX_URL) as router:
        yield router


@pytest.fixture
def client(mock_api):
    """Sync client with retries disabled for deterministic tests."""
    c = MeoWalletClient(
        api_key=TEST_API_KEY,
        environment=Environment.SANDBOX,
        retry=NO_RETRY,
    )
    yield c
    c.close()


@pytest.fixture
def async_client(mock_api):
    """Async client with retries disabled."""
    return AsyncMeoWalletClient(
        api_key=TEST_API_KEY,
        environment=Environment.SANDBOX,
        retry=NO_RETRY,
    )


# Reusable response payloads

CHECKOUT_RESPONSE = {
    "id": "chk-uuid-001",
    "url_confirm": "https://example.com/confirm?checkoutid=chk-uuid-001",
    "url_cancel": "https://example.com/cancel?checkoutid=chk-uuid-001",
    "url_redirect": "https://wallet.pt/checkout/chk-uuid-001",
    "payment": {
        "id": "op-uuid-001",
        "amount": 10.00,
        "amount_net": 9.70,
        "currency": "EUR",
        "type": "PAYMENT",
        "channel": "WEBSITE",
        "status": "NEW",
        "date": "2025-01-15T10:00:00+0000",
        "modified_date": "2025-01-15T10:00:00+0000",
        "fee": -0.30,
        "refundable": False,
        "merchant": {"id": 12345, "name": "Test Merchant", "email": "merchant@test.com"},
        "items": [{"name": "Test Item", "qt": 1, "descr": "A test item"}],
    },
}

OPERATION_RESPONSE = {
    "id": "op-uuid-001",
    "amount": 10.00,
    "amount_net": 9.70,
    "currency": "EUR",
    "type": "PAYMENT",
    "status": "COMPLETED",
    "method": "CC",
    "channel": "WEBSITE",
    "date": "2025-01-15T10:00:00+0000",
    "modified_date": "2025-01-15T10:00:01+0000",
    "fee": -0.30,
    "refundable": True,
    "merchant": {"id": 12345, "name": "Test Merchant", "email": "merchant@test.com"},
    "items": [{"name": "Test Item", "qt": 1}],
    "card": {
        "token": "card-token-001",
        "last4": "0027",
        "type": "VISA",
        "valdate": "12/2030",
        "expired": False,
    },
}

REFUND_RESPONSE = {
    "id": "op-uuid-002",
    "amount": -10.00,
    "amount_net": -10.00,
    "currency": "EUR",
    "type": "REFUND",
    "status": "COMPLETED",
    "method": "CC",
    "fee": 0,
    "refundable": False,
    "parent": "op-uuid-001",
    "date": "2025-01-16T10:00:00+0000",
    "modified_date": "2025-01-16T10:00:00+0000",
}

OPERATION_LIST_RESPONSE = {
    "total": 2,
    "elements": [OPERATION_RESPONSE, REFUND_RESPONSE],
}

AUTHORIZATION_RESPONSE = {
    "id": "auth-uuid-001",
    "amount": 50.00,
    "amount_net": 50.00,
    "currency": "EUR",
    "type": "AUTH",
    "status": "COMPLETED",
    "method": "CC",
    "date": "2025-01-15T10:00:00+0000",
    "modified_date": "2025-01-15T10:00:00+0000",
    "fee": 0,
    "refundable": False,
    "captures": [],
    "releases": [],
}

CAPTURE_RESPONSE = {
    "id": "op-uuid-003",
    "amount": 25.00,
    "amount_net": 24.50,
    "currency": "EUR",
    "type": "CAPTURE",
    "status": "COMPLETED",
    "method": "CC",
    "fee": -0.50,
    "refundable": True,
    "date": "2025-01-17T10:00:00+0000",
    "modified_date": "2025-01-17T10:00:00+0000",
}

CALLBACK_PAYLOAD = {
    "amount": 10.00,
    "create_date": "2025-01-15T10:00:00+0000",
    "currency": "EUR",
    "event": "COMPLETED",
    "ext_customerid": "cust-001",
    "ext_invoiceid": "inv-001",
    "ext_email": "shop@test.com",
    "method": "CC",
    "modified_date": "2025-01-15T10:00:01+0000",
    "operation_id": "op-uuid-001",
    "operation_status": "COMPLETED",
    "user": 99999,
}

ERROR_RESPONSE_404 = {
    "code": 10004,
    "message": "Resource not found",
    "reason": "The requested resource does not exist",
    "link": "https://developers.wallet.pt/en/procheckout/errorhandling.html",
    "tid": "err-tid-001",
}

ERROR_RESPONSE_AUTH = {
    "code": 20005,
    "message": "Invalid API KEY",
    "reason": "The provided API key is not valid",
    "tid": "err-tid-002",
}
