"""Callback/webhook payload model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import field_validator

from meowallet.models.common import _BaseModel


def _parse_timestamp(v: object) -> datetime | None:
    """Parse MEO Wallet timestamp formats into datetime.

    Accepts ISO 8601 formats like '2026-04-07T23:18:54+0000'.
    Returns None for None/empty values.
    """
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        # MEO Wallet uses +0000 format (no colon), normalize for fromisoformat
        s = v.strip()
        # Handle +0000 → +00:00
        if len(s) >= 5 and s[-5] in ("+", "-") and s[-4:].isdigit():
            s = s[:-2] + ":" + s[-2:]
        return datetime.fromisoformat(s)
    return None


class CallbackPayload(_BaseModel):
    """Payload delivered by MEO Wallet to merchant callback endpoints.

    Timestamps are parsed into datetime objects. If parsing fails,
    a ValidationError is raised rather than silently accepting strings.
    """

    amount: Decimal | None = None
    create_date: datetime | None = None
    currency: str | None = None
    event: str | None = None
    ext_customerid: str | None = None
    ext_invoiceid: str | None = None
    ext_email: str | None = None
    method: str | None = None
    modified_date: datetime | None = None
    operation_id: str | None = None
    operation_status: str | None = None
    user: int | str | None = None

    # Optional fields
    error: str | None = None
    type: str | None = None
    checkout_id: str | None = None
    mb_entity: str | None = None
    mb_ref: str | None = None
    mandate_id: str | None = None
    mandate_status: str | None = None
    dd_status_code: str | None = None
    parent_operation_id: str | None = None

    @field_validator("create_date", "modified_date", mode="before")
    @classmethod
    def _parse_dates(cls, v: object) -> datetime | None:
        return _parse_timestamp(v)
