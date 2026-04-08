"""Create a payment checkout and redirect the user."""

import os

from meowallet import MeoWalletClient, Environment

client = MeoWalletClient(
    api_key=os.environ["MEOWALLET_API_KEY"],
    environment=Environment.SANDBOX,
)

# Create a payment checkout
checkout = client.checkouts.create_payment(
    amount=25.50,
    currency="EUR",
    items=[
        {"name": "Livro Python", "descr": "Um livro sobre Python", "qt": 1, "ref": "BOOK-001"},
        {"name": "Autocolante", "descr": "Autocolante MEO Wallet", "qt": 2, "ref": "STICKER-001"},
    ],
    client={"name": "João Silva", "email": "joao@example.com"},
    url_confirm="https://myshop.example.com/payment/confirm",
    url_cancel="https://myshop.example.com/payment/cancel",
)

print(f"Checkout ID: {checkout.id}")
print(f"Redirect user to: {checkout.url_redirect}")

# After the user completes payment, check the status
status = client.checkouts.get(checkout.id)
print(f"Payment status: {status.payment.status}")

client.close()
