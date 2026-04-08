"""Tests for exception hierarchy and error mapping."""

import json

import pytest

from meowallet.exceptions import (
    APIError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    InvalidStateError,
    NotFoundError,
    NotRefundableError,
    PaymentDeclinedError,
    RateLimitError,
    raise_for_status,
)


class TestRaiseForStatus:
    def test_200_does_not_raise(self):
        raise_for_status(200, b'{"id": "test"}')

    def test_201_does_not_raise(self):
        raise_for_status(201, b'{"id": "test"}')

    def test_204_does_not_raise(self):
        raise_for_status(204, b"")

    def test_400_raises_bad_request(self):
        body = json.dumps({"code": 10001, "message": "Missing parameter"}).encode()
        with pytest.raises(BadRequestError) as exc_info:
            raise_for_status(400, body)
        assert exc_info.value.status_code == 400
        assert exc_info.value.api_code == 10001

    def test_401_raises_authentication_error(self):
        body = json.dumps({"code": 20005, "message": "Invalid API KEY"}).encode()
        with pytest.raises(AuthenticationError) as exc_info:
            raise_for_status(401, body)
        assert exc_info.value.api_code == 20005

    def test_404_raises_not_found(self):
        body = json.dumps({"code": 10004, "message": "Resource not found", "tid": "t1"}).encode()
        with pytest.raises(NotFoundError) as exc_info:
            raise_for_status(404, body)
        assert exc_info.value.tid == "t1"

    def test_429_raises_rate_limit(self):
        with pytest.raises(RateLimitError):
            raise_for_status(429, b"{}")

    def test_500_raises_internal_server_error(self):
        with pytest.raises(InternalServerError):
            raise_for_status(500, b'{"code": 19999, "message": "Internal Server Error"}')

    # Code overrides take priority over HTTP status

    def test_code_10013_raises_invalid_state(self):
        """Code 10013 should raise InvalidStateError even on a 400."""
        body = json.dumps({"code": 10013, "message": "Invalid state"}).encode()
        with pytest.raises(InvalidStateError):
            raise_for_status(400, body)

    def test_code_30007_raises_payment_declined(self):
        """Card decline code should override generic 400."""
        body = json.dumps({"code": 30007, "message": "Credit Card declined!"}).encode()
        with pytest.raises(PaymentDeclinedError):
            raise_for_status(400, body)

    def test_code_40010_raises_not_refundable(self):
        body = json.dumps({"code": 40010, "message": "Payment is not refundable"}).encode()
        with pytest.raises(NotRefundableError):
            raise_for_status(400, body)

    def test_code_20005_on_400_raises_auth_error(self):
        """Auth code overrides the HTTP status."""
        body = json.dumps({"code": 20005, "message": "Invalid API KEY"}).encode()
        with pytest.raises(AuthenticationError):
            raise_for_status(400, body)

    # Error attributes

    def test_error_attributes(self):
        body = json.dumps(
            {
                "code": 10004,
                "message": "Resource not found",
                "reason": "Does not exist",
                "link": "https://docs.example.com",
                "tid": "tid-123",
            }
        ).encode()
        with pytest.raises(NotFoundError) as exc_info:
            raise_for_status(404, body)
        exc = exc_info.value
        assert exc.status_code == 404
        assert exc.api_code == 10004
        assert exc.tid == "tid-123"
        assert exc.error_response is not None
        assert exc.error_response.reason == "Does not exist"
        assert exc.raw_body == body

    def test_unparseable_body_still_raises(self):
        """Even if the body isn't valid JSON, we should still raise."""
        with pytest.raises(APIError):
            raise_for_status(500, b"not json")

    def test_repr(self):
        body = json.dumps({"code": 10004, "tid": "t1"}).encode()
        with pytest.raises(NotFoundError) as exc_info:
            raise_for_status(404, body)
        r = repr(exc_info.value)
        assert "NotFoundError" in r
        assert "404" in r
        assert "10004" in r
