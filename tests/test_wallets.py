"""Tests for the wallets resource."""

import httpx
import pytest


class TestWalletsSync:
    def test_list_methods(self, client, mock_api):
        mock_api.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"methods": ["CC", "MB", "WALLET"]})
        )
        methods = client.wallets.list_methods()
        assert methods == ["CC", "MB", "WALLET"]

    def test_list_methods_empty(self, client, mock_api):
        mock_api.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"methods": []})
        )
        methods = client.wallets.list_methods()
        assert methods == []

    def test_list_methods_unknown_method(self, client, mock_api):
        """Forward-compatible: unknown methods should be returned as-is."""
        mock_api.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"methods": ["CC", "FUTURE_METHOD"]})
        )
        methods = client.wallets.list_methods()
        assert "FUTURE_METHOD" in methods

    def test_list_methods_unexpected_shape_raises(self, client, mock_api):
        """Unexpected response shape should raise, not silently return []."""
        mock_api.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"unexpected": "shape"})
        )
        with pytest.raises(ValueError, match="Unexpected response shape"):
            client.wallets.list_methods()


class TestWalletsAsync:
    @pytest.mark.asyncio
    async def test_list_methods(self, async_client, mock_api):
        mock_api.get("/api/v2/wallets/methods").mock(
            return_value=httpx.Response(200, json={"methods": ["CC", "MBWAY"]})
        )
        methods = await async_client.wallets.list_methods()
        assert methods == ["CC", "MBWAY"]
        await async_client.close()
