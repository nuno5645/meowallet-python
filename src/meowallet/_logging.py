"""Logging utilities with secret masking."""

from __future__ import annotations

import logging

logger = logging.getLogger("meowallet")


def mask_key(key: str) -> str:
    """Mask an API key for safe logging, showing first 4 and last 4 chars."""
    if len(key) <= 10:
        return "****"
    return f"{key[:4]}...{key[-4:]}"
