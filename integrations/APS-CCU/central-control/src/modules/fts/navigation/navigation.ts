import { randomUUID } from 'node:crypto';
import { FtsTopic, getFtsTopic, OrderResponse, Workpiece } from '../../../../../common/protocol';
import {
  AvailableState,
  FtsPairedModule,
  OrderManufactureStep,
  OrderNavigationStep,
  PairedModule,
} from '../../../../../common/protocol/ccu';
import { FtsCommandType, LOADING_BAY_COUNT, LoadingBay } from '../../../../../common/protocol/fts';
import { ModuleCommandType, ModuleType } from '../../../../../common/protocol/module';
import { ControllerNotReadyError, FTSNotReadyError, FtsPathResult } from '../../../models/models';
import { getMqttClient } from '../../../mqtt/mqtt';
import { FactoryLayoutService, FactoryNodeBlocker } from '../../layout/factory-layout-service';
import { FtsPairingStates } from '../../pairing/fts-pairing-states';
import { PairingStates } from '../../pairing/pairing-states';
import { DockingMetadata, FtsOrder } from '../model';
import { NavigatorService, Path } from './navigator-service';

/**
 * Calculate the length of the available FTS paths to choose the nearest FTS.
 * @param target
 */
export const getSortedUnassignedFtsPaths = (target: string): Array<{ fts: FtsPairedModule; path: Path }> => {
  const ftsPairingStates = FtsPairingStates.getInstance();
  const allFts = ftsPairingStates.getAllReadyUnassigned();
  const result: Array<{ fts: FtsPairedModule; path: Path }> = [];

  for (const fts of allFts) {
    const serialNumber = fts.state.serialNumber;
    const startPosition = fts.state.lastModuleSerialNumber;
    if (!startPosition) {
      continue;
    }

    const path = NavigatorService.getFTSPath(startPosition, target, serialNumber);
    if (path) {
      result.push({
        fts: fts.state,
        path: path,
      });
    }
  }
  // sort ascending, smallest distances first
  return result.sort((a, b) => a.path.distance - b.path.distance);
};

/**
 * Calculate the length of the available FTS paths to choose the nearest free module from a list.
 * @param fts
 * @param targetModules
 */
export const getSortedModulePaths = (
  fts: FtsPairedModule,
  targetModules: Array<PairedModule>,
): Array<{ module: PairedModule; path: Path }> => {
  const result: Array<{ module: PairedModule; path: Path }> = [];
  if (!fts.lastModuleSerialNumber) {
    return result;
  }
  for (const mod of targetModules) {
    const path = NavigatorService.getFTSPath(fts.lastModuleSerialNumber, mod.serialNumber, fts.serialNumber);
    if (path) {
      result.push({
        module: mod,
        path: path,
      });
    }
  }
  // sort ascending, smallest distances first
  return result.sort((a, b) => a.path.distance - b.path.distance);
};

/**
 * Choose an FTS wuile keeping one loading bay open if no PICK action can be guaranteed for the last workpiece
 * @param order
 * @param nav
 * @param orderId
 * @param paths
 * @param ftsPairingStates
 */
