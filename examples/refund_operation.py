"""Find an operation by invoice ID and issue a refund."""

import os
from uuid import uuid4

from meowallet import MeoWalletClient, Environment

client = MeoWalletClient(
    api_key=os.environ["MEOWALLET_API_KEY"],
    environment=Environment.SANDBOX,
)

# Find operations by merchant invoice reference
operations = client.operations.list(ext_invoiceid="INV-2025-001", limit=5)
print(f"Found {operations.total} operations")

for op in operations.elements:
    print(f"  {op.id} | {op.type} | {op.status} | {op.amount} {op.currency}")

# Refund the first completed payment
for op in operations.elements:
    if op.type == "PAYMENT" and op.status == "COMPLETED" and op.refundable:
        # Use request_id for idempotent refund (safe to retry)
        refund = client.operations.refund(
            op.id,
            type="full",
            request_id=str(uuid4()),
        )
        print(f"Refund created: {refund.id} | status={refund.status}")
        break
else:
    print("No refundable payment found")

client.close()
