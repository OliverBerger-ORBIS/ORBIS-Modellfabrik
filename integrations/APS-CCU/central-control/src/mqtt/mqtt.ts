import { AsyncMqttClient } from 'async-mqtt';
import config from '../config';
import * as MQTT from 'async-mqtt';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export { AsyncMqttClient } from 'async-mqtt';

let mqttClient: AsyncMqttClient;

/**
 * Connects to the configured MQTT broker
 *
 * The connection is retried a configurable amount, by default 10 times with a delay of 500ms.
 * They retry is necessary if the mqtt broker starts slower than this control unit
 */
export async function connectMqtt(): Promise<AsyncMqttClient> {
  if (mqttClient) {
    return mqttClient;
  }

  let error = null;
  for (let tries = 0; tries < config.mqtt.init_retries; tries++) {
    console.debug(`Starting MQTT on [${config.mqtt.url}] - Try ${tries + 1} of ${config.mqtt.init_retries} retries`);
    try {
      const mqtt = await MQTT.connectAsync(config.mqtt.url, {
        username: config.mqtt.user,
        password: config.mqtt.pass,
      });
      if (mqtt) {
        mqttClient = mqtt;
        return mqttClient;
      }
    } catch (e) {
      console.info('Attempt failed, waiting ' + config.mqtt.init_retry_delay);
      await delay(config.mqtt.init_retry_delay);
      error = e;
    }
  }
  throw error ?? new Error('Unable to connect to mqtt');
}

export const getMqttClient = (): AsyncMqttClient => {
  return mqttClient;
};
