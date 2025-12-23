import json
import os
import paho.mqtt.client as mqtt
import time
from fischertechnik.mqtt.MqttClient import MqttClient

topic = None
payload = None
result_code = None
mqtt_config_file = None
mqtt_connection = None
mqtt_controller_id = None
temp = None
mqtt_config = None
def _mqtt_create_client():
    global topic, payload, result_code, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    class FFMqttClient(MqttClient):
        def __init__(self, client_id="", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp", path="/"):
            MqttClient.__init__(self, client_id, clean_session, userdata, protocol, transport, path)
            self.connect_handler = None
            self.disconnect_handler = None
            self.connectionbroken = False
            self.__original_on_disconnect = self.paho_client.on_disconnect
            self.__original_on_connect = self.paho_client.on_connect
            self.paho_client.on_disconnect = self.__on_disconnect
            self.paho_client.on_connect = self.__on_connect

        def __del__(self):
            MqttClient.__del__(self)

        # takes callback: connect_callback(result_code: int)
        def set_connect_callback(self, handler):
            self.connect_handler = handler

        # takes callback: disconnect_callback(unexpected: bool)
        def set_disconnect_callback(self, handler):
            self.disconnect_handler = handler

        def __on_connect(self, client, userdata, flags, rc):
            self.__original_on_connect(client, userdata, flags, rc)
            # the connection migh not be sucessfully established. rc will contain the reason as an error code
            print ("CONNECT", rc, mqtt_connect_result_to_string(rc))
            if rc == 0:
                self.connectionbroken = False
            if callable(self.connect_handler):
                self.connect_handler(rc)

        def __on_disconnect(self, client, userdata, rc):
            self.__original_on_disconnect(client, userdata, rc)
            # according to documentation, rc != 0 is an unexpected disconnect.
            print ("DISCONNECT", rc)
            if rc != 0:
                self.connectionbroken = True
            if callable(self.disconnect_handler):
                self.disconnect_handler(rc != 0)

    return  FFMqttClient()



def mqtt_load_config():
    global topic, payload, result_code, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    mqtt_config_file = open(os.path.join(os.path.dirname(__file__), '../data/config.json'), 'r', encoding='utf8')
    mqtt_config = (json.loads(mqtt_config_file.read()))['mqtt']
    mqtt_config_file.close()


def mqtt_get_client():
    global topic, payload, result_code, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    if mqtt_connection:
        return mqtt_connection
    mqtt_connection = _mqtt_create_client()
    return mqtt_connection


def mqtt_connect():
    global topic, payload, result_code, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    mqtt_load_config()
    mqtt_get_client().connect(host=mqtt_config['host'], port=mqtt_config['port'], user=mqtt_config['username'], password=mqtt_config['password'])


def mqtt_publish(topic, payload):
    global result_code, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    mqtt_connection.publish(topic=topic, payload=payload, qos=2, retain=True)


def mqtt_get_id():
    global topic, payload, result_code, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    if not mqtt_controller_id:
        mqtt_controller_id = 0
    return mqtt_controller_id


# Retry until an initial connection has been accepted
# Do not abort on network errors, but repeat until the the server is found
def mqtt_connect_always():
    global topic, payload, result_code, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    # do not rely on mqtt_get_client().is_connected() to detect success.
    # the documentation does not guarantee that the on_connect-callback is called before mqtt_connect returns
    # that might cause a race condition resulting in continous reconnects.
    _not_connected = True
    while _not_connected == True:
        try:
            mqtt_connect()
            _not_connected = False
        except OSError as error:
            print("Error while connecting to mqtt. Retrying", error)
            time.sleep(1)


def mqtt_connect_result_to_string(result_code):
    global topic, payload, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    _results = [
        'Connection successful',
        'Connection refused – incorrect protocol version',
        'Connection refused – invalid client identifier',
        'Connection refused – server unavailable',
        'Connection refused – bad username or password',
        'Connection refused – not authorised'
    ]
    if result_code >= 0 and result_code <= 5:
        return _results[int(result_code)]
    return 'Unknown connection error'


def mqtt_wait_connected():
    global topic, payload, result_code, mqtt_config_file, mqtt_connection, mqtt_controller_id, temp, mqtt_config
    temp = mqtt_get_client()
    while not (temp.is_connected()):
        time.sleep(0.1)


