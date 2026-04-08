"""Common data structures shared across the MEO Wallet API."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def _walk_decimals(obj: Any) -> Any:
    """Recursively convert Decimal values to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _walk_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk_decimals(item) for item in obj]
    return obj


class _BaseModel(BaseModel):
    """Response base model with forward-compatible extra field handling.

    Uses ``extra="allow"`` so unknown fields from the API are preserved
    rather than rejected.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    def to_api_dict(self) -> dict[str, Any]:
        """Serialize to dict suitable for API requests (Decimals as floats, no Nones)."""
        data = self.model_dump(exclude_none=True, mode="python")
        result = _walk_decimals(data)
        assert isinstance(result, dict)
        return result


class _RequestModel(BaseModel):
    """Request base model with strict field validation.

    Uses ``extra="forbid"`` so misspelled kwargs fail fast locally instead
    of being silently sent to the API.
    """

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    def to_api_dict(self) -> dict[str, Any]:
        """Serialize to dict suitable for API requests (Decimals as floats, no Nones)."""
        data = self.model_dump(exclude_none=True, mode="python")
        result = _walk_decimals(data)
        assert isinstance(result, dict)
        return result


class Address(_BaseModel):
    """Postal address structure."""

    address: str | None = Field(None, min_length=2, max_length=255)
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=2, description="ISO 3166-1 alpha-2")
    postalcode: str | None = Field(None, max_length=15)


class ClientInfo(_BaseModel):
    """Client/payer information."""

    name: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=250)
    phone: str | None = Field(None, description="E.164 format")
    nif: str | None = Field(None, max_length=255, description="Fiscal number")
    address: Address | None = None


class CreditCard(_BaseModel):
    """Credit card details (output only, tokenized)."""

    token: str | None = None
    last4: str | None = None
    type: str | None = None
    valdate: str | None = Field(None, description="Expiration in MM/YYYY format")
    expired: bool | None = None


class MBReference(_BaseModel):
    """Multibanco payment reference."""

    entity: str | None = None
    ref: str | None = None


class Merchant(_BaseModel):
    """Merchant/transaction recipient information."""

    id: int | str | None = None
    name: str | None = None
    email: str | None = None


class PaymentItem(_BaseModel):
    """Invoice line item for checkout display."""

    name: str = Field(..., max_length=500)
    qt: int = Field(..., ge=1, le=2147483648)
    descr: str | None = Field(None, max_length=255)
    ref: str | None = Field(None, max_length=100)
    amount: Decimal | None = Field(None, ge=Decimal("0.001"), le=Decimal("99999.99"))


class RequiredFields(_BaseModel):
    """Boolean flags controlling which fields are required during checkout."""

    email: bool | None = None
    name: bool | None = None
    phone: bool | None = None
    shipping: bool | None = None


class User(_BaseModel):
    """MEO Wallet user descriptor."""

    email: str | None = None
    name: str | None = None
