import pytest

from src.box_chart_maker.config import check_parameter, check_configs, check_name_type, check_limits, read_config, ConfigError, get_pattern, NAME_TYPES

VALID_LIMITS = [
    ("ff", {"min": 40, "max": 100}),     # обе границы
    ("ff", {"min": 40}),                 # только нижняя
    ("pce", {"max": 30.5}),              # только верхняя, float
    ("voc", {}),                         # пустой — ничего не ограничивает
]

INVALID_LIMITS = [
    ("ff", {"min": "abc"}),              # строка
    ("ff", {"min": True}),               # bool под видом int
    ("ff", {"min": None}),               # min: без значения
    ("ff", {"min": 50, "max": 40}),      # min > max
    ("ff", {"min": 40, "max": 40}),      # min == max
    ("ff", {"mn": 40}),                  # опечатка в ключе
    ("ff", 40),                          # скаляр вместо словаря
]

GOOD_CONFIG = {
    "configs": {"Control": ["c2", "c3"], "Config A": ["c5"]},
    "name_type": "small",
    "limits": {"ff": {"min": 40}},
}

BAD_FOR_CONFIGS = [
    {"name_type": "small", "limits": {"ff": {"min": 40}}},   # нет ключа
    GOOD_CONFIG | {"configs": {"Control": "c2"}},            # скаляр вместо списка
    GOOD_CONFIG | {"configs": ["c2"]},                       # список вместо словаря
    GOOD_CONFIG | {"configs": {}},                           # пустой
]

BAD_FOR_NAME_TYPE = [
    {"configs": {"Control": ["c2"]}, "limits": {"ff": {"min": 40}}},  # нет ключа
    GOOD_CONFIG | {"name_type": "big"},                               # неизвестная схема
]

BAD_FOR_LIMITS = [
    {"configs": {"Control": ["c2"]}, "name_type": "small"},  # нет ключа
    GOOD_CONFIG | {"limits": [40, 100]},                     # список вместо словаря
    GOOD_CONFIG | {"limits": {"fff": {"min": 1}}},           # опечатка в параметре
]

GOOD_YAML = """configs:
  Control: [c2, c3]
name_type: small
limits:
  ff:
    min: 40
"""

BROKEN_YAML = """configs:
  Control: [c2, c3
"""                          # незакрытая скобка — YAMLError

LIST_YAML = """- c2
- c3
"""                          # валидный YAML, но не словарь

INVALID_YAML = """configs:
  Control: [c2, c3]
name_type: big
limits:
  ff:
    min: 40
"""


def test_valid_check_parameter():
    for param_name, minmax_dict in VALID_LIMITS:
        error_list = check_parameter(param_name, minmax_dict)
        assert error_list == []

def test_invalid_check_parameter():
    for param_name, minmax_dict in INVALID_LIMITS:
        error_list = check_parameter(param_name, minmax_dict)
        assert error_list != []

def test_check_configs():
    assert check_configs(GOOD_CONFIG) == []
    assert check_name_type(GOOD_CONFIG) == []
    assert check_limits(GOOD_CONFIG) == []

def test_invalid_configs():
    for config in BAD_FOR_CONFIGS:
        assert check_configs(config) != []

def test_invalid_name_type():
    for config in BAD_FOR_NAME_TYPE:
        assert check_name_type(config) != []

def test_invalid_limits():
    for config in BAD_FOR_LIMITS:
        assert check_limits(config) != []


def test_read_config(tmp_path):
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(GOOD_YAML, encoding="utf-8")
    config = read_config(yaml_path)
    result = {'configs': {'Control': ['c2', 'c3']}, 'name_type': 'small', 'limits': {'ff': {'min': 40}}}
    assert config == result

@pytest.mark.parametrize("yaml,error_msg",[
    (BROKEN_YAML, "while parsing"),
    (LIST_YAML, "Config file is empty or have an invalid structure."),
    (INVALID_YAML, "Unknown name_type"),
])
def test_broken_yaml(yaml, error_msg, tmp_path):
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text(yaml, encoding="utf-8")
    with pytest.raises(ConfigError, match=error_msg):
        read_config(yaml_path)

def test_get_pattern():
    assert get_pattern(GOOD_CONFIG) == NAME_TYPES["small"]