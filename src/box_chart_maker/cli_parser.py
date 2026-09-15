import argparse
from pathlib import Path
import logging
import sys
from box_chart_maker.agregator import GroupingError, choose_best, group_config
from box_chart_maker.box_chart_builder import build_datatable, build_graphs
from box_chart_maker.box_chart_builder import PARAMS
from box_chart_maker.jv_parser import BrokenFolder, MissingFiles, WrongFileName, parse_dir


logger = logging.getLogger()

def parse_cmd():
    parser = argparse.ArgumentParser(prog="BOX_CHART_MAKER", description="This program build box chart in originpro 2021 for LASE")
    parser.add_argument('-d',"--data-dir", help="Directory path for raw data. Better to put whole path", required=True, type=Path)
    parser.add_argument('-y',"--yaml", help="Specify configs in .yaml file", required=True, type=Path)
    parser.add_argument('-o',"--out-dir", help="Directory path for output. Better to put whole path", required=True, type=Path)
    parser.add_argument('-t',"--template", help="Path for origin template", required=True, type=Path)
    parser.add_argument("--param", choices=PARAMS.keys(), help="Choose selection parameter", default="pce")
    parser.add_argument("--verbose", choices=["DEBUG", "INFO", "ERROR", "WARNING"], help="Choose logging level", default="INFO")
    args = parser.parse_args()
    return args


def log_setup(verbose: str) -> None:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(message)s -%(asctime)s - [%(levelname)s]",
        datefmt="%Y-%m-%d, %H-%M-%S"
        )
    handler.setFormatter(formatter)
    logger.setLevel(verbose)
    logger.addHandler(handler)

def main():

    args = parse_cmd()
    log_setup(args.verbose)
    try:
        scan_list = parse_dir(args.data_dir)
        final_dict = choose_best(scan_list, args.param)
        scan_dict = group_config(args.yaml, final_dict)
    except (GroupingError, BrokenFolder, MissingFiles) as e:
        logger.error("%s", e)
        sys.exit(1)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    book = build_datatable(scan_dict)
    build_graphs(book, args.out_dir, args.template)

if __name__ == "__main__":
    main()