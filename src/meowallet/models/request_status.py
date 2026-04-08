"""Request status model for idempotency lookups."""

from __future__ import annotations

from meowallet.models.common import _BaseModel


class RequestStatus(_BaseModel):
    """Response from GET /api/v2/requests/{uuid}.

    Attributes:
        href: URL to the operation resource.
        status: Operation state (e.g. COMPLETED).
        method: HTTP method used for the original request.
    """

    href: str | None = None
    status: str | None = None
    method: str | None = None
