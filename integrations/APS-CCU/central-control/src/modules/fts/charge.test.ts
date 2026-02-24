import { FactoryLayoutService } from '../layout/factory-layout-service';
import { OrderManagement } from '../order/management/order-management';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { PairingStates } from '../pairing/pairing-states';
import * as chargeSpies from './charge';
import {
  freeBlockedChargers,
  FTS_WAITING_FOR_RECHARGE,
  handleChargingUpdate,
  isBatteryLow,
  sendChargingNavigationRequest,
  triggerChargeOrderForFts,
} from './charge';
import * as navigationSpies from './navigation/navigation';
import * as mqttSpies from '../../mqtt/mqtt';
import { FtsPairedModule, PairedModule } from '../../../../common/protocol/ccu';
import { ModuleType } from '../../../../common/protocol/module';
import { NavigatorService } from './navigation/navigator-service';
import { FtsOrder } from './model';
import { FtsCommandType, FtsState, LoadingBay } from '../../../../common/protocol/fts';
import { AsyncMqttClient } from 'async-mqtt';
import config from '../../config';

jest.mock('../pairing/fts-pairing-states');
jest.mock('../pairing/pairing-states');
jest.mock('../order/management/order-management');
describe('Test sending charging commands', () => {
  beforeEach(() => {
    jest.spyOn(mqttSpies, 'getMqttClient').mockReturnValue({ publish: jest.fn() } as unknown as AsyncMqttClient);
    jest.spyOn(FtsPairingStates, 'getInstance').mockReturnValue({
      getFtsAtPosition: jest.fn(),
      updateAvailability: jest.fn(),
      isReady: jest.fn(),
      isCharging: jest.fn(),
      get: jest.fn(),
      updateCharge: jest.fn(),
    } as unknown as FtsPairingStates);
    jest.spyOn(OrderManagement, 'getInstance').mockReturnValue({
      getTargetModuleTypeForNavActionId: jest.fn(),
      getWorkpieceType: jest.fn(),
    } as unknown as OrderManagement);
    jest.spyOn(PairingStates, 'getInstance').mockReturnValue({
      updateAvailability: jest.fn(),
      get: jest.fn(),
      getAllReady: jest.fn(),
      isReady: jest.fn(),
      getForModuleType: jest.fn(),
      clearModuleForOrder: jest.fn(),
    } as unknown as PairingStates);
    jest.spyOn(FactoryLayoutService, 'releaseNodesBefore').mockReturnValue();
    jest.spyOn(FactoryLayoutService, 'blockNodeSequence').mockReturnValue();
    FTS_WAITING_FOR_RECHARGE.clear();
  });

  afterEach(() => {
    OrderManagement['instance'] = undefined as unknown as OrderManagement;
    jest.clearAllMocks();
    jest.restoreAllMocks();
    FTS_WAITING_FOR_RECHARGE.clear();
  });

  it('should ignore a partially filled battery without percentage and minVolt', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        currentVoltage: 8.6,
        minVolt: undefined,
        percentage: null as unknown as number,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(false);
  });

  it('should ignore a battery info without percentage and minVolt', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        currentVoltage: 8.2,
        minVolt: undefined,
        percentage: null as unknown as number,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(false);
  });

  it('should ignore a battery info without percentage', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        currentVoltage: 8.6,
        minVolt: 8.5,
        percentage: null as unknown as number,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(false);
  });

  it('should detect a low battery', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        currentVoltage: 8.6,
        minVolt: 8.5,
        percentage: 10,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(true);
  });

  it('should detect an extremely low battery', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        currentVoltage: 7.7,
        minVolt: 8.4,
        maxVolt: 10,
        percentage: -15,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(true);
  });

  it('should detect a low battery with configured values from the fts', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        currentVoltage: 8.52,
        minVolt: 8.4,
        maxVolt: 10.0,
        percentage: 10,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(true);
  });

  it('should detect a battery that is partially charged', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        currentVoltage: 8.76,
        minVolt: 8.4,
        maxVolt: 10.0,
        percentage: 30,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(false);
  });

  it('should detect a full battery', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        currentVoltage: 8.94,
        minVolt: 8.4,
        percentage: 45,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(false);
  });

  it('should detect a low battery with percentage only', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        minVolt: 8.4,
        percentage: 4,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(true);
  });

  it('should detect a full battery with percentage only', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        minVolt: 8.5,
        percentage: 80,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(false);
  });

  it('should not detect a missing value as a low battery', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        minVolt: 8.5,
        percentage: undefined as unknown as number,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    const isLow = isBatteryLow(state);
    expect(isLow).toBe(false);
  });

  it('should set charging state', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        charging: true,
        currentVoltage: 8,
        percentage: 10,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    jest.spyOn(FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
    jest.spyOn(FtsPairingStates.getInstance(), 'updateCharge').mockReturnValue();
    jest.spyOn(PairingStates.getInstance(), 'clearModuleForOrder').mockReturnValue();
    handleChargingUpdate(state);
    expect(FtsPairingStates.getInstance().isCharging).not.toHaveBeenCalled();
    expect(PairingStates.getInstance().clearModuleForOrder).not.toHaveBeenCalled();
    expect(FtsPairingStates.getInstance().updateCharge).toHaveBeenCalledWith(
      ftsSerial,
      true,
      state.batteryState!.currentVoltage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
      state.batteryState!.percentage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
    );
  });

  it('should set charging state to false', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: '1',
      batteryState: {
        charging: false,
        currentVoltage: 8,
        percentage: 10,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    jest.spyOn(FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
    jest.spyOn(FtsPairingStates.getInstance(), 'updateCharge').mockReturnValue();
    jest.spyOn(PairingStates.getInstance(), 'clearModuleForOrder').mockReturnValue();
    handleChargingUpdate(state);
    expect(FtsPairingStates.getInstance().isCharging).toHaveBeenCalledWith(ftsSerial);
    expect(PairingStates.getInstance().clearModuleForOrder).not.toHaveBeenCalled();
    expect(FtsPairingStates.getInstance().updateCharge).toHaveBeenCalledWith(
      ftsSerial,
      false,
      state.batteryState!.currentVoltage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
      state.batteryState!.percentage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
    );
  });

  it('should set charging state to false and clear the module if the old state was charging', () => {
    const ftsSerial = 'FTS';
    const state: FtsState = {
      serialNumber: ftsSerial,
      orderId: 'orderId',
      batteryState: {
        charging: false,
        currentVoltage: 8,
        percentage: 10,
      },
      lastNodeId: '',
      paused: true,
      timestamp: new Date(),
      orderUpdateId: 0,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      errors: [],
      load: [],
    };

    jest.spyOn(FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(true);
    jest.spyOn(FtsPairingStates.getInstance(), 'updateCharge').mockReturnValue();
    jest.spyOn(PairingStates.getInstance(), 'clearModuleForOrder').mockReturnValue();
    handleChargingUpdate(state);
    expect(FtsPairingStates.getInstance().isCharging).toHaveBeenCalledWith(ftsSerial);
    expect(PairingStates.getInstance().clearModuleForOrder).toHaveBeenCalledWith(state.orderId);
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    expect(FtsPairingStates.getInstance().updateCharge).toHaveBeenCalledWith(
      ftsSerial,
      false,
      state.batteryState!.currentVoltage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
      state.batteryState!.percentage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
    );
  });

  it('should trigger a charge order', async () => {
    const ftsSerial = 'FTS';
    const chargeModule: PairedModule = {
      type: 'MODULE',
      subType: ModuleType.CHRG,
      serialNumber: 'CHRG1',
    };
    jest.spyOn(FtsPairingStates.getInstance(), 'get').mockReturnValue(<FtsPairedModule>{
      serialNumber: ftsSerial,
      type: 'FTS',
      lastModuleSerialNumber: 'someModule',
    });
    jest.spyOn(FtsPairingStates.getInstance(), 'isReady').mockReturnValue(true);
    jest.spyOn(FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
    jest.spyOn(PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
    jest.spyOn(chargeSpies, 'sendChargingNavigationRequest').mockResolvedValue();
    jest.spyOn(navigationSpies, 'getSortedModulePaths').mockReturnValue([{ module: chargeModule, path: { distance: 2, path: [] } }]);
    await triggerChargeOrderForFts(ftsSerial);
    if (!config.ftsCharge.disabled) {
      expect(chargeSpies.sendChargingNavigationRequest).toHaveBeenCalledWith(ftsSerial, chargeModule.serialNumber);
    } else {
      expect(chargeSpies.sendChargingNavigationRequest).not.toHaveBeenCalledWith(ftsSerial, chargeModule.serialNumber);
    }
    expect(FTS_WAITING_FOR_RECHARGE).toEqual(new Set());
    expect(FTS_WAITING_FOR_RECHARGE.size).toEqual(0);
  });

  it('should not trigger a charge order if the FTS is not ready and add it to the queue', async () => {
    const ftsSerial = 'FTS';
    jest.spyOn(FtsPairingStates.getInstance(), 'get').mockReturnValue(<FtsPairedModule>{
      serialNumber: ftsSerial,
      type: 'FTS',
      lastModuleSerialNumber: 'someModule',
    });
    jest.spyOn(FtsPairingStates.getInstance(), 'isReady').mockReturnValue(false);
    jest.spyOn(chargeSpies, 'sendChargingNavigationRequest').mockResolvedValue();
    await triggerChargeOrderForFts(ftsSerial);
    expect(chargeSpies.sendChargingNavigationRequest).not.toHaveBeenCalled();
    if (!config.ftsCharge.disabled) {
      expect(FTS_WAITING_FOR_RECHARGE.size).toEqual(1);
      expect(FTS_WAITING_FOR_RECHARGE).toEqual(new Set([ftsSerial]));
    } else {
      expect(FTS_WAITING_FOR_RECHARGE.size).toEqual(0);
      expect(FTS_WAITING_FOR_RECHARGE).toEqual(new Set());
    }
  });

  it('should not trigger a charge order if there is no ready charging module', async () => {
    const ftsSerial = 'FTS';
    jest.spyOn(FtsPairingStates.getInstance(), 'get').mockReturnValue(<FtsPairedModule>{
      serialNumber: ftsSerial,
      type: 'FTS',
      lastModuleSerialNumber: 'someModule',
    });
    jest.spyOn(FtsPairingStates.getInstance(), 'isReady').mockReturnValue(true);
    jest.spyOn(FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
    jest.spyOn(PairingStates.getInstance(), 'getAllReady').mockReturnValue([]);
    jest.spyOn(chargeSpies, 'sendChargingNavigationRequest').mockResolvedValue();
    await triggerChargeOrderForFts(ftsSerial);
    expect(chargeSpies.sendChargingNavigationRequest).not.toHaveBeenCalled();
    if (!config.ftsCharge.disabled) {
      expect(FTS_WAITING_FOR_RECHARGE.size).toEqual(1);
      expect(FTS_WAITING_FOR_RECHARGE).toEqual(new Set([ftsSerial]));
    } else {
      expect(FTS_WAITING_FOR_RECHARGE.size).toEqual(0);
      expect(FTS_WAITING_FOR_RECHARGE).toEqual(new Set());
    }
  });

  it('should not trigger a charge order if there is no path to a ready charging module', async () => {
    const ftsSerial = 'FTS';
    const chargeModule: PairedModule = {
      type: 'MODULE',
      subType: ModuleType.CHRG,
      serialNumber: 'CHRG1',
    };
    jest.spyOn(FtsPairingStates.getInstance(), 'get').mockReturnValue(<FtsPairedModule>{
      serialNumber: ftsSerial,
      type: 'FTS',
      lastModuleSerialNumber: 'someModule',
    });
    jest.spyOn(FtsPairingStates.getInstance(), 'isReady').mockReturnValue(true);
    jest.spyOn(FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
    jest.spyOn(PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
    jest.spyOn(navigationSpies, 'getSortedModulePaths').mockReturnValue([]);
    jest.spyOn(chargeSpies, 'sendChargingNavigationRequest').mockResolvedValue();
    await triggerChargeOrderForFts(ftsSerial);
    expect(chargeSpies.sendChargingNavigationRequest).not.toHaveBeenCalled();
    if (!config.ftsCharge.disabled) {
      expect(FTS_WAITING_FOR_RECHARGE.size).toEqual(1);
      expect(FTS_WAITING_FOR_RECHARGE).toEqual(new Set([ftsSerial]));
    } else {
      expect(FTS_WAITING_FOR_RECHARGE.size).toEqual(0);
      expect(FTS_WAITING_FOR_RECHARGE).toEqual(new Set());
    }
  });

  it('should send a navigation request for charging', async () => {
    const ftsSerial = 'FTS';
    const chargeModule: PairedModule = {
      type: 'MODULE',
      subType: ModuleType.CHRG,
      serialNumber: 'CHRG1',
    };
    jest.spyOn(FtsPairingStates.getInstance(), 'get').mockReturnValue(<FtsPairedModule>{
      serialNumber: ftsSerial,
      type: 'FTS',
      lastModuleSerialNumber: 'someModule',
    });
    const orderToSend: FtsOrder = {
      orderId: 'orderId',
      timestamp: new Date('2022-02-02T12:12:12Z'),
      orderUpdateId: 0,
      serialNumber: ftsSerial,
      nodes: [
        { id: '1', action: { type: FtsCommandType.PASS, id: 'action1' }, linkedEdges: [] },
        { id: chargeModule.serialNumber, action: { type: FtsCommandType.DOCK, id: 'actionDock' }, linkedEdges: [] },
      ],
      edges: [],
    };
    const expectedOrder: FtsOrder = JSON.parse(JSON.stringify(orderToSend));
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    expectedOrder.nodes[1]!.action!.metadata = {
      loadPosition: LoadingBay.MIDDLE,
      charge: true,
    };

    jest.spyOn(FtsPairingStates.getInstance(), 'isReady').mockReturnValue(true);
    jest.spyOn(PairingStates.getInstance(), 'get').mockReturnValue(chargeModule);
    jest.spyOn(PairingStates.getInstance(), 'isReady').mockReturnValue(true);
    jest.spyOn(navigationSpies, 'getBlockedNodesForOrder').mockReturnValue([]);
    jest.spyOn(NavigatorService, 'getFTSOrder').mockReturnValue(orderToSend);

    await sendChargingNavigationRequest(ftsSerial, chargeModule.serialNumber);
    expect(mqttSpies.getMqttClient().publish).toHaveBeenCalledWith('fts/v1/ff/FTS/order', JSON.stringify(expectedOrder));
  });

  it('should free a blocked charger if an FTS wants to charge', async () => {
    const ftsSerial = 'FTS';
    const chargeModule: PairedModule = {
      type: 'MODULE',
      subType: ModuleType.CHRG,
      serialNumber: 'CHRG1',
    };
    const fts: FtsPairedModule = {
      serialNumber: ftsSerial,
      type: 'FTS',
      lastModuleSerialNumber: 'someModule',
    };
    FTS_WAITING_FOR_RECHARGE.add('someFts');
    jest.spyOn(PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
    jest.spyOn(FtsPairingStates.getInstance(), 'getFtsAtPosition').mockReturnValue(fts);
    jest.spyOn(navigationSpies, 'sendClearModuleNodeNavigationRequest').mockResolvedValue();

    await freeBlockedChargers();
    expect(navigationSpies.sendClearModuleNodeNavigationRequest).toHaveBeenCalledWith(chargeModule.serialNumber);
  });

  it('should not free a blocked charger if no FTS wants to charge', async () => {
    const ftsSerial = 'FTS';
    const chargeModule: PairedModule = {
      type: 'MODULE',
      subType: ModuleType.CHRG,
      serialNumber: 'CHRG1',
    };
    const fts: FtsPairedModule = {
      serialNumber: ftsSerial,
      type: 'FTS',
      lastModuleSerialNumber: 'someModule',
    };
    FTS_WAITING_FOR_RECHARGE.clear();
    jest.spyOn(PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
    jest.spyOn(FtsPairingStates.getInstance(), 'getFtsAtPosition').mockReturnValue(fts);
    jest.spyOn(navigationSpies, 'sendClearModuleNodeNavigationRequest').mockResolvedValue();

    await freeBlockedChargers();
    expect(navigationSpies.sendClearModuleNodeNavigationRequest).not.toHaveBeenCalled();
  });

  it('should free a blocked charger if no FTS wants to charge and clearing is forced', async () => {
    const ftsSerial = 'FTS';
    const chargeModule: PairedModule = {
      type: 'MODULE',
      subType: ModuleType.CHRG,
      serialNumber: 'CHRG1',
    };
    const fts: FtsPairedModule = {
      serialNumber: ftsSerial,
      type: 'FTS',
      lastModuleSerialNumber: 'someModule',
    };
    FTS_WAITING_FOR_RECHARGE.clear();
    jest.spyOn(PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
    jest.spyOn(FtsPairingStates.getInstance(), 'getFtsAtPosition').mockReturnValue(fts);
    jest.spyOn(navigationSpies, 'sendClearModuleNodeNavigationRequest').mockResolvedValue();

    await freeBlockedChargers(true);
    expect(navigationSpies.sendClearModuleNodeNavigationRequest).toHaveBeenCalledWith(chargeModule.serialNumber);
  });
});
