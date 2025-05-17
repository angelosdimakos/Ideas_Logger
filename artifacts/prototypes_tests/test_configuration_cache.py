import pytest

import pytest
  from unittest.mock import AsyncMock, patch
  from configuration_cache.cache import AbstractCache, ConfigCache

  @pytest.fixture(name="config_source")
  def config_source_fixture():
      """
      Provides a pytest fixture that returns a mock asynchronous configuration source.
      """
      return AsyncMock()

  # Test methods for the ConfigCache class

  def test_configcache_loads_item_on_first_call(config_source):
      """
      Tests that the ConfigCache loads an item from the config source on the first call to load_item.
      """
      cache = ConfigCache(config_source)
      cache_key = "test_cache_key"
      loaded_item = {"key": "value"}
      config_source.load_item.return_value = loaded_item

      assert cache.load_item(cache_key) == loaded_item
      assert config_source.load_item.called_once()

  def test_configcache_reuses_stored_item_on_subsequent_calls(config_source):
      """
      Verifies that ConfigCache returns the cached item on repeated load_item calls with the same key.
      
      Ensures that after the first retrieval, subsequent calls with the same cache key return the stored item instead of reloading it from the configuration source.
      """
      cache = ConfigCache(config_source)
      cache_key = "test_cache_key"
      loaded_item = {"key": "value"}
      config_source.load_item.side_effect = [loaded_item, cached_item := loaded_item]

      assert cache.load_item(cache_key) == loaded_item
      assert cache.load_item(cache_key) == cached_item
      assert config_source.load_item.called_with(cache_key) == config_source.load_item.call_count == 2