const selectFtsWithoutOverfilling = (
  order: OrderResponse,
  nav: OrderNavigationStep,
  orderId: string,
  paths: Array<FtsPathResult>,
  ftsPairingStates: FtsPairingStates,
): FtsPathResult | undefined => {
  // make sure to always have an empty loading bay unless the workpiece can be dropped immediately
  const nextStep = order.productionSteps.find(nextStep => nextStep.dependentActionId === nav.id);
  if (nextStep && nextStep.type === 'MANUFACTURE' && nextStep.command === ModuleCommandType.DROP) {
    let nextManufactureStep: OrderNavigationStep | OrderManufactureStep | undefined = nextStep;
    do {
      // there is always a next manufacture step available in the loop.
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      nextManufactureStep = order.productionSteps.find(step => step.dependentActionId === nextManufactureStep!.id);
    } while (nextManufactureStep && nextManufactureStep.type !== 'MANUFACTURE');
    if (
      nextManufactureStep &&
      nextManufactureStep.command === ModuleCommandType.PICK &&
      PairingStates.getInstance().getReadyForModuleType(nextManufactureStep.moduleType, orderId)
    ) {
      // The drop is followed by a PICK with a module that is ready
      console.debug(`ORDER_MANAGEMENT: CHOOSE_FTS with guaranteed pick.`);
      for (const ftspath of paths) {
        if (ftsPairingStates.getOpenloadingBay(ftspath.fts.serialNumber)) {
          return ftspath;
        }
      }
    } else {
      console.debug(`ORDER_MANAGEMENT: CHOOSE_FTS WITHOUT guaranteed pick.`);
      for (const ftspath of paths) {
        if (ftsPairingStates.getLoadedOrderIds(ftspath.fts.serialNumber).length < LOADING_BAY_COUNT - 1) {
          return ftspath;
        }
      }
      return undefined;
    }
  }
  // Choose the first ready FTS if there was no need to choose a specific one
  return paths[0];
};

export function selectFtsPathForStep(
  order: OrderResponse,
  targetSerialNumber: string,
  nav: OrderNavigationStep,
): FtsPathResult | undefined {
  const orderId = order.orderId;
  const ftsPairingStates = FtsPairingStates.getInstance();
  const orderFts = ftsPairingStates.getForOrder(orderId);
  console.log('ftsPairingStates', ftsPairingStates);
  console.log('orderFts', orderFts);
  if (orderFts) {
    if (!ftsPairingStates.isReadyForOrder(orderFts.serialNumber, orderId) || !orderFts.lastModuleSerialNumber) {
      console.log(`NAVIGATION: FTS is not ready or has no last module serial number: ${orderFts.serialNumber}`);
      return undefined;
    }
    const path = NavigatorService.getFTSPath(orderFts.lastModuleSerialNumber, targetSerialNumber, orderFts.serialNumber);
    console.log(`NAVIGATION: PATH found for FTS: ${path}`);
    if (!path) {
      return undefined;
    }
    return {
      fts: orderFts,
      path: path,
    };
  }

  const fts = ftsPairingStates.getFtsAtPosition(targetSerialNumber, order.orderId);
  console.log('Continuing with new fts', orderFts, fts);
  if (fts) {
    return {
      fts: fts,
      path: {
        path: [],
        distance: 0,
      },
    };
  }

  const paths = getSortedUnassignedFtsPaths(targetSerialNumber);
  if (!paths.length) {
    return;
  }
  return selectFtsWithoutOverfilling(order, nav, orderId, paths, ftsPairingStates);
}

/**
 * Sets the loading bay information in the order and update the loading bay cache
 * @param order The order to update
 * @param ftsPairingStates The FTS pairing states to update the loading bay cache
 * @param serialNumber The serial number of the FTS
 * @param dockingMetadata The loading bay information if undefined the loading bay information is not set
 */
export const addDockingMetadataToOrder = (
  order: FtsOrder,
  ftsPairingStates: FtsPairingStates,
  serialNumber: string,
  dockingMetadata?: DockingMetadata,
) => {
  if (!dockingMetadata) {
    return;
  }

  order.nodes
    .filter(node => node.action?.type === FtsCommandType.DOCK)
    .forEach(node => {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      node.action!.metadata = dockingMetadata;
    });

  console.debug(`Order ${order.orderId} updated with loading bay ${JSON.stringify(dockingMetadata)}`);
  ftsPairingStates.setLoadingBay(serialNumber, dockingMetadata.loadPosition, order.orderId);
};

