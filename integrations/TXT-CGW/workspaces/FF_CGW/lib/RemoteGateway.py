import datetime
import json
import logging
import threading
import time
from fischertechnik.mqtt.Constants import CONTROLLER_ID
from fischertechnik.mqtt.Constants import CONTROLLER_ID
from fischertechnik.mqtt.FTCloudClient import FTCloudClient
from fischertechnik.mqtt.FTCloudClient import FTCloudClient
from fischertechnik.mqtt.MqttClient import MqttClient
from lib.display import *
from lib.Factory_Variables import *
from lib.mqtt_utils import *

_tr0 = None
_tr = None
_dg = None
msg = None
unexpected = None
result_code = None
topic = None
mqtt_client = None
r = None
CLOUD_CONNECTED = None
TOPIC_TIMESTAMP_CACHE = None
localControllerPrefix = None
_new_topic = None
_new_message = None
ffCloudTopicPrefix = None
def _gateway_check_connections():
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    while True:
        CLOUD_CONNECTED = FTCloudClient.getInstance().is_connected()
        display.set_attr("txt_status_cloud.active", str(FTCloudClient.getInstance().is_connected()).lower())
        if not (FTCloudClient.getInstance().is_connected()):
            try:
                _fischertechnik_cloud_setup()
            except:
                logging.warn("Error while creating cloud connection")
        time.sleep(5)



def initlog_RGW(_tr0, _tr, _dg):
    global msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    logging.TRACE0_RGW = _tr0
    logging.addLevelName(logging.TRACE0_RGW , 'TRACE0_RGW')
    logging.TRACE_RGW = _tr
    logging.addLevelName(logging.TRACE_RGW , 'TRACE_RGW')
    logging.DEBUG_RGW = _dg
    logging.addLevelName(logging.DEBUG_RGW, 'DEBUG_RGW')


def RGW_publish_to_cloud_handler(message):
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    topic = message.topic
    logging.log(logging.TRACE_RGW, "Message received from topic [%s]", topic)
    if topic.startswith(localControllerPrefix):
        topic = topic[len(localControllerPrefix):]
        if not (topic.startswith("f/i/") or topic.startswith("i/")):
            logging.log(logging.TRACE_RGW, "Not forwarding local only topic [%s]", topic)
            return
    elif topic.startswith('/j1/txt/'):
        logging.log(logging.TRACE_RGW, "Not forwarding invalid topic [%s]", topic)
        return

    newTopic = "/j1/txt/" + str(CONTROLLER_ID) + "/" + topic;
    logging.log(logging.TRACE_RGW, "Sending message to topic [%s]", newTopic)
    FTCloudClient.getInstance().publish(newTopic, message.payload.decode('utf-8'))



def gateway_setup():
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    logging.log(logging.TRACE_RGW, '-')
    TOPIC_TIMESTAMP_CACHE = json.loads('{}')
    localControllerPrefix = '/j1/txt/1/'
    ffCloudTopicPrefix = ''
    ffCloudTopicPrefix = "/j1/txt/" + str(CONTROLLER_ID) + "/"
    setup_aps_connection()
    clear_txt_labels()
    setup_cloud_connection()
    clear_txt_labels()
    threading.Thread(target=_gateway_check_connections, daemon=True).start()
    set_cloud_active(True)


def _RGW_message_from_cloud(msg):
    global _tr0, _tr, _dg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    logging.log(logging.TRACE_RGW, "Cloud message received from topic [%s]", msg.topic)
    _new_topic = msg.topic[len(ffCloudTopicPrefix):]
    _new_message = msg.payload.decode("utf-8")
    if not gateway_is_new_command(msg.topic, _new_message):
        logging.log(logging.TRACE_RGW, "Skip duplicate message [%s]", msg.topic)
        return
    if not (_new_topic.startswith("ccu") or _new_topic.startswith("module") or _new_topic.startswith("fts")):
        _new_topic = localControllerPrefix + _new_topic
    mqtt_get_client().publish(topic=_new_topic, payload=_new_message, qos=2, retain=False)


def clear_txt_labels():
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    display.set_attr("txt_label_message.text", str(''))
    display.set_attr("txt_label_message2.text", str(''))


def setup_aps_connection():
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    display.set_attr("txt_label_message.text", str('Connecting to APS...'))
    mqtt_get_client().set_disconnect_callback(handle_mqtt_disconnected)
    mqtt_get_client().set_connect_callback(handle_mqtt_connected)
    mqtt_connect_always()
    display.set_attr("txt_label_message.text", str('Connected to APS'))
    print('--------------------------------------- Broker connected')
    setup_mqtt_subscriptions(mqtt_get_client())


