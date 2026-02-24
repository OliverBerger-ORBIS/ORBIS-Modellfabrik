import { AsyncMqttClient, IClientSubscribeOptions } from 'async-mqtt';
import { readFile, writeFile } from 'node:fs/promises';
import * as packageJson from '../package.json';

const generateRegexForTopicSub = (subscribedTopic: string): RegExp => {
  return new RegExp(`^${subscribedTopic}\$`.replaceAll('/+', '/\\w+').replace('/#', '/.+$').replaceAll('/', '\\/'));
};
export const matchTopics = (subscribedTopics: string | string[], topic: string): boolean => {
  if (Array.isArray(subscribedTopics)) {
    return subscribedTopics.map(st => generateRegexForTopicSub(st)).some(rg => rg.test(topic));
  } else {
    return generateRegexForTopicSub(subscribedTopics).test(topic);
  }
};

/**
 * Subscribe to provided mqtt topics by using the provided mqtt client and subscription options.
 * @param topics the topics to subscribe to
 * @param subscriptionOptions the subscription options to use
 * @param mqtt the mqtt client to use
 */
export const subscribeTopics = (topics: string[], subscriptionOptions: IClientSubscribeOptions, mqtt: AsyncMqttClient) => {
  if (!mqtt) {
    throw new Error('MQTT client not provided');
  }
  mqtt
    .subscribe(topics, subscriptionOptions)
    .then(grants => console.debug('Subscriptions :', grants))
    .catch(err => {
      console.error('FATAL', err);
      process.exit(1);
    });
};

/**
 * Listen to provided mqtt topics by using the provided mqtt client and callback.
 * The message is only handled if the topic matches one of the provided topics.
 * @param mqtt The mqtt client to use
 * @param topics The topics to listen to
 * @param callback The callback to call when a message is received on a topic
 */
export const listenToTopics = (mqtt: AsyncMqttClient, topics: string[], callback: (message: string) => Promise<void>) => {
  if (!mqtt) {
    throw new Error('MQTT client not provided');
  }
  mqtt.on('message', async (topic, payload: Buffer) => {
    const payloadAsString = payload.toString();
    try {
      if (matchTopics(topics, topic)) {
        await callback(payloadAsString);
      }
    } catch (error) {
      console.error('Error while handling message', payloadAsString, 'on topic', topic, ':', error);
    }
  });
};

/**
 * Writes an object as a JSON file.
 *
 * @param {string} filename - The name of the file to write.
 * @param {any} data - The object to write as JSON.
 */
export async function writeJsonFile(filename: string, data: unknown): Promise<void> {
  await writeFile(filename, JSON.stringify(data, undefined, 2), { encoding: 'utf8' });
}

/**
 * Reads a JSON file and returns the parsed object.
 *
 * @template T
 * @param {string} filename - The name of the file to read.
 * @returns {T} - The parsed JSON object.
 */
export async function readJsonFile<T>(filename: string): Promise<T> {
  const data = await readFile(filename, { encoding: 'utf8' });
  return JSON.parse(data);
}

/**
 * Reads the package version from the package.json file.
 */
export function getPackageVersion(): string {
  return packageJson?.version;
}
