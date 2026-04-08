"""FastAPI webhook handler for MEO Wallet callbacks.

Callbacks may be retried for ~2 days with exponential backoff.
Your handler MUST be idempotent — process each operation_id at most once.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from meowallet import AsyncMeoWalletClient, CallbackVerificationError, Environment

client: AsyncMeoWalletClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = AsyncMeoWalletClient(
        api_key=os.environ["MEOWALLET_API_KEY"],
        environment=Environment.SANDBOX,
    )
    yield
    await client.close()


app = FastAPI(lifespan=lifespan)

# Track processed operations to ensure idempotent handling.
# In production, use a database or cache (Redis, etc.).
_processed: set[str] = set()


@app.post("/webhooks/meowallet")
async def handle_callback(request: Request) -> Response:
    """Receive and verify MEO Wallet callback notifications."""
    raw_body = await request.body()

    try:
        payload = await client.callbacks.verify_and_parse(raw_body)
    except CallbackVerificationError:
        return Response(status_code=400, content="Invalid callback")

    # Idempotent handling: skip if already processed
    if payload.operation_id in _processed:
        return Response(status_code=200, content="Already processed")

    # Process the callback based on event type
    if payload.event == "COMPLETED":
        print(f"Payment completed: {payload.operation_id} — {payload.amount} {payload.currency}")
        # Update your order status, send confirmation email, etc.

    elif payload.event == "FAIL":
        print(f"Payment failed: {payload.operation_id}")
        # Handle failure

    _processed.add(payload.operation_id)
    return Response(status_code=200, content="OK")
