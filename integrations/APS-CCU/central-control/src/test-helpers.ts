import { AsyncMqttClient } from 'async-mqtt';
import * as localMqtt from './mqtt/mqtt';

/**
 * This function creates a mocked version of the {import('async-mqtt').AsyncMqttClient} and returns it.
 * Additionally it mocks the getMqttClient function from the mqtt module.
 * In addition, the mock includes spies on the publish and subscribe functions.
 *
 * @returns {import('async-mqtt').AsyncMqttClient}
 */
export function createMockMqttClient(): AsyncMqttClient {
  // mock the mqtt client
  jest.mock('async-mqtt');
  const mqtt = {
    publish: jest.fn(() => Promise.resolve()),
    subscribe: jest.fn(() => Promise.resolve()),
    on: jest.fn(),
  } as unknown as AsyncMqttClient;
  jest.spyOn(localMqtt, 'getMqttClient').mockReturnValue(mqtt);
  return mqtt;
}
