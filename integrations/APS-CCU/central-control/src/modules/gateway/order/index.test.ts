import { TOPICS, handleMessage } from './index';
import * as mqttMock from '../../../mqtt/mqtt';
import { AsyncMqttClient } from 'async-mqtt';
import { CcuTopic, OrderRequest, Workpiece } from '../../../../../common/protocol';
describe('Test Gateway handler', () => {
  let mqttPublishSpy: jest.Mock;

  beforeEach(() => {
    mqttPublishSpy = jest.fn().mockImplementation(() => Promise.resolve());
    jest.spyOn(mqttMock, 'getMqttClient').mockReturnValue({ publish: mqttPublishSpy } as unknown as AsyncMqttClient);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  const testGatewayOrderType = async (workpieceType: Workpiece, timestampString: string) => {
    const givenGatewayOrder = `{"type": "${workpieceType}", "ts": "${timestampString}"}`;

    const expectedOrder: OrderRequest = {
      type: workpieceType,
      timestamp: new Date(timestampString),
      orderType: 'PRODUCTION',
    };

    await handleMessage(givenGatewayOrder);

    expect(mqttPublishSpy).toHaveBeenCalledWith(CcuTopic.ORDER_REQUEST, JSON.stringify(expectedOrder), { qos: 2 });
  };

  it('should have the correct topic to subscribe to', () => {
    const sourceTopic = '/j1/txt/1/f/o/order';
    expect(TOPICS).toContain(sourceTopic);
  });

  it('should send the correct order for a received cloud order for a RED workpiece', async () => {
    const timestampString = '2022-02-03T12:13:14.1234Z';
    const workpieceType = 'RED';

    await testGatewayOrderType(workpieceType, timestampString);
  });

  it('should send the correct order for a received cloud order for a WHITE workpiece', async () => {
    const timestampString = '2022-02-03T12:13:14.1234Z';
    const workpieceType = 'WHITE';

    await testGatewayOrderType(workpieceType, timestampString);
  });

  it('should send the correct order for a received cloud order for a BLUE workpiece', async () => {
    const timestampString = '2022-02-03T12:13:14.1234Z';
    const workpieceType = 'BLUE';
    await testGatewayOrderType(workpieceType, timestampString);
  });

  it('should not send an order for an incomplete request missing the timestamp', async () => {
    const workpieceType = 'BLUE';
    const givenGatewayOrder = `{"type": "${workpieceType}"}`;

    await handleMessage(givenGatewayOrder);
    expect(mqttPublishSpy).not.toHaveBeenCalled();
  });

  it('should not send an order for an incomplete request missing the workpiece', async () => {
    const timestampString = '2022-02-03T12:13:14.1234Z';
    const givenGatewayOrder = `{"ts": "${timestampString}"}`;

    await handleMessage(givenGatewayOrder);
    expect(mqttPublishSpy).not.toHaveBeenCalled();
  });
});
