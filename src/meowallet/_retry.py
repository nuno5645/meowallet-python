"""Retry policy for MEO Wallet API requests.

Critical safety invariant: POST requests are NEVER retried unless a request_id
(idempotency key) is present in the request body. This prevents duplicate payments.
"""

from __future__ import annotations

import random
from typing import Any

from meowallet._logging import logger
from meowallet.config import RetryConfig


class RetryPolicy:
    """Determines whether a failed request should be retried."""

    def __init__(self, config: RetryConfig) -> None:
        self._config = config

    @property
    def max_retries(self) -> int:
        return self._config.max_retries

    def should_retry(
        self,
        *,
        method: str,
        status_code: int | None,
        api_code: int | None,
        attempt: int,
        is_transport_error: bool,
        request_body: dict[str, Any] | None,
    ) -> bool:
        """Decide whether to retry a failed request.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.).
            status_code: HTTP status code (None for transport errors).
            api_code: MEO Wallet error code from response body (None if unparseable).
            attempt: Current attempt number (0-indexed).
            is_transport_error: True for network-level failures (timeout, connection).
            request_body: Parsed request body dict (to check for request_id).

        Returns:
            True if the request should be retried.
        """
        if attempt >= self._config.max_retries:
            return False

        method_upper = method.upper()

        # Transport errors (timeout, connection reset) are always retried
        if is_transport_error:
            if self._is_safe_to_retry(method_upper, request_body):
                logger.debug("Retrying %s after transport error (attempt %d)", method, attempt + 1)
                return True
            logger.debug("Not retrying unsafe %s after transport error", method)
            return False

        # Check if the error is retryable
        is_retryable = False
        if status_code is not None and status_code in self._config.retryable_status_codes:
            is_retryable = True
        if api_code is not None and api_code in self._config.retryable_api_codes:
            is_retryable = True

        if not is_retryable:
            return False

        if self._is_safe_to_retry(method_upper, request_body):
            logger.debug(
                "Retrying %s (status=%s, code=%s, attempt %d)",
                method,
                status_code,
                api_code,
                attempt + 1,
            )
            return True

        logger.debug(
            "Not retrying unsafe %s without request_id (status=%s, code=%s)",
            method,
            status_code,
            api_code,
        )
        return False

    def _is_safe_to_retry(self, method: str, request_body: dict[str, Any] | None) -> bool:
        """Check if a request method is safe to retry.

        Safe means either:
        - The method is in the safe methods set (GET, DELETE), OR
        - The method is POST and the request body contains a request_id
        """
        if method in self._config.retry_safe_methods:
            return True
        return (
            method == "POST"
            and self._config.retry_post_with_request_id
            and request_body is not None
            and _has_request_id(request_body)
        )

    def get_delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry attempt with jitter."""
        delay = self._config.backoff_base * (self._config.backoff_factor**attempt)
        delay = min(delay, self._config.backoff_max)
        # Apply jitter: random factor between 0.5 and 1.5
        jitter = random.uniform(0.5, 1.5)
        return delay * jitter


def _has_request_id(body: dict[str, Any]) -> bool:
    """Check if a non-empty request_id is present in the body or nested payment/authorization.

    An empty string is NOT treated as a valid idempotency key.
    """
    rid = body.get("request_id")
    if isinstance(rid, str) and rid:
        return True
    for key in ("payment", "authorization"):
        nested = body.get(key)
        if isinstance(nested, dict):
            nested_rid = nested.get("request_id")
            if isinstance(nested_rid, str) and nested_rid:
                return True
    return False
