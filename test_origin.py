from datetime import datetime
from pathlib import Path
from jv_parser import Scan
from box_chart_builder import build_box_chart, build_datatable

def _s(sub, px, pce, ff, voc, jsc, ts):
    return Scan(
        substrate_id=sub, pixel_num=px,
        pce=pce, ff=ff, voc=voc, jsc=jsc, pm=pce,
        source_file=Path(f"20260903_Witnesses_Alena_Light_{sub}p{px}_Kirill_P.txt"),
        timestamp=datetime.strptime(ts, "%d.%m.%Y %H:%M:%S"),
        direction="Forward scan", illumination="Light",
    )

DEMO = {
    "Control": [
        _s("c11", 1, 15.096548, 70.815105, 1.141473, -18.67610, "03.09.2026 11:57:43"),
        _s("c11", 2, 15.096400, 69.420223, 1.141601, -19.04904, "03.09.2026 11:58:01"),
        _s("c11", 3, 15.107289, 70.172497, 1.141770, -18.85563, "03.09.2026 11:58:27"),
        _s("c11", 4, 14.980019, 69.280421, 1.141613, -18.94013, "03.09.2026 11:58:54"),
    ],
    "PdSe2": [
        _s("c10", 2, 14.778493, 68.776448, 1.141598, -18.82250, "03.09.2026 12:01:58"),
        _s("c10", 3, 13.115814, 61.692246, 1.141490, -18.62484, "03.09.2026 12:02:42"),
        _s("c10", 4, 11.941906, 59.123279, 1.114687, -18.12016, "03.09.2026 12:03:09"),
    ],
}

book = build_datatable(DEMO)
