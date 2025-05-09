# tests/test_data_extractors.py
import pytest
import networkx as nx
from scripts.kg.modules.data_extractors import DataRelationExtractor, FunctionExtractor

def test_extract_data_relations_empty_description():
    G = nx.DiGraph()
    module_node = "module:empty"
    DataRelationExtractor.extract_data_relations(G, module_node, "")
    assert G.number_of_nodes() == 0
    assert G.number_of_edges() == 0

@pytest.mark.parametrize("desc, expected_nodes, expected_edges", [
    (
        "Stores info in DB",
        ["data:Storage"],
        [("data:Storage", "stores", 0.8)]
    ),
    (
        "Config parameters are loaded",
        ["data:Config", "data:Input"],
        [
            ("data:Config", "configures", 0.85),
            ("data:Input", "loads", 0.85)
        ]
    ),
])
def test_extract_data_relations_patterns(desc, expected_nodes, expected_edges):
    G = nx.DiGraph()
    module_node = "module:test_patterns"
    DataRelationExtractor.extract_data_relations(G, module_node, desc)

    # Check that each expected data node was added
    for node in expected_nodes:
        assert G.has_node(node), f"Expected node {node} in graph"

    # Check each edge has the correct relation and confidence
    for node, relation, confidence in expected_edges:
        ed = G.get_edge_data(module_node, node)
        assert ed is not None, f"Missing edge to {node}"
        assert ed["relation"] == relation
        assert ed["confidence"] == pytest.approx(confidence)

def test_extract_data_relations_object_patterns():
    G = nx.DiGraph()
    module_node = "module:objects"
    desc = "Functions to load users and parse items for analysis"
    DataRelationExtractor.extract_data_relations(G, module_node, desc)

    # Object-based extraction should pick up Users and Items
    assert G.has_node("data:Users")
    ed_users = G.get_edge_data(module_node, "data:Users")
    assert ed_users["relation"] == "loads"
    assert ed_users["confidence"] == pytest.approx(0.7)

    assert G.has_node("data:Items")
    ed_items = G.get_edge_data(module_node, "data:Items")
    assert ed_items["relation"] == "loads"
    assert ed_items["confidence"] == pytest.approx(0.7)

def test_extract_data_relations_filtering_short_words():
    G = nx.DiGraph()
    module_node = "module:filter"
    desc = "Load the log and track the db"
    DataRelationExtractor.extract_data_relations(G, module_node, desc)

    # Short or common words should not be turned into data:<Word>
    for short in ("The", "Log", "Db"):
        assert not G.has_node(f"data:{short}")

    # But RELATION_PATTERNS should still fire for 'load', 'track', and 'db'
    assert G.has_node("data:Input")
    ed_input = G.get_edge_data(module_node, "data:Input")
    assert ed_input["relation"] == "loads"
    assert ed_input["confidence"] == pytest.approx(0.85)

    assert G.has_node("data:Logs")
    ed_logs = G.get_edge_data(module_node, "data:Logs")
    assert ed_logs["relation"] == "monitors"
    assert ed_logs["confidence"] == pytest.approx(0.8)

def test_extract_parameters_and_returns_from_dict():
    fn_entry = {
        "args": {"x": 1, "y": 2},
        "returns": {"r1": "desc", "r2": "desc"}
    }
    params, rets = FunctionExtractor.extract_parameters_and_returns(fn_entry)
    assert set(params) == {"x", "y"}
    assert set(rets) == {"r1", "r2"}

def test_extract_parameters_from_string():
    fn_entry = {
        "args": "alpha(int): first parameter\n  beta: second parameter\nnot_a_param"
    }
    params, _ = FunctionExtractor.extract_parameters_and_returns(fn_entry)
    assert params == ["alpha", "beta"]

def test_extract_returns_from_string():
    fn_entry = {
        "returns": "result(int): something\nflag: indicates success\nfallback"
    }
    _, rets = FunctionExtractor.extract_parameters_and_returns(fn_entry)
    assert rets == ["result", "flag", "fallback"]

def test_extract_parameters_and_returns_empty():
    params, rets = FunctionExtractor.extract_parameters_and_returns({})
    assert params == []
    assert rets == []
