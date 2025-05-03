# tests/test_visualization.py
import pytest
from scripts.kg.modules.visualization import GraphVisualizer

def test_get_complexity_color():
    gv = GraphVisualizer()
    assert gv._get_complexity_color(10) == "#ccffcc"   # <20
    assert gv._get_complexity_color(20) == "#ffffcc"   # ==20
    assert gv._get_complexity_color(25) == "#ffffcc"   # between 20 and 30
    assert gv._get_complexity_color(31) == "#ffcccc"   # >30

def test_shorten_label_variants():
    gv = GraphVisualizer()
    # module: strips everything up to last slash
    assert gv._shorten_label("module:scripts/refactor/foo/bar.py") == "bar.py"
    # data: strips everything before 'data:'
    assert gv._shorten_label("data:my_dataset") == "my_dataset"
    # fallback: splits on dot
    assert gv._shorten_label("pkg.module.ClassName") == "ClassName"

def test_position_nodes_in_layers_empty():
    gv = GraphVisualizer()
    layers = {t: [] for t in ["folder","module","class","function","parameter","return","data"]}
    pos = gv._position_nodes_in_layers(layers)
    # no nodes, so expect empty dict
    assert pos == {}
