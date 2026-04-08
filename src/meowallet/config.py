"""Client configuration: environments, retry policy, and client settings."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from meowallet._logging import mask_key


class Environment(str, Enum):
    """MEO Wallet API environments."""

    SANDBOX = "https://services.sandbox.meowallet.pt"
    PRODUCTION = "https://services.wallet.pt"


@dataclass(frozen=True)
class RetryConfig:
    """Configuration for automatic request retries.

    Attributes:
        max_retries: Maximum number of retry attempts (0 to disable).
        backoff_base: Base delay in seconds for exponential backoff.
        backoff_factor: Multiplier applied per retry attempt.
        backoff_max: Maximum delay in seconds between retries.
        retryable_status_codes: HTTP status codes that trigger a retry.
        retryable_api_codes: MEO Wallet error codes that trigger a retry.
        retry_safe_methods: HTTP methods considered safe to always retry.
        retry_post_with_request_id: If True, POST requests with a request_id are retried.
    """

    max_retries: int = 3
    backoff_base: float = 0.5
    backoff_factor: float = 2.0
    backoff_max: float = 30.0
    retryable_status_codes: frozenset[int] = frozenset({500, 502, 503, 504})
    retryable_api_codes: frozenset[int] = frozenset({19999, 20008, 40021})
    retry_safe_methods: frozenset[str] = frozenset({"GET"})
    retry_post_with_request_id: bool = True


DEFAULT_RETRY = RetryConfig()
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "meowallet-python/0.1.0"


EventHook = Callable[..., Any]


@dataclass
class ClientConfig:
    """Full configuration for a MEO Wallet client.

    Attributes:
        api_key: Merchant API key.
        environment: SANDBOX or PRODUCTION.
        base_url: Override base URL (takes precedence over environment).
        timeout: Request timeout in seconds.
        retry: Retry configuration.
        extra_headers: Additional headers sent on every request.
        event_hooks: httpx-compatible event hooks dict.
    """

    api_key: str
    environment: Environment = Environment.SANDBOX
    base_url: str | None = None
    timeout: float = DEFAULT_TIMEOUT
    retry: RetryConfig = field(default_factory=lambda: DEFAULT_RETRY)
    extra_headers: dict[str, str] = field(default_factory=dict)
    event_hooks: dict[str, list[EventHook]] = field(default_factory=dict)

    @property
    def effective_base_url(self) -> str:
        """Resolve the base URL: explicit override or environment default."""
        return self.base_url if self.base_url is not None else self.environment.value

    def __repr__(self) -> str:
        return (
            f"ClientConfig(api_key='{mask_key(self.api_key)}', "
            f"environment={self.environment.name}, "
            f"base_url={self.base_url!r}, "
            f"timeout={self.timeout})"
        )
