import json
import logging
import subprocess
from os.path import exists

default_values = None
path = None
default_value = None
value = None
dictionary = None
parent_key = None
calibration_defaults = None
calib_file = None
calib_text = None
calib_map = None


def calibration_init(default_values):
    global path, default_value, value, dictionary, parent_key, calibration_defaults, calib_file, calib_text, calib_map
    calibration_defaults = default_values
    calibration_reload()


def calibration_reload():
    global default_values, path, default_value, value, dictionary, parent_key, calibration_defaults, calib_file, calib_text, calib_map
    logging.info("Loading calibration.")
    if exists('/opt/ft/workspaces/FactoryCalibration.json'):
        logging.info("Loading calibration from existing file.")
        _calibration_read_file()
    else:
        calibration_reset_defaults()
    subprocess.Popen(['chmod', '777', '/opt/ft/workspaces/FactoryCalibration.json'])


def _calibration_read_file():
    global default_values, path, default_value, value, dictionary, parent_key, calibration_defaults, calib_file, calib_text, calib_map
    calib_file = open('/opt/ft/workspaces/FactoryCalibration.json', 'r', encoding='utf8')
    calib_text = calib_file.read()
    calib_file.close()
    calib_map = json.loads(calib_text)
    print('Read calibration:')
    print(calib_map)


def calibration_reset_defaults():
    global default_values, path, default_value, value, dictionary, parent_key, calibration_defaults, calib_file, calib_text, calib_map
    logging.info("Loading calibration from defaults.")
    if exists('/opt/ft/workspaces/FactoryCalibration.json'):
        _calibration_read_file()
        calib_file = open('/opt/ft/workspaces/FactoryCalibration_backup.json', 'w', encoding='utf8')
        calib_file.write(json.dumps(calib_map) + '\n')
        calib_file.flush()
        calib_file.close()
    calib_file = open('/opt/ft/workspaces/FactoryCalibration.json', 'w', encoding='utf8')
    calib_file.write(json.dumps(calibration_defaults) + '\n')
    calib_file.flush()
    calib_file.close()
    _calibration_read_file()


def calibration_save():
    global default_values, path, default_value, value, dictionary, parent_key, calibration_defaults, calib_file, calib_text, calib_map
    calib_file = open('/opt/ft/workspaces/FactoryCalibration.json', 'w', encoding='utf8')
    calib_file.write(json.dumps(calib_map) + '\n')
    calib_file.flush()
    calib_file.close()


def calibration_get(path, default_value):
    global default_values, value, dictionary, parent_key, calibration_defaults, calib_file, calib_text, calib_map
    # access value in a nested dictionary structure
    # CATEGORY.SECTION.name
    # returns the value stored as
    #
    # {
    #     "CATEGORY": {
    #         "SECTION": {
    #             "name": True
    #         }
    #     }
    # }
    #
    #  the default value will be returned if the path is not found
    #
    if isinstance(path, str):
        path = path.split(".")
    result = calib_map
    for key in path[:-1]:
            result = result.get(key, {})
    return result.get(path[-1], default_value)


def calibration_set(path, value):
    global default_values, default_value, dictionary, parent_key, calibration_defaults, calib_file, calib_text, calib_map
    # set the value in a nested dictionary structure
    # "CATEGORY.SECTION.name", "value"
    # sets the value stored as
    #
    # {
    #     "CATEGORY": {
    #         "SECTION": {
    #             "name": "value"
    #         }
    #     }
    # }
    #
    #
    #

    if isinstance(path, str):
        path = path.split(".")
    result = calib_map
    for key in path[:-1]:
            result = result.setdefault(key, {})
    result[path[-1]] = value


def calibration_get_flattened():
    global default_values, path, default_value, value, dictionary, parent_key, calibration_defaults, calib_file, calib_text, calib_map
    return _calibration_flatten(calib_map, None)


def _calibration_flatten(dictionary, parent_key):
    global default_values, path, default_value, value, calibration_defaults, calib_file, calib_text, calib_map
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + "." + key if parent_key else key
        if isinstance(value, dict):
            items.extend(_calibration_flatten(value, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


