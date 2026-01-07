import os
from lib.controller import *
from lib.display import *
from lib.File import *
from lib.iw_log import *
from lib.machine_learning import *
from lib.mqtt_utils import *
from lib.node_red import *
from lib.sorting_line import *
from lib.vda5050 import *

display.set_attr("version_label.text", str('<h3>APS AI (Version: {})</h3>'.format(vda_get_factsheet_version())))
print('Starting Module with image')
main_SLD()