const getDockingMetadataForOrder = (
  serialNumber: string,
  orderId: string,
  workpieceId: string | undefined,
  workpiece: Workpiece,
  targetModule: ModuleType,
  ftsPairingStates: FtsPairingStates,
): DockingMetadata | undefined => {
  let loadingbay = ftsPairingStates.getLoadingBayForOrder(serialNumber, orderId);
  if (!loadingbay) {
    const loadingBayPosition = ftsPairingStates.getOpenloadingBay(serialNumber);
    if (loadingBayPosition === undefined) {
      throw new ControllerNotReadyError('FTS');
    }

    loadingbay = loadingBayPosition;
  }

  console.debug(`Docking metadata for workpiece ${workpieceId} is ${loadingbay} with workpieceId ${workpieceId} and loadType ${workpiece}`);

  return {
    loadId: workpieceId,
    loadType: workpiece,
    loadPosition: loadingbay,
  };
};
/**
 * Get the nodes that are blocked by an order in the correct sequence to free them later
 * @param order
 */
export const getBlockedNodesForOrder = (order: FtsOrder): Array<FactoryNodeBlocker> => {
  const serialNumber = order.serialNumber;
  let previousNodeId: string | undefined = undefined;
  const blockers: Array<FactoryNodeBlocker> = [];
  for (const node of order.nodes) {
    if (node.id === previousNodeId) {
      // skip repeated nodes
      continue;
    }
    blockers.push({
      nodeId: node.id,
      ftsSerialNumber: serialNumber,
      afterNodeId: previousNodeId,
    });
    previousNodeId = node.id;
  }
  return blockers;
};

export const sendNavigationRequest = async (
  navigationStep: OrderNavigationStep,
  orderId: string,
  orderUpdatedId: number,
  workpiece: Workpiece,
  workpieceId: string | undefined,
  fts: FtsPairedModule,
  targetSerial: string,
): Promise<void> => {
  // Is there an FTS ready to take the navigation Request?
  const ftsPairingStates = FtsPairingStates.getInstance();
  const pairingStates = PairingStates.getInstance();

  // sanity check to validate that the FTS is ready, to validate that it did not change in a node event loop
  const isFtsReady = ftsPairingStates.isReady(fts.serialNumber);
  if (!isFtsReady) {
    throw new FTSNotReadyError('No FTS in state READY found');
  }

  const serialNumber = fts.serialNumber;

  const startPosition = fts.lastModuleSerialNumber;
  if (!startPosition) {
    throw new FTSNotReadyError(
      `FTS with serial number ${serialNumber} has no last module serial number unable to defer starting position, order: ${orderId} actionId: ${navigationStep.id} target: ${navigationStep.target}`,
    );
  }

  const targetType = navigationStep.target;
  const isReady = pairingStates.isReadyForOrder(targetSerial, orderId);
  if (!isReady) {
    throw new ControllerNotReadyError(
      'MODULE',
      targetType,
      `target of type ${targetType} is not ready to accept a new Order therefor FTS cannot navigate to it`,
    );
  }
  const targetPosition = targetSerial;

  const dockingMetadata = getDockingMetadataForOrder(serialNumber, orderId, workpieceId, workpiece, targetType, ftsPairingStates);

  console.debug(`Fts ${serialNumber} starts at position ${startPosition} to position ${targetPosition}`);

  try {
    const newOrder: FtsOrder = NavigatorService.getFTSOrder(
      startPosition,
      targetPosition,
      orderId,
      orderUpdatedId,
      serialNumber,
      navigationStep.id,
    );
    addDockingMetadataToOrder(newOrder, ftsPairingStates, serialNumber, dockingMetadata);

    console.debug('FTS_ORDER publish', JSON.stringify(newOrder, null, 2));
    const mqtt = getMqttClient();
    console.debug(
      `ORDER_MANAGEMENT: Publishing order ${orderId} and action ${navigationStep.id} to ${getFtsTopic(serialNumber, FtsTopic.ORDER)} with`,
    );
    const blockedNodes = getBlockedNodesForOrder(newOrder);
    FactoryLayoutService.blockNodeSequence(blockedNodes);
    await ftsPairingStates.updateAvailability(
      serialNumber,
      AvailableState.BUSY,
      orderId,
      fts.lastNodeId,
      fts.lastModuleSerialNumber,
      dockingMetadata?.loadPosition,
    );
    // block the target for the current order so that the command can be sent to the correct one and no other order can use it
    await pairingStates.updateAvailability(targetPosition, AvailableState.READY, orderId);
    await mqtt.publish(getFtsTopic(serialNumber, FtsTopic.ORDER), JSON.stringify(newOrder), {
      qos: 2,
    });
    console.debug('ORDER_MANAGEMENT: FTS_ORDER published');

    return Promise.resolve();
  } catch (e) {
    // revert the availability if the order could not be sent
    await ftsPairingStates.updateAvailability(
      serialNumber,
      AvailableState.READY,
      orderId,
      fts.lastNodeId,
      fts.lastModuleSerialNumber,
      dockingMetadata?.loadPosition,
    );
    await pairingStates.updateAvailability(targetPosition, AvailableState.READY);
    return Promise.reject(e);
  }
};

