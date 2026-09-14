import sys
import originpro as op
from jv_parser import Scan


PARAMS = {
    "pce": ("PCE", "%", 1),
    "ff": ("FF", "%", 1),
    "voc": ("Voc", "V", 1),
    "jsc": ("Jsc", "mA/cm²", -1)
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
        build_box_chart(len(scans_dict), wks)
    return book

        
def build_box_chart(configs_num, wks):
    gr = op.new_graph(template=r"F:\CustomBoxChart.otpu")
    gl = gr[0]
    for i in range(configs_num):
        gl.add_plot(wks, coly=i*2)
    gl.rescale()