import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

PARAMS = {
    "voc": ("Voc", "V", 1),
    "jsc": ("Jsc", "mA/cm²", -1),
    "ff": ("FF", "%", 1),
    "pce": ("PCE", "%", 1),
}

NAME_TYPES= {
    "small": r"(?P<substrate>[a-z]\d+)p(?P<pixel>\d+)",
    "module": r"(?P<substrate>\d+ \d+)"
}

class ConfigError(Exception):
    pass


def check_configs(config: dict) -> list:
    error_list = []
    if "configs" in config:
        if not isinstance(config["configs"], dict):
            error_list.append("configs are not in a dict format")
            return error_list

        if not config["configs"]:
            error_list.append("configs is empty")
            return error_list

        for key, value in config["configs"].items():
            if type(value) is not list:
                error_list.append(f"{key} is not a list")

    else:
        error_list.append("configs not found in yaml")

    return error_list


def check_name_type(config: dict) -> list:
    error_list = []
    if "name_type" not in config:
        error_list.append("name_type not found in yaml")
        return error_list
    if config["name_type"] not in NAME_TYPES:
        error_list.append(f"Unknown name_type {config["name_type"]}, use one of {", ".join(NAME_TYPES.keys())}")

    return error_list


def check_parameter(param_name: str, minmax_dict: dict) -> list:
    error_list = []
    if type(minmax_dict) is not dict:
        error_list.append(f"Wrong limits syntax: {minmax_dict}")
        return error_list

    unknown = set(minmax_dict) - {"min", "max"}
    if unknown:
        error_list.append(f"unknown parameters in {param_name}: {unknown}")

    for key in ("min", "max"):
        if key in minmax_dict:
            minmax_value = minmax_dict[key]
            if not isinstance(minmax_value, (int, float)) or isinstance(minmax_value, bool):
                error_list.append(f"{minmax_value} is not a valid number for {param_name}")
                break
    else:
        min_value = minmax_dict.get("min", float("-inf"))
        max_value = minmax_dict.get("max", float("inf"))
        if min_value >= max_value:
                error_list.append(f"{param_name} - min: {min_value} >= max: {max_value}")

    return error_list

def check_limits(config: dict) -> list:
    error_list = []
    if "limits" in config:
        if not isinstance(config["limits"], dict):
            error_list.append("limits are not in a dict format")
            return error_list

        unknown = set(config["limits"]) - set(PARAMS)
        if unknown:
            error_list.append(f"unknown limits: {unknown}")

        for key, minmax_dict in config["limits"].items():
            error_list.extend(check_parameter(key, minmax_dict))

    else:
        error_list.append("limits not found in yaml")

    return error_list


def read_config(yaml_path: Path) -> dict:
    error_list = []

    with open(yaml_path, "r", encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ConfigError(exc)

    if not isinstance(config, dict):
        raise ConfigError("Config file is empty or have an invalid structure.")

    error_list.extend(check_configs(config))
    error_list.extend(check_name_type(config))
    error_list.extend(check_limits(config))

    if error_list:
        raise ConfigError("\n".join(error_list))
    return config

def get_pattern(config: dict) -> str:
    pattern = NAME_TYPES[config["name_type"]]
    return pattern