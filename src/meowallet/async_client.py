"""Asynchronous MEO Wallet client."""

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
from meowallet.resources.authorizations import AsyncAuthorizations
from meowallet.resources.callbacks import AsyncCallbacks
from meowallet.resources.checkouts import AsyncCheckouts
from meowallet.resources.mb import AsyncMB, AsyncMBWay
from meowallet.resources.operations import AsyncOperations
from meowallet.resources.requests import AsyncRequests
from meowallet.resources.subscriptions import AsyncSubscriptions
from meowallet.resources.wallets import AsyncWallets
from meowallet.transport import AsyncTransport


class AsyncMeoWalletClient:
    """Asynchronous client for the MEO Wallet payment API.

    Usage::

        async with AsyncMeoWalletClient(api_key="your-key") as client:
            checkout = await client.checkouts.create_payment(
                amount=10.0,
                currency="EUR",
                items=[{"name": "Item", "qt": 1}],
                url_confirm="https://example.com/confirm",
                url_cancel="https://example.com/cancel",
            )
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
        self._transport = AsyncTransport(config)

        self.checkouts = AsyncCheckouts(self._transport)
        self.operations = AsyncOperations(self._transport)
        self.authorizations = AsyncAuthorizations(self._transport)
        self.subscriptions = AsyncSubscriptions(self._transport)
        self.wallets = AsyncWallets(self._transport)
        self.requests = AsyncRequests(self._transport)
        self.callbacks = AsyncCallbacks(self._transport)
        self.mb = AsyncMB(self._transport)
        self.mbway = AsyncMBWay(self._transport)

    async def close(self) -> None:
        """Close the underlying async HTTP connection pool."""
        await self._transport.close()

    async def __aenter__(self) -> AsyncMeoWalletClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
