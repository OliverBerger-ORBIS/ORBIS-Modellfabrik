import { OrderResponse, Workpiece } from '../../../../../common/protocol';
import { FtsPairedModule, OrderManufactureStep, OrderNavigationStep, OrderState, PairedModule } from '../../../../../common/protocol/ccu';
import { ModuleCommandType, ModuleType } from '../../../../../common/protocol/module';
import { FtsPathResult } from '../../../models/models';
import * as navCommandSender from '../../fts/navigation/navigation';
import { NavigatorService, Path } from '../../fts/navigation/navigator-service';
import { FtsPairingStates } from '../../pairing/fts-pairing-states';
import { PairingStates } from '../../pairing/pairing-states';
import * as moduleCommandSender from '../../production/production';
import { StockManagementService } from '../stock/stock-management-service';
import { OrderManagement, OrderManagementAction } from './order-management';

describe('Test order management handling for DPS announcements', () => {
  const MOCKED_DATE = new Date('2021-01-01T00:00:00.000Z');
  const MOCKED_PATH: Path = { path: [1], distance: 1 };
  const MOCKED_MODULE_SERIAL = 'mockedSerial';
  let underTest: OrderManagement;

  beforeEach(() => {
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockResolvedValue();
    jest.spyOn(navCommandSender, 'sendClearModuleNodeNavigationRequest').mockRejectedValue('Tests should not try to clear a module.');
    jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockResolvedValue();
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue(undefined);
    jest.spyOn(NavigatorService, 'getFTSPath').mockReturnValue(MOCKED_PATH);
    jest.useFakeTimers().setSystemTime(MOCKED_DATE);
    jest.mock('../../pairing/fts-pairing-states');
    FtsPairingStates.getInstance().getAllReadyUnassigned = jest.fn().mockReturnValue([]);
    FtsPairingStates.getInstance().getReady = jest.fn();
    PairingStates.getInstance().getReadyForModuleType = jest.fn().mockReturnValue({ serialNumber: MOCKED_MODULE_SERIAL });
    PairingStates.getInstance().isReadyForOrder = jest.fn().mockReturnValue(true);
    underTest = OrderManagement.getInstance();
    StockManagementService.reset();

    jest.mock('../../production/helper');
  });

  afterEach(() => {
    // resetting the singleton for clean tests
    underTest['orderQueue'] = new Array<OrderResponse>();
    underTest['activeOrders'] = [];
    underTest['completedOrders'] = [];
    underTest['navStepsToExecute'] = [];
    underTest['manufactureStepsToExecute'] = [];
    jest.resetAllMocks();
    jest.restoreAllMocks();
    jest.useRealTimers();
  });

  it('should announce the output to the DPS when the navigation to it is started for PICK', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = undefined;
    const navStepOrder2Id = 'navStepOrder2';
    const dpsSerial = 'dpsSerial';
    await setupAndTriggerNavigationRequestExpectSuccess(
      ModuleCommandType.PICK,
      workpiece2,
      workpieceId2,
      navStepOrder2Id,
      orderId2,
      dpsSerial,
      ModuleType.DPS,
    );
    expect(moduleCommandSender.sendAnnounceDpsOutput).toHaveBeenCalledWith(dpsSerial, orderId2, workpiece2);
  });

  it('should not announce the output to the DPS when the navigation to it is started for DROP', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = undefined;
    const navStepOrder2Id = 'navStepOrder2';
    const dpsSerial = 'dpsSerial';
    await setupAndTriggerNavigationRequestExpectSuccess(
      ModuleCommandType.DROP,
      workpiece2,
      workpieceId2,
      navStepOrder2Id,
      orderId2,
      dpsSerial,
      ModuleType.DPS,
    );
    expect(moduleCommandSender.sendAnnounceDpsOutput).not.toHaveBeenCalled();
    expect(underTest['navStepsToExecute']).toEqual([]);
    expect(underTest['manufactureStepsToExecute']).toEqual([]);
  });

  it('should NOT announce the output for a not-DPS when the navigation to it is started for PICK', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = undefined;
    const navStepOrder2Id = 'navStepOrder2';
    const hbwSerial = 'dpsSerial';
    await setupAndTriggerNavigationRequestExpectSuccess(
      ModuleCommandType.PICK,
      workpiece2,
      workpieceId2,
      navStepOrder2Id,
      orderId2,
      hbwSerial,
      ModuleType.HBW,
    );
    expect(moduleCommandSender.sendAnnounceDpsOutput).toHaveBeenCalledWith(hbwSerial, orderId2, workpiece2);
  });

  it('should not announce the output to the DPS when the navigation to it is started for DROP', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = undefined;
    const navStepOrder2Id = 'navStepOrder2';
    const hbwSerial = 'dpsSerial';
    await setupAndTriggerNavigationRequestExpectSuccess(
      ModuleCommandType.DROP,
      workpiece2,
      workpieceId2,
      navStepOrder2Id,
      orderId2,
      hbwSerial,
      ModuleType.HBW,
    );
    expect(moduleCommandSender.sendAnnounceDpsOutput).not.toHaveBeenCalled();
    expect(underTest['navStepsToExecute']).toEqual([]);
    expect(underTest['manufactureStepsToExecute']).toEqual([]);
  });

  async function setupAndTriggerNavigationRequestExpectSuccess(
    command: ModuleCommandType,
    workpiece2: Workpiece,
    workpieceId2: string | undefined,
    navStepOrder2Id: string,
    orderId2: string,
    moduleSerial: string,
    moduleType: ModuleType,
  ) {
    const navStepOrder2: OrderNavigationStep = {
      id: navStepOrder2Id,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
    };
    const dropStepOrder2: OrderManufactureStep = {
      id: navStepOrder2Id,
      type: 'MANUFACTURE',
      moduleType: ModuleType.DPS,
      command: command,
      dependentActionId: navStepOrder2Id,
      state: OrderState.ENQUEUED,
    };

    const navStepOrder2Action: OrderManagementAction = {
      index: 0,
      workpieceId: workpieceId2,
      workpiece: workpiece2,
      value: navStepOrder2,
      orderId: orderId2,
    };

    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId2,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId2,
      type: workpiece2,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStepOrder2, dropStepOrder2],
    };

    underTest['activeOrders'] = [order2];
    underTest['orderQueue'] = [order2];
    underTest['navStepsToExecute'] = [navStepOrder2Action];

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'HBW',
      lastLoadPosition: '2',
    };
    const module: PairedModule = {
      serialNumber: moduleSerial,
      type: 'MODULE',
      subType: moduleType,
    };
    let ftsIsBusy = false;
    jest.spyOn(PairingStates.getInstance(), 'getModuleForOrder').mockReturnValue(undefined);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(module);
    jest
      .spyOn(underTest, 'chooseReadyFtsForStep')
      .mockImplementation(() => (ftsIsBusy ? undefined : <FtsPathResult>{ fts, path: { path: [1], distance: 0 } }));
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockImplementation(() => {
      ftsIsBusy = true;
      return Promise.resolve();
    });
    jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockImplementation(() => {
      return Promise.reject();
    });
    jest.spyOn(moduleCommandSender, 'sendAnnounceDpsOutput').mockImplementation(() => {
      return Promise.resolve();
    });
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue(undefined);
    jest.spyOn(StockManagementService, 'reserveWorkpiece').mockReturnValue(undefined);

    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, moduleSerial, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      navStepOrder2Action.value,
      orderId2,
      navStepOrder2Action.index,
      workpiece2,
      workpieceId2,
      fts,
      module.serialNumber,
    );
    expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalled();
    expect(underTest['navStepsToExecute']).toEqual([]);
    expect(underTest['manufactureStepsToExecute']).toEqual([]);
  }
});
