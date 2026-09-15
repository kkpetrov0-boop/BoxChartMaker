from box_chart_maker.agregator import choose_best, group_config, GroupingError
import pytest
import math
from datetime import datetime
from pathlib import Path
from box_chart_maker.jv_parser import Scan

def make_scan(sub="c10", px=1, pce=15.0, ff=70.0, voc=1.14, jsc=-19.0,
              ts="03.09.2026 11:58:01", illumination="Light",
              direction="Forward scan"):
    return Scan(
        substrate_id=sub, pixel_num=px, pce=pce,
        ff=ff, voc=voc, jsc=jsc, pm=pce,
        source_file=Path(f"20260903_Test_Light_{sub}p{px}_X.txt"),
        timestamp=datetime.strptime(ts, "%d.%m.%Y %H:%M:%S"),
        direction=direction, illumination=illumination
    )

SCANS = [
    # c10p1 — три скана, лучший по pce второй, но по ff первый
    make_scan("c10", 1, pce=14.0, ff=72.0, ts="03.09.2026 11:58:01"),
    make_scan("c10", 1, pce=15.5, ff=68.0, ts="03.09.2026 11:58:05"),
    make_scan("c10", 1, pce=13.2, ff=70.0, ts="03.09.2026 11:58:09"),
    # c10p2 — два скана с одинаковым pce, должен взяться первый
    make_scan("c10", 2, pce=14.8, ff=69.0, ts="03.09.2026 11:59:01"),
    make_scan("c10", 2, pce=14.8, ff=71.0, ts="03.09.2026 11:59:05"),
    # c11p1 — один Light и один Dark, Dark должен отсеяться
    make_scan("c11", 1, pce=12.0, ts="03.09.2026 12:01:01"),
    make_scan("c11", 1, pce=99.0, ts="03.09.2026 12:01:05", illumination="Dark"),
    make_scan("c11", 1, pce=1.0, ts="03.09.2026 12:01:01", direction="Reverse scan"),
]

def test_choose_best():
    final_dict = choose_best(SCANS)
    assert math.isclose(final_dict[("c10", 1)].pce, 15.5)
    assert math.isclose(final_dict[("c10", 2)].ff, 69.0)
    assert math.isclose(final_dict[("c11", 1)].pce, 12.0)
    assert len(final_dict) == 3
    final_dict = choose_best(SCANS, "ff")
    assert math.isclose(final_dict[("c10", 1)].ff, 72.0)


CONFIG_YAML = """configs:
  Control: [c2, c3]
  Config A: [c5, c6]
"""

BEST = {
    ("c2", 1): make_scan("c2", 1, pce=14.1),
    ("c2", 2): make_scan("c2", 2, pce=14.6),
    ("c3", 1): make_scan("c3", 1, pce=13.9),
    ("c5", 1): make_scan("c5", 1, pce=16.2),
    ("c6", 1): make_scan("c6", 1, pce=15.8),
}

def test_group_config(tmp_path):
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(CONFIG_YAML, encoding="utf-8")

    result = group_config(yaml_path, BEST)
    assert [scan.substrate_id for scan in result["Control"]] == ["c2", "c2", "c3"]
    assert [scan.substrate_id for scan in result["Config A"]] == ["c5", "c6"]
    assert list(result) == ["Control", "Config A"]

def test_extra_sub(tmp_path):
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(CONFIG_YAML, encoding="utf-8")    
    new_best = BEST | {("c9", 1): make_scan("c9", 1)}
    with pytest.raises(GroupingError):
        group_config(yaml_path, new_best)      

def test_extra_config(tmp_path):
    yaml_path = tmp_path / "config.yaml"
    config_yaml = """configs:
  Control: [c2, c3]
  Config A: [c5, c6]
  Config B: [c8, c12]
"""

    yaml_path.write_text(config_yaml, encoding="utf-8")
    with pytest.raises(GroupingError):
        group_config(yaml_path, BEST)

def test_double_in_config(tmp_path):
    yaml_path = tmp_path / "config.yaml"
    config_yaml = """configs:
  Control: [c2, c3]
  Config A: [c2, c5, c6]
"""
    
    yaml_path.write_text(config_yaml, encoding="utf-8")
    with pytest.raises(GroupingError):
        result = group_config(yaml_path, BEST)    