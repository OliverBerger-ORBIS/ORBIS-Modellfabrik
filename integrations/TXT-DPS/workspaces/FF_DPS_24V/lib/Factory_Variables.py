import logging

client = None
state = None
value = None
client_local = None
factory_error_state = None
ALARM_TIMER = None
LDR_PERIOD = None
CAMERA_FPS = None
BME680_PERIOD = None
CAMERA_ON = None
INIT_FINISHED = None
KEEP_ALIVE = None
CLOUD_ACTIVE = None
ROBOT_ACTIVE = None
OUTPUT_ANNOUNCED = None
FACTORY_VERSION = None


def set_client_local(client):
    global state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    client_local = client


def get_client_local():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return client_local


def get_factory_error_state():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    logging.log(logging.TRACE0, factory_error_state)
    return factory_error_state


def set_factory_error_state(state):
    global client, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    logging.log(logging.TRACE, state)
    factory_error_state = state


def get_alarm_timer():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return ALARM_TIMER


def set_alarm_timer(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    ALARM_TIMER = value


def get_ldr_period():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return LDR_PERIOD


def set_ldr_period(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    LDR_PERIOD = value


def get_camera_fps():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return CAMERA_FPS


def set_camera_fps(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    CAMERA_FPS = value


def get_bme680_period():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return BME680_PERIOD


def set_bme680_period(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    BME680_PERIOD = value


def get_camera_on():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return CAMERA_ON


def set_camera_on(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    CAMERA_ON = value


def get_init_finished():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return INIT_FINISHED


def set_init_finished(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    INIT_FINISHED = value


def set_keep_alive(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    KEEP_ALIVE = value


def get_keep_alive():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return KEEP_ALIVE


def set_cloud_active(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    CLOUD_ACTIVE = value


def get_cloud_active():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return CLOUD_ACTIVE


def set_robot_active(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    ROBOT_ACTIVE = value


def get_robot_active():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return ROBOT_ACTIVE


def set_output_announced(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    OUTPUT_ANNOUNCED = value


def get_output_announced():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return OUTPUT_ANNOUNCED


def set_version(value):
    global client, state, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    FACTORY_VERSION = value


def get_version():
    global client, state, value, client_local, factory_error_state, ALARM_TIMER, LDR_PERIOD, CAMERA_FPS, BME680_PERIOD, CAMERA_ON, INIT_FINISHED, KEEP_ALIVE, CLOUD_ACTIVE, ROBOT_ACTIVE, OUTPUT_ANNOUNCED, FACTORY_VERSION
    return FACTORY_VERSION