def handle_mqtt_disconnected(unexpected):
    global _tr0, _tr, _dg, msg, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    display.set_attr("txt_status_connected.active", str(False).lower())
    display.set_attr("txt_label_message.text", str('Disconnected from APS'))
    if unexpected:
        display.set_attr("txt_label_message2.text", str('due to unexpected reasons'))
    else:
        print('---------- MQTT: Disconnected')


def setup_cloud_connection():
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    FTCloudClient.getInstance().subscribe(ffCloudTopicPrefix + 'ccu/order/request', _RGW_message_from_cloud)
    FTCloudClient.getInstance().subscribe(ffCloudTopicPrefix + 'ccu/order/cancel', _RGW_message_from_cloud)
    FTCloudClient.getInstance().subscribe(ffCloudTopicPrefix + 'ccu/pairing/pair_fts', _RGW_message_from_cloud)
    FTCloudClient.getInstance().subscribe(ffCloudTopicPrefix + 'ccu/set/#', _RGW_message_from_cloud)
    FTCloudClient.getInstance().subscribe(ffCloudTopicPrefix + 'f/o/#', _RGW_message_from_cloud)
    FTCloudClient.getInstance().subscribe(ffCloudTopicPrefix + 'o/broadcast', _RGW_message_from_cloud)
    FTCloudClient.getInstance().subscribe(ffCloudTopicPrefix + 'o/ptu', _RGW_message_from_cloud)
    FTCloudClient.getInstance().subscribe(ffCloudTopicPrefix + 'c/#', _RGW_message_from_cloud)
    for count in range(15):
        display.set_attr("txt_label_message.text", str('Connecting to Cloud...'))
        try:
            _fischertechnik_cloud_setup()
        except:
            logging.warn("Error while creating cloud connection")
            display.set_attr("txt_label_message.text", str('Error while connecting to Cloud'))
        if FTCloudClient.getInstance().is_connected():
            print('--------------------------------------- Cloud connected')
            display.set_attr("txt_label_message.text", str('Connected to Cloud'))
            break
        time.sleep(2)
    time.sleep(1)


def handle_mqtt_connected(result_code):
    global _tr0, _tr, _dg, msg, unexpected, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    clear_txt_labels()
    display.set_attr("txt_status_connected.active", str(False).lower())
    if not result_code:
        display.set_attr("txt_status_connected.active", str(True).lower())
        display.set_attr("txt_label_message.text", str('Connected to APS'))
        time.sleep(2)
        clear_txt_labels()


def gateway_is_new_command(topic, msg):
    global _tr0, _tr, _dg, unexpected, result_code, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    if not CLOUD_CONNECTED:
        return False
    _message_data = {}
    try:
        _message_data = json.loads(msg)
    except json.JSONDecodeError:
        return False

    # Ignore lists for topic "ccu/order/cancel" and return true
    if isinstance(_message_data, list) and "ccu/order/cancel" in topic:
        return True

    _timestamp = _message_data.get("ts") or _message_data.get("timestamp")
    if not (topic in TOPIC_TIMESTAMP_CACHE) or (_timestamp is None) or (_timestamp != TOPIC_TIMESTAMP_CACHE.get(topic)):
        TOPIC_TIMESTAMP_CACHE[topic] = _timestamp
        return True
    return False


def _fischertechnik_cloud_setup():
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    FTCloudClient.getInstance().connect()


def setup_mqtt_subscriptions(mqtt_client):
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    mqtt_client.subscribe(topic='ccu/order/response', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='ccu/order/active', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='ccu/order/completed', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='ccu/pairing/state', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='ccu/state/#', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='fts/v1/ff/+/connection', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='fts/v1/ff/+/state', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='fts/v1/ff/+/factsheet', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='module/v1/ff/+/connection', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='module/v1/ff/+/state', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic='module/v1/ff/+/factsheet', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic=str(localControllerPrefix) + 'f/i/#', callback=RGW_publish_to_cloud_handler, qos=1)
    mqtt_client.subscribe(topic=str(localControllerPrefix) + 'i/#', callback=RGW_publish_to_cloud_handler, qos=1)


def gateway_timestamp():
    global _tr0, _tr, _dg, msg, unexpected, result_code, topic, mqtt_client, r, CLOUD_CONNECTED, TOPIC_TIMESTAMP_CACHE, localControllerPrefix, _new_topic, _new_message, ffCloudTopicPrefix
    logging.log(logging.TRACE0_RGW, '-')
    r = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return r


