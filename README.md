# meowallet

Production-ready Python client for the [MEO Wallet](https://developers.wallet.pt/en/) payment API.

Typed, ergonomic, and safe for financial use. Supports both synchronous and asynchronous usage.

## Features

- Sync and async clients (`MeoWalletClient` / `AsyncMeoWalletClient`)
- Pydantic v2 models for all request/response schemas
- Rich exception hierarchy with MEO Wallet error code mapping
- Safe retry policy (POST only retried with `request_id` for idempotency)
- Callback verification via the documented API handshake
- `Decimal` for all monetary amounts
- Configurable timeout, retry, headers, and event hooks
- Context manager support
- Forward-compatible: unknown API fields are preserved, not rejected

## Installation

```bash
pip install meowallet
```

**Python 3.11+** required. Dependencies: `httpx`, `pydantic`.

## Quick Start

### Synchronous

```python
import os
from meowallet import MeoWalletClient, Environment

client = MeoWalletClient(
    api_key=os.environ["MEOWALLET_API_KEY"],
    environment=Environment.SANDBOX,
)

checkout = client.checkouts.create_payment(
    amount=10.0,
    currency="EUR",
    items=[{"name": "Livro", "descr": "Um livro", "qt": 1, "ref": "123"}],
    client={"name": "João", "email": "joao@example.com"},
    url_confirm="https://myshop.com/confirm",
    url_cancel="https://myshop.com/cancel",
)

# Redirect user to complete payment
print(checkout.url_redirect)
```

### Asynchronous

```python
import os
from meowallet import AsyncMeoWalletClient, Environment

async with AsyncMeoWalletClient(
    api_key=os.environ["MEOWALLET_API_KEY"],
    environment=Environment.SANDBOX,
) as client:
    checkout = await client.checkouts.create_payment(
        amount=10.0,
        currency="EUR",
        items=[{"name": "Widget", "qt": 1}],
        url_confirm="https://myshop.com/confirm",
        url_cancel="https://myshop.com/cancel",
    )
```

## Environment Configuration

```python
from meowallet import Environment

# Via constructor
client = MeoWalletClient(api_key="...", environment=Environment.PRODUCTION)

# Or via env var (api_key auto-reads MEOWALLET_API_KEY)
client = MeoWalletClient(environment=Environment.PRODUCTION)
```

| Environment | Base URL |
|---|---|
| `Environment.SANDBOX` | `https://services.sandbox.meowallet.pt` |
| `Environment.PRODUCTION` | `https://services.wallet.pt` |

## API Reference

### Checkouts

```python
# Payment checkout
checkout = client.checkouts.create_payment(
    amount=25.50, currency="EUR",
    items=[{"name": "Product", "qt": 1}],
    url_confirm="https://myshop.com/ok",
    url_cancel="https://myshop.com/cancel",
    exclude=["MB"],  # Exclude payment methods
)

# Authorization checkout (reserve funds for later capture)
checkout = client.checkouts.create_authorization(
    amount=100.0, currency="EUR",
    url_confirm="https://myshop.com/ok",
    url_cancel="https://myshop.com/cancel",
)

# Get checkout status
checkout = client.checkouts.get("checkout-uuid")

# Delete/void checkout (before customer selects method)
client.checkouts.delete("checkout-uuid")
```

### Operations

```python
# List operations with filters
ops = client.operations.list(
    method="CC", type="PAYMENT",
    startdate="2025-01-01", enddate="2025-12-31",
    ext_invoiceid="INV-001",
    limit=10,
)

# Get single operation
op = client.operations.get("operation-uuid")

# Full refund
refund = client.operations.refund("operation-uuid")

# Partial refund with idempotency
from uuid import uuid4
refund = client.operations.refund(
    "operation-uuid",
    type="partial", amount=5.0,
    request_id=str(uuid4()),
)
```

### Authorizations

```python
# List authorizations
auths = client.authorizations.list(method="CC", limit=10)

# Get authorization with captures/releases
auth = client.authorizations.get("auth-uuid")

# Capture full amount
op = client.authorizations.capture("auth-uuid")

# Capture partial amount
op = client.authorizations.capture("auth-uuid", amount=25.0)

# Release (void) authorization
op = client.authorizations.release("auth-uuid")
```

### Wallet Methods

```python
methods = client.wallets.list_methods()
# ["CC", "MB", "WALLET"]
```

### Callback/Webhook Verification

MEO Wallet sends payment notifications to your configured endpoint. Verify them:

```python
# In your webhook handler:
raw_body = request.body  # Raw bytes from the HTTP request

# Option 1: Verify + parse in one step (recommended)
try:
    payload = client.callbacks.verify_and_parse(raw_body)
except CallbackVerificationError:
    return Response(status=400)

# Option 2: Verify separately
is_valid = client.callbacks.verify(raw_body)

# Option 3: Parse without verification
payload = client.callbacks.parse(raw_body)
```

See `examples/fastapi_callback.py` and `examples/flask_callback.py` for complete webhook handlers.

**Important:** Callbacks are retried for ~2 days with exponential backoff. Your handler **must be idempotent** — track `operation_id` and skip duplicates.

### Request ID / Idempotency

Use `request_id` (UUID) to make requests safely retryable:

```python
from uuid import uuid4

# If this request fails due to network issues, retrying with the
# same request_id will return the original result instead of
# creating a duplicate payment.
checkout = client.checkouts.create_payment(
    amount=10.0, currency="EUR",
    items=[{"name": "Item", "qt": 1}],
    url_confirm="https://myshop.com/ok",
    url_cancel="https://myshop.com/cancel",
    request_id=str(uuid4()),
)

# Look up request status by UUID
status = client.requests.get("your-request-uuid")
print(status.status)  # "COMPLETED"
print(status.href)    # "/api/v2/operations/..."
```

The library's retry policy respects `request_id`: POST requests are only automatically retried when `request_id` is present. Without it, POST failures are raised immediately to prevent duplicate charges.

## Error Handling

```python
from meowallet import (
    MeoWalletError,       # Base for all errors
    AuthenticationError,  # Invalid API key (codes 20001/20004/20005)
    NotFoundError,        # Resource not found (code 10004)
    InvalidStateError,    # Invalid operation state (code 10013)
    PaymentDeclinedError, # Card declined (code 30007)
    NotRefundableError,   # Not refundable (code 40010)
    RateLimitError,       # 429 Too Many Requests
    InternalServerError,  # 500+ or codes 19999/20008
    TransportError,       # Network failures
    TimeoutError,         # Request timeout
    CallbackVerificationError,  # Callback failed verification
)

try:
    client.operations.refund("op-uuid")
except NotRefundableError as e:
    print(f"Cannot refund: {e.error_response.reason}")
    print(f"Error code: {e.api_code}, TID: {e.tid}")
except APIError as e:
    print(f"API error: HTTP {e.status_code}, code={e.api_code}")
```

All `APIError` instances have: `status_code`, `api_code`, `tid`, `error_response` (parsed model), `raw_body`.

## Configuration

```python
from meowallet import MeoWalletClient, RetryConfig

client = MeoWalletClient(
    api_key="...",
    timeout=20.0,                    # Request timeout in seconds (default: 30)
    retry=RetryConfig(
        max_retries=5,               # Default: 3
        backoff_base=1.0,            # Default: 0.5
        backoff_max=60.0,            # Default: 30.0
        retry_post_with_request_id=True,  # Default: True
    ),
    extra_headers={"X-Custom": "value"},
    base_url="https://custom-proxy.example.com",  # Override base URL
)
```

## Test Cards (Sandbox)

| Brand | Number | Type |
|---|---|---|
| VISA | `4176660000000027` | Frictionless |
| VISA | `4176660000000092` | 3DS Challenge (OTP: `0101`) |
| Mastercard | `5299990270000368` | Frictionless |
| Mastercard | `5299910010000015` | 3DS Challenge (OTP: `4445`) |

All test cards accept any CVC and future expiration dates.

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Quality Commands

```bash
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/meowallet

# Test with coverage
pytest tests/ -v --cov=meowallet --cov-report=term-missing
```

## Supported Endpoints

| Resource | Method | Endpoint |
|---|---|---|
| Checkouts | `create_payment` | `POST /api/v2/checkout` |
| Checkouts | `create_authorization` | `POST /api/v2/checkout` |
| Checkouts | `get` | `GET /api/v2/checkout/{id}` |
| Checkouts | `delete` | `DELETE /api/v2/checkout/{id}` |
| Operations | `list` | `GET /api/v2/operations` |
| Operations | `get` | `GET /api/v2/operations/{id}` |
| Operations | `refund` | `POST /api/v2/operations/{id}/refund` |
| Authorizations | `list` | `GET /api/v2/authorizations` |
| Authorizations | `get` | `GET /api/v2/authorizations/{id}` |
| Authorizations | `capture` | `POST /api/v2/authorizations/{id}/capture` |
| Authorizations | `release` | `POST /api/v2/authorizations/{id}/release` |
| Wallets | `list_methods` | `GET /api/v2/wallets/methods` |
| Requests | `get` | `GET /api/v2/requests/{uuid}` |
| Callbacks | `verify` | `POST /api/v2/callback/verify` |

## Not Yet Implemented

The following documented endpoints are excluded from v0.1.0 and may be added in future releases:

- **Subscriptions** — recurring billing via checkout + charge management
- **MB WAY direct payments** — push-notification payments (`POST /api/v2/payment`)
- **MB references** — Multibanco reference management (`/api/v2/mb/*`)
- **SEPA Direct Debit** — mandate + payment management (`/api/v2/sepa/*`)
- **Marketplace splits** — payment splitting to sub-merchants
- **Prows2 server-to-server** — card/MBWay payments without checkout (requires ESB token)
- **Open Banking / PSD2** — account info + payment initiation for TPPs
- **Secure Form Fields** — JavaScript tokenization for custom checkout pages
- **Payment button/badge images** — `GET /api/v2/anon/images/*`

## License

MIT
