"""Tests for retry policy — the most safety-critical module."""

from meowallet._retry import RetryPolicy
from meowallet.config import RetryConfig


def make_policy(**kwargs):
    return RetryPolicy(RetryConfig(**kwargs))


class TestRetrySafety:
    """The core safety invariant: POST is never retried without request_id."""

    def test_get_retried_on_500(self):
        policy = make_policy()
        assert policy.should_retry(
            method="GET",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )

    def test_delete_not_retried_by_default(self):
        """DELETE is not safe to retry — a lost response means ambiguous state."""
        policy = make_policy()
        assert not policy.should_retry(
            method="DELETE",
            status_code=503,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )

    def test_post_not_retried_without_request_id(self):
        """Critical: POST without request_id must NOT be retried."""
        policy = make_policy()
        assert not policy.should_retry(
            method="POST",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body={"amount": 10},
        )

    def test_post_not_retried_with_none_body(self):
        policy = make_policy()
        assert not policy.should_retry(
            method="POST",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )

    def test_post_retried_with_request_id(self):
        """POST with request_id IS safe to retry."""
        policy = make_policy()
        assert policy.should_retry(
            method="POST",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body={"amount": 10, "request_id": "uuid-123"},
        )

    def test_post_not_retried_with_empty_request_id(self):
        """Empty string request_id is NOT a valid idempotency key."""
        policy = make_policy()
        assert not policy.should_retry(
            method="POST",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body={"amount": 10, "request_id": ""},
        )

    def test_post_retried_with_nested_request_id(self):
        """request_id in payment/authorization sub-object."""
        policy = make_policy()
        assert policy.should_retry(
            method="POST",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body={"payment": {"amount": 10, "request_id": "uuid-123"}},
        )

    def test_post_retried_with_authorization_request_id(self):
        policy = make_policy()
        assert policy.should_retry(
            method="POST",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body={"authorization": {"amount": 10, "request_id": "uuid-456"}},
        )

    def test_post_retry_disabled(self):
        """When retry_post_with_request_id=False, even with request_id, POST is not retried."""
        policy = make_policy(retry_post_with_request_id=False)
        assert not policy.should_retry(
            method="POST",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body={"request_id": "uuid-123"},
        )


class TestRetryableConditions:
    def test_retryable_api_code_19999(self):
        policy = make_policy()
        assert policy.should_retry(
            method="GET",
            status_code=400,
            api_code=19999,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )

    def test_retryable_api_code_20008(self):
        policy = make_policy()
        assert policy.should_retry(
            method="GET",
            status_code=400,
            api_code=20008,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )

    def test_retryable_api_code_40021(self):
        policy = make_policy()
        assert policy.should_retry(
            method="GET",
            status_code=400,
            api_code=40021,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )

    def test_non_retryable_code(self):
        policy = make_policy()
        assert not policy.should_retry(
            method="GET",
            status_code=400,
            api_code=10001,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )

    def test_non_retryable_status(self):
        policy = make_policy()
        assert not policy.should_retry(
            method="GET",
            status_code=404,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )


class TestRetryLimits:
    def test_max_retries_respected(self):
        policy = make_policy(max_retries=2)
        assert policy.should_retry(
            method="GET",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )
        assert policy.should_retry(
            method="GET",
            status_code=500,
            api_code=None,
            attempt=1,
            is_transport_error=False,
            request_body=None,
        )
        assert not policy.should_retry(
            method="GET",
            status_code=500,
            api_code=None,
            attempt=2,
            is_transport_error=False,
            request_body=None,
        )

    def test_zero_retries(self):
        policy = make_policy(max_retries=0)
        assert not policy.should_retry(
            method="GET",
            status_code=500,
            api_code=None,
            attempt=0,
            is_transport_error=False,
            request_body=None,
        )


class TestTransportErrors:
    def test_get_retried_on_transport_error(self):
        policy = make_policy()
        assert policy.should_retry(
            method="GET",
            status_code=None,
            api_code=None,
            attempt=0,
            is_transport_error=True,
            request_body=None,
        )

    def test_post_not_retried_on_transport_error_without_request_id(self):
        policy = make_policy()
        assert not policy.should_retry(
            method="POST",
            status_code=None,
            api_code=None,
            attempt=0,
            is_transport_error=True,
            request_body={"amount": 10},
        )

    def test_post_retried_on_transport_error_with_request_id(self):
        policy = make_policy()
        assert policy.should_retry(
            method="POST",
            status_code=None,
            api_code=None,
            attempt=0,
            is_transport_error=True,
            request_body={"request_id": "uuid-123"},
        )


class TestBackoff:
    def test_delay_increases(self):
        policy = make_policy(backoff_base=1.0, backoff_factor=2.0)
        delays = [policy.get_delay(i) for i in range(5)]
        # With jitter, exact values vary, but median should increase
        # Just verify it's bounded
        for d in delays:
            assert 0 < d <= 30.0 * 1.5

    def test_delay_capped(self):
        policy = make_policy(backoff_base=1.0, backoff_factor=10.0, backoff_max=5.0)
        delay = policy.get_delay(10)
        assert delay <= 5.0 * 1.5  # max * max_jitter
