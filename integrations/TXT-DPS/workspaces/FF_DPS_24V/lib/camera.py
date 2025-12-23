# auto generated content from camera configuration
from lib.controller import *
import fischertechnik.factories as txt_factory

TXT_M_USB1_1_camera.set_rotate(False)
TXT_M_USB1_1_camera.set_height(240)
TXT_M_USB1_1_camera.set_width(320)
TXT_M_USB1_1_camera.set_fps(15)
TXT_M_USB1_1_camera.start()

motion_detector = txt_factory.camera_factory.create_motion_detector(0, 0, 320, 240, 1)
TXT_M_USB1_1_camera.add_detector(motion_detector)

