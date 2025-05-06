"""
Complexity analysis tools for codebase knowledge graphs.
"""

from typing import Dict, Any

import networkx as nx


class ComplexityAnalyzer:
    """Analyzes graph complexity using various metrics."""

    @staticmethod
    def analyze_density(graph: nx.Graph, name: str = "") -> Dict[str, Any]:
        """
        Analyze the density and complexity of a given graph.

        Args:
            graph: The graph to analyze.
            name: An optional name for the graph.

        Returns:
            A dictionary containing various metrics of the graph's complexity.
        """
        node_count = graph.number_of_nodes()
        edge_count = graph.number_of_edges()

        # Calculate metrics with safeguards against division by zero
        avg_degree = (2 * edge_count) / node_count if node_count > 0 else 0
        density = (2 * edge_count) / (node_count * (node_count - 1)) if node_count > 1 else 0
        busyness = edge_count / node_count if node_count > 0 else 0

        # Get top nodes by degree
        degrees = sorted(graph.degree, key=lambda x: x[1], reverse=True)
        top_nodes = degrees[:5]

        # Calculate complexity score using weighted metrics
        complexity_score = (
            0.15 * (node_count / 100)
            + 0.20 * (edge_count / 200)
            + 0.35 * (avg_degree / 5)
            + 0.20 * (busyness / 2)
            + 0.10 * (density / 0.2)
        ) * 100

        return {
            "name": name,
            "nodes": node_count,
            "edges": edge_count,
            "avg_degree": avg_degree,
            "density": density,
            "busyness": busyness,
            "complexity_score": complexity_score,
            "top_nodes": top_nodes,
        }
