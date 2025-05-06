"""
Knowledge graph construction and management tools.
"""

import logging
from typing import Dict, Any, Tuple, Optional

import networkx as nx

from scripts.kg.modules.utils import DocMap, load_json_file, DocMapNormalizer
from scripts.kg.modules.data_extractors import DataRelationExtractor, FunctionExtractor
from scripts.kg.modules.analysis import ComplexityAnalyzer
from scripts.kg.modules.visualization import GraphVisualizer


class KnowledgeGraphBuilder:
    """Builds knowledge graphs from docmap data."""

    def __init__(self, docmap: DocMap):
        """
        Initialize with normalized docmap data.

        Args:
            docmap: A dictionary mapping module paths to their data attributes.
        """
        self.docmap = DocMapNormalizer.normalize_keys(docmap)

    def build_knowledge_graph(self, focus_prefix: Optional[str] = None) -> nx.DiGraph:
        """
        Constructs a knowledge graph from the docmap data, optionally filtering by prefix.

        Args:
            focus_prefix: Optional prefix to filter modules.

        Returns:
            A directed graph representing the relationships between modules and their data.
        """
        # Filter docmap if prefix is provided
        filtered_docmap = self.docmap
        if focus_prefix:
            filtered_docmap = {k: v for k, v in self.docmap.items() if k.startswith(focus_prefix)}

        return self._build_graph(filtered_docmap)

    def _build_graph(self, docmap: DocMap) -> nx.DiGraph:
        """
        Build the knowledge graph from the filtered docmap.

        Args:
            docmap: A filtered dictionary mapping module paths to their data attributes.

        Returns:
            A directed graph representing the relationships.
        """
        G = nx.DiGraph()
        folder_nodes = set()

        for module_path, info in docmap.items():
            if not module_path.startswith("scripts/"):
                continue

            # Create folder structure
            parts = module_path.split("/")
            folder_path = ""
            last_folder = None

            for part in parts[:-1]:
                folder_path = f"{folder_path}/{part}" if folder_path else part
                if folder_path not in folder_nodes:
                    G.add_node(folder_path, type="folder")
                    if last_folder:
                        G.add_edge(last_folder, folder_path, relation="contains", confidence=1.0)
                    last_folder = folder_path
                    folder_nodes.add(folder_path)
                else:
                    last_folder = folder_path

            # Add module node
            module_node = f"module:{module_path}"
            G.add_node(module_node, type="module")
            if last_folder:
                G.add_edge(last_folder, module_node, relation="contains", confidence=1.0)

            # Add classes
            for cls in info.get("classes", []):
                if isinstance(cls, dict) and "name" in cls:
                    cname = f"{module_path}.{cls['name']}"
                    G.add_node(cname, type="class")
                    G.add_edge(module_node, cname, relation="contains", confidence=1.0)

            # Add functions and their parameters/returns
            for fn in info.get("functions", []):
                if isinstance(fn, dict) and "name" in fn:
                    fname = f"{module_path}.{fn['name']}"
                    G.add_node(fname, type="function")
                    G.add_edge(module_node, fname, relation="contains", confidence=1.0)

                    params, returns = FunctionExtractor.extract_parameters_and_returns(fn)

                    # Add parameters
                    for p in params:
                        pnode = f"{fname}.{p}"
                        G.add_node(pnode, type="parameter")
                        G.add_edge(fname, pnode, relation="has_parameter", confidence=0.8)

                    # Add returns
                    for r in returns:
                        rnode = f"{fname}.returns.{r}"
                        G.add_node(rnode, type="return")
                        G.add_edge(fname, rnode, relation="returns", confidence=0.9)

            # Extract data relations from module docstring
            module_doc = info.get("module_doc", {})
            if isinstance(module_doc, dict):
                desc = module_doc.get("description", "")
                if desc:
                    DataRelationExtractor.extract_data_relations(G, module_node, desc)

        return G


class CodebaseAnalyzer:
    """Main class for analyzing and visualizing codebase knowledge graphs."""

    def __init__(self, json_path: str, focus_prefix: str = "scripts/refactor/"):
        """
        Initialize the analyzer with JSON data.

        Args:
            json_path: Path to the docstring summary JSON file
            focus_prefix: Prefix to filter modules
        """
        self.json_path = json_path
        self.focus_prefix = focus_prefix
        self.docmap = load_json_file(json_path)

    def analyze(self) -> Tuple[nx.DiGraph, Dict[str, Any]]:
        """
        Analyze the codebase and build knowledge graph.

        Returns:
            Tuple containing the graph and complexity report
        """
        # Build graph
        builder = KnowledgeGraphBuilder(self.docmap)
        graph = builder.build_knowledge_graph(self.focus_prefix)

        # No modules found
        if graph.number_of_nodes() == 0:
            logging.warning(
                f"No modules found under focus '{self.focus_prefix}'. Check slashes or focus name."
            )
            return graph, {}

        # Analyze complexity
        analyzer = ComplexityAnalyzer()
        density_report = analyzer.analyze_density(graph, name=self.focus_prefix)

        return graph, density_report

    def visualize(self, graph: nx.DiGraph, density_report: Dict[str, Any]) -> None:
        """
        Visualize the knowledge graph with complexity indicators.

        Args:
            graph: The knowledge graph
            density_report: Complexity metrics report
        """
        mod_name = self.focus_prefix.replace("scripts/refactor/", "").strip("/")
        complexity_scores = {mod_name: density_report["complexity_score"]}

        visualizer = GraphVisualizer()
        visualizer.visualize_graph(graph, complexity_scores, title=self.focus_prefix)

    def export_graph(self, graph: nx.DiGraph, format_type: str) -> str:
        """
        Export the graph to a file.

        Args:
            graph: The knowledge graph
            format_type: Export format ('graphml' or 'gexf')

        Returns:
            Filename of the exported graph
        """
        filename = self.focus_prefix.replace("/", "_").replace("\\", "_").strip("_")

        if format_type == "graphml":
            nx.write_graphml(graph, f"{filename}.graphml")
        elif format_type == "gexf":
            nx.write_gexf(graph, f"{filename}.gexf")

        return f"{filename}.{format_type}"
