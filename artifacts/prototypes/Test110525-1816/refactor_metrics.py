"""Calculate various metrics for the refactoring process.

This module provides additional metrics to help developers make informed decisions during refactoring, leading to cleaner and more maintainable code.

Integrates with: ClassMethodInfo, ComplexityVisitor, MethodRangeVisitor, Radon, McCabe
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class MetricCalculator(ABC):
    """Abstract base class for metric calculators.

    Each subclass should implement specific metrics calculation logic.

    Attributes:
        name (str): The name of the metric being calculated.

    Methods:
        calculate_metric(self, nodes: List[Any] = None) -> Dict[str, float]:
            Calculate the specified metric based on the given code nodes.
    """

    def __init__(self, name: str):
        """
        Initializes the MetricCalculator with a specified metric name.
        
        Args:
            name: The name identifying the metric.
        """
        self.name = name

    @abstractmethod
    def calculate_metric(self, nodes: List[Any] = None) -> Dict[str, float]:
        """
        Calculates metric values based on the provided code nodes.
        
        Args:
            nodes: Optional list of code nodes to analyze. If not provided, the metric may be calculated using default or previously set data.
        
        Returns:
            A dictionary mapping metric names to their computed float values.
        """
        pass
