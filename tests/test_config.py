"""Tests for configuration module."""

from meowallet.config import ClientConfig, Environment, RetryConfig


class TestEnvironment:
    def test_sandbox_url(self):
        assert Environment.SANDBOX.value == "https://services.sandbox.meowallet.pt"

    def test_production_url(self):
        assert Environment.PRODUCTION.value == "https://services.wallet.pt"


class TestRetryConfig:
    def test_defaults(self):
        cfg = RetryConfig()
        assert cfg.max_retries == 3
        assert cfg.backoff_base == 0.5
        assert 500 in cfg.retryable_status_codes
        assert 19999 in cfg.retryable_api_codes
        assert "GET" in cfg.retry_safe_methods
        assert cfg.retry_post_with_request_id is True

    def test_custom_values(self):
        cfg = RetryConfig(max_retries=5, backoff_base=1.0)
        assert cfg.max_retries == 5
        assert cfg.backoff_base == 1.0


class TestClientConfig:
    def test_effective_base_url_uses_environment(self):
        cfg = ClientConfig(api_key="test", environment=Environment.PRODUCTION)
        assert cfg.effective_base_url == "https://services.wallet.pt"

    def test_effective_base_url_override(self):
        cfg = ClientConfig(api_key="test", base_url="https://custom.example.com")
        assert cfg.effective_base_url == "https://custom.example.com"

    def test_repr_masks_api_key(self):
        cfg = ClientConfig(api_key="abcdef1234567890abcdef1234567890abcdef12")
        r = repr(cfg)
        assert "abcdef1234567890" not in r
        assert "abcd" in r
        assert "f12" in r
