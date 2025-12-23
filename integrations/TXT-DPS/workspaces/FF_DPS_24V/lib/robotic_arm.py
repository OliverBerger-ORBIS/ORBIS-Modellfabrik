import json
import logging
import math
import numpy as np
import os
import time
import yaml
from lib.calibration_data import calibration_get
from lib.controller import *
from lib.controller import *
from robotic_arm.kinematic import Kinematic, KinematicConfig
from robotic_arm.robot import AxesConfig, RobotArm
from robotic_arm.transform import Transform
from threading import RLock

config = None
pos_name = None
wait_s = None
lockRA = None
def move_ptp(pos_name, wait_s):
    global config, lockRA
    try:
        lockRA.acquire()
        location = robot_calibration_get(pos_name)
        transform_pos = Transform().rotate_x(np.radians(180)).translate(location)
        pos = None
        # reimplementation of pos_cartesian to
        # enable throwing an exception when the target is unreachable instead of silently failing
        try:
            pos = robot_arm.kinematic.backward(transform_pos)
        except BaseException as e:
            print("TCP can not be reached")
            raise ValueError('TCP is unreachable')
        if not pos:
            raise ValueError('TCP can not be calculated')
        robot_arm.pos(pos)
        time.sleep(wait_s)
    finally:
        lockRA.release()



def init_robotic_arm():
    global config, pos_name, wait_s, lockRA
    # copy lib to TXT 4.0 controller:
    # from:
    #  - ff-modul-dps/robotic_arm
    #  - https://github.com/dmholtz/ft_robot/tree/ft_dps/robotic_arm/
    # to:
    #  - /usr/lib/python3.5/site-packages/robotic_arm
    global robot_arm, listpos, calibration_names
    robot_setup_defaults()
    calibration_names = {
        'home1':  "RA.HOME.BASE",
        'home2': "RA.HOME.INPUT", #home for din, cs, nfc, nio
        'home3': "RA.HOME.OUTPUT", #home for fts, dout

        'dinp':    "RA.INPUT.PICK.APPROACH_A",
        'dinp2':    "RA.INPUT.PICK.APPROACH_B",
        'dinp3':  "RA.INPUT.PICK.TARGET",

        'dind':    "RA.INPUT.DROP.APPROACH_A",
        'dind2':    "RA.INPUT.DROP.APPROACH_B",
        'dind3':  "RA.INPUT.DROP.TARGET",

        'nfc':      "RA.NFC.APPROACH",
        'nfc2':    "RA.NFC.TARGET",

        'cs':         "RA.CS.APPROACH",
        'cs2':       "RA.CS.TARGET",

        'nio':       "RA.NIO.APPROACH",
        'nio2':    "RA.NIO.TARGET",

        'ftsd1':  "RA.FTS.DROP.APPROACH_A",
        'ftsd2':  "RA.FTS.DROP.APPROACH_B",
        'ftsd3':  "RA.FTS.DROP.TARGET",

        'ftsp1':  "RA.FTS.PICK.APPROACH_A",
        'ftsp2':  "RA.FTS.PICK.APPROACH_B",
        'ftsp3':  "RA.FTS.PICK.TARGET",

        'doutd': "RA.OUTPUT.DROP.APPROACH_A",
        'doutd2': "RA.OUTPUT.DROP.APPROACH_B",
        'doutd3':  "RA.OUTPUT.DROP.TARGET",

        'doutp': "RA.OUTPUT.PICK.APPROACH_A",
        'doutp2': "RA.OUTPUT.PICK.APPROACH_B",
        'doutp3':  "RA.OUTPUT.PICK.TARGET"
    }
    logging.basicConfig(level=logging.DEBUG)

    #TODO: rename .json to .txt -> bug in RPC 6.1.3
    from os.path import dirname
    path = dirname(__file__) + "/.."
    with open(path + "/data/robot_config.json") as f:
        robot_config = yaml.safe_load(f)
    robot_config_add_servo_calib(robot_config)

    axes_config = AxesConfig(**robot_config["axes"])
    kinematic_config = KinematicConfig(**robot_config["kinematic"])
    kinematic = Kinematic(kinematic_config)
    lockRA = RLock()

    robot_arm = RobotArm(axes_config, kinematic)
    moveRefHome()


def get_lock_RA():
    global config, pos_name, wait_s, lockRA
    logging.debug('-')
    return lockRA


