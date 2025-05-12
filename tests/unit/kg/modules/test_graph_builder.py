# tests/test_graph_builder.py

import scripts.kg.modules.graph_builder as graph_builder
from scripts.kg.modules.graph_builder import KnowledgeGraphBuilder

# --- Monkey-patch external dependencies so tests don't error out ---
graph_builder.DocMapNormalizer.normalize_keys = staticmethod(lambda d: d)
graph_builder.FunctionExtractor = type(
    "DummyFE", (), {"extract_parameters_and_returns": staticmethod(lambda fn: ([], []))}
)
graph_builder.DataRelationExtractor = type(
    "DummyDR", (), {"extract_data_relations": staticmethod(lambda G, node, desc: None)}
)
# -------------------------------------------------------------------

def make_docmap():
    return {
        "scripts/pkg/module.py": {
            "classes": [{"name": "MyClass"}],
            "functions": [{"name": "func"}],
            "module_doc": {"description": "some text"},
        }
    }

def test_build_graph_basic_structure():
    builder = KnowledgeGraphBuilder(make_docmap())
    G = builder.build_knowledge_graph()

    # folder nodes
    assert G.has_node("scripts")
    assert G.nodes["scripts"]["type"] == "folder"
    assert G.has_node("scripts/pkg")
    assert G.nodes["scripts/pkg"]["type"] == "folder"

    # module node
    mod = "module:scripts/pkg/module.py"
    assert G.has_node(mod)
    assert G.nodes[mod]["type"] == "module"

    # class and function nodes
    cls = "scripts/pkg/module.py.MyClass"
    fn = "scripts/pkg/module.py.func"
    assert G.has_node(cls) and G.nodes[cls]["type"] == "class"
    assert G.has_node(fn) and G.nodes[fn]["type"] == "function"

    # all edges should carry 'relation' metadata
    for _, _, data in G.edges(data=True):
        assert "relation" in data

def test_focus_prefix_filtering():
    docmap = {
        "scripts/a.py": {},
        "scripts/b.py": {},
        "other/c.py": {},
    }
    builder = KnowledgeGraphBuilder(docmap)
    G_all = builder.build_knowledge_graph()
    # both a and b should be included
    assert G_all.has_node("module:scripts/a.py")
    assert G_all.has_node("module:scripts/b.py")

    # filter to just 'scripts/a'
    G_a = builder.build_knowledge_graph(focus_prefix="scripts/a")
    assert G_a.has_node("module:scripts/a.py")
    assert not G_a.has_node("module:scripts/b.py")
