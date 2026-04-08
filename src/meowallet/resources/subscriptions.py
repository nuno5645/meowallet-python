"""Subscriptions resource: create, list, get, cancel, charge."""

from __future__ import annotations

import json
from typing import Any

from meowallet.models.checkout import PaymentBody
from meowallet.models.subscription import (
    ChargeOrder,
    ChargeOrderList,
    ChargeRequest,
    Subscription,
    SubscriptionBody,
    SubscriptionCheckoutResponse,
    SubscriptionList,
)
from meowallet.resources._base import BaseAsyncResource, BaseSyncResource

_CHECKOUT_PATH = "/api/v2/checkout"
_SUBS_PATH = "/api/v2/subscriptions"


def _build_sub_checkout(
    subscription: SubscriptionBody,
    url_confirm: str,
    url_cancel: str,
    payment: PaymentBody | None,
    request_id: str | None,
) -> bytes:
    """Build the raw JSON for a subscription checkout request."""
    data: dict[str, Any] = {
        "subscription": subscription.to_api_dict(),
        "url_confirm": url_confirm,
        "url_cancel": url_cancel,
    }
    if payment is not None:
        data["payment"] = payment.to_api_dict()
    if request_id is not None:
        data["request_id"] = request_id
    return json.dumps(data).encode()


def _build_charge(charge: ChargeRequest) -> bytes:
    """Build the raw JSON for a charge request (wrapped in payment key)."""
    return json.dumps({"payment": charge.to_api_dict()}).encode()


class Subscriptions(BaseSyncResource):
    """Synchronous subscription management."""

    def create(
        self,
        body: SubscriptionBody | None = None,
        /,
        *,
        url_confirm: str,
        url_cancel: str,
        payment: PaymentBody | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> SubscriptionCheckoutResponse:
        """Create a subscription via checkout.

        Pass subscription data as a ``SubscriptionBody`` or kwargs
        (amount, currency, frequency, period, start_date, etc.).

        Optionally include ``payment`` for a combined initial payment + subscription.
        """
        if body is not None and kwargs:
            raise TypeError("Pass either a SubscriptionBody or keyword arguments, not both.")
        subscription = body if body is not None else SubscriptionBody.model_validate(kwargs)
        raw = _build_sub_checkout(subscription, url_confirm, url_cancel, payment, request_id)
        return self._transport.request(  # type: ignore[return-value]
            "POST",
            _CHECKOUT_PATH,
            raw_body=raw,
            response_model=SubscriptionCheckoutResponse,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> SubscriptionList:
        """List subscriptions."""
        return self._get(  # type: ignore[no-any-return]
            _SUBS_PATH,
            params={"limit": limit, "offset": offset},
            response_model=SubscriptionList,
        )

    def get(self, subscription_id: str) -> Subscription:
        """Get a single subscription."""
        return self._get(f"{_SUBS_PATH}/{subscription_id}", response_model=Subscription)  # type: ignore[no-any-return]

    def cancel(self, subscription_id: str) -> Subscription:
        """Cancel a subscription (status → VOIDED)."""
        return self._delete(f"{_SUBS_PATH}/{subscription_id}", response_model=Subscription)  # type: ignore[no-any-return]

    def charge(
        self,
        subscription_id: str,
        body: ChargeRequest | None = None,
        /,
        **kwargs: Any,
    ) -> ChargeOrder:
        """Create a charge against a subscription."""
        if body is not None and kwargs:
            raise TypeError("Pass either a ChargeRequest or keyword arguments, not both.")
        charge_body = body if body is not None else ChargeRequest.model_validate(kwargs)
        raw = _build_charge(charge_body)
        return self._transport.request(  # type: ignore[return-value]
            "POST",
            f"{_SUBS_PATH}/{subscription_id}/charge",
            raw_body=raw,
            response_model=ChargeOrder,
        )

    def list_charges(
        self,
        subscription_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ChargeOrderList:
        """List charges for a subscription."""
        return self._get(  # type: ignore[no-any-return]
            f"{_SUBS_PATH}/{subscription_id}/charge",
            params={"limit": limit, "offset": offset},
            response_model=ChargeOrderList,
        )

    def get_charge(self, subscription_id: str, charge_id: str) -> ChargeOrder:
        """Get a single charge."""
        return self._get(  # type: ignore[no-any-return]
            f"{_SUBS_PATH}/{subscription_id}/charge/{charge_id}",
            response_model=ChargeOrder,
        )


class AsyncSubscriptions(BaseAsyncResource):
    """Asynchronous subscription management."""

    async def create(
        self,
        body: SubscriptionBody | None = None,
        /,
        *,
        url_confirm: str,
        url_cancel: str,
        payment: PaymentBody | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> SubscriptionCheckoutResponse:
        """Create a subscription via checkout."""
        if body is not None and kwargs:
            raise TypeError("Pass either a SubscriptionBody or keyword arguments, not both.")
        subscription = body if body is not None else SubscriptionBody.model_validate(kwargs)
        raw = _build_sub_checkout(subscription, url_confirm, url_cancel, payment, request_id)
        return await self._transport.request(  # type: ignore[return-value]
            "POST",
            _CHECKOUT_PATH,
            raw_body=raw,
            response_model=SubscriptionCheckoutResponse,
        )

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> SubscriptionList:
        """List subscriptions."""
        return await self._get(  # type: ignore[no-any-return]
            _SUBS_PATH,
            params={"limit": limit, "offset": offset},
            response_model=SubscriptionList,
        )

    async def get(self, subscription_id: str) -> Subscription:
        """Get a single subscription."""
        return await self._get(f"{_SUBS_PATH}/{subscription_id}", response_model=Subscription)  # type: ignore[no-any-return]

    async def cancel(self, subscription_id: str) -> Subscription:
        """Cancel a subscription."""
        return await self._delete(f"{_SUBS_PATH}/{subscription_id}", response_model=Subscription)  # type: ignore[no-any-return]

    async def charge(
        self,
        subscription_id: str,
        body: ChargeRequest | None = None,
        /,
        **kwargs: Any,
    ) -> ChargeOrder:
        """Create a charge against a subscription."""
        if body is not None and kwargs:
            raise TypeError("Pass either a ChargeRequest or keyword arguments, not both.")
        charge_body = body if body is not None else ChargeRequest.model_validate(kwargs)
        raw = _build_charge(charge_body)
        return await self._transport.request(  # type: ignore[return-value]
            "POST",
            f"{_SUBS_PATH}/{subscription_id}/charge",
            raw_body=raw,
            response_model=ChargeOrder,
        )

    async def list_charges(
        self,
        subscription_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ChargeOrderList:
        """List charges for a subscription."""
        return await self._get(  # type: ignore[no-any-return]
            f"{_SUBS_PATH}/{subscription_id}/charge",
            params={"limit": limit, "offset": offset},
            response_model=ChargeOrderList,
        )

    async def get_charge(self, subscription_id: str, charge_id: str) -> ChargeOrder:
        """Get a single charge."""
        return await self._get(  # type: ignore[no-any-return]
            f"{_SUBS_PATH}/{subscription_id}/charge/{charge_id}",
            response_model=ChargeOrder,
        )
