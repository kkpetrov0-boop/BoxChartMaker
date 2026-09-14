import logging
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from datetime import datetime
import re

@dataclass(frozen=True)
class Scan:
    substrate_id: str
    pixel_num: int
    pce: float
    ff: float
    voc: float
    jsc: float
    pm: float
    source_file: Path
    timestamp: datetime
    direction: str
    illumination: str

logger = logging.getLogger(__name__)

class Illumination(StrEnum):
    LIGHT = "Light"
    DARK = "Dark"

class WrongFileName(Exception):
    pass

class BrokenFolder(Exception):
    pass

class MissingFiles(Exception):
    pass

def parse_file_name(file_path: Path):
    str_path = file_path.name.split("_")
    pattern = re.compile(r"([a-z]\d+)p(\d+)")
    full_id_list = []
    illumination = None
    for token in str_path:
        full_id = pattern.fullmatch(token)
        if full_id:
            full_id_list.append(full_id)
        if token in Illumination:
            illumination = token

    if len(full_id_list) == 1 and illumination:
        substrate_id = full_id_list[0].group(1)
        pixel_num = full_id_list[0].group(2)
        pixel_num = int(pixel_num)
    else:
        raise WrongFileName(f"Wrong name of the file: {file_path}")
    return substrate_id, pixel_num, illumination


def get_data(data_line: str, sup_line: str):
    time_data = sup_line.split("\t")
    splited_data = data_line.strip().split("\t")
    logger.debug(splited_data)
    voc = float(splited_data[0].lstrip("#"))
    jsc = float(splited_data[1])
    ff = float(splited_data[2])
    pce = float(splited_data[3])
    pm = float(splited_data[4])
    datetime_str = time_data[1] + " " + time_data[2]
    direction = time_data[0].lstrip("#")
    date = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M:%S")
    logger.debug(date)
    return voc, jsc, ff, pce, pm, date, direction


def parse(file_path: Path, file_encoding="cp1251") -> list[Scan]:
    scans = []
    substrate_id, pixel_num, illumination = parse_file_name(file_path)
    with (open(file_path, "r", encoding=file_encoding) as f):
        line_num = 0

        while True:
            line = f.readline()
            line_num += 1
            if not line:
                break
            if not line.startswith("#Uoc (V)"):
                continue
            try:
                raw_data = f.readline()
                sup_data = f.readline().strip()
                line_num += 2
                voc, jsc, ff, pce, pm, date, direction = get_data(raw_data, sup_data)

                scan = Scan(voc=voc,
                            jsc=jsc,
                            ff=ff,
                            pce=pce,
                            pm=pm,
                            substrate_id=substrate_id,
                            pixel_num=pixel_num,
                            source_file=file_path,
                            timestamp=date,
                            direction=direction,
                            illumination=illumination)
                scans.append(scan)
            except (ValueError, IndexError) as e:
                logger.warning("Corrupted scan in %s: %s in line %d", file_path, e, line_num)
                
    logger.info("Получено измерений: %d, из файла %s",len(scans), file_path)

    return scans


def parse_dir(dir_path: Path) -> list[Scan]:
    scan_list = []
    error_list = []
    for file_path in sorted(dir_path.glob("*.txt")):
        try:
            scan_list.extend(parse(file_path))
        except WrongFileName as e:
            logger.warning("Wrong file name: %s", e)
            error_list.append(e)
    if error_list:
        raise BrokenFolder(f"Something got wrong with the files or directory: {error_list}")
    if not scan_list:
        raise MissingFiles("Could not find any suitable file. Check your folder path")
    return scan_list



parse_dir(Path(r"F:\python\box_chart_maker\JV"))
