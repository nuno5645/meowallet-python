"""Shared client configuration logic."""

from __future__ import annotations

from meowallet.config import (
    DEFAULT_RETRY,
    DEFAULT_TIMEOUT,
    ClientConfig,
    Environment,
    EventHook,
    RetryConfig,
)
from meowallet.exceptions import ConfigurationError


def build_config(
    api_key: str | None,
    *,
    environment: Environment = Environment.SANDBOX,
    base_url: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    retry: RetryConfig = DEFAULT_RETRY,
    extra_headers: dict[str, str] | None = None,
    event_hooks: dict[str, list[EventHook]] | None = None,
) -> ClientConfig:
    """Validate inputs and build a ClientConfig."""
    resolved_key = api_key
    if resolved_key is None:
        import os

        resolved_key = os.environ.get("MEOWALLET_API_KEY")

    if not resolved_key:
        raise ConfigurationError(
            "API key is required. Pass api_key= or set the MEOWALLET_API_KEY environment variable."
        )

    return ClientConfig(
        api_key=resolved_key,
        environment=environment,
        base_url=base_url,
        timeout=timeout,
        retry=retry,
        extra_headers=extra_headers or {},
        event_hooks=event_hooks or {},
    )
