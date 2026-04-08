"""Flask webhook handler for MEO Wallet callbacks.

Callbacks may be retried for ~2 days with exponential backoff.
Your handler MUST be idempotent — process each operation_id at most once.
"""

import os

from flask import Flask, Response, request

from meowallet import CallbackVerificationError, Environment, MeoWalletClient

app = Flask(__name__)

client = MeoWalletClient(
    api_key=os.environ["MEOWALLET_API_KEY"],
    environment=Environment.SANDBOX,
)

# Track processed operations for idempotent handling.
# In production, use a database or cache.
_processed: set[str] = set()


@app.post("/webhooks/meowallet")
def handle_callback() -> Response:
    """Receive and verify MEO Wallet callback notifications."""
    raw_body = request.get_data()

    try:
        payload = client.callbacks.verify_and_parse(raw_body)
    except CallbackVerificationError:
        return Response("Invalid callback", status=400)

    # Idempotent handling: skip if already processed
    if payload.operation_id in _processed:
        return Response("Already processed", status=200)

    # Process the callback
    if payload.event == "COMPLETED":
        print(f"Payment completed: {payload.operation_id} — {payload.amount} {payload.currency}")
        # Update order, send email, etc.

    elif payload.event == "FAIL":
        print(f"Payment failed: {payload.operation_id}")

    _processed.add(payload.operation_id)
    return Response("OK", status=200)
