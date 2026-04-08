"""Subscription models: create, list, get, cancel, charge."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from meowallet.models.common import CreditCard, Merchant, PaymentItem, _BaseModel, _RequestModel


class SubscriptionBody(_RequestModel):
    """Subscription data for checkout creation.

    This is the ``subscription`` key in the checkout request body.
    """

    amount: Decimal = Field(..., ge=Decimal("0.01"))
    currency: str = "EUR"
    frequency: int = Field(..., ge=1, le=365)
    period: str = Field(..., description="DAY, WEEK, or MONTH")
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str | None = Field(None, description="YYYY-MM-DD, omit for no expiration")
    description: str | None = None
    ext_subscriptionid: str | None = None


class Subscription(_BaseModel):
    """A subscription returned from the API."""

    id: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    frequency: int | None = None
    period: str | None = None
    start_date: datetime | str | None = None
    end_date: datetime | str | None = None
    description: str | None = None
    ext_subscriptionid: str | None = None
    status: str | None = None
    default_payment_method: str | None = None
    card: CreditCard | None = None
    merchant: Merchant | None = None


class SubscriptionList(_BaseModel):
    """Paginated list of subscriptions."""

    total: int | str = 0
    elements: list[Subscription] = Field(default_factory=list)


class SubscriptionCheckoutResponse(_BaseModel):
    """Response from creating a subscription checkout."""

    id: str | None = None
    url_confirm: str | None = None
    url_cancel: str | None = None
    url_redirect: str | None = None
    date: datetime | str | None = None
    merchant: Merchant | None = None
    subscription: Subscription | None = None


class ChargeRequest(_RequestModel):
    """Request body for POST /api/v2/subscriptions/{id}/charge."""

    amount: Decimal = Field(..., ge=Decimal("0.01"))
    currency: str = "EUR"
    ext_invoiceid: str | None = None
    client: dict | None = None  # type: ignore[type-arg]
    items: list[PaymentItem | dict] | None = None  # type: ignore[type-arg]


class ChargeOrder(_BaseModel):
    """A charge order against a subscription."""

    id: str | None = None
    subscription_id: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    date: datetime | str | None = None
    status: str | None = None
    ext_invoiceid: str | None = None
    ext_subscriptionid: str | None = None


class ChargeOrderList(_BaseModel):
    """Paginated list of charge orders."""

    total: int | str = 0
    elements: list[ChargeOrder] = Field(default_factory=list)
