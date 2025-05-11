"""
  A module for registering event listeners that react to changes in the loaded configuration.
  This can be useful for updating dependent modules, reloading data sources, or triggering tests.
  """

  import abc
  from typing import Any, Callable

  class AbstractObserver(metaclass=abc.ABCMeta):
      """
      An abstract base class for configuration observers.

      This class provides an interface for observers to register their callbacks and receive notification when the configuration changes.
      Subclasses should implement the `on_config_changed` method to perform the appropriate action based on the changed configuration.

      Args:
          None
      """

      @abc.abstractmethod
      def on_config_changed(self, new_config: dict) -> None:
          """
          Called when the configuration has been updated.

          This method should perform the appropriate action based on the new configuration.

          Args:
              new_config (dict): The updated configuration as a dictionary.
          Returns:
              None
          """

  class ConfigObserver(AbstractObserver):
      """
      A concrete implementation of the `AbstractObserver` for observing configuration changes.
      """

      def __init__(self, callback: Callable[[dict], Any]) -> None:
          """
          Initialize the observer with a callback function to be called when the configuration changes.

          Args:
              callback (Callable[[dict], Any]): A callable that takes the new configuration as an argument and returns the result of the action to be performed.
          """

  # Suggested Integrations: load_config, reset