def robot_calibration_get_defaults():
    global config, pos_name, wait_s, lockRA
    robot_setup_defaults()
    return {
        "RA": {
            "HOME": {
                "BASE": {
                    "X": listpos["home1"][0], "Y": listpos["home1"][1], "Z": listpos["home1"][2]
                },
                "INPUT": {
                    "X": listpos["home2"][0], "Y": listpos["home2"][1], "Z": listpos["home2"][2]
                },
                "OUTPUT": {
                    "X": listpos["home3"][0], "Y": listpos["home3"][1], "Z": listpos["home3"][2]
                }
            },
            "INPUT": {
                "PICK": {
                    "APPROACH_A": {
                        "X": listpos["dinp"][0], "Y": listpos["dinp"][1], "Z": listpos["dinp"][2]
                    },
                    "APPROACH_B": {
                        "X": listpos["dinp2"][0], "Y": listpos["dinp2"][1], "Z": listpos["dinp2"][2]
                    },
                    "TARGET": {
                        "X": listpos["dinp3"][0], "Y": listpos["dinp3"][1], "Z": listpos["dinp3"][2]
                    }
                },
                 "DROP": {
                    "APPROACH_A": {
                        "X": listpos["dind"][0], "Y": listpos["dind"][1], "Z": listpos["dind"][2]
                    },
                    "APPROACH_B": {
                        "X": listpos["dind2"][0], "Y": listpos["dind2"][1], "Z": listpos["dind2"][2]
                    },
                    "TARGET": {
                        "X": listpos["dind3"][0], "Y": listpos["dind3"][1], "Z": listpos["dind3"][2]
                    }
                }
            },
            "NFC": {
                "APPROACH": {
                    "X": listpos["nfc"][0], "Y": listpos["nfc"][1], "Z": listpos["nfc"][2]
                },
                "TARGET": {
                    "X": listpos["nfc2"][0], "Y": listpos["nfc2"][1], "Z": listpos["nfc2"][2]
                }
            },
            "CS": {
                "APPROACH": {
                    "X": listpos["cs"][0], "Y": listpos["cs"][1], "Z": listpos["cs"][2]
                },
                "TARGET": {
                    "X": listpos["cs2"][0], "Y": listpos["cs2"][1], "Z": listpos["cs2"][2]
                }
            },
            "NIO": {
                "APPROACH": {
                    "X": listpos["nio"][0], "Y": listpos["nio"][1], "Z": listpos["nio"][2]
                },
                "TARGET": {
                    "X": listpos["nio2"][0], "Y": listpos["nio2"][1], "Z": listpos["nio2"][2]
                }
            },
            "FTS": {
                "PICK": {
                    "APPROACH_A": {
                        "X": listpos["ftsp1"][0], "Y": listpos["ftsp1"][1], "Z": listpos["ftsp1"][2]
                    },
                    "APPROACH_B": {
                        "X": listpos["ftsp2"][0], "Y": listpos["ftsp2"][1], "Z": listpos["ftsp2"][2]
                    },
                    "TARGET": {
                        "X": listpos["ftsp3"][0], "Y": listpos["ftsp3"][1], "Z": listpos["ftsp3"][2]
                    }
                },
                 "DROP": {
                    "APPROACH_A": {
                        "X": listpos["ftsd1"][0], "Y": listpos["ftsd1"][1], "Z": listpos["ftsd1"][2]
                    },
                    "APPROACH_B": {
                        "X": listpos["ftsd2"][0], "Y": listpos["ftsd2"][1], "Z": listpos["ftsd2"][2]
                    },
                    "TARGET": {
                        "X": listpos["ftsd3"][0], "Y": listpos["ftsd3"][1], "Z": listpos["ftsd3"][2]
                    }
                }
            },
            "OUTPUT": {
                "PICK": {
                    "APPROACH_A": {
                        "X": listpos["doutp"][0], "Y": listpos["doutp"][1], "Z": listpos["doutp"][2]
                    },
                    "APPROACH_B": {
                        "X": listpos["doutp2"][0], "Y": listpos["doutp2"][1], "Z": listpos["doutp2"][2]
                    },
                    "TARGET": {
                        "X": listpos["doutp3"][0], "Y": listpos["doutp3"][1], "Z": listpos["doutp3"][2]
                    }
                },
                 "DROP": {
                    "APPROACH_A": {
                        "X": listpos["doutd"][0], "Y": listpos["doutd"][1], "Z": listpos["doutd"][2]
                    },
                    "APPROACH_B": {
                        "X": listpos["doutd2"][0], "Y": listpos["doutd2"][1], "Z": listpos["doutd2"][2]
                    },
                    "TARGET": {
                        "X": listpos["doutd3"][0], "Y": listpos["doutd3"][1], "Z": listpos["doutd3"][2]
                    }
                }
            }
        }
    }


