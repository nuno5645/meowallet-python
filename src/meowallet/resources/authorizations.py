"""Authorizations resource: list, get, capture, and release."""

from __future__ import annotations

from typing import Any

from meowallet._utils import resolve_body
from meowallet.models.authorization import Authorization, AuthorizationList
from meowallet.models.operation import CaptureRequest, Operation, ReleaseRequest
from meowallet.resources._base import BaseAsyncResource, BaseSyncResource

_PATH = "/api/v2/authorizations"


class Authorizations(BaseSyncResource):
    """Synchronous authorization management."""

    def list(
        self,
        *,
        id: str | None = None,
        startdate: str | None = None,
        enddate: str | None = None,
        method: str | None = None,
        number4: int | None = None,
        phone: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        ext_invoiceid: str | None = None,
    ) -> AuthorizationList:
        """List authorizations with optional filters.

        Args:
            id: Filter by authorization ID.
            startdate: Start date filter (yyyy-mm-dd).
            enddate: End date filter (yyyy-mm-dd).
            method: Filter by payment method (CC, MBWAY).
            number4: Last 4 credit card digits.
            phone: Mobile number for MBWAY.
            offset: Pagination page number.
            limit: Records per page (max 30).
            ext_invoiceid: Merchant invoice reference.
        """
        params: dict[str, Any] = {
            "id": id,
            "startdate": startdate,
            "enddate": enddate,
            "method": method,
            "number4": number4,
            "phone": phone,
            "offset": offset,
            "limit": limit,
            "ext_invoiceid": ext_invoiceid,
        }
        return self._get(_PATH, params=params, response_model=AuthorizationList)  # type: ignore[no-any-return]

    def get(self, authorization_id: str) -> Authorization:
        """Retrieve a single authorization with its captures and releases."""
        return self._get(f"{_PATH}/{authorization_id}", response_model=Authorization)  # type: ignore[no-any-return]

    def capture(
        self,
        authorization_id: str,
        body: CaptureRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Capture an authorized amount.

        Omit amount to capture the full authorized amount.
        Up to 10 partial captures are allowed.
        """
        capture_body = resolve_body(CaptureRequest, body, kwargs)
        if capture_body is None:
            capture_body = CaptureRequest()
        return self._post(  # type: ignore[no-any-return]
            f"{_PATH}/{authorization_id}/capture",
            body=capture_body,
            response_model=Operation,
        )

    def release(
        self,
        authorization_id: str,
        body: ReleaseRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Release an authorized amount.

        Omit amount to release the full authorized amount.
        Cannot release after a capture has been made.
        """
        release_body = resolve_body(ReleaseRequest, body, kwargs)
        if release_body is None:
            release_body = ReleaseRequest()
        return self._post(  # type: ignore[no-any-return]
            f"{_PATH}/{authorization_id}/release",
            body=release_body,
            response_model=Operation,
        )


class AsyncAuthorizations(BaseAsyncResource):
    """Asynchronous authorization management."""

    async def list(
        self,
        *,
        id: str | None = None,
        startdate: str | None = None,
        enddate: str | None = None,
        method: str | None = None,
        number4: int | None = None,
        phone: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        ext_invoiceid: str | None = None,
    ) -> AuthorizationList:
        """List authorizations with optional filters."""
        params: dict[str, Any] = {
            "id": id,
            "startdate": startdate,
            "enddate": enddate,
            "method": method,
            "number4": number4,
            "phone": phone,
            "offset": offset,
            "limit": limit,
            "ext_invoiceid": ext_invoiceid,
        }
        return await self._get(_PATH, params=params, response_model=AuthorizationList)  # type: ignore[no-any-return]

    async def get(self, authorization_id: str) -> Authorization:
        """Retrieve a single authorization with its captures and releases."""
        return await self._get(f"{_PATH}/{authorization_id}", response_model=Authorization)  # type: ignore[no-any-return]

    async def capture(
        self,
        authorization_id: str,
        body: CaptureRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Capture an authorized amount."""
        capture_body = resolve_body(CaptureRequest, body, kwargs)
        if capture_body is None:
            capture_body = CaptureRequest()
        return await self._post(  # type: ignore[no-any-return]
            f"{_PATH}/{authorization_id}/capture",
            body=capture_body,
            response_model=Operation,
        )

    async def release(
        self,
        authorization_id: str,
        body: ReleaseRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Release an authorized amount."""
        release_body = resolve_body(ReleaseRequest, body, kwargs)
        if release_body is None:
            release_body = ReleaseRequest()
        return await self._post(  # type: ignore[no-any-return]
            f"{_PATH}/{authorization_id}/release",
            body=release_body,
            response_model=Operation,
        )
