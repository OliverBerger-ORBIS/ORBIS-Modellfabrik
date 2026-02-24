import { AsyncMqttClient } from 'async-mqtt';
import crypt_spies from 'node:crypto';
import { AvailableState, OrderManufactureStep, OrderState, PairedModule, Workpiece } from '../../../../common/protocol/ccu';
import { DurationMetadata, ModuleCommandType, ModuleType, ProductionCommand, StoreMetadata } from '../../../../common/protocol/module';
import { InstantAction, InstantActions } from '../../../../common/protocol/vda';
import { ControllerNotReadyError } from '../../models/models';
import { createMockMqttClient } from '../../test-helpers';
import { PairingStates } from '../pairing/pairing-states';
import { sendAnnounceDpsOutput, sendProductionCommand } from './production';

describe('Test production updates', () => {
  let mqtt: AsyncMqttClient;
  let uuid_counter = 0;

  beforeEach(() => {
    mqtt = createMockMqttClient();
    jest.useFakeTimers().setSystemTime(new Date('2023-02-010T10:20:19Z'));

    // mock uuids with sequential deterministic values
    jest.spyOn(crypt_spies, 'randomUUID').mockImplementation(() => {
      uuid_counter++;
      return `aabbccdd-eeee-ffff-1111-${uuid_counter}`;
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.restoreAllMocks();
    jest.useRealTimers();
  });

  it('should should send a production command without metadata', async () => {
    const actionId = 'actionId';
    const serialNumber = 'serNr';
    const orderId = 'orderId';
    const orderUpdateId = 0;

    const prodStep: OrderManufactureStep = {
      id: actionId,
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DROP,
      dependentActionId: 'dependentActionId',
    };

    const workpiece: Workpiece = 'RED';
    const metadata: StoreMetadata = {
      type: workpiece,
      workpieceId: 'workpieceId',
    };
    const command = {
      timestamp: new Date(),
      serialNumber: serialNumber,
      orderId,
      orderUpdateId,
      action: {
        id: actionId,
        command: ModuleCommandType.DROP,
        metadata,
      },
    };

    const pairedModule: PairedModule = {
      type: 'MODULE',
      serialNumber: serialNumber,
      available: AvailableState.READY,
      pairedSince: new Date(),
      connected: true,
      lastSeen: new Date(),
    };

    mockPairedState(pairedModule);

    await sendProductionCommand(prodStep, orderId, orderUpdateId, pairedModule, metadata);

    const topic = `module/v1/ff/${serialNumber}/order`;
    expect(mqtt.publish).toHaveBeenCalledWith(topic, JSON.stringify(command));
  });

  it('should should send a production command with metadata', async () => {
    const actionId = 'actionId';
    const serialNumber = 'serNr';
    const orderId = 'orderId';
    const orderUpdateId = 0;

    const prodStep: OrderManufactureStep = {
      id: actionId,
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
      dependentActionId: 'dependentActionId',
    };

    const metadata: DurationMetadata = {
      duration: 5,
    };

    const command: ProductionCommand = {
      timestamp: new Date(),
      serialNumber: serialNumber,
      orderId,
      orderUpdateId,
      action: {
        id: actionId,
        command: ModuleCommandType.DRILL,
        metadata,
      },
    };

    const pairedModule: PairedModule = {
      type: 'MODULE',
      serialNumber: serialNumber,
      available: AvailableState.READY,
      pairedSince: new Date(),
      connected: true,
      lastSeen: new Date(),
      productionDuration: 5,
    };

    mockPairedState(pairedModule);

    await sendProductionCommand(prodStep, orderId, orderUpdateId, pairedModule, metadata);

    const topic = `module/v1/ff/${serialNumber}/order`;
    expect(mqtt.publish).toHaveBeenCalledWith(topic, JSON.stringify(command));
  });

  it('should throw an error when the requested module is not ready to accept a new production command', async () => {
    const actionId = 'actionId';
    const orderId = 'orderId';
    const orderUpdateId = 0;
    const moduleType = ModuleType.MILL;

    const prodStep: OrderManufactureStep = {
      id: actionId,
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      moduleType,
      command: ModuleCommandType.MILL,
      dependentActionId: 'dependentActionId',
    };

    mockPairedState(undefined);
    const metadata: DurationMetadata = {
      duration: 5,
    };

    try {
      await sendProductionCommand(prodStep, orderId, orderUpdateId, { serialNumber: 'not_ready' } as PairedModule, metadata);
    } catch (e) {
      expect(e).toBeInstanceOf(ControllerNotReadyError);
    }
    expect(mqtt.publish).not.toHaveBeenCalled();
    expect.assertions(2);
  });

  const mockPairedState = (pairedModule: PairedModule | undefined): void => {
    PairingStates['instance'] = {
      getReadyForModuleType: jest.fn().mockReturnValue(pairedModule),
      isReadyForOrder: jest.fn().mockReturnValue(!!pairedModule),
    } as unknown as PairingStates;
  };

  it('should should send a announceOutput instant action', async () => {
    const serialNumber = 'serNr';
    const orderId = 'orderId';
    const workpiece = Workpiece.RED;
    const expected: InstantAction = {
      serialNumber,
      timestamp: new Date(),
      actions: [
        {
          actionId: 'aabbccdd-eeee-ffff-1111-1',
          actionType: InstantActions.ANNOUNCE_OUTPUT,
          metadata: {
            orderId: orderId,
            type: workpiece,
          },
        },
      ],
    };

    await sendAnnounceDpsOutput(serialNumber, orderId, workpiece);

    const topic = `module/v1/ff/${serialNumber}/instantAction`;
    expect(mqtt.publish).toHaveBeenCalledWith(topic, JSON.stringify(expected), { qos: 2 });
  });
});
