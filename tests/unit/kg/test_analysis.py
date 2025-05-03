# tests/test_analysis.py
import pytest
import networkx as nx
from scripts.kg.modules.analysis import ComplexityAnalyzer

def test_analyze_density_empty_graph():
    G = nx.Graph()
    report = ComplexityAnalyzer.analyze_density(G, name="empty")
    assert report["name"] == "empty"
    assert report["nodes"] == 0
    assert report["edges"] == 0
    assert report["avg_degree"] == 0
    assert report["density"] == 0
    assert report["busyness"] == 0
    # score should be zero
    assert report["complexity_score"] == pytest.approx(0.0)

def test_analyze_density_simple_graph():
    G = nx.Graph()
    # 3 nodes, 2 edges forming a line: 1-2-3
    G.add_nodes_from([1, 2, 3])
    G.add_edges_from([(1, 2), (2, 3)])
    report = ComplexityAnalyzer.analyze_density(G, name="line")
    assert report["name"] == "line"
    assert report["nodes"] == 3
    assert report["edges"] == 2

    node_count = 3
    edge_count = 2
    avg_degree = (2 * edge_count) / node_count
    density = (2 * edge_count) / (node_count * (node_count - 1))
    busyness = edge_count / node_count
    expected_score = (
        0.15 * (node_count / 100)
        + 0.20 * (edge_count / 200)
        + 0.35 * (avg_degree / 5)
        + 0.20 * (busyness / 2)
        + 0.10 * (density / 0.2)
    ) * 100

    assert report["avg_degree"] == pytest.approx(avg_degree)
    assert report["density"] == pytest.approx(density)
    assert report["busyness"] == pytest.approx(busyness)
    assert report["complexity_score"] == pytest.approx(expected_score)

    # top_nodes should list node 2 first with degree 2
    top = report["top_nodes"]
    assert top[0][0] == 2 and top[0][1] == 2
