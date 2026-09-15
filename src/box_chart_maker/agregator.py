from box_chart_maker.jv_parser import Illumination, Scan
from collections import defaultdict
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

class GroupingError(Exception):
    pass

def choose_best(scans: list[Scan], param: str="pce") -> dict[tuple[str, int], Scan]:
    scans_dict = defaultdict(list)
    final_dict = {}
    for scan in scans:
        if scan.illumination != Illumination.LIGHT:
            continue
        key = (scan.substrate_id, scan.pixel_num)
        scans_dict[key].append(scan)
    for key, value in scans_dict.items():
        unique_dir_count = len({scan.direction for scan in value})
        if unique_dir_count > 1:
            logger.warning("File '%s' contains more than one scan direction", key)
        best_scan = max(value, key=lambda scan: getattr(scan, param))
        final_dict[key] = best_scan
    return final_dict


def group_config(yaml_path:Path, scans: dict) -> dict[str]:
    error_list = []
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    reverse_dict = {}
    result_set = set()

    for config_name, substrates in config["configs"].items():
        for substrate_name in substrates:
            if substrate_name in reverse_dict:
                error_list.append(f"One substrate '{substrate_name}' in two or more configs {config_name}, {reverse_dict[substrate_name]}")
                continue
            reverse_dict[substrate_name] = config_name
            
    yaml_set = set(reverse_dict)

    scan_dict = {}
    for config_name in config["configs"]:
        scan_dict[config_name] = []

    for scan in scans.values():
        if scan.substrate_id not in reverse_dict:
            error_list.append(f"Substrate '{scan.substrate_id}' not in any config")
            continue
        scan_dict[reverse_dict[scan.substrate_id]].append(scan)
        result_set.add(scan.substrate_id)


    missing = yaml_set - result_set
    if missing:
        logger.warning("Could not find some substrates: %s", ", ".join(sorted(missing)))

    for config_name in config["configs"]:
        if not scan_dict[config_name]:
            error_list.append(f"Could not find any result for this config {config_name}")

    if error_list:
        raise GroupingError(f"Some errors appear: {error_list}")
    
    return scan_dict
