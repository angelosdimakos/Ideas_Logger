# Docstring Report for `scripts/kg/modules/`


## `scripts\kg\modules\__init__`


## `scripts\kg\modules\analysis`


Complexity Analysis for Knowledge Graphs
===============================
This module provides tools for analyzing the complexity of knowledge graphs.
It includes metrics for density, degree, busyness, and overall complexity scores.


### Classes

#### ComplexityAnalyzer

Analyzes graph complexity using various metrics.
Attributes:
None
Methods:
analyze_density: Analyzes the density and complexity of a given graph.

### Functions

#### analyze_density

Analyze the density and complexity of a given graph.

**Arguments:**
graph (nx.Graph): The graph to analyze.
name (str): An optional name for the graph.

**Returns:**
Dict[str, Any]: A dictionary containing various metrics of the graph's complexity.
Raises:
None

## `scripts\kg\modules\data_extractors`


Data extractors for analyzing Python docstrings and extracting relationships.


### Classes

#### DataRelationExtractor

Extracts data relations from module docstrings.

#### FunctionExtractor

Extracts function parameters and return values from docstrings.

### Functions

#### extract_data_relations

Extract data relations from module docstrings using pattern matching.

**Arguments:**
graph: The directed graph to which data relations will be added.
module_node: The module node identifier.
description: The module description from which to extract relations.

#### _add_data_node

Add a data node and its relation to the graph.

**Arguments:**
graph: The directed graph to which the node will be added.
module_node: The module node identifier.
data_node: The data node identifier.
relation: The type of relation to the data node.
confidence: The confidence level of the relation.

#### extract_parameters_and_returns

Extract parameters and return values from a function entry.

**Arguments:**
fn_entry: A dictionary containing function metadata.

**Returns:**
A tuple containing lists of parameters and return values.

## `scripts\kg\modules\graph_builder`


Knowledge graph construction and management tools.


### Classes

#### KnowledgeGraphBuilder

Builds knowledge graphs from docmap data.

#### CodebaseAnalyzer

Main class for analyzing and visualizing codebase knowledge graphs.

### Functions

#### __init__

Initialize with normalized docmap data.

**Arguments:**
docmap: A dictionary mapping module paths to their data attributes.

#### build_knowledge_graph

Constructs a knowledge graph from the docmap data, optionally filtering by prefix.

**Arguments:**
focus_prefix: Optional prefix to filter modules.

**Returns:**
A directed graph representing the relationships between modules and their data.

#### _build_graph

Build the knowledge graph from the filtered docmap.

**Arguments:**
docmap: A filtered dictionary mapping module paths to their data attributes.

**Returns:**
A directed graph representing the relationships.

#### __init__

Initialize the analyzer with JSON data.

**Arguments:**
json_path: Path to the docstring summary JSON file
focus_prefix: Prefix to filter modules

#### analyze

Analyze the codebase and build knowledge graph.

**Returns:**
Tuple containing the graph and complexity report

#### visualize

Visualize the knowledge graph with complexity indicators.

**Arguments:**
graph: The knowledge graph
density_report: Complexity metrics report

#### export_graph

Export the graph to a file.

**Arguments:**
graph: The knowledge graph
format_type: Export format ('graphml' or 'gexf')

**Returns:**
Filename of the exported graph

## `scripts\kg\modules\utils`


Utility functions for the codebase analysis and graph generation.


### Classes

#### DocMapNormalizer

Handles normalization of module path keys in docmap dictionaries.

### Functions

#### load_json_file

Load and parse a JSON file.

**Arguments:**
file_path: Path to the JSON file.

**Returns:**
The parsed JSON content or empty dict on error.

#### safe_get

Safely get a value from a dictionary.

**Arguments:**
data: Dictionary to get value from.
key: Key to lookup.
default: Default value if key not found.

**Returns:**
The value from the dictionary or default.

#### normalize_keys

Normalize all keys to use forward slashes for consistency.

**Arguments:**
docmap: A dictionary mapping module paths to their respective data.

**Returns:**
A new dictionary with normalized keys.

## `scripts\kg\modules\visualization`


Visualization tools for knowledge graphs.


### Classes

#### GraphVisualizer

Handles visualization of knowledge graphs with complexity information.

### Functions

#### __init__

Initialize the visualizer.

#### visualize_graph

Visualize the graph with complexity scores.

**Arguments:**
graph: The graph to visualize.
complexity_scores: A dictionary of complexity scores for nodes.
title: The title of the visualization.

#### _position_nodes_in_layers

Position nodes in horizontal layers by type.

**Arguments:**
layers: Dictionary of node types and their nodes.

**Returns:**
Dictionary of node positions.

#### _handle_remaining_nodes

Add positions for any nodes that weren't positioned in the initial layout.
This modifies the pos dictionary in-place.

**Arguments:**
pos: Dictionary of node positions to update.

#### _draw_module_rectangles

Draw colored rectangles around modules based on complexity.

**Arguments:**
ax: Matplotlib axes to draw on.
modules: Dictionary of module nodes.
pos: Dictionary of node positions.
complexity_scores: Dictionary of complexity scores.

#### _get_node_colors

Get node colors based on node type and module complexity.

**Arguments:**
graph: The knowledge graph.
complexity_scores: Dictionary of complexity scores.

**Returns:**
List of colors for each node.

#### _get_complexity_color

Get the color representation based on the complexity score.

**Arguments:**
score: The complexity score.

**Returns:**
The color corresponding to the complexity score.

#### _shorten_label

Shorten a label for display purposes.

**Arguments:**
name: The label to shorten.

**Returns:**
The shortened label.