"""MEO Wallet Python client library.

A production-ready, typed Python wrapper for the MEO Wallet payment API.
Supports both synchronous and asynchronous usage.

Quick start::

    from meowallet import MeoWalletClient, Environment

    client = MeoWalletClient(
        api_key="your-api-key",
        environment=Environment.SANDBOX,
    )
    checkout = client.checkouts.create_payment(
        amount=10.0,
        currency="EUR",
        items=[{"name": "Product", "qt": 1}],
        url_confirm="https://example.com/confirm",
        url_cancel="https://example.com/cancel",
    )
    print(checkout.url_redirect)
"""

from meowallet._version import __version__
from meowallet.async_client import AsyncMeoWalletClient
from meowallet.client import MeoWalletClient
from meowallet.config import ClientConfig, Environment, RetryConfig
from meowallet.enums import (
    CallbackEvent,
    CallbackOperationType,
    Channel,
    MandateStatus,
    OperationStatus,
    OperationType,
    PaymentMethod,
)
from meowallet.exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    CallbackVerificationError,
    ConfigurationError,
    ConflictError,
    ConnectionError,
    ForbiddenError,
    InternalServerError,
    InvalidStateError,
    MeoWalletError,
    NotFoundError,
    NotRefundableError,
    PaymentDeclinedError,
    RateLimitError,
    TimeoutError,
    TransportError,
    ValidationError,
)
from meowallet.models import (
    Address,
    Authorization,
    AuthorizationBody,
    AuthorizationList,
    CallbackPayload,
    CaptureRequest,
    ChargeOrder,
    ChargeOrderList,
    ChargeRequest,
    CheckoutResponse,
    ClientInfo,
    CreditCard,
    ErrorResponse,
    MBDeleteReferenceRequest,
    MBPaymentRequest,
    MBReference,
    MBReferenceRequest,
    MBReferenceResponse,
    MBWayPaymentRequest,
    Merchant,
    Operation,
    OperationList,
    PaymentBody,
    PaymentItem,
    RefundRequest,
    ReleaseRequest,
    RequestStatus,
    RequiredFields,
    Subscription,
    SubscriptionBody,
    SubscriptionCheckoutResponse,
    SubscriptionList,
    User,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "AsyncMeoWalletClient",
    "MeoWalletClient",
    # Config
    "ClientConfig",
    "Environment",
    "RetryConfig",
    # Enums
    "CallbackEvent",
    "CallbackOperationType",
    "Channel",
    "MandateStatus",
    "OperationStatus",
    "OperationType",
    "PaymentMethod",
    # Exceptions
    "APIError",
    "AuthenticationError",
    "BadRequestError",
    "CallbackVerificationError",
    "ConfigurationError",
    "ConflictError",
    "ConnectionError",
    "ForbiddenError",
    "InternalServerError",
    "InvalidStateError",
    "MeoWalletError",
    "NotFoundError",
    "NotRefundableError",
    "PaymentDeclinedError",
    "RateLimitError",
    "TimeoutError",
    "TransportError",
    "ValidationError",
    # Models
    "Address",
    "Authorization",
    "AuthorizationBody",
    "AuthorizationList",
    "CallbackPayload",
    "CaptureRequest",
    "ChargeOrder",
    "ChargeOrderList",
    "ChargeRequest",
    "CheckoutResponse",
    "ClientInfo",
    "CreditCard",
    "ErrorResponse",
    "MBDeleteReferenceRequest",
    "MBPaymentRequest",
    "MBReference",
    "MBReferenceRequest",
    "MBReferenceResponse",
    "MBWayPaymentRequest",
    "Merchant",
    "Operation",
    "OperationList",
    "PaymentBody",
    "PaymentItem",
    "RefundRequest",
    "ReleaseRequest",
    "RequestStatus",
    "RequiredFields",
    "Subscription",
    "SubscriptionBody",
    "SubscriptionCheckoutResponse",
    "SubscriptionList",
    "User",
]
