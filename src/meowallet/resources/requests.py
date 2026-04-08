"""Requests resource: idempotency key status lookup."""

from __future__ import annotations

from meowallet.models.request_status import RequestStatus
from meowallet.resources._base import BaseAsyncResource, BaseSyncResource

_PATH = "/api/v2/requests"


class Requests(BaseSyncResource):
    """Synchronous request status lookups."""

    def get(self, request_id: str) -> RequestStatus:
        """Look up the status of a previously submitted request by its UUID.

        Useful for recovering from errors when the outcome of a request is unknown.
        """
        return self._get(f"{_PATH}/{request_id}", response_model=RequestStatus)  # type: ignore[no-any-return]


class AsyncRequests(BaseAsyncResource):
    """Asynchronous request status lookups."""

    async def get(self, request_id: str) -> RequestStatus:
        """Look up the status of a previously submitted request by its UUID."""
        return await self._get(f"{_PATH}/{request_id}", response_model=RequestStatus)  # type: ignore[no-any-return]
