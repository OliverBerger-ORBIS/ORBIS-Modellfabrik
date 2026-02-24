import { AsyncMqttClient } from 'async-mqtt';
import { PairedModule } from '../../../../common/protocol/ccu';
import { InstantAction, InstantActions } from '../../../../common/protocol/vda';
import { getMqttClient } from '../../mqtt/mqtt';
import { createMockMqttClient } from '../../test-helpers';
import { requestFactsheet } from './factsheets';

jest.mock('uuid', () => ({ v4: () => '12345-6789-ABCDEF' }));

describe('Test requesting and recieving factsheets', () => {
  let mqtt: AsyncMqttClient;
  const MOCKED_DATE = new Date('2023-02-010T10:20:19Z');

  beforeEach(() => {
    mqtt = createMockMqttClient();
    jest.useFakeTimers().setSystemTime(MOCKED_DATE);
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it('should be able to request an factshet', async () => {
    const module: PairedModule = {
      type: 'MODULE',
      serialNumber: 'mockedSerial',
    };
    await requestFactsheet(module);
    const topic = `module/v1/ff/mockedSerial/instantAction`;
    const action: InstantAction = {
      timestamp: MOCKED_DATE,
      serialNumber: module.serialNumber,
      actions: [{ actionId: '12345-6789-ABCDEF', actionType: InstantActions.FACTSHEET_REQUEST }],
    };

    expect(mqtt.publish).toHaveBeenCalledWith(topic, JSON.stringify(action), { qos: 2 });
    expect(getMqttClient).toHaveBeenCalled();
  });
});
