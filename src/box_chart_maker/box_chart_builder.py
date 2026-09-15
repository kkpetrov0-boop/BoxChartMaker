import sys
import originpro as op
from box_chart_maker.jv_parser import Scan
import pandas as pd
import dataclasses
from pathlib import Path

PARAMS = {
    "voc": ("Voc", "V", 1),
    "jsc": ("Jsc", "mA/cm²", -1),
    "ff": ("FF", "%", 1),
    "pce": ("PCE", "%", 1),
}

def origin_shutdown_exception_hook(exctype, value, traceback):
    op.exit()
    sys.__excepthook__(exctype, value, traceback)
if op and op.oext:
    sys.excepthook = origin_shutdown_exception_hook

def build_datatable(scans_dict: dict[str, list[Scan]]) -> op.worksheet.WBook:
    if op.oext:
        op.set_show(True)

    book = op.new_book("w")

    for field, (lname, unit, sign) in PARAMS.items():
        wks = book.add_sheet(lname)
        for i, (config_name, scans) in enumerate(scans_dict.items()):
            wks.from_list(i*2, [sign * getattr(scan, field) for scan in scans], lname=lname, units=unit, comments=config_name,axis="Y")
            wks.from_list(i*2+1, [scan.substrate_id + "p" + str(scan.pixel_num) for scan in scans], axis="L")

    wks = book[0]
    wks.name = "Data"
    wks.from_df(scans_to_df(scans_dict))
    return book

def build_graphs(book: op.worksheet.WBook, filepath: Path, graph_template: Path) -> None:
    for field, (lname, *_) in PARAMS.items():
        wks = book[lname]
        gr = build_box_chart(wks.cols // 2, wks, str(graph_template))
        out_path = filepath / f"{lname}.png"
        gr.save_fig(path=str(out_path), width=2000)
    op.lt_exec(
        "merge_graph option:=open row:=2 col:=2 keep:=1 labeltext:=1 "
        "xgap:=10 ygap:=10 leftmg:=10 rightmg:=10 topmg:=10 bottommg:=10;"
    )
    gr = op.find_graph()
    gr.save_fig(str(filepath / "merged.png"), width=3000)
        
def build_box_chart(configs_num: int, wks: op.worksheet.WSheet, graph_template: Path) -> op.graph.GPage:
    gr = op.new_graph(template=graph_template)
    gl = gr[0]
    for i in range(configs_num):
        gl.add_plot(wks, coly=i*2)
    gl.rescale()
    return gr

def scans_to_df(scan_dict: dict[str, list[Scan]]) -> pd.DataFrame:
    rows = []
    for config, scans in scan_dict.items():
        for scan in scans:
            row = {}
            row["config"] = config
            row.update(dataclasses.asdict(scan)) 
            row["source_file"] = str(row["source_file"])
            row["timestamp"] = row["timestamp"].strftime(r"%Y-%m-%d %H:%M:%S")
            rows.append(row)
    return pd.DataFrame(rows)
    