"""Checkout resource: create, get, and delete checkouts."""

from __future__ import annotations

from typing import Any

from meowallet.models.checkout import (
    AuthorizationBody,
    CheckoutRequest,
    CheckoutResponse,
    PaymentBody,
)
from meowallet.models.common import RequiredFields
from meowallet.resources._base import BaseAsyncResource, BaseSyncResource

_PATH = "/api/v2/checkout"


def _build_payment_checkout(
    body: PaymentBody | None,
    kwargs: dict[str, Any],
    url_confirm: str,
    url_cancel: str,
    exclude: list[str] | None,
    required_fields: RequiredFields | None,
    default_method: str | None,
    request_id: str | None,
) -> CheckoutRequest:
    """Build a CheckoutRequest for a payment checkout."""
    if body is not None and kwargs:
        raise TypeError("Pass either a PaymentBody instance or keyword arguments, not both.")
    payment = body if body is not None else PaymentBody.model_validate(kwargs)
    return CheckoutRequest(
        payment=payment,
        url_confirm=url_confirm,
        url_cancel=url_cancel,
        exclude=exclude,
        required_fields=required_fields,
        default_method=default_method,
        request_id=request_id,
    )


def _build_auth_checkout(
    body: AuthorizationBody | None,
    kwargs: dict[str, Any],
    url_confirm: str,
    url_cancel: str,
    exclude: list[str] | None,
    required_fields: RequiredFields | None,
    default_method: str | None,
    request_id: str | None,
) -> CheckoutRequest:
    """Build a CheckoutRequest for an authorization checkout."""
    if body is not None and kwargs:
        raise TypeError(
            "Pass either an AuthorizationBody instance or keyword arguments, not both."
        )
    authorization = body if body is not None else AuthorizationBody.model_validate(kwargs)
    return CheckoutRequest(
        authorization=authorization,
        url_confirm=url_confirm,
        url_cancel=url_cancel,
        exclude=exclude,
        required_fields=required_fields,
        default_method=default_method,
        request_id=request_id,
    )


class Checkouts(BaseSyncResource):
    """Synchronous checkout operations."""

    def create_payment(
        self,
        body: PaymentBody | None = None,
        /,
        *,
        url_confirm: str,
        url_cancel: str,
        exclude: list[str] | None = None,
        required_fields: RequiredFields | None = None,
        default_method: str | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> CheckoutResponse:
        """Create a payment checkout.

        Pass payment data as a ``PaymentBody`` instance or as keyword arguments
        (amount, currency, items, client, etc.).

        Args:
            request_id: UUID for idempotent checkout creation. Must be at the
                top level (not inside the payment body) for the API to honor it.
        """
        request = _build_payment_checkout(
            body,
            kwargs,
            url_confirm,
            url_cancel,
            exclude,
            required_fields,
            default_method,
            request_id,
        )
        return self._post(_PATH, body=request, response_model=CheckoutResponse)  # type: ignore[no-any-return]

    def create_authorization(
        self,
        body: AuthorizationBody | None = None,
        /,
        *,
        url_confirm: str,
        url_cancel: str,
        exclude: list[str] | None = None,
        required_fields: RequiredFields | None = None,
        default_method: str | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> CheckoutResponse:
        """Create an authorization checkout.

        Pass authorization data as an ``AuthorizationBody`` instance or as keyword arguments.
        """
        request = _build_auth_checkout(
            body,
            kwargs,
            url_confirm,
            url_cancel,
            exclude,
            required_fields,
            default_method,
            request_id,
        )
        return self._post(_PATH, body=request, response_model=CheckoutResponse)  # type: ignore[no-any-return]

    def get(self, checkout_id: str) -> CheckoutResponse:
        """Retrieve a checkout by ID."""
        return self._get(f"{_PATH}/{checkout_id}", response_model=CheckoutResponse)  # type: ignore[no-any-return]

    def delete(self, checkout_id: str) -> None:
        """Delete/void a checkout. Only works if the customer hasn't selected a method yet."""
        self._delete(f"{_PATH}/{checkout_id}")


class AsyncCheckouts(BaseAsyncResource):
    """Asynchronous checkout operations."""

    async def create_payment(
        self,
        body: PaymentBody | None = None,
        /,
        *,
        url_confirm: str,
        url_cancel: str,
        exclude: list[str] | None = None,
        required_fields: RequiredFields | None = None,
        default_method: str | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> CheckoutResponse:
        """Create a payment checkout."""
        request = _build_payment_checkout(
            body,
            kwargs,
            url_confirm,
            url_cancel,
            exclude,
            required_fields,
            default_method,
            request_id,
        )
        return await self._post(_PATH, body=request, response_model=CheckoutResponse)  # type: ignore[no-any-return]

    async def create_authorization(
        self,
        body: AuthorizationBody | None = None,
        /,
        *,
        url_confirm: str,
        url_cancel: str,
        exclude: list[str] | None = None,
        required_fields: RequiredFields | None = None,
        default_method: str | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> CheckoutResponse:
        """Create an authorization checkout."""
        request = _build_auth_checkout(
            body,
            kwargs,
            url_confirm,
            url_cancel,
            exclude,
            required_fields,
            default_method,
            request_id,
        )
        return await self._post(_PATH, body=request, response_model=CheckoutResponse)  # type: ignore[no-any-return]

    async def get(self, checkout_id: str) -> CheckoutResponse:
        """Retrieve a checkout by ID."""
        return await self._get(f"{_PATH}/{checkout_id}", response_model=CheckoutResponse)  # type: ignore[no-any-return]

    async def delete(self, checkout_id: str) -> None:
        """Delete/void a checkout."""
        await self._delete(f"{_PATH}/{checkout_id}")
