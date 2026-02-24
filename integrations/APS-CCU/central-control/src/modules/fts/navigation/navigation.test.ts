import { AsyncMqttClient } from 'async-mqtt';
import {
  AvailableState,
  FtsPairedModule,
  OrderNavigationStep,
  OrderResponse,
  OrderState,
  PairedModule,
} from '../../../../../common/protocol/ccu';
import { FtsCommandType, LoadingBay } from '../../../../../common/protocol/fts';
import { ModuleType } from '../../../../../common/protocol/module';
import { FTSNotReadyError, FtsPathResult } from '../../../models/models';
import { createMockMqttClient } from '../../../test-helpers';
import { FactoryLayoutService, FactoryNodeBlocker } from '../../layout/factory-layout-service';
import { FtsPairingStates } from '../../pairing/fts-pairing-states';
import { ModuleData, PairingStates } from '../../pairing/pairing-states';
import { Direction, DockingMetadata, FtsOrder } from '../model';
import {
  addDockingMetadataToOrder,
  getBlockedNodesForOrder,
  getSortedUnassignedFtsPaths,
  selectFtsPathForStep,
  sendClearModuleNodeNavigationRequest,
  sendNavigationRequest,
} from './navigation';
import { NavigatorService, Path } from './navigator-service';
import { jsonIsoDateReviver } from '../../../../../common/util/json.revivers';
import { FtsTopic, getFtsTopic } from '../../../../../common/protocol';

