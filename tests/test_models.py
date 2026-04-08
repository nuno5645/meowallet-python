"""Tests for Pydantic models."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from meowallet.models.callback import CallbackPayload
from meowallet.models.checkout import PaymentBody
from meowallet.models.common import Address, ClientInfo, PaymentItem, RequiredFields
from meowallet.models.error import ErrorResponse
from meowallet.models.operation import (
    CaptureRequest,
    Operation,
    OperationList,
    RefundRequest,
    ReleaseRequest,
)
from meowallet.models.request_status import RequestStatus


class TestPaymentItem:
    def test_valid_item(self):
        item = PaymentItem(
            name="Widget",
            qt=2,
            descr="A widget",
            ref="W001",
            amount=Decimal("9.99"),
        )
        assert item.name == "Widget"
        assert item.qt == 2
        assert item.amount == Decimal("9.99")

    def test_minimum_fields(self):
        item = PaymentItem(name="X", qt=1)
        assert item.descr is None
        assert item.ref is None

    def test_qt_must_be_positive(self):
        with pytest.raises(ValidationError):
            PaymentItem(name="X", qt=0)

    def test_amount_bounds(self):
        with pytest.raises(ValidationError):
            PaymentItem(name="X", qt=1, amount=Decimal("0.0001"))

    def test_name_max_length(self):
        item = PaymentItem(name="A" * 500, qt=1)
        assert len(item.name) == 500
        with pytest.raises(ValidationError):
            PaymentItem(name="A" * 501, qt=1)


class TestClientInfo:
    def test_full_client(self):
        client = ClientInfo(
            name="Test User",
            email="test@example.com",
            phone="351961234567",
            address=Address(address="Rua X", city="Lisboa", country="PT", postalcode="1000-001"),
        )
        assert client.name == "Test User"
        assert client.address.city == "Lisboa"

    def test_empty_client(self):
        client = ClientInfo()
        assert client.name is None


class TestPaymentBody:
    def test_serialization_excludes_none(self):
        body = PaymentBody(amount=Decimal("10.50"), currency="EUR")
        data = body.to_api_dict()
        assert data["amount"] == 10.50
        assert "items" not in data
        assert "client" not in data


class TestOperation:
    def test_from_api_response(self):
        op = Operation.model_validate(
            {
                "id": "op-001",
                "amount": 10.00,
                "currency": "EUR",
                "type": "PAYMENT",
                "status": "COMPLETED",
                "method": "CC",
                "fee": -0.30,
                "refundable": True,
            }
        )
        assert op.id == "op-001"
        assert op.status == "COMPLETED"
        assert op.refundable is True

    def test_extra_fields_preserved(self):
        """Forward-compatible: unknown fields should be accepted."""
        op = Operation.model_validate(
            {
                "id": "op-001",
                "amount": 10,
                "currency": "EUR",
                "type": "PAYMENT",
                "status": "NEW",
                "method": "CC",
                "future_field": "some_value",
            }
        )
        assert op.model_extra["future_field"] == "some_value"


class TestOperationList:
    def test_empty_list(self):
        ol = OperationList.model_validate({"total": 0, "elements": []})
        assert ol.total == 0
        assert ol.elements == []

    def test_with_elements(self):
        ol = OperationList.model_validate(
            {
                "total": 1,
                "elements": [{"id": "op-001", "amount": 5, "currency": "EUR", "status": "NEW"}],
            }
        )
        assert ol.total == 1
        assert ol.elements[0].id == "op-001"


class TestRefundRequest:
    def test_default_full_refund(self):
        req = RefundRequest()
        data = req.model_dump(exclude_none=True)
        assert data["type"] == "full"
        assert "amount" not in data

    def test_partial_refund(self):
        req = RefundRequest(type="partial", amount=Decimal("5.00"))
        assert req.amount == Decimal("5.00")

    def test_amount_min(self):
        with pytest.raises(ValidationError):
            RefundRequest(amount=Decimal("0.001"))


class TestCaptureRequest:
    def test_amount_min(self):
        with pytest.raises(ValidationError):
            CaptureRequest(amount=Decimal("0.1"))

    def test_valid(self):
        req = CaptureRequest(amount=Decimal("0.20"), notes="partial capture")
        assert req.amount == Decimal("0.20")


class TestReleaseRequest:
    def test_empty_release(self):
        """Omitting amount releases full authorization."""
        req = ReleaseRequest()
        data = req.model_dump(exclude_none=True)
        assert "amount" not in data


class TestCallbackPayload:
    def test_parse_full_payload(self):
        cb = CallbackPayload.model_validate(
            {
                "amount": 10.0,
                "create_date": "2025-01-15T10:00:00+0000",
                "currency": "EUR",
                "event": "COMPLETED",
                "ext_customerid": "c001",
                "ext_invoiceid": "i001",
                "ext_email": "test@test.com",
                "method": "CC",
                "modified_date": "2025-01-15T10:00:01+0000",
                "operation_id": "op-001",
                "operation_status": "COMPLETED",
                "user": 12345,
            }
        )
        assert cb.operation_id == "op-001"
        assert cb.event == "COMPLETED"

    def test_timestamps_parsed_to_datetime(self):
        """Timestamps should be parsed into datetime, not left as strings."""
        from datetime import datetime

        cb = CallbackPayload.model_validate(
            {
                "create_date": "2026-04-07T23:18:54+0000",
                "modified_date": "2026-04-07T23:18:55+0000",
            }
        )
        assert isinstance(cb.create_date, datetime)
        assert isinstance(cb.modified_date, datetime)
        assert cb.create_date.year == 2026
        assert cb.create_date.month == 4

    def test_none_timestamps_accepted(self):
        cb = CallbackPayload.model_validate({"create_date": None, "modified_date": None})
        assert cb.create_date is None
        assert cb.modified_date is None

    def test_user_as_string(self):
        """Doc says integer but could be string in practice."""
        cb = CallbackPayload.model_validate({"user": "12345"})
        assert cb.user == "12345"


class TestErrorResponse:
    def test_parse(self):
        err = ErrorResponse.model_validate(
            {
                "code": 10004,
                "message": "Resource not found",
                "reason": "Not found",
                "link": "https://docs.example.com",
                "tid": "tid-001",
            }
        )
        assert err.code == 10004
        assert err.tid == "tid-001"


class TestRequestStatus:
    def test_parse(self):
        rs = RequestStatus.model_validate(
            {
                "href": "/api/v2/operations/op-001",
                "status": "COMPLETED",
                "method": "GET",
            }
        )
        assert rs.status == "COMPLETED"


class TestRequiredFields:
    def test_all_set(self):
        rf = RequiredFields(email=True, name=True, phone=False, shipping=True)
        assert rf.email is True
        assert rf.phone is False