def robot_config_add_servo_calib(config):
    global pos_name, wait_s, lockRA
    if not os.path.exists("/opt/ft/workspaces/ServoCalib_DPS.json"):
        return
    with open("/opt/ft/workspaces/ServoCalib_DPS.json") as f:
        # {"servo_degree_S1": 85.4296875, "servo_degree_S3": 84.7265625, "servo_degree_S2": 93.515625, "ts": "2023-11-08T17:00:27.138Z"}
        try:
            servo_data = json.loads(f.read())
            # the calibration values do not include the kinematic direction, so copy the sign from the old value
            newval = servo_data["servo_degree_S1"]
            oldval = config["axes"]["axis4"]["degree_offset"]
            config["axes"]["axis4"]["degree_offset"] = 180 - math.copysign(newval, oldval)
            newval = servo_data["servo_degree_S2"]
            oldval = config["axes"]["axis5"]["degree_offset"]
            config["axes"]["axis5"]["degree_offset"] = 180 - math.copysign(newval, oldval)
            newval = servo_data["servo_degree_S3"]
            oldval = config["axes"]["axis6"]["degree_offset"]
            config["axes"]["axis6"]["degree_offset"] = math.copysign(newval, oldval)
        except Exception as error:
            return


def robot_setup_defaults():
    global config, pos_name, wait_s, lockRA
    global listpos
    listpos = {
        'home1': [ -100,  -10,  130],
        'home2': [  -60, -100,  130], #home for din, cs, nfc, nio
        'home3': [  100,   10,  130], #home for fts, dout

        'dinp':    [-106, -209, 100],
        'dinp2':    [-106, -208, 85],
        'dinp3':  [-96, -193,  58],

        'dind':    [-100, -224, 100],
        'dind2':  [-100, -224, 92],
        'dind3':  [-100, -226, 65],

        'nfc':      [15, -210, 110],
        'nfc2':    [15, -205, 75],

        'cs':        [ -38, -206, 110],
        'cs2':      [ -39, -205,  76],

        'nio':       [  50, -155, 100],
        'nio2':    [  35, -145,  70],

        'ftsd1':  [ 117,  167, 110],
        'ftsd2':  [ 134,  165, 110],
        'ftsd3':  [ 134,  171,  88],

        'ftsp1':  [ 132,  100, 110],
        'ftsp2':  [ 139,  171, 110],
        'ftsp3':  [ 139,  174,  75],

        'doutd': [ 110,  -195, 110],
        'doutd2': [ 110,  -210, 90],
        'doutd3':  [ 90,  -180,  80],

        'doutp': [ 110,  -195, 110],
        'doutp2': [ 110,  -195, 90],
        'doutp3':  [ 110,  -185,  70]
    }


def moveRefHome():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    robot_arm.reference()
    time.sleep(1)
    robot_arm.home()
    time.sleep(1)
    lockRA.release()


def moveRefPark():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    robot_arm.reference()
    time.sleep(1)
    lockRA.release()


def robot_calibration_get(pos_name):
    global config, wait_s, lockRA
    position = calibration_names[pos_name]
    x = calibration_get(position + ".X", None)
    y = calibration_get(position + ".Y", None)
    z = calibration_get(position + ".Z", None)
    print([x, y, z])
    if x and y and z:
        return [x, y, z]
    return listpos[pos_name]


def grip():
    global config, pos_name, wait_s, lockRA
    TXT_M_O7_compressor.on()
    time.sleep(1)
    TXT_M_O8_magnetic_valve.on()
    time.sleep(1)


def gripOnce():
    global config, pos_name, wait_s, lockRA
    TXT_M_O7_compressor.on()
    time.sleep(1)
    TXT_M_O8_magnetic_valve.on()
    time.sleep(2)
    TXT_M_O7_compressor.off()


def drop():
    global config, pos_name, wait_s, lockRA
    TXT_M_O7_compressor.off()
    TXT_M_O8_magnetic_valve.off()
    time.sleep(1)


def dropGrip():
    global config, pos_name, wait_s, lockRA
    drop()
    time.sleep(1)
    grip()


def din2cs1():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    move_ptp('home1', 0)
    move_ptp('home2', 0)

    move_ptp('dinp', 0)
    move_ptp('dinp2', 0)
    move_ptp('dinp3', 1)
    grip()
    move_ptp('dinp2', 0)
    move_ptp('dinp', 0)

    move_ptp('cs',  0)
    move_ptp('cs2', 1)
    drop()
    lockRA.release()


def cs2nfc1():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    dropGrip()
    move_ptp('cs', 0)

    move_ptp('nfc', 0)
    move_ptp('nfc2',  1)
    lockRA.release()


