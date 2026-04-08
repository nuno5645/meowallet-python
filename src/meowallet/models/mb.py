"""Multibanco reference and MB WAY direct payment models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from meowallet.models.common import ClientInfo, MBReference, PaymentItem, _BaseModel, _RequestModel


class MBPaymentRequest(_RequestModel):
    """Request body for POST /api/v2/mb/pay — create MB payment with reference."""

    amount: Decimal = Field(..., ge=Decimal("0.01"))
    currency: str = "EUR"
    type: str = "PAYMENT"
    method: str = "MB"
    expires: str | None = Field(None, description="ISO 8601, must be >= 2 days in future")
    instant: bool | None = None
    starts: str | None = Field(None, description="ISO 8601, for instant refs only")
    ext_invoiceid: str | None = Field(None, max_length=45)
    ext_customerid: str | None = Field(None, max_length=45)
    ext_email: str | None = Field(None, max_length=100)
    ext_employee: str | None = Field(None, max_length=45)
    client: ClientInfo | dict | None = None  # type: ignore[type-arg]
    items: list[PaymentItem | dict] | None = None  # type: ignore[type-arg]
    store: int | None = None
    notes: str | None = None


class MBReferenceRequest(_RequestModel):
    """Request body for POST /api/v2/mb/reference — create recurring reference."""

    max_amount: Decimal = Field(..., ge=Decimal("0.20"))
    min_amount: Decimal = Field(..., ge=Decimal("0.20"))
    currency: str = "EUR"
    op_type: str = "PAYMENT"
    expires: str | None = None
    ext_invoiceid: str | None = Field(None, max_length=45)
    ext_customerid: str | None = Field(None, max_length=45)
    ext_email: str | None = Field(None, max_length=100)


class MBDeleteReferenceRequest(_RequestModel):
    """Request body for DELETE /api/v2/mb/reference."""

    entity: str
    ref: str


class MBReferenceResponse(_BaseModel):
    """Response from creating a recurring MB reference."""

    mb: MBReference | None = None


class MBWayPaymentRequest(_RequestModel):
    """Request body for POST /api/v2/payment with method=MBWAY."""

    method: str = "MBWAY"
    type: str = "PAYMENT"
    amount: Decimal = Field(..., ge=Decimal("0.01"))
    currency: str = "EUR"
    mbway: dict = Field(..., description='{"phone": "960000000"}')  # type: ignore[type-arg]
    callback: str | None = Field(None, description="Webhook URL for this payment")
    client: ClientInfo | dict | None = None  # type: ignore[type-arg]
    items: list[PaymentItem | dict] | None = None  # type: ignore[type-arg]
    ext_invoiceid: str | None = Field(None, max_length=45)
    ext_customerid: str | None = Field(None, max_length=45)
    request_id: str | None = None
    notes: str | None = None