describe('Test Navigation', () => {
  let mqtt: AsyncMqttClient;
  const FTS_SERIAL = 'FTS1';

  beforeEach(() => {
    mqtt = createMockMqttClient();
    jest.spyOn(FtsPairingStates, 'getInstance').mockReturnValue({
      getOpenloadingBay: () => undefined,
      getForOrder: () => undefined,
      isReadyForOrder: () => false,
      setLoadingBay: () => undefined,
      getFtsAtPosition: () => undefined,
      updateAvailability: () => jest.fn(),
      getAllReadyUnassigned: () => jest.fn(),
      getAll: () => jest.fn(),
    } as unknown as FtsPairingStates);
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it('should send a navigation request for navigation step', async () => {
    const actionId = 'actionId';
    const topic = `fts/v1/ff/${FTS_SERIAL}/order`;
    jest.useFakeTimers().setSystemTime(new Date('2023-02-02T11:46:19Z'));
    jest.mock('node:crypto');
    const orderId = 'orderId';
    const orderUpdateId = 0;
    const navStep: OrderNavigationStep = {
      id: 'id',
      type: 'NAVIGATION',
      state: OrderState.ENQUEUED,
      target: ModuleType.DPS,
      source: ModuleType.DRILL,
    };

    const dpsSerial = 'DPS_SERIAL';
    const drillSerial = 'DRILL1';

    const pairedFts: FtsPairedModule = {
      serialNumber: FTS_SERIAL,
      type: 'FTS',
      lastModuleSerialNumber: drillSerial,
    };
    const loadPosition = '1';
    const workpiece = 'RED';
    const workpieceId = 'test';

    const expectedOrder: FtsOrder = {
      edges: [
        {
          id: '2-4',
          linkedNodes: ['2', '4'],
          length: 400,
        },
        {
          id: '1-2',
          length: 400,
          linkedNodes: ['1', '2'],
        },
      ],
      nodes: [
        {
          id: '2',
          linkedEdges: ['1-2', '2-3', '2-4', '2-5'],
          action: {
            type: FtsCommandType.PASS,
            id: actionId,
          },
        },
        {
          id: '1',
          linkedEdges: ['1-2'],
          action: {
            type: FtsCommandType.TURN,
            metadata: {
              direction: Direction.BACK,
            },
            id: 'id',
          },
        },
      ],
      orderId,
      orderUpdateId,
      serialNumber: FTS_SERIAL,
      timestamp: new Date('2023-02-02T11:46:19.000Z'),
    };

    const expectedBlockedNodes: Array<FactoryNodeBlocker> = [
      { afterNodeId: undefined, ftsSerialNumber: 'FTS1', nodeId: '2' },
      { afterNodeId: '2', ftsSerialNumber: 'FTS1', nodeId: '1' },
    ];

    jest.mock('../../pairing/pairing-states');
    FtsPairingStates.getInstance().isReady = jest.fn().mockReturnValue(true);
    FtsPairingStates.getInstance().getOpenloadingBay = jest.fn().mockReturnValue(loadPosition);
    FtsPairingStates.getInstance().getLoadingBayForOrder = jest.fn().mockReturnValue(undefined);
    FtsPairingStates.getInstance().setLoadingBay = jest.fn();
    FtsPairingStates.getInstance().updateAvailability = jest.fn();
    jest.mock('../../pairing/pairing-states');
    jest.spyOn(PairingStates.getInstance(), 'isReadyForOrder').mockImplementation(() => true);
    jest.spyOn(NavigatorService, 'getFTSOrder').mockReturnValue(expectedOrder);
    jest.spyOn(FactoryLayoutService, 'blockNodeSequence').mockReturnValue();

    await sendNavigationRequest(navStep, orderId, orderUpdateId, workpiece, workpieceId, pairedFts, dpsSerial);
    expect(FtsPairingStates.getInstance().isReady).toHaveBeenCalledWith(FTS_SERIAL);
    expect(mqtt.publish).toHaveBeenCalledWith(topic, expect.anything(), { qos: 2 });
    expect(PairingStates.getInstance().isReadyForOrder).toHaveBeenCalledWith(dpsSerial, orderId);
    expect(NavigatorService.getFTSOrder).toHaveBeenCalledWith(drillSerial, dpsSerial, orderId, orderUpdateId, FTS_SERIAL, navStep.id);
    expect(FactoryLayoutService.blockNodeSequence).toHaveBeenCalledWith(expectedBlockedNodes);
    expect(FtsPairingStates.getInstance().setLoadingBay).toHaveBeenCalledWith(FTS_SERIAL, loadPosition, orderId);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      FTS_SERIAL,
      AvailableState.BUSY,
      orderId,
      pairedFts.lastNodeId,
      pairedFts.lastModuleSerialNumber,
      loadPosition,
    );
  });

  it('should throw an error when there is not FTS in a ready state', async () => {
    const navStep: OrderNavigationStep = {
      id: 'id',
      type: 'NAVIGATION',
      state: OrderState.ENQUEUED,
      target: ModuleType.DPS,
      source: ModuleType.DRILL,
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
    };

    jest.mock('../../pairing/pairing-states');
    FtsPairingStates.getInstance().isReady = jest.fn().mockReturnValue(false);
    jest.spyOn(FactoryLayoutService, 'blockNodeSequence').mockReturnValue();

    try {
      await sendNavigationRequest(navStep, 'orderId', 0, 'RED', 'test', fts, 'targetSerial');
    } catch (e) {
      expect(e).toBeInstanceOf(FTSNotReadyError);
    }
    expect(FtsPairingStates.getInstance().isReady).toHaveBeenCalledWith(fts.serialNumber);
    expect(mqtt.publish).not.toHaveBeenCalled();
    expect.assertions(3);
  });

  it('should calculate and sort the paths for all unassigned ready FTS', async () => {
    const targetSerial = 'targetSerial';
    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'startMod',
    };

    const fts2: FtsPairedModule = {
      serialNumber: 'serialNumber2',
      type: 'FTS',
      lastModuleSerialNumber: 'startMod2',
    };

    const fts3: FtsPairedModule = {
      serialNumber: 'serialNumber3',
      type: 'FTS',
      lastModuleSerialNumber: 'startMod3',
    };

    const fts4: FtsPairedModule = {
      serialNumber: 'serialNumber4',
      type: 'FTS',
    };

    const ftsPaths: { [s: string]: Path } = {
      [fts.serialNumber]: {
        path: [1, 2],
        distance: 50,
      },
      [fts2.serialNumber]: {
        path: [0, 2],
        distance: 30,
      },
      [fts3.serialNumber]: {
        path: [1],
        distance: 40,
      },
    };

    const readyData: Array<ModuleData<FtsPairedModule>> = [{ state: fts }, { state: fts2 }, { state: fts3 }, { state: fts4 }];

    const expectedResult: FtsPathResult[] = [
      {
        fts: fts2,
        path: ftsPaths[fts2.serialNumber],
      },
      {
        fts: fts3,
        path: ftsPaths[fts3.serialNumber],
      },
      {
        fts: fts,
        path: ftsPaths[fts.serialNumber],
      },
    ];

    jest.mock('../../pairing/pairing-states');
    jest.spyOn(FtsPairingStates.getInstance(), 'getAllReadyUnassigned').mockReturnValue(readyData);
    jest.spyOn(NavigatorService, 'getFTSPath').mockImplementation((start, target, ftsSerial) => ftsPaths[ftsSerial]);

    const result = getSortedUnassignedFtsPaths(targetSerial);

    expect(FtsPairingStates.getInstance().getAllReadyUnassigned).toHaveBeenCalled();
    expect(NavigatorService.getFTSPath).toHaveBeenCalledTimes(3);
    expect(NavigatorService.getFTSPath).toHaveBeenNthCalledWith(1, fts.lastModuleSerialNumber, targetSerial, fts.serialNumber);
    expect(NavigatorService.getFTSPath).toHaveBeenNthCalledWith(2, fts2.lastModuleSerialNumber, targetSerial, fts2.serialNumber);
    expect(NavigatorService.getFTSPath).toHaveBeenNthCalledWith(3, fts3.lastModuleSerialNumber, targetSerial, fts3.serialNumber);
    expect(result).toEqual(expectedResult);
  });

  it('should add bay information', () => {
    const orderId = 'orderID';
    const order: FtsOrder = {
      edges: [
        {
          id: '2-4',
          linkedNodes: ['2', '4'],
          length: 400,
        },
        {
          id: '1-2',
          length: 400,
          linkedNodes: ['1', '2'],
        },
      ],
      nodes: [
        {
          id: '2',
          linkedEdges: ['1-2', '2-3', '2-4', '2-5'],
          action: {
            type: FtsCommandType.PASS,
            id: '4',
          },
        },
        {
          id: '1',
          linkedEdges: ['1-2'],
          action: {
            type: FtsCommandType.DOCK,
            id: '5',
          },
        },
      ],
      orderId,
      orderUpdateId: 0,
      serialNumber: FTS_SERIAL,
      timestamp: new Date('2023-02-02T11:46:19.000Z'),
    };

    const loadId = 'asdasd';
    const loadPosition = '1';
    const loadType = 'RED';
    const ftsPairingStates: FtsPairingStates = {
      setLoadingBay: jest.fn().mockReturnValue(loadPosition),
    } as unknown as FtsPairingStates;
    jest.spyOn(FtsPairingStates, 'getInstance').mockReturnValue(ftsPairingStates);

    const dockingMetaData: DockingMetadata = { loadPosition, loadType, loadId };
    addDockingMetadataToOrder(order, ftsPairingStates, FTS_SERIAL, dockingMetaData);
    const expectedOrder: FtsOrder = {
      edges: [
        {
          id: '2-4',
          linkedNodes: ['2', '4'],
          length: 400,
        },
        {
          id: '1-2',
          length: 400,
          linkedNodes: ['1', '2'],
        },
      ],
      nodes: [
        {
          id: '2',
          linkedEdges: ['1-2', '2-3', '2-4', '2-5'],
          action: {
            type: FtsCommandType.PASS,
            id: '4',
          },
        },
        {
          id: '1',
          linkedEdges: ['1-2'],
          action: {
            type: FtsCommandType.DOCK,
            id: '5',
            metadata: {
              loadPosition,
              loadType,
              loadId,
            },
          },
        },
      ],
      orderId,
      orderUpdateId: 0,
      serialNumber: FTS_SERIAL,
      timestamp: new Date('2023-02-02T11:46:19.000Z'),
    };

    expect(order).toEqual(expectedOrder);
    expect(ftsPairingStates.setLoadingBay).toHaveBeenCalledWith(FTS_SERIAL, loadPosition, orderId);
  });

  it('should get the blocked nodes for an order, duplicate nodes are filtered', () => {
    const orderId = 'orderID';
    const order: FtsOrder = {
      edges: [
        {
          id: '2-4',
          linkedNodes: ['2', '4'],
          length: 400,
        },
        {
          id: '1-2',
          length: 400,
          linkedNodes: ['1', '2'],
        },
      ],
      nodes: [
        {
          id: '2',
          linkedEdges: ['1-2', '2-3', '2-4', '2-5'],
          action: {
            type: FtsCommandType.PASS,
            id: '4',
          },
        },
        {
          id: '1',
          linkedEdges: ['1-2'],
          action: {
            type: FtsCommandType.TURN,
            id: '23',
          },
        },
        {
          id: '1',
          linkedEdges: ['1-2'],
          action: {
            type: FtsCommandType.DOCK,
            id: '5',
          },
        },
      ],
      orderId,
      orderUpdateId: 0,
      serialNumber: FTS_SERIAL,
      timestamp: new Date('2023-02-02T11:46:19.000Z'),
    };

    const expectedBlockers: Array<FactoryNodeBlocker> = [
      { afterNodeId: undefined, ftsSerialNumber: 'FTS1', nodeId: '2' },
      { afterNodeId: '2', ftsSerialNumber: 'FTS1', nodeId: '1' },
    ];

    const blockers = getBlockedNodesForOrder(order);

    expect(blockers).toEqual(expectedBlockers);
  });

  it('should send a non-waiting docking order to remove an FTS from a module.', async () => {
    const fts: FtsPairedModule = {
      serialNumber: FTS_SERIAL,
      type: 'FTS',
      lastModuleSerialNumber: 'startMod',
    };
    const blockedModuleId = 'blockedId';
    const targetModuleId = 'targetModuleId';
    const targetModule: PairedModule = {
      serialNumber: targetModuleId,
      type: 'MODULE',
      connected: true,
      pairedSince: new Date(),
    };
    const initialOrder: FtsOrder = {
      edges: [
        {
          id: `${blockedModuleId}-4`,
          linkedNodes: [blockedModuleId, '4'],
          length: 375,
        },
        {
          id: `4-${targetModuleId}`,
          length: 375,
          linkedNodes: ['4', targetModuleId],
        },
      ],
      nodes: [
        {
          id: blockedModuleId,
          linkedEdges: [`${blockedModuleId}-4`],
        },
        {
          id: '4',
          linkedEdges: [`${blockedModuleId}-4`, `4-${targetModuleId}`],
          action: {
            type: FtsCommandType.TURN,
            metadata: {
              direction: Direction.RIGHT,
            },
            id: 'id2',
          },
        },
        {
          id: targetModuleId,
          linkedEdges: [`4-${targetModuleId}`],
          action: {
            type: FtsCommandType.DOCK,
            id: 'id3',
          },
        },
      ],
      orderId: 'someOrderId',
      orderUpdateId: 0,
      serialNumber: FTS_SERIAL,
      timestamp: new Date('2023-02-02T11:46:19.000Z'),
    };

    const expectedOrder: FtsOrder = JSON.parse(JSON.stringify(initialOrder), jsonIsoDateReviver);
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    expectedOrder.nodes[2]!.action!.metadata = <DockingMetadata>{
      loadPosition: LoadingBay.MIDDLE,
      noLoadChange: true,
    };

    const readyFtsMock = jest
      .spyOn(FtsPairingStates.getInstance(), 'getFtsAtPosition')
      .mockImplementation(moduleId => (moduleId === blockedModuleId ? fts : undefined));

    jest.spyOn(PairingStates.getInstance(), 'getAll').mockReturnValue([targetModule]);
    jest.spyOn(NavigatorService, 'getFTSOrder').mockReturnValue(initialOrder);
    jest.spyOn(FactoryLayoutService, 'blockNodeSequence').mockReturnValue();

    await sendClearModuleNodeNavigationRequest(blockedModuleId);

    expect(mqtt.publish).toHaveBeenCalledWith(getFtsTopic(FTS_SERIAL, FtsTopic.ORDER), JSON.stringify(expectedOrder));
    expect(readyFtsMock).toHaveBeenNthCalledWith(1, blockedModuleId);
    expect(readyFtsMock).toHaveBeenNthCalledWith(2, targetModuleId);
  });

  it('should return a valid path for an FTS that can fulfill the order', async () => {
    const fts: FtsPairedModule = {
      type: 'FTS',
      serialNumber: 'mockedFts',
      lastModuleSerialNumber: 'mockedModule',
      available: AvailableState.READY,
      connected: true,
    };
    const order: OrderResponse = {
      orderId: 'mockOrder',
      orderType: 'PRODUCTION',
      type: 'RED',
      timestamp: new Date(),
      productionSteps: [],
      state: OrderState.IN_PROGRESS,
    };
    const step: OrderNavigationStep = {
      id: '1234567890',
      type: 'NAVIGATION',
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
      target: ModuleType.CHRG,
    };
    const path: Path = { path: [1], distance: 1 };
    jest.spyOn(FtsPairingStates.getInstance(), 'getForOrder').mockReturnValue(fts);
    jest.spyOn(FtsPairingStates.getInstance(), 'isReadyForOrder').mockReturnValue(true);
    jest.spyOn(NavigatorService, 'getFTSPath').mockReturnValue(path);
    const result = selectFtsPathForStep(order, 'target', step);
    expect(result).toEqual({ fts, path });
  });

  it('should not return a valid path for an FTS that has the workpiece loaded, but is working on another order', async () => {
    const fts: FtsPairedModule = {
      type: 'FTS',
      serialNumber: 'mockedFts',
      lastModuleSerialNumber: 'mockedModule',
      available: AvailableState.READY,
      connected: true,
    };
    const order: OrderResponse = {
      orderId: 'mockOrder',
      orderType: 'PRODUCTION',
      type: 'RED',
      timestamp: new Date(),
      productionSteps: [],
      state: OrderState.IN_PROGRESS,
    };
    const step: OrderNavigationStep = {
      id: '1234567890',
      type: 'NAVIGATION',
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
      target: ModuleType.CHRG,
    };
    const path: Path = { path: [1], distance: 1 };
    jest.spyOn(FtsPairingStates.getInstance(), 'getForOrder').mockReturnValue(fts);
    jest.spyOn(FtsPairingStates.getInstance(), 'isReadyForOrder').mockReturnValue(false);
    jest.spyOn(NavigatorService, 'getFTSPath').mockReturnValue(path);
    const result = selectFtsPathForStep(order, 'target', step);
    expect(result).toBeUndefined();
  });
});
