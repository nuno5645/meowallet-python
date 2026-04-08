"""HTTP transport layer wrapping httpx with retry logic and error mapping."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from meowallet._logging import logger, mask_key
from meowallet._retry import RetryPolicy
from meowallet.config import USER_AGENT, ClientConfig
from meowallet.exceptions import (
    APIError,
    TransportError,
    raise_for_status,
)
from meowallet.exceptions import (
    ConnectionError as MeoConnectionError,
)
from meowallet.exceptions import (
    TimeoutError as MeoTimeoutError,
)

T = TypeVar("T", bound=BaseModel)


def _build_headers(config: ClientConfig) -> dict[str, str]:
    """Build default headers from config."""
    headers = {
        "Authorization": f"WalletPT {config.api_key}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    headers.update(config.extra_headers)
    return headers


class SyncTransport:
    """Synchronous HTTP transport with retry support."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._retry = RetryPolicy(config.retry)
        self._client = httpx.Client(
            base_url=config.effective_base_url,
            headers=_build_headers(config),
            timeout=config.timeout,
            event_hooks=config.event_hooks if config.event_hooks else {},
        )
        logger.debug(
            "SyncTransport initialized: base_url=%s, key=%s",
            config.effective_base_url,
            mask_key(config.api_key),
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        body: BaseModel | None = None,
        raw_body: bytes | None = None,
        params: dict[str, Any] | None = None,
        response_model: type[T] | None = None,
    ) -> T | dict[str, Any] | str | None:
        """Send an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, DELETE).
            path: URL path (e.g., "/api/v2/checkout").
            body: Pydantic model to serialize as JSON body.
            raw_body: Raw bytes to send as body (for callback verify).
            params: Query parameters.
            response_model: Pydantic model to parse response into.

        Returns:
            Parsed response model, raw dict, string, or None for 204.
        """
        json_body: dict[str, Any] | None = None
        content: bytes | None = None

        if body is not None:
            if hasattr(body, "to_api_dict"):
                json_body = body.to_api_dict()
            else:
                json_body = body.model_dump(exclude_none=True, mode="python")
        if raw_body is not None:
            content = raw_body

        last_exception: Exception | None = None

        for attempt in range(self._retry.max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    path,
                    json=json_body if content is None else None,
                    content=content,
                    params=_clean_params(params),
                )

                # Check for errors
                try:
                    raise_for_status(response.status_code, response.content)
                except APIError as exc:
                    api_code = exc.api_code
                    if self._retry.should_retry(
                        method=method,
                        status_code=response.status_code,
                        api_code=api_code,
                        attempt=attempt,
                        is_transport_error=False,
                        request_body=json_body,
                    ):
                        last_exception = exc
                        delay = self._retry.get_delay(attempt)
                        logger.debug("Sleeping %.2fs before retry", delay)
                        time.sleep(delay)
                        continue
                    raise

                return _parse_response(response, response_model)

            except httpx.HTTPError as exc:
                transport_exc: TransportError
                if isinstance(exc, httpx.TimeoutException):
                    transport_exc = MeoTimeoutError(str(exc), original=exc)
                elif isinstance(exc, httpx.ConnectError):
                    transport_exc = MeoConnectionError(str(exc), original=exc)
                else:
                    transport_exc = TransportError(str(exc), original=exc)

                if self._retry.should_retry(
                    method=method,
                    status_code=None,
                    api_code=None,
                    attempt=attempt,
                    is_transport_error=True,
                    request_body=json_body,
                ):
                    last_exception = transport_exc
                    delay = self._retry.get_delay(attempt)
                    logger.debug("Sleeping %.2fs before retry (transport error)", delay)
                    time.sleep(delay)
                    continue
                raise transport_exc from exc

        # All retries exhausted
        if last_exception is not None:
            raise last_exception
        raise TransportError("All retries exhausted")  # pragma: no cover

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()


class AsyncTransport:
    """Asynchronous HTTP transport with retry support."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._retry = RetryPolicy(config.retry)
        self._client = httpx.AsyncClient(
            base_url=config.effective_base_url,
            headers=_build_headers(config),
            timeout=config.timeout,
            event_hooks=config.event_hooks if config.event_hooks else {},
        )
        logger.debug(
            "AsyncTransport initialized: base_url=%s, key=%s",
            config.effective_base_url,
            mask_key(config.api_key),
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        body: BaseModel | None = None,
        raw_body: bytes | None = None,
        params: dict[str, Any] | None = None,
        response_model: type[T] | None = None,
    ) -> T | dict[str, Any] | str | None:
        """Send an async HTTP request with retry logic."""
        json_body: dict[str, Any] | None = None
        content: bytes | None = None

        if body is not None:
            if hasattr(body, "to_api_dict"):
                json_body = body.to_api_dict()
            else:
                json_body = body.model_dump(exclude_none=True, mode="python")
        if raw_body is not None:
            content = raw_body

        last_exception: Exception | None = None

        for attempt in range(self._retry.max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    path,
                    json=json_body if content is None else None,
                    content=content,
                    params=_clean_params(params),
                )

                try:
                    raise_for_status(response.status_code, response.content)
                except APIError as exc:
                    api_code = exc.api_code
                    if self._retry.should_retry(
                        method=method,
                        status_code=response.status_code,
                        api_code=api_code,
                        attempt=attempt,
                        is_transport_error=False,
                        request_body=json_body,
                    ):
                        last_exception = exc
                        delay = self._retry.get_delay(attempt)
                        await asyncio.sleep(delay)
                        continue
                    raise

                return _parse_response(response, response_model)

            except httpx.HTTPError as exc:
                transport_exc: TransportError
                if isinstance(exc, httpx.TimeoutException):
                    transport_exc = MeoTimeoutError(str(exc), original=exc)
                elif isinstance(exc, httpx.ConnectError):
                    transport_exc = MeoConnectionError(str(exc), original=exc)
                else:
                    transport_exc = TransportError(str(exc), original=exc)

                if self._retry.should_retry(
                    method=method,
                    status_code=None,
                    api_code=None,
                    attempt=attempt,
                    is_transport_error=True,
                    request_body=json_body,
                ):
                    last_exception = transport_exc
                    delay = self._retry.get_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
                raise transport_exc from exc

        if last_exception is not None:
            raise last_exception
        raise TransportError("All retries exhausted")  # pragma: no cover

    async def close(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()


def _parse_response(
    response: httpx.Response, response_model: type[T] | None
) -> T | dict[str, Any] | str | None:
    """Parse a successful HTTP response."""
    if response.status_code == 204:
        return None

    text = response.text.strip()

    # Callback verify returns bare "true" or "false"
    if text in ('"true"', '"false"', "true", "false"):
        return text.strip('"')

    if response_model is not None:
        try:
            data = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise TransportError(
                f"Failed to decode JSON from {response.status_code} response"
                f" (body={response.content[:200]!r})",
                original=exc,
            ) from exc
        try:
            return response_model.model_validate(data)
        except PydanticValidationError as exc:
            raise TransportError(
                f"Failed to parse response into {response_model.__name__}: {exc}",
                original=exc,
            ) from exc

    try:
        return response.json()  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        return text


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove None values from query parameters."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}
