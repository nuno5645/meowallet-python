"""Wallets resource: list active payment methods."""

from __future__ import annotations

from typing import Any

from meowallet.resources._base import BaseAsyncResource, BaseSyncResource

_PATH = "/api/v2/wallets/methods"


def _extract_methods(data: Any) -> list[str]:
    """Extract the methods list from the API response, raising on unexpected shape."""
    if isinstance(data, dict) and "methods" in data:
        methods = data["methods"]
        if isinstance(methods, list):
            return methods
    msg = f"Unexpected response shape from {_PATH}: {type(data).__name__}"
    raise ValueError(msg)


class Wallets(BaseSyncResource):
    """Synchronous wallet operations."""

    def list_methods(self) -> list[str]:
        """List active payment methods for the authenticated wallet.

        Returns a list of method codes (e.g. ["CC", "MB", "WALLET"]).
        """
        return _extract_methods(self._get(_PATH))


class AsyncWallets(BaseAsyncResource):
    """Asynchronous wallet operations."""

    async def list_methods(self) -> list[str]:
        """List active payment methods for the authenticated wallet."""
        return _extract_methods(await self._get(_PATH))
