"""Tests for client lifecycle and configuration."""

import os

import httpx
import pytest
import respx

from meowallet import (
    AsyncMeoWalletClient,
    Environment,
    MeoWalletClient,
)
from meowallet.exceptions import ConfigurationError
from tests.conftest import NO_RETRY, SANDBOX_URL, TEST_API_KEY


class TestClientInit:
    def test_missing_api_key_raises(self):
        # Ensure env var is not set
        env = os.environ.pop("MEOWALLET_API_KEY", None)
        try:
            with pytest.raises(ConfigurationError, match="API key is required"):
                MeoWalletClient(api_key=None)
        finally:
            if env is not None:
                os.environ["MEOWALLET_API_KEY"] = env

    def test_api_key_from_env(self):
        os.environ["MEOWALLET_API_KEY"] = TEST_API_KEY
        try:
            client = MeoWalletClient(environment=Environment.SANDBOX, retry=NO_RETRY)
            client.close()
        finally:
            del os.environ["MEOWALLET_API_KEY"]

    def test_production_environment(self):
        client = MeoWalletClient(
            api_key=TEST_API_KEY,
            environment=Environment.PRODUCTION,
            retry=NO_RETRY,
        )
        assert client._transport._config.effective_base_url == "https://services.wallet.pt"
        client.close()


class TestContextManager:
    @respx.mock(base_url=SANDBOX_URL)
    def test_sync_context_manager(self, respx_mock):
        respx_mock.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"methods": ["CC"]})
        )
        with MeoWalletClient(api_key=TEST_API_KEY, retry=NO_RETRY) as client:
            methods = client.wallets.list_methods()
            assert methods == ["CC"]

    @pytest.mark.asyncio
    @respx.mock(base_url=SANDBOX_URL)
    async def test_async_context_manager(self, respx_mock):
        respx_mock.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"methods": ["MB"]})
        )
        async with AsyncMeoWalletClient(api_key=TEST_API_KEY, retry=NO_RETRY) as client:
            methods = await client.wallets.list_methods()
            assert methods == ["MB"]


class TestResourceAttributes:
    def test_sync_has_all_resources(self):
        client = MeoWalletClient(api_key=TEST_API_KEY, retry=NO_RETRY)
        assert hasattr(client, "checkouts")
        assert hasattr(client, "operations")
        assert hasattr(client, "authorizations")
        assert hasattr(client, "wallets")
        assert hasattr(client, "requests")
        assert hasattr(client, "callbacks")
        client.close()

    def test_async_has_all_resources(self):
        client = AsyncMeoWalletClient(api_key=TEST_API_KEY, retry=NO_RETRY)
        assert hasattr(client, "checkouts")
        assert hasattr(client, "operations")
        assert hasattr(client, "authorizations")
        assert hasattr(client, "wallets")
        assert hasattr(client, "requests")
        assert hasattr(client, "callbacks")
