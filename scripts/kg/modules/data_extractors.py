"""
Data extractors for analyzing Python docstrings and extracting relationships.
"""

import re
from typing import Dict, Any, List, Tuple

import networkx as nx

from scripts.kg.modules.utils import NodeID


class DataRelationExtractor:
    """Extracts data relations from module docstrings."""

    # Define relationships patterns with their confidence levels
    RELATION_PATTERNS = {
        # Data storage patterns
        r"(stor(e|ing)|persist|sav(e|ing)|database|db)": ("data:Storage", "stores", 0.8),
        # Configuration patterns
        r"(config|settings|options|parameters)": ("data:Config", "configures", 0.85),
        # Analysis patterns
        r"(analyz|analys|summariz|extract)": ("data:Analysis", "analyzes", 0.8),
        # Initialization patterns
        r"(initializ|bootstrap|setup|start)": ("data:System", "initializes", 0.9),
        # Loading patterns
        r"(load|read|import|parse)": ("data:Input", "loads", 0.85),
        # Monitoring patterns
        r"(monitor|track|log|debug)": ("data:Logs", "monitors", 0.8),
        # Visualization patterns
        r"(visualiz|display|render|show)": ("data:Visualization", "visualizes", 0.85),
        # Processing patterns
        r"(process|transform|convert)": ("data:Processing", "processes", 0.75),
    }

    # Patterns to extract specific objects that follow certain verbs
    OBJECT_PATTERNS = [
        (r"(load|read|parse)s?\s+(\w+)", "loads"),
        (r"(generat|creat)es?\s+(\w+)", "generates"),
        (r"(manag|handl)es?\s+(\w+)", "manages"),
        (r"(track|monitor)s?\s+(\w+)", "tracks")
    ]

    # Filter words for object extraction
    FILTER_WORDS = {"the", "and", "for", "with"}

    @classmethod
    def extract_data_relations(cls, graph: nx.DiGraph, module_node: NodeID, description: str) -> None:
        """
        Extract data relations from module docstrings using pattern matching.

        Args:
            graph: The directed graph to which data relations will be added.
            module_node: The module node identifier.
            description: The module description from which to extract relations.
        """
        if not description:
            return

        desc_lower = description.lower()

        # Apply patterns to find relationships
        for pattern, (data_node, relation, confidence) in cls.RELATION_PATTERNS.items():
            if re.search(pattern, desc_lower):
                cls._add_data_node(graph, module_node, data_node, relation, confidence)

        # Extract specific objects that follow certain verbs
        for pattern, relation in cls.OBJECT_PATTERNS:
            for match in re.finditer(pattern, desc_lower):
                object_name = match.group(2)
                # Filter out common words that aren't likely to be data objects
                if len(object_name) > 3 and object_name not in cls.FILTER_WORDS:
                    cls._add_data_node(
                        graph,
                        module_node,
                        f"data:{object_name.capitalize()}",
                        relation,
                        0.7
                    )

    @staticmethod
    def _add_data_node(
            graph: nx.DiGraph,
            module_node: NodeID,
            data_node: NodeID,
            relation: str,
            confidence: float
    ) -> None:
        """
        Add a data node and its relation to the graph.

        Args:
            graph: The directed graph to which the node will be added.
            module_node: The module node identifier.
            data_node: The data node identifier.
            relation: The type of relation to the data node.
            confidence: The confidence level of the relation.
        """
        graph.add_node(data_node, type="data")
        graph.add_edge(module_node, data_node, relation=relation, confidence=confidence)


class FunctionExtractor:
    """Extracts function parameters and return values from docstrings."""

    @staticmethod
    def extract_parameters_and_returns(fn_entry: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        Extract parameters and return values from a function entry.

        Args:
            fn_entry: A dictionary containing function metadata.

        Returns:
            A tuple containing lists of parameters and return values.
        """
        params = []
        returns = []

        # Extract parameters
        args = fn_entry.get("args", {})
        if isinstance(args, dict):
            params = list(args.keys())
        elif isinstance(args, str):
            for line in args.splitlines():
                match = re.match(r"^\s*(\w+)\s*(\([^)]*\))?:", line)
                if match:
                    params.append(match.group(1))

        # Extract returns
        rets = fn_entry.get("returns", {})
        if isinstance(rets, dict):
            returns = list(rets.keys())
        elif isinstance(rets, str):
            for line in rets.splitlines():
                match = re.match(r"^\s*(\w+)\s*(\([^)]*\))?:", line)
                if match:
                    returns.append(match.group(1))
                else:
                    fallback = re.match(r"^\s*(\w+)", line)
                    if fallback:
                        returns.append(fallback.group(1))

        return params, returns