def din2nfc():
    global config, pos_name, wait_s, lockRA
    din2cs1()
    cs2nfc1()
    dropGrip()
    move_ptp('nfc', 0)


def din2nio():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    din2nfc()

    move_ptp('nio', 0)
    move_ptp('nio2', 1)
    drop()

    lockRA.release()


def nio2homeRef2():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    move_ptp('home1', 0)
    lockRA.release()
    moveRefHome()


def nfc2nio():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    move_ptp('nfc', 0)

    move_ptp('nio', 0)
    move_ptp('nio2', 1)
    drop()

    lockRA.release()


def din2fts():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    din2nfc()

    move_ptp('home3', 0)

    move_ptp('ftsd1', 0)
    move_ptp('ftsd2', 0)
    move_ptp('ftsd3', 1)
    drop()
    move_ptp('ftsd2', 0)
    move_ptp('ftsd1', 0)
    lockRA.release()


def fts2homeRef():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    move_ptp('home3', 0)
    move_ptp('home1', 0)
    lockRA.release()
    moveRefHome()


def nfc2fts():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    move_ptp('nfc', 0)

    move_ptp('home3', 0)

    move_ptp('ftsd1', 0)
    move_ptp('ftsd2', 0)
    move_ptp('ftsd3', 1)
    drop()
    move_ptp('ftsd2', 0)
    move_ptp('ftsd1', 0)
    lockRA.release()


def fts2dout():
    global config, pos_name, wait_s, lockRA
    global robot_arm
    lockRA.acquire()
    robot_arm.home()

    move_ptp('home1', 0)
    move_ptp('home2', 0)
    move_ptp('home3', 0)

    move_ptp('ftsp1', 0)
    move_ptp('ftsp2', 0)
    move_ptp('ftsp3', 1)
    grip()
    move_ptp('ftsp2', 0)
    move_ptp('ftsp1', 0)

    move_ptp('home3', 0)

    move_ptp('doutd', 0)
    move_ptp('doutd2', 0)
    move_ptp('doutd3', 1)
    drop()
    move_ptp('doutd2', 0)
    move_ptp('doutd', 0)

    move_ptp('home2', 0)
    robot_arm.home()
    lockRA.release()
    moveRefHome()


def fts2nfc1():
    global config, pos_name, wait_s, lockRA
    global robot_arm
    lockRA.acquire()
    robot_arm.home()

    move_ptp('home1', 0)
    move_ptp('home2', 0)
    move_ptp('home3', 0)

    move_ptp('ftsp1', 0)
    move_ptp('ftsp2', 0)
    move_ptp('ftsp3', 1)
    grip()
    move_ptp('ftsp2', 0)
    move_ptp('ftsp1', 0)

    move_ptp('home3', 0)

    move_ptp('nfc', 0)
    move_ptp('nfc2',  1)
    lockRA.release()


def dout2homeRef():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    move_ptp('home2', 0)
    lockRA.release()
    moveRefHome()


def nfc2dout():
    global config, pos_name, wait_s, lockRA
    global robot_arm
    lockRA.acquire()
    move_ptp('nfc', 0)

    move_ptp('home3', 0)

    move_ptp('doutd', 0)
    move_ptp('doutd2', 0)
    move_ptp('doutd3', 1)
    drop()
    move_ptp('doutd2', 0)
    move_ptp('doutd', 0)

    lockRA.release()


def din2dout():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    move_ptp('home2', 0)

    move_ptp('dinp', 0)
    move_ptp('dinp2', 0)
    move_ptp('dinp3', 1)
    grip()
    move_ptp('dinp2', 0)
    move_ptp('dinp', 0)

    move_ptp('home2', 0)

    move_ptp('doutd', 0)
    move_ptp('doutd2', 0)
    move_ptp('doutd3', 1)
    drop()
    move_ptp('doutd2', 0)
    move_ptp('doutd', 0)

    move_ptp('home2', 0)
    lockRA.release()


def dout2din():
    global config, pos_name, wait_s, lockRA
    lockRA.acquire()
    move_ptp('home2', 0)

    move_ptp('doutp', 0)
    move_ptp('doutp2', 0)
    move_ptp('doutp3', 1)
    grip()
    move_ptp('doutp2', 0)
    move_ptp('doutp', 0)

    move_ptp('home2', 0)

    move_ptp('dind', 0)
    move_ptp('dind2', 0)
    move_ptp('dind3', 1)
    drop()
    move_ptp('dind2', 0)
    move_ptp('dind', 0)

    move_ptp('home2', 0)
    lockRA.release()


