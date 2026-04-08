"""Error response model from MEO Wallet API."""

from __future__ import annotations

from pydantic import ConfigDict

from meowallet.models.common import _BaseModel


class ErrorResponse(_BaseModel):
    """Structured error payload returned by the MEO Wallet API.

    Fields:
        code: Numeric error code (10xxx=technical, 20xxx=auth, 30xxx/40xxx=payment).
        message: Brief error description.
        reason: Human-readable explanation.
        link: Documentation URL for the error.
        tid: Transaction/error GUID for support reference.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    code: int | None = None
    message: str | None = None
    reason: str | None = None
    link: str | None = None
    tid: str | None = None
