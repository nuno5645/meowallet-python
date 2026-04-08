"""Checkout request and response models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import Field

from meowallet.enums import OperationStatus, OperationType, PaymentMethod
from meowallet.models.common import (
    ClientInfo,
    CreditCard,
    MBReference,
    Merchant,
    PaymentItem,
    RequiredFields,
    _BaseModel,
    _RequestModel,
)


class _OperationBase(_BaseModel):
    """Shared fields for payment/authorization operation objects within checkout."""

    id: str | None = None
    amount: Decimal | None = None
    amount_net: Decimal | None = None
    currency: str | None = None
    type: OperationType | str | None = None
    channel: str | None = None
    status: OperationStatus | str | None = None
    date: datetime | str | None = None
    modified_date: datetime | str | None = None
    ipaddress: str | None = None
    fee: Decimal | None = None
    refundable: bool | None = None
    client: ClientInfo | None = None
    merchant: Merchant | None = None
    items: list[PaymentItem] | None = None
    method: PaymentMethod | str | None = None
    card: CreditCard | None = None
    mb: MBReference | None = None
    notes: str | None = None
    user_notes: str | None = None
    ext_invoiceid: str | None = None
    ext_customerid: str | None = None
    ext_email: str | None = None
    ext_employee: str | None = None
    request_id: str | None = None
    expires: datetime | str | None = None
    instant: bool | None = None
    operation_id: str | None = None


class PaymentBody(_RequestModel):
    """Payment data for checkout creation request.

    This is the ``payment`` key in the checkout request body.
    """

    amount: Decimal = Field(..., ge=Decimal("0.001"), le=Decimal("99999.99"))
    currency: str = "EUR"
    client: ClientInfo | dict[str, Any] | None = None
    items: list[PaymentItem | dict[str, Any]] | None = None
    ext_invoiceid: str | None = Field(None, max_length=45)
    ext_customerid: str | None = Field(None, max_length=45)
    ext_email: str | None = Field(None, max_length=100)
    ext_employee: str | None = Field(None, max_length=45)
    ipaddress: str | None = None
    notes: str | None = None
    store: int | None = None
    expires: str | None = None
    instant: bool | None = None
    request_id: str | None = None


class AuthorizationBody(_RequestModel):
    """Authorization data for checkout creation request.

    This is the ``authorization`` key in the checkout request body.
    """

    amount: Decimal = Field(..., ge=Decimal("0.001"), le=Decimal("99999.99"))
    currency: str = "EUR"
    client: ClientInfo | dict[str, Any] | None = None
    items: list[PaymentItem | dict[str, Any]] | None = None
    ext_invoiceid: str | None = Field(None, max_length=45)
    ext_customerid: str | None = Field(None, max_length=45)
    ext_email: str | None = Field(None, max_length=100)
    ext_employee: str | None = Field(None, max_length=45)
    ipaddress: str | None = None
    notes: str | None = None
    expires: str | None = None
    request_id: str | None = None


class CheckoutRequest(_RequestModel):
    """Full checkout creation request body sent to POST /api/v2/checkout."""

    payment: PaymentBody | None = None
    authorization: AuthorizationBody | None = None
    url_confirm: str
    url_cancel: str
    exclude: list[str] | None = None
    required_fields: RequiredFields | None = None
    default_method: str | None = None
    request_id: str | None = None


class CheckoutResponse(_BaseModel):
    """Response from checkout creation or retrieval."""

    id: str | None = None
    url_confirm: str | None = None
    url_cancel: str | None = None
    url_redirect: str | None = None
    exclude: list[str] | None = None
    shipping: bool | None = None
    payment: _OperationBase | None = None
    authorization: _OperationBase | None = None
    required_fields: RequiredFields | None = None
