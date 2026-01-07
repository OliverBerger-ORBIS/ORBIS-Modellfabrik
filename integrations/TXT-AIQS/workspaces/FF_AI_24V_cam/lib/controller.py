import fischertechnik.factories as txt_factory

txt_factory.init()
txt_factory.init_output_factory()
txt_factory.init_usb_factory()
txt_factory.init_camera_factory()


TXT_SLD_M = txt_factory.controller_factory.create_graphical_controller()
TXT_SLD_M_O4_led = txt_factory.output_factory.create_led(TXT_SLD_M, 4)
TXT_SLD_M_USB1_1_camera = txt_factory.usb_factory.create_camera(TXT_SLD_M, 1)

txt_factory.initialized()