export const sendClearModuleNodeNavigationRequest = async (blockedModuleId: string): Promise<void> => {
  // Is there an FTS ready to take the navigation Request?
  const ftsPairingStates = FtsPairingStates.getInstance();
  const pairingStates = PairingStates.getInstance();
  const orderId = randomUUID();

  const ftsAtModule = ftsPairingStates.getFtsAtPosition(blockedModuleId);
  if (!ftsAtModule) {
    return;
  }
  // Only try to drive to connected modules in the layout, but do not use the charger as that is no normal docking location
  const freeModule = pairingStates
    .getAll()
    .find(m => m.pairedSince && m.connected && m.subType !== ModuleType.CHRG && !ftsPairingStates.getFtsAtPosition(m.serialNumber));
  if (!freeModule) {
    console.log(
      `ORDER_MANAGEMENT: The docking node for module ${blockedModuleId} is blocked by an FTS, but no other docking location is free`,
    );
    return;
  }

  const serialNumber = ftsAtModule.serialNumber;

  const startPosition = blockedModuleId;
  const targetPosition = freeModule.serialNumber;

  const openBay = ftsPairingStates.getOpenloadingBay(serialNumber);

  const dockingMetadata: DockingMetadata = {
    loadPosition: openBay || LoadingBay.MIDDLE,
    noLoadChange: true,
  };

  console.debug(
    `ORDER_MANAGEMENT: Fts ${serialNumber} starts at position ${startPosition} to position ${targetPosition} to free up the start position`,
  );

  try {
    const newOrder: FtsOrder = NavigatorService.getFTSOrder(startPosition, targetPosition, orderId, 0, serialNumber, randomUUID());
    console.debug(JSON.stringify(newOrder, null, 2));

    newOrder.nodes
      .filter(node => node.action?.type === FtsCommandType.DOCK)
      .forEach(node => {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        node.action!.metadata = dockingMetadata;
      });

    const mqtt = getMqttClient();
    console.debug(`ORDER_MANAGEMENT: Publishing untracked clearing order ${orderId} to ${getFtsTopic(serialNumber, FtsTopic.ORDER)} with`);
    const blockedNodes = getBlockedNodesForOrder(newOrder);
    FactoryLayoutService.blockNodeSequence(blockedNodes);
    await mqtt.publish(getFtsTopic(serialNumber, FtsTopic.ORDER), JSON.stringify(newOrder));
    await ftsPairingStates.updateAvailability(
      serialNumber,
      AvailableState.BUSY,
      orderId,
      ftsAtModule.lastNodeId,
      ftsAtModule.lastModuleSerialNumber,
      dockingMetadata.loadPosition,
    );
    return Promise.resolve();
  } catch (e) {
    return Promise.reject(e);
  }
};
