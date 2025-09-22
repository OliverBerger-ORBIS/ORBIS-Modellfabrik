from lib.controller import *
from lib.display import *
from lib.File import *
from lib.iw_log import *
from lib.machine_learning import *
from lib.mqtt_utils import *
from lib.node_red import *
from lib.sorting_line import *
from lib.vda5050 import *

display.set_attr("version_label.text", str(f'<h3>APS AI (Version: {vda_get_factsheet_version()})</h3>'))
print('Starting Module')
main_SLD()
