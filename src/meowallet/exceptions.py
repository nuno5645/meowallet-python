"""Exception hierarchy for MEO Wallet API errors.

Two-level mapping: API error codes override HTTP status codes for semantic accuracy.
For example, a 400 response with error code 30007 raises PaymentDeclinedError, not BadRequestError.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from meowallet.models.error import ErrorResponse


class MeoWalletError(Exception):
    """Base exception for all MEO Wallet errors."""


class ConfigurationError(MeoWalletError):
    """Invalid client configuration (missing API key, bad URL, etc.)."""


class ValidationError(MeoWalletError):
    """Local validation error before sending request."""


class TransportError(MeoWalletError):
    """Network-level transport failure."""

    def __init__(self, message: str, original: Exception | None = None) -> None:
        super().__init__(message)
        self.original = original


class TimeoutError(TransportError):  # noqa: A001
    """Request timed out."""


class ConnectionError(TransportError):  # noqa: A001
    """Could not connect to the server."""


class APIError(MeoWalletError):
    """Error response from the MEO Wallet API.

    Attributes:
        status_code: HTTP status code.
        error_response: Parsed ErrorResponse model (may be None if unparseable).
        api_code: The MEO Wallet error code (e.g. 10004, 20005).
        tid: Transaction/error GUID for support reference.
        raw_body: Raw response body for debugging.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        error_response: ErrorResponse | None = None,
        raw_body: bytes = b"",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_response = error_response
        self.raw_body = raw_body
        self.api_code: int | None = error_response.code if error_response else None
        self.tid: str | None = error_response.tid if error_response else None

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(status_code={self.status_code}, "
            f"api_code={self.api_code}, tid={self.tid!r})"
        )


class BadRequestError(APIError):
    """400 Bad Request — invalid parameters or JSON."""


class AuthenticationError(APIError):
    """401 Unauthorized — invalid or missing API key."""


class ForbiddenError(APIError):
    """403 Forbidden — insufficient permissions."""


class NotFoundError(APIError):
    """404 Not Found — resource does not exist."""


class ConflictError(APIError):
    """409 Conflict."""


class InvalidStateError(APIError):
    """Resource is in a state that does not allow the requested operation (code 10013)."""


class RateLimitError(APIError):
    """429 Too Many Requests."""


class PaymentDeclinedError(APIError):
    """Credit card was declined (code 30007)."""


class NotRefundableError(APIError):
    """Operation is not refundable (code 40010)."""


class InternalServerError(APIError):
    """500+ server error or codes 19999/20008."""


class CallbackVerificationError(MeoWalletError):
    """Callback payload failed verification against the MEO Wallet API."""


# Two-level mapping: API error code overrides take priority over HTTP status codes.

_CODE_OVERRIDES: dict[int, type[APIError]] = {
    10004: NotFoundError,
    10013: InvalidStateError,
    20001: AuthenticationError,
    20004: AuthenticationError,
    20005: AuthenticationError,
    30007: PaymentDeclinedError,
    40010: NotRefundableError,
    19999: InternalServerError,
    20008: InternalServerError,
}

_STATUS_MAP: dict[int, type[APIError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    422: BadRequestError,
    429: RateLimitError,
}


def _build_message(status_code: int, error_response: ErrorResponse | None) -> str:
    """Build a human-readable error message from the API response."""
    parts: list[str] = [f"HTTP {status_code}"]
    if error_response:
        if error_response.code is not None:
            parts.append(f"[{error_response.code}]")
        if error_response.message:
            parts.append(error_response.message)
        if error_response.reason and error_response.reason != error_response.message:
            parts.append(f"— {error_response.reason}")
    return " ".join(parts)


def raise_for_status(
    status_code: int,
    body: bytes,
    _error_response_cls: Any = None,
) -> None:
    """Parse the response and raise the appropriate exception.

    Args:
        status_code: HTTP status code.
        body: Raw response body bytes.
        _error_response_cls: Override for ErrorResponse class (for testing).
    """
    if 200 <= status_code < 300:
        return

    from meowallet.models.error import ErrorResponse as _ErrorResponse

    cls = _error_response_cls or _ErrorResponse

    import json
    import logging

    from pydantic import ValidationError as PydanticValidationError

    _logger = logging.getLogger("meowallet")

    error_response: ErrorResponse | None = None
    try:
        data = json.loads(body)
        if isinstance(data, dict):
            error_response = cls.model_validate(data)
    except (json.JSONDecodeError, PydanticValidationError) as parse_exc:
        _logger.debug("Failed to parse error response body: %s", parse_exc)

    # Level 1: check API error code overrides
    exc_cls: type[APIError] = APIError
    if error_response and error_response.code is not None:
        exc_cls = _CODE_OVERRIDES.get(error_response.code, exc_cls)

    # Level 2: fall back to HTTP status code
    if exc_cls is APIError:
        if status_code >= 500:
            exc_cls = InternalServerError
        else:
            exc_cls = _STATUS_MAP.get(status_code, APIError)

    message = _build_message(status_code, error_response)
    raise exc_cls(
        message,
        status_code=status_code,
        error_response=error_response,
        raw_body=body,
    )
