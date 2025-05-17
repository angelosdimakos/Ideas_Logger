import pytest

import pytest
  from unittest.mock import Mock
  from configuration_transformers.transformer import AbstractTransformer, ConfigValidator

  def test_configvalidator_validates_config(transformer):
      """
      Tests that the ConfigValidator validates the configuration data.
      """
      transformer = ConfigValidator()
      invalid_config = {"invalid": "data"}
      valid_config = {"key": "value"}

      assert transformer.transform(valid_config) == valid_config
      with pytest.raises(ValueError):
          transformer.transform(invalid_config)
