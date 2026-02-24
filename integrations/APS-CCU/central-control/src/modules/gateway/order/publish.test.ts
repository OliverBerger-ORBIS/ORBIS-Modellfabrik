import { publishGatewayOrderUpdate } from './publish';
import * as mqttMock from '../../../mqtt/mqtt';
import { AsyncMqttClient } from 'async-mqtt';
import { OrderResponse } from '../../../../../common/protocol';
import { OrderState } from '../../../../../common/protocol/ccu';
import { GatewayOrderStateEnum } from '../model';

describe('Test Gateway publishing', () => {
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

  it('should publish an in-progress order state when any order is in progress', async () => {
    const orders: OrderResponse[] = [
      {
        orderType: 'PRODUCTION',
        state: OrderState.CANCELLED,
        orderId: '1',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.ERROR,
        orderId: '2',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.FINISHED,
        orderId: '3',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.IN_PROGRESS,
        orderId: '4',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.ENQUEUED,
        orderId: '5',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
    ];
    await publishGatewayOrderUpdate(orders);
    const expectedTopic = '/j1/txt/1/f/i/order';
    const expectedMessage = JSON.stringify({ ts: MOCK_DATE, type: 'BLUE', state: GatewayOrderStateEnum.INPROCESS });

    expect(mqttPublishSpy).toHaveBeenCalledWith(expectedTopic, expectedMessage, { retain: true, qos: 1 });
  });

  it('should publish an ordered order state when any order is enqueued and none is in progress', async () => {
    const orders: OrderResponse[] = [
      {
        orderType: 'PRODUCTION',
        state: OrderState.CANCELLED,
        orderId: '1',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.ERROR,
        orderId: '2',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.FINISHED,
        orderId: '3',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.ENQUEUED,
        orderId: '4',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.CANCELLED,
        orderId: '5',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
    ];
    await publishGatewayOrderUpdate(orders);
    const expectedTopic = '/j1/txt/1/f/i/order';
    const expectedMessage = JSON.stringify({ ts: MOCK_DATE, type: 'BLUE', state: GatewayOrderStateEnum.ORDERED });

    expect(mqttPublishSpy).toHaveBeenCalledWith(expectedTopic, expectedMessage, { retain: true, qos: 1 });
  });

  it('should publish an waiting for order state when no order is waiting or in progress', async () => {
    const orders: OrderResponse[] = [
      {
        orderType: 'PRODUCTION',
        state: OrderState.CANCELLED,
        orderId: '1',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.ERROR,
        orderId: '2',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.FINISHED,
        orderId: '3',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
      {
        orderType: 'PRODUCTION',
        state: OrderState.CANCELLED,
        orderId: '5',
        type: 'BLUE',
        timestamp: new Date(),
        productionSteps: [],
        workpieceId: '',
      },
    ];
    await publishGatewayOrderUpdate(orders);
    const expectedTopic = '/j1/txt/1/f/i/order';
    const expectedMessage = JSON.stringify({ ts: MOCK_DATE, state: GatewayOrderStateEnum.WAITINGFORORDER });

    expect(mqttPublishSpy).toHaveBeenCalledWith(expectedTopic, expectedMessage, { retain: true, qos: 1 });
  });
});
