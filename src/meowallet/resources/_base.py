"""Base resource classes providing HTTP convenience methods."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

from meowallet.transport import AsyncTransport, SyncTransport

T = TypeVar("T", bound=BaseModel)


class BaseSyncResource:
    """Base class for synchronous API resources."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        response_model: type[T] | None = None,
    ) -> Any:
        return self._transport.request("GET", path, params=params, response_model=response_model)

    def _post(
        self,
        path: str,
        *,
        body: BaseModel | None = None,
        raw_body: bytes | None = None,
        response_model: type[T] | None = None,
    ) -> Any:
        return self._transport.request(
            "POST", path, body=body, raw_body=raw_body, response_model=response_model
        )

    def _delete(
        self,
        path: str,
        *,
        response_model: type[T] | None = None,
    ) -> Any:
        return self._transport.request("DELETE", path, response_model=response_model)


class BaseAsyncResource:
    """Base class for asynchronous API resources."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        response_model: type[T] | None = None,
    ) -> Any:
        return await self._transport.request(
            "GET", path, params=params, response_model=response_model
        )

    async def _post(
        self,
        path: str,
        *,
        body: BaseModel | None = None,
        raw_body: bytes | None = None,
        response_model: type[T] | None = None,
    ) -> Any:
        return await self._transport.request(
            "POST", path, body=body, raw_body=raw_body, response_model=response_model
        )

    async def _delete(
        self,
        path: str,
        *,
        response_model: type[T] | None = None,
    ) -> Any:
        return await self._transport.request("DELETE", path, response_model=response_model)
