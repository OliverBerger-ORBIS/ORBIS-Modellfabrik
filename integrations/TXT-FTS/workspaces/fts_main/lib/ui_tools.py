from lib.charger import *
from lib.display import *
from lib.vda5050 import *

loads = None
position1 = None
position2 = None
position3 = None


def ui_util_finish_charging():
    global loads, position1, position2, position3
    charger_disconnect()
    vda_set_paused(False)
    vda_set_charging(False)


def ui_set_load_indicators():
    global loads, position1, position2, position3
    loads = vda_get_loads()
    position1 = loads.get("1", {}).get("loadType")

    position2 = loads.get("2", {}).get("loadType")

    position3 = loads.get("3", {}).get("loadType")
    display.set_attr("txt_status_load1_r.active", str(position1 == 'RED').lower())
    display.set_attr("txt_status_load1_w.active", str(position1 == 'WHITE').lower())
    display.set_attr("txt_status_load1_b.active", str(position1 == 'BLUE').lower())
    display.set_attr("txt_status_load2_r.active", str(position2 == 'RED').lower())
    display.set_attr("txt_status_load2_w.active", str(position2 == 'WHITE').lower())
    display.set_attr("txt_status_load2_b.active", str(position2 == 'BLUE').lower())
    display.set_attr("txt_status_load3_r.active", str(position3 == 'RED').lower())
    display.set_attr("txt_status_load3_w.active", str(position3 == 'WHITE').lower())
    display.set_attr("txt_status_load3_b.active", str(position3 == 'BLUE').lower())
