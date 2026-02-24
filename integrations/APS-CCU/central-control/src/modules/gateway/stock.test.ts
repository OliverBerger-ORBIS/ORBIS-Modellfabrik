import * as mqttMock from '../../mqtt/mqtt';
import { AsyncMqttClient } from 'async-mqtt';
import { publishGatewayStock } from './stock';
import { CloudStock } from '../../../../common/protocol/ccu';

describe('Test Gateway Stock publishing', () => {
  let mqttPublishSpy: jest.Mock;
  const MOCK_DATE = new Date('2022-02-03T11:12:13.1234Z');

  beforeEach(() => {
    mqttPublishSpy = jest.fn().mockImplementation(() => Promise.resolve());
    jest.spyOn(mqttMock, 'getMqttClient').mockReturnValue({ publish: mqttPublishSpy } as unknown as AsyncMqttClient);
    jest.useFakeTimers();
    jest.setSystemTime(MOCK_DATE);
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.restoreAllMocks();
  });

  it('should publish stock update', async () => {
    const stock: CloudStock = {
      ts: MOCK_DATE,
      stockItems: [
        { location: 'A3', workpiece: { id: 'wp1', type: 'BLUE', state: 'RAW' } },
        { location: 'B2', workpiece: { id: 'wp2', type: 'RED', state: 'RAW' } },
        { location: 'C1', workpiece: { id: 'wp5', type: 'WHITE', state: 'RAW' } },
      ],
    };
    await publishGatewayStock(stock);
    const expectedTopic = '/j1/txt/1/f/i/stock';
    const expectedMessage = JSON.stringify(stock);

    expect(mqttPublishSpy).toHaveBeenCalledWith(expectedTopic, expectedMessage, { retain: true, qos: 1 });
  });
});
