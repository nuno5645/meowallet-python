"""Enumerations for MEO Wallet API values."""

from __future__ import annotations

from enum import Enum


class PaymentMethod(str, Enum):
    """Payment methods supported by MEO Wallet."""

    CC = "CC"
    MB = "MB"
    MBWAY = "MBWAY"
    PAYPAL = "PAYPAL"
    WALLET = "WALLET"
    GPAY = "GPAY"
    APAY = "APAY"
    SAMSUNG_PAY = "SAMSUNG_PAY"
    SEPA = "SEPA"
    BANK = "BANK"


class OperationType(str, Enum):
    """Types of operations in MEO Wallet."""

    PAYMENT = "PAYMENT"
    REFUND = "REFUND"
    USERTRANSFER = "USERTRANSFER"
    WALLETFUNDS = "WALLETFUNDS"
    AUTH = "AUTH"
    CAPTURE = "CAPTURE"
    RELEASE = "RELEASE"


class OperationStatus(str, Enum):
    """Possible statuses of an operation."""

    COMPLETED = "COMPLETED"
    FAIL = "FAIL"
    NEW = "NEW"
    PENDING = "PENDING"
    VOIDED = "VOIDED"


class CallbackEvent(str, Enum):
    """Event types delivered in callback notifications."""

    COMPLETED = "COMPLETED"
    FAIL = "FAIL"
    USERERROR = "USERERROR"
    APPROVED = "APPROVED"
    CANCELED = "CANCELED"


class CallbackOperationType(str, Enum):
    """Operation types that appear in callback payloads."""

    AUTH = "AUTH"
    CAPTURE = "CAPTURE"
    RELEASE = "RELEASE"
    PAYMENT = "PAYMENT"
    REFUND_REVERSAL = "REFUND_REVERSAL"


class Channel(str, Enum):
    """Transaction channel."""

    WEBSITE = "WEBSITE"


class MandateStatus(str, Enum):
    """SEPA mandate statuses."""

    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    DELETED = "DELETED"
