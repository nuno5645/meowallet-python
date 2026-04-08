"""Authorization models with captures and releases."""

from __future__ import annotations

from pydantic import Field

from meowallet.models.common import _BaseModel
from meowallet.models.operation import Operation


class Authorization(Operation):
    """An authorization operation with its captures and releases history."""

    captures: list[Operation] | None = None
    releases: list[Operation] | None = None


class AuthorizationList(_BaseModel):
    """Paginated list of authorizations."""

    total: int = 0
    elements: list[Authorization] = Field(default_factory=list)
