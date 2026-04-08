"""Synchronous MEO Wallet client."""

from __future__ import annotations

from typing import Any

from meowallet._base_client import build_config
from meowallet.config import (
    DEFAULT_RETRY,
    DEFAULT_TIMEOUT,
    Environment,
    EventHook,
    RetryConfig,
)
from meowallet.resources.authorizations import Authorizations
from meowallet.resources.callbacks import Callbacks
from meowallet.resources.checkouts import Checkouts
from meowallet.resources.mb import MB, MBWay
from meowallet.resources.operations import Operations
from meowallet.resources.requests import Requests
from meowallet.resources.subscriptions import Subscriptions
from meowallet.resources.wallets import Wallets
from meowallet.transport import SyncTransport


class MeoWalletClient:
    """Synchronous client for the MEO Wallet payment API.

    Usage::

        client = MeoWalletClient(api_key="your-key", environment=Environment.SANDBOX)
        checkout = client.checkouts.create_payment(
            amount=10.0,
            currency="EUR",
            items=[{"name": "Item", "qt": 1}],
            url_confirm="https://example.com/confirm",
            url_cancel="https://example.com/cancel",
        )

    Or as a context manager::

        with MeoWalletClient(api_key="your-key") as client:
            methods = client.wallets.list_methods()
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        environment: Environment = Environment.SANDBOX,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        retry: RetryConfig = DEFAULT_RETRY,
        extra_headers: dict[str, str] | None = None,
        event_hooks: dict[str, list[EventHook]] | None = None,
    ) -> None:
        config = build_config(
            api_key,
            environment=environment,
            base_url=base_url,
            timeout=timeout,
            retry=retry,
            extra_headers=extra_headers,
            event_hooks=event_hooks,
        )
        self._transport = SyncTransport(config)

        self.checkouts = Checkouts(self._transport)
        self.operations = Operations(self._transport)
        self.authorizations = Authorizations(self._transport)
        self.subscriptions = Subscriptions(self._transport)
        self.wallets = Wallets(self._transport)
        self.requests = Requests(self._transport)
        self.callbacks = Callbacks(self._transport)
        self.mb = MB(self._transport)
        self.mbway = MBWay(self._transport)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._transport.close()

    def __enter__(self) -> MeoWalletClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
