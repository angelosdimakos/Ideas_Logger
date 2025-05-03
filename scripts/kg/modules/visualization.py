"""
Visualization tools for knowledge graphs.
"""

import logging
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from typing import Dict, Any

from scripts.kg.modules.utils import NodeID, ComplexityScores


class GraphVisualizer:
    """Handles visualization of knowledge graphs with complexity information."""

    def __init__(self):
        """Initialize the visualizer."""
        self.figsize = (16, 12)

    def visualize_graph(self, graph: nx.DiGraph, complexity_scores: ComplexityScores, title: str) -> None:
        """
        Visualize the graph with complexity scores.

        Args:
            graph: The graph to visualize.
            complexity_scores: A dictionary of complexity scores for nodes.
            title: The title of the visualization.
        """
        try:
            fig = plt.figure(figsize=self.figsize)
            # Store graph reference in the figure for helper methods to access
            fig.graph = graph

            # Organize nodes by type into layers
            layers = {t: [] for t in ["folder", "module", "class", "function", "parameter", "return", "data"]}
            modules = {}

            for n, d in graph.nodes(data=True):
                t = d.get("type", "unknown")
                if t in layers:
                    layers[t].append(n)
                if t == "module":
                    modules[n] = []

            # Position nodes in layers
            pos = self._position_nodes_in_layers(layers)

            # Create a clean axis
            ax = plt.gca()

            # Draw module rectangles with complexity coloring
            self._draw_module_rectangles(ax, modules, pos, complexity_scores)

            # Color nodes based on type and module complexity
            node_colors = self._get_node_colors(graph, complexity_scores)

            # Create shortened labels
            labels = {n: self._shorten_label(n) for n in graph.nodes()}

            # Draw the graph
            nx.draw(
                graph,
                pos,
                with_labels=True,
                labels=labels,
                node_color=node_colors,
                edge_color="gray",
                node_size=1000,
                font_size=9,
                font_weight="bold"
            )

            # Add edge labels
            edge_labels = nx.get_edge_attributes(graph, "relation")
            nx.draw_networkx_edge_labels(
                graph,
                pos,
                edge_labels=edge_labels,
                font_color="red",
                font_size=8
            )

            # Finalize plot
            plt.title(f"KG: {title} (Complexity Aware)", fontsize=14)
            plt.axis("off")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            logging.error(f"Graph visualization with complexity failed: {e}")

    def _position_nodes_in_layers(self, layers: Dict[str, list]) -> Dict[NodeID, tuple]:
        """
        Position nodes in horizontal layers by type.

        Args:
            layers: Dictionary of node types and their nodes.

        Returns:
            Dictionary of node positions.
        """
        pos = {}
        y_gap = -2.0
        x_gap = 1.5

        for i, t in enumerate(layers.keys()):
            nodes = layers[t]
            x_start = -(len(nodes) - 1) * x_gap / 2 if nodes else 0
            for j, n in enumerate(nodes):
                pos[n] = (x_start + j * x_gap, -i * y_gap)

        # Handle any nodes without positions
        self._handle_remaining_nodes(pos)

        return pos

    def _handle_remaining_nodes(self, pos: Dict[NodeID, tuple]) -> None:
        """
        Add positions for any nodes that weren't positioned in the initial layout.
        This modifies the pos dictionary in-place.

        Args:
            pos: Dictionary of node positions to update.
        """
        # Get the current graph from pyplot figure if available
        graph = plt.gcf().graph if hasattr(plt.gcf(), 'graph') else None
        if not graph:
            return

        for n in graph.nodes():
            if n not in pos:
                for p in graph.predecessors(n):
                    if p in pos:
                        pos[n] = (pos[p][0], pos[p][1] - 2.0)
                        break

    def _draw_module_rectangles(
            self,
            ax: plt.Axes,
            modules: Dict[NodeID, list],
            pos: Dict[NodeID, tuple],
            complexity_scores: ComplexityScores
    ) -> None:
        """
        Draw colored rectangles around modules based on complexity.

        Args:
            ax: Matplotlib axes to draw on.
            modules: Dictionary of module nodes.
            pos: Dictionary of node positions.
            complexity_scores: Dictionary of complexity scores.
        """
        graph = plt.gcf().graph if hasattr(plt.gcf(), 'graph') else None

        for m in modules.keys():
            # Get predecessors if graph is available, otherwise use empty list
            preds = list(graph.predecessors(m)) if graph else []
            parent = preds[0] if preds else None

            # Get children (the module itself + successors)
            children = [m]
            if graph:
                children.extend(list(graph.successors(m)))

            xs = [pos[n][0] for n in children if n in pos]
            ys = [pos[n][1] for n in children if n in pos]

            if not xs:
                continue

            min_x, max_x = min(xs) - 1, max(xs) + 1
            min_y, max_y = min(ys) - 1, max(ys) + 1

            mod_name = m.replace("module:scripts/refactor/", "").split("/")[0]
            score = complexity_scores.get(mod_name, 20.0)
            rect_color = self._get_complexity_color(score)

            # Add the colored rectangle
            ax.add_patch(
                mpatches.Rectangle(
                    (min_x, min_y),
                    max_x - min_x,
                    max_y - min_y,
                    facecolor=rect_color,
                    alpha=0.3,
                    edgecolor='gray'
                )
            )

            # Add module name label
            plt.text(
                (min_x + max_x) / 2,
                max_y + 0.5,
                mod_name,
                ha='center',
                fontsize=10,
                fontweight="bold"
            )

    def _get_node_colors(self, graph: nx.DiGraph, complexity_scores: ComplexityScores) -> list:
        """
        Get node colors based on node type and module complexity.

        Args:
            graph: The knowledge graph.
            complexity_scores: Dictionary of complexity scores.

        Returns:
            List of colors for each node.
        """
        node_colors = []

        for n, d in graph.nodes(data=True):
            if d.get("type") == "module":
                mod_name = n.replace("module:scripts/refactor/", "").split("/")[0]
                score = complexity_scores.get(mod_name, 20.0)
                node_colors.append(self._get_complexity_color(score))
            else:
                default_colors = {
                    "folder": "white",
                    "class": "lightgreen",
                    "function": "orange",
                    "parameter": "yellow",
                    "return": "gray",
                    "data": "pink"
                }
                node_colors.append(default_colors.get(d.get("type"), "lightgray"))

        return node_colors

    @staticmethod
    def _get_complexity_color(score: float) -> str:
        """
        Get the color representation based on the complexity score.

        Args:
            score: The complexity score.

        Returns:
            The color corresponding to the complexity score.
        """
        if score < 20:
            return "#ccffcc"  # Light green
        elif 20 <= score <= 30:
            return "#ffffcc"  # Light yellow
        else:
            return "#ffcccc"  # Light red

    @staticmethod
    def _shorten_label(name: str) -> str:
        """
        Shorten a label for display purposes.

        Args:
            name: The label to shorten.

        Returns:
            The shortened label.
        """
        if name.startswith("module:"):
            return name.split("/")[-1]
        elif "data:" in name:
            return name.split("data:")[-1]
        else:
            return name.split(".")[-1]