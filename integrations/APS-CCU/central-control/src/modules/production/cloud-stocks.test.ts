import crypto from 'node:crypto';
import { CcuTopic } from '../../../../common/protocol';
import { ModuleCommandType, ModuleState, ModuleType } from '../../../../common/protocol/module';
import { ActionState, Load, LoadType, State } from '../../../../common/protocol/vda';
import { createMockMqttClient } from '../../test-helpers';
import { OrderManagement } from '../order/management/order-management';
import { StockManagementService, StockStoredLoad } from '../order/stock/stock-management-service';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { PairingStates } from '../pairing/pairing-states';
import { handleStock, mapHbwToCloudStock } from './cloud-stock';

jest.mock('../pairing/pairing-states');
jest.mock('../pairing/fts-pairing-states');
jest.mock('../order/management/order-management');

describe('test stockhandling', () => {
  let pairingStates: PairingStates;
  let ftsPairingStates: FtsPairingStates;
  let orderManagement: OrderManagement;

  const MOCKED_DATE = new Date('2021-01-01T00:00:00.000Z');

  beforeEach(() => {
    pairingStates = {
      updateAvailability: jest.fn(),
      getFactsheet: jest.fn(),
      getWorkpieceId: jest.fn(),
    } as unknown as PairingStates;
    PairingStates.getInstance = jest.fn().mockReturnValue(pairingStates);
    ftsPairingStates = {
      clearLoadingBay: jest.fn(),
      getFtsSerialNumberForOrderId: jest.fn(),
    } as unknown as FtsPairingStates;
    FtsPairingStates.getInstance = jest.fn().mockReturnValue(ftsPairingStates);
    orderManagement = {
      getWorkpieceId: jest.fn(),
      startNextOrder: jest.fn(),
    } as unknown as OrderManagement;
    OrderManagement.getInstance = jest.fn().mockReturnValue(orderManagement);
    jest.useFakeTimers().setSystemTime(MOCKED_DATE);
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it('publishes updated stock to MQTT if module type is HBW', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.HBW;
    const actionState: ActionState<ModuleCommandType> = {
      state: State.FINISHED,
      command: ModuleCommandType.PICK,
      timestamp: new Date(),
      id: 'actionStateId',
    };
    const load: Load = {
      loadPosition: 'A1',
      loadId: '2318',
      loadType: LoadType.WHITE,
    };
    const load2: Load = {
      loadPosition: 'A2',
      loadId: '2314',
      loadType: LoadType.RED,
    };

    const moduleState: ModuleState = {
      actionState: actionState,
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load, load2],
    };

    jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue({
      serialNumber,
      headerId: 1,
      timestamp: new Date(),
      version: '2',
      manufacturer: 'manufacturer',
      typeSpecification: {
        seriesName: 'seriesName',
        moduleClass: ModuleType.HBW,
      },
      protocolFeatures: {
        moduleParameters: {
          clearModuleOnPick: false,
        },
      },
    });

    const mockedUUID = 'mockedUUID';
    const mqttClientMock = createMockMqttClient();

    jest.mock('node:crypto');
    crypto.randomUUID = jest.fn().mockReturnValue(mockedUUID);

    jest.spyOn(StockManagementService, 'setStock');

    await handleStock(moduleState);

    expect(StockManagementService.setStock).toHaveBeenCalledWith(serialNumber, [load, load2]);
    expect(orderManagement.startNextOrder).toHaveBeenCalled();
    expect(pairingStates.getFactsheet).toHaveBeenCalledWith(serialNumber);
    expect(mqttClientMock.publish).toHaveBeenCalledWith('/j1/txt/1/f/i/stock', expect.anything(), {
      qos: 1,
      retain: true,
    });
    expect(mqttClientMock.publish).toHaveBeenCalledWith(CcuTopic.STOCK, expect.anything(), { qos: 1, retain: true });
  });

  it('should not publish an array with the stock of the HBW-Module, not the right module', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.DRILL;
    const actionState: ActionState<ModuleCommandType> = {
      state: State.FINISHED,
      command: ModuleCommandType.PICK,
      timestamp: new Date(),
      id: 'actionStateId',
    };
    const load: Load = {
      loadPosition: 'A1',
      loadId: '2318',
      loadType: LoadType.WHITE,
    };
    const load2: Load = {
      loadPosition: 'A2',
      loadId: '2314',
      loadType: LoadType.RED,
    };

    const moduleState: ModuleState = {
      actionState: actionState,
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load, load2],
    };

    jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue({
      serialNumber,
      headerId: 1,
      timestamp: new Date(),
      version: '2',
      manufacturer: 'manufacturer',
      typeSpecification: {
        seriesName: 'seriesName',
        moduleClass: ModuleType.DRILL,
      },
      protocolFeatures: {
        moduleParameters: {
          clearModuleOnPick: false,
        },
      },
    });

    const mqttClientMock = createMockMqttClient();

    await handleStock(moduleState);

    expect(pairingStates.getFactsheet).toHaveBeenCalledWith(serialNumber);
    expect(mqttClientMock.publish).not.toHaveBeenCalled();
  });

  it('should map empty stock to an empty cloud stock', () => {
    const stock: StockStoredLoad[] = [];

    const result = mapHbwToCloudStock(stock, []);
    expect(result).toEqual({
      ts: expect.any(Date),
      stockItems: [],
    });
  });

  it('should map the stored stock to the correct cloud stock', () => {
    const stock: StockStoredLoad[] = [
      {
        hbwSerial: 'hbwA',
        reserved: false,
        workpiece: {
          loadId: 'wp1',
          loadType: LoadType.BLUE,
          loadPosition: 'A1',
        },
      },
      {
        hbwSerial: 'hbwA',
        reserved: true,
        workpiece: {
          loadId: 'wp2',
          loadType: LoadType.RED,
          loadPosition: 'C3',
        },
      },
      {
        hbwSerial: 'hbwB',
        reserved: true,
        workpiece: {
          loadId: 'wp3',
          loadType: LoadType.WHITE,
          loadPosition: 'A2',
        },
      },
      {
        hbwSerial: 'hbwC',
        reserved: false,
        workpiece: {
          loadId: 'wp4',
          loadType: LoadType.BLUE,
          loadPosition: 'B2',
        },
      },
    ];

    const expectedResult = [
      {
        hbw: 'hbwA',
        location: 'A1',
        workpiece: {
          id: 'wp1',
          state: 'RAW',
          type: 'BLUE',
        },
      },
      {
        hbw: 'hbwA',
        location: 'C3',
        workpiece: {
          id: 'wp2',
          state: 'RESERVED',
          type: 'RED',
        },
      },
      {
        hbw: 'hbwB',
        location: 'A2',
        workpiece: {
          id: 'wp3',
          state: 'RESERVED',
          type: 'WHITE',
        },
      },
      {
        hbw: 'hbwC',
        location: 'B2',
        workpiece: {
          id: 'wp4',
          state: 'RAW',
          type: 'BLUE',
        },
      },
    ];

    const result = mapHbwToCloudStock(stock, []);
    expect(result.stockItems).toEqual(expectedResult);
  });

  it('should fill unused bays as empty', () => {
    const stock: StockStoredLoad[] = [
      {
        hbwSerial: 'hbwA',
        reserved: false,
        workpiece: {
          loadId: 'wp1',
          loadType: LoadType.BLUE,
          loadPosition: 'A1',
        },
      },
    ];

    const expectedResult = [
      {
        hbw: 'hbwA',
        location: 'A1',
        workpiece: {
          id: 'wp1',
          state: 'RAW',
          type: 'BLUE',
        },
      },
      {
        hbw: 'hbwA',
        location: 'A2',
      },
      {
        hbw: 'hbwA',
        location: 'A3',
      },
      {
        hbw: 'hbwA',
        location: 'B1',
      },
      {
        hbw: 'hbwA',
        location: 'B2',
      },
      {
        hbw: 'hbwA',
        location: 'B3',
      },
      {
        hbw: 'hbwA',
        location: 'C1',
      },
      {
        hbw: 'hbwA',
        location: 'C2',
      },
      {
        hbw: 'hbwA',
        location: 'C3',
      },
    ];

    const result = mapHbwToCloudStock(stock, ['hbwA']);
    expect(result.stockItems).toEqual(expectedResult);
  });
});
