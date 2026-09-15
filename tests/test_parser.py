from box_chart_maker.jv_parser import get_data, parse_file_name, WrongFileName, parse
import pytest
from pathlib import Path
import math
from datetime import datetime

def test_get_data():
    data_line = "#1.141601E+0\t-1.904904E+1\t69.420223\t15.096400\t15.096400"
    sup_line = "#Forward scan\t03.09.2026\t11:58:01"
    voc, jsc, ff, pce, pm, date, direction = get_data(data_line, sup_line)
    assert math.isclose(voc, 1.141601)
    assert math.isclose(jsc, -19.04904)
    assert math.isclose(ff, 69.420223)
    assert math.isclose(pce, 15.096400)
    assert math.isclose(pm, 15.096400)
    assert date == datetime(2026, 9, 3, 11, 58, 1)
    assert direction == "Forward scan"

@pytest.mark.parametrize("bad_line,exception",[
    ("#sdfs\t-1.904904E+1\t69.420223\t15.096400\t15.096400", ValueError),
    ("#1.141601E+0\t-1.904904E+1\t69.420223\t15.096400", IndexError),
    ("", ValueError)
])
def test_bad_data(bad_line,exception):
    sup_line = "#Forward scan\t03.09.2026\t11:58:01"
    with pytest.raises(exception):
        get_data(bad_line, sup_line)

@pytest.mark.parametrize("file_path,expected_id,expected_num,expected_illum",[
    (Path("20260903_Witnesses_Alena_Light_c10p1_Kirill_P.txt"), "c10", 1, "Light"),
    (Path("20260903_Witnesses_Alena_Light_c10p12_Kirill_P.txt"), "c10", 12, "Light"),
])
def test_parse_file_name(file_path,expected_id,expected_num,expected_illum):
    substrate_id, pixel_num, illumination = parse_file_name(file_path)
    assert substrate_id == expected_id
    assert pixel_num == expected_num
    assert illumination == expected_illum

@pytest.mark.parametrize("file_path",[
    Path("20260903_Witnesses_Alena_Light_c10p1_b12p3_Kirill_P.txt"),
    Path("20260903_Witnesses_Alena_Light_p12_Kirill_P.txt"),
    Path("20260903_Witnesses_Alena_c10p12_Kirill_P.txt")
])
def test_bad_parse_file_name(file_path):
    with pytest.raises(WrongFileName):
        parse_file_name(file_path)


FILE_DATA = """
#Uoc (V)	Jsc (mA/cm2)	FF		PCE	Pm, W/cm2
#8.138441E-3	6.927765E-2	0.000000	0.000000	0.000000
#Forward scan	22.01.2026	15:10:34
#Time, s	Voltage, V	Current density, mA/cm2	Power, W/cm2

#Forward scan stopped 

#Uoc (V)	Jsc (mA/cm2)	FF		PCE	Pm, W/cm2
#8.113147E-3	6.303291E-2	0.000000	0.000000	0.000000
#Forward scan	22.01.2026	15:10:36
#Time, s	Voltage, V	Current density, mA/cm2	Power, W/cm2

#Forward scan stopped 

#Uoc (V)	Jsc (mA/cm2)	FF		PCE	Pm, W/cm2
#8.138739E-3	
"""
def test_parse(tmp_path, caplog):
    file_path = tmp_path / "20260122_SnO2_172_Light_c2p2_Alena.txt"
    file_path.write_text(FILE_DATA, encoding="cp1251")
    scans = parse(file_path)
    assert len(scans) == 2
    assert math.isclose(scans[0].voc, 0.008138441)
    assert math.isclose(scans[1].voc, 0.008113147)
    assert "Corrupted scan in" in caplog.text