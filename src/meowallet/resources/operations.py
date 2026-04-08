"""Operations resource: list, get, and refund operations."""

from __future__ import annotations

from typing import Any

from meowallet._utils import resolve_body
from meowallet.models.operation import Operation, OperationList, RefundRequest
from meowallet.resources._base import BaseAsyncResource, BaseSyncResource

_PATH = "/api/v2/operations"


class Operations(BaseSyncResource):
    """Synchronous operation management."""

    def list(
        self,
        *,
        id: str | None = None,
        method: str | None = None,
        type: str | None = None,
        startdate: str | None = None,
        enddate: str | None = None,
        number4: int | None = None,
        mb_ref: int | None = None,
        phone: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        ext_invoiceid: str | None = None,
    ) -> OperationList:
        """List operations with optional filters.

        Args:
            id: Filter by operation ID.
            method: Filter by payment method (CC, MB, MBWAY, etc.).
            type: Filter by operation type.
            startdate: Start date filter (yyyy-mm-dd).
            enddate: End date filter (yyyy-mm-dd).
            number4: Last 4 credit card digits.
            mb_ref: Full Multibanco reference (9 digits).
            phone: Mobile number for MBWAY.
            offset: Pagination page number.
            limit: Records per page (max 30).
            ext_invoiceid: Merchant invoice reference.
        """
        params: dict[str, Any] = {
            "id": id,
            "method": method,
            "type": type,
            "startdate": startdate,
            "enddate": enddate,
            "number4": number4,
            "mb_ref": mb_ref,
            "phone": phone,
            "offset": offset,
            "limit": limit,
            "ext_invoiceid": ext_invoiceid,
        }
        return self._get(_PATH, params=params, response_model=OperationList)  # type: ignore[no-any-return]

    def get(self, operation_id: str) -> Operation:
        """Retrieve a single operation by ID."""
        return self._get(f"{_PATH}/{operation_id}", response_model=Operation)  # type: ignore[no-any-return]

    def refund(
        self,
        operation_id: str,
        body: RefundRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Refund an operation.

        Pass a ``RefundRequest`` or keyword arguments (type="full", amount=..., etc.).
        Defaults to a full refund if no arguments are provided.
        """
        refund_body = resolve_body(RefundRequest, body, kwargs)
        if refund_body is None:
            refund_body = RefundRequest()
        return self._post(  # type: ignore[no-any-return]
            f"{_PATH}/{operation_id}/refund",
            body=refund_body,
            response_model=Operation,
        )


class AsyncOperations(BaseAsyncResource):
    """Asynchronous operation management."""

    async def list(
        self,
        *,
        id: str | None = None,
        method: str | None = None,
        type: str | None = None,
        startdate: str | None = None,
        enddate: str | None = None,
        number4: int | None = None,
        mb_ref: int | None = None,
        phone: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        ext_invoiceid: str | None = None,
    ) -> OperationList:
        """List operations with optional filters."""
        params: dict[str, Any] = {
            "id": id,
            "method": method,
            "type": type,
            "startdate": startdate,
            "enddate": enddate,
            "number4": number4,
            "mb_ref": mb_ref,
            "phone": phone,
            "offset": offset,
            "limit": limit,
            "ext_invoiceid": ext_invoiceid,
        }
        return await self._get(_PATH, params=params, response_model=OperationList)  # type: ignore[no-any-return]

    async def get(self, operation_id: str) -> Operation:
        """Retrieve a single operation by ID."""
        return await self._get(f"{_PATH}/{operation_id}", response_model=Operation)  # type: ignore[no-any-return]

    async def refund(
        self,
        operation_id: str,
        body: RefundRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Refund an operation."""
        refund_body = resolve_body(RefundRequest, body, kwargs)
        if refund_body is None:
            refund_body = RefundRequest()
        return await self._post(  # type: ignore[no-any-return]
            f"{_PATH}/{operation_id}/refund",
            body=refund_body,
            response_model=Operation,
        )
