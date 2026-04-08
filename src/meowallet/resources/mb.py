"""MB references and MB WAY direct payment resources."""

from __future__ import annotations

import json
from typing import Any

from meowallet._utils import resolve_body
from meowallet.models.mb import (
    MBDeleteReferenceRequest,
    MBPaymentRequest,
    MBReferenceRequest,
    MBReferenceResponse,
    MBWayPaymentRequest,
)
from meowallet.models.operation import Operation
from meowallet.resources._base import BaseAsyncResource, BaseSyncResource

_MB_PAY_PATH = "/api/v2/mb/pay"
_MB_REF_PATH = "/api/v2/mb/reference"
_PAYMENT_PATH = "/api/v2/payment"


class MB(BaseSyncResource):
    """Synchronous Multibanco reference management."""

    def create_payment(
        self,
        body: MBPaymentRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Create an MB payment with a Multibanco reference.

        The response includes ``mb.entity`` and ``mb.ref`` for the customer to pay at ATM.
        """
        req = resolve_body(MBPaymentRequest, body, kwargs)
        if req is None:
            raise TypeError("Payment data is required.")
        return self._post(_MB_PAY_PATH, body=req, response_model=Operation)  # type: ignore[no-any-return]

    def create_reference(
        self,
        body: MBReferenceRequest | None = None,
        /,
        **kwargs: Any,
    ) -> MBReferenceResponse:
        """Create a recurring MB reference (accepts multiple payments within amount range)."""
        req = resolve_body(MBReferenceRequest, body, kwargs)
        if req is None:
            raise TypeError("Reference data is required.")
        return self._post(_MB_REF_PATH, body=req, response_model=MBReferenceResponse)  # type: ignore[no-any-return]

    def delete_reference(
        self,
        body: MBDeleteReferenceRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Any:
        """Delete a recurring MB reference. Instant references cannot be cancelled."""
        req = resolve_body(MBDeleteReferenceRequest, body, kwargs)
        if req is None:
            raise TypeError("Entity and ref are required.")
        # DELETE with body — send as raw JSON
        raw = json.dumps(req.to_api_dict()).encode()
        return self._transport.request("DELETE", _MB_REF_PATH, raw_body=raw)


class AsyncMB(BaseAsyncResource):
    """Asynchronous Multibanco reference management."""

    async def create_payment(
        self,
        body: MBPaymentRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Create an MB payment with a Multibanco reference."""
        req = resolve_body(MBPaymentRequest, body, kwargs)
        if req is None:
            raise TypeError("Payment data is required.")
        return await self._post(  # type: ignore[no-any-return]
            _MB_PAY_PATH,
            body=req,
            response_model=Operation,
        )

    async def create_reference(
        self,
        body: MBReferenceRequest | None = None,
        /,
        **kwargs: Any,
    ) -> MBReferenceResponse:
        """Create a recurring MB reference."""
        req = resolve_body(MBReferenceRequest, body, kwargs)
        if req is None:
            raise TypeError("Reference data is required.")
        return await self._post(  # type: ignore[no-any-return]
            _MB_REF_PATH,
            body=req,
            response_model=MBReferenceResponse,
        )

    async def delete_reference(
        self,
        body: MBDeleteReferenceRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Any:
        """Delete a recurring MB reference."""
        req = resolve_body(MBDeleteReferenceRequest, body, kwargs)
        if req is None:
            raise TypeError("Entity and ref are required.")
        raw = json.dumps(req.to_api_dict()).encode()
        return await self._transport.request("DELETE", _MB_REF_PATH, raw_body=raw)


class MBWay(BaseSyncResource):
    """Synchronous MB WAY direct payments (push notification to phone)."""

    def create_payment(
        self,
        body: MBWayPaymentRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Create an MB WAY payment.

        Sends push notification to the customer's phone.
        Status will be PENDING until the customer approves on their device.
        """
        req = resolve_body(MBWayPaymentRequest, body, kwargs)
        if req is None:
            raise TypeError("Payment data is required.")
        return self._post(  # type: ignore[no-any-return]
            _PAYMENT_PATH,
            body=req,
            response_model=Operation,
        )


class AsyncMBWay(BaseAsyncResource):
    """Asynchronous MB WAY direct payments."""

    async def create_payment(
        self,
        body: MBWayPaymentRequest | None = None,
        /,
        **kwargs: Any,
    ) -> Operation:
        """Create an MB WAY payment."""
        req = resolve_body(MBWayPaymentRequest, body, kwargs)
        if req is None:
            raise TypeError("Payment data is required.")
        return await self._post(  # type: ignore[no-any-return]
            _PAYMENT_PATH,
            body=req,
            response_model=Operation,
        )
