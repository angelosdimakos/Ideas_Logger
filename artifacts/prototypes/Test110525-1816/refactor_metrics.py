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
        Initializes the metric calculator with the specified metric name.
        
        Args:
            name: The name of the metric to be calculated.
        """
        self.name = name

    @abstractmethod
    def calculate_metric(self, nodes: List[Any] = None) -> Dict[str, float]:
        """
        Calculates the metric based on the provided code nodes.
        
        Args:
            nodes: Optional list of code nodes to analyze.
        
        Returns:
            A dictionary mapping metric names to their calculated float values.
        """
        pass
