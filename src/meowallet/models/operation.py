"""Operation models: list, detail, refund, capture, release."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from meowallet.enums import OperationStatus, OperationType, PaymentMethod
from meowallet.models.common import (
    ClientInfo,
    CreditCard,
    MBReference,
    Merchant,
    PaymentItem,
    User,
    _BaseModel,
    _RequestModel,
)


class Operation(_BaseModel):
    """A single operation (payment, refund, capture, release, etc.)."""

    id: str | None = None
    amount: Decimal | None = None
    amount_net: Decimal | None = None
    currency: str | None = None
    type: OperationType | str | None = None
    status: OperationStatus | str | None = None
    method: PaymentMethod | str | None = None
    channel: str | None = None
    date: datetime | str | None = None
    modified_date: datetime | str | None = None
    ipaddress: str | None = None
    fee: Decimal | None = None
    refundable: bool | None = None
    client: ClientInfo | None = None
    merchant: Merchant | None = None
    items: list[PaymentItem] | None = None
    card: CreditCard | None = None
    mb: MBReference | None = None
    notes: str | None = None
    user_notes: str | None = None
    ext_invoiceid: str | None = None
    ext_customerid: str | None = None
    ext_email: str | None = None
    ext_employee: str | None = None
    parent: str | None = None
    origin: User | None = None
    destination: User | None = None
    store: int | None = None
    request_id: str | None = None
    expires: datetime | str | None = None
    instant: bool | None = None
    callback: str | None = None


class OperationList(_BaseModel):
    """Paginated list of operations."""

    total: int = 0
    elements: list[Operation] = Field(default_factory=list)


class RefundRequest(_RequestModel):
    """Request body for POST /api/v2/operations/{id}/refund."""

    type: str = "full"
    amount: Decimal | None = Field(None, ge=Decimal("0.01"))
    ext_customerid: str | None = Field(None, max_length=255)
    ext_email: str | None = Field(None, max_length=255)
    ext_invoiceid: str | None = Field(None, max_length=255)
    notes: str | None = Field(None, max_length=255)
    request_id: str | None = None


class CaptureRequest(_RequestModel):
    """Request body for POST /api/v2/authorizations/{id}/capture."""

    amount: Decimal | None = Field(None, ge=Decimal("0.2"))
    ext_customerid: str | None = Field(None, max_length=45)
    ext_email: str | None = Field(None, max_length=100)
    ext_invoiceid: str | None = Field(None, max_length=45)
    ext_employee: str | None = Field(None, max_length=45)
    notes: str | None = Field(None, max_length=255)
    request_id: str | None = None


class ReleaseRequest(_RequestModel):
    """Request body for POST /api/v2/authorizations/{id}/release."""

    amount: Decimal | None = Field(None, ge=Decimal("0.2"))
    ext_customerid: str | None = Field(None, max_length=45)
    ext_email: str | None = Field(None, max_length=100)
    ext_invoiceid: str | None = Field(None, max_length=45)
    ext_employee: str | None = Field(None, max_length=45)
    notes: str | None = Field(None, max_length=255)
    request_id: str | None = None
