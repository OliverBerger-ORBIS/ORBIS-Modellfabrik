import { randomUUID } from 'node:crypto';
import { FtsTopic, getFtsTopic } from '../../../../common/protocol';
import { AvailableState } from '../../../../common/protocol/ccu';
import { FtsCommandType, FtsErrors, FtsState, NODE_ID_UNKNOWN } from '../../../../common/protocol/fts';
import { ModuleType } from '../../../../common/protocol/module';
import { InstantAction, InstantActions, State, VdaError } from '../../../../common/protocol/vda';
import config from '../../config';
import { getMqttClient } from '../../mqtt/mqtt';
import { FactoryLayoutService } from '../layout/factory-layout-service';
import { OrderManagement } from '../order/management/order-management';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { PairingStates } from '../pairing/pairing-states';
import { clearLoadingBay } from '../production';
import { sendResetModuleInstantAction } from '../production/production';
import { LogLevel, getVdaErrorsLogLevel } from '../state';
import {
  freeBlockedChargers,
  handleChargingUpdate,
  isBatteryLow,
  resetBusyChargersThatAreEmpty,
  retriggerChargeOrders,
  triggerChargeOrderForFts,
} from './charge';
import CurrentErrorsService from '../current-errors/current-errors.service';

/**
 * Determine the last module serial number for the FTS based on the last finished action
 * @param state
 */
export const getLastModuleSerialNumber = (state: FtsState): string | undefined => {
  if (state.driving) {
    console.debug('FTS_AVAIL: last module is undefined because of driving');
    return undefined;
  }

  // During initialisation of the FTS lastNodeId will be set to the serial number of the DPS
  // The last node in a docking action is also the ID of the module that the FTS is docked at.
  if (state.lastNodeId && isNaN(+state.lastNodeId)) {
    console.debug(`FTS_AVAIL: No action state found. Using given lastNodeId `);
    return state.lastNodeId;
  }

  // If there is no action state and the last node id is not numeric, then the last module of the FTS cannot be determined.
  if (!state.actionState || Object.keys(state.actionState).length === 0) {
    console.debug(
      `FTS_AVAIL: last module is undefined because of no action state found and last node id is not non-numeric: ${state.lastNodeId}`,
    );
    return undefined;
  }

  // if the FTS is not driving and there is an action, use it to determine the position
  if (state.actionState.state !== State.FINISHED) {
    console.debug(`FTS_AVAIL: last module is undefined because of action is: ${state.actionState.state}`);
    return undefined;
  }

  const targetModuleType = OrderManagement.getInstance().getTargetModuleTypeForNavActionId(state.actionState.id);
  if (!targetModuleType) {
    console.debug(`FTS_AVAIL: last module is undefined because target module type was not found for action id: ${state.actionState.id}`);
    return undefined;
  }

  const targetModule = PairingStates.getInstance().getForModuleType(targetModuleType, state.orderId);
  if (!targetModule) {
    console.debug(
      `FTS_AVAIL: last module is undefined because target module was not found for action id: ${state.actionState.id} and type: ${targetModuleType}`,
    );
    return undefined;
  }

  console.debug(`FTS_AVAIL: last module is ${targetModule.serialNumber}`);
  return targetModule.serialNumber;
};

export const updateFtsAvailability = async (state: FtsState): Promise<AvailableState> => {
  const pairings = FtsPairingStates.getInstance();

  // errors of type warning do not make the FTS unavailable.
  const error = getVdaErrorsLogLevel(state.errors);
  if (error === LogLevel.ERROR || state.paused || state.lastNodeId == NODE_ID_UNKNOWN) {
    console.debug(
      `FTS_AVAIL: update FTS availability for ${state.serialNumber} to BLOCKED because of error (${error === LogLevel.ERROR}) or paused (${
        state.paused
      }) or unknown node (${state.lastNodeId == NODE_ID_UNKNOWN})`,
    );
    await pairings.updateAvailability(state.serialNumber, AvailableState.BLOCKED, state.orderId, state.lastNodeId);
    return AvailableState.BLOCKED;
  }

  const lastModuleSerialNumber = getLastModuleSerialNumber(state);
  if (state.driving || state.waitingForLoadHandling) {
    console.debug(
      `FTS_AVAIL: update FTS availability for ${state.serialNumber} to BUSY because of driving or waiting for load handler with last module serial number: ${lastModuleSerialNumber}`,
    );
    await pairings.updateAvailability(state.serialNumber, AvailableState.BUSY, state.orderId, state.lastNodeId, lastModuleSerialNumber);
    return AvailableState.BUSY;
  } else if (!state.actionState || state.actionState.state === State.FINISHED) {
    // Ready if the FTS has no actionState, this can only happen if the FTS has been started. Or if the action is finished
    console.debug(
      `FTS_AVAIL: update FTS availability for ${state.serialNumber} to READY, last module serial number: ${lastModuleSerialNumber}`,
    );
    await pairings.updateAvailability(state.serialNumber, AvailableState.READY, undefined, state.lastNodeId, lastModuleSerialNumber);
    return AvailableState.READY;
  } else {
    // If the FTS is not driving and the action is not finished, it is busy
    console.debug(
      `FTS_AVAIL: update FTS availability for ${state.serialNumber} to BUSY because action is not finished, last module serial number: ${lastModuleSerialNumber}`,
    );
    await pairings.updateAvailability(state.serialNumber, AvailableState.BUSY, state.orderId, state.lastNodeId, lastModuleSerialNumber);
    return AvailableState.BUSY;
  }
};

export const handleResetWarning = async (resetWarnings: Array<VdaError>, serialNumber: string): Promise<void> => {
  const management = OrderManagement.getInstance();
  const pairingStates = FtsPairingStates.getInstance();

  for (const e of resetWarnings) {
    if (e.errorType === FtsErrors.RESET) {
      CurrentErrorsService.getInstance().removeError(serialNumber);
      // reset orders for loaded workpieces
      const orderIds = pairingStates.getLoadedOrderIds(serialNumber);
      pairingStates.resetLoadingBay(serialNumber);
      for (const id of orderIds) {
        PairingStates.getInstance().clearModuleForOrder(id);
        await management.resetOrder(id);
      }

      // Update readiness of the FTS and set the last docked module to UNKNOWN
      console.log(`FTS_AVAIL: update FTS availability for ${serialNumber} to BLOCKED after reset at position UNKNOWN`);
      await pairingStates.updateAvailability(serialNumber, AvailableState.READY, undefined, NODE_ID_UNKNOWN, NODE_ID_UNKNOWN);

      // always reset the current order, even if there is no workpiece loaded
      const orderId = e.errorReferences?.find(r => r.referenceKey === 'orderId')?.referenceValue as string;
      if (!orderId) {
        console.debug(`FTS Reset without associated orderId`);
        continue;
      }
      console.debug(`FTS Reset for order ${orderId}`);
      // completely reset the module of the active order in case it knew about the order
      const module = PairingStates.getInstance().getModuleForOrder(orderId);
      if (module && module.subType !== ModuleType.HBW && module.subType !== ModuleType.CHRG) {
        CurrentErrorsService.getInstance().removeError(module.serialNumber);
        await sendResetModuleInstantAction(module.serialNumber);
        PairingStates.getInstance().clearModuleForOrder(orderId);
      }
      await management.resetOrder(orderId);
    }
  }
};

type TempResetContain = {
  isResetContained: boolean;
  resetErrors: Array<VdaError>;
};

const isResetContained = (state: FtsState): TempResetContain => {
  const resetErrors = state.errors?.filter(e => e.errorType === FtsErrors.RESET) || [];
  return {
    isResetContained: resetErrors.length > 0,
    resetErrors,
  };
};

/**
 * Checks the paired modules for a charger and returns true if a charger is available and ready to be used.
 * @returns true if a charger is available and ready to be used
 */
export const checkChargerAvailability = (): boolean => {
  const pairedChargers = PairingStates.getInstance().getAllReady(ModuleType.CHRG);
  return pairedChargers.length > 0;
};

/**
 * Updates the blocked nodes for a given FTS state.
 * If the lastNodeId is NODE_ID_UNKNOWN, releases all nodes associated with the FTS.
 * If the FTS sends a completed docking action that has not been handled,
 *    releases all nodes except the lastNodeId.
 * Otherwise, releases nodes before the lastNodeId.
 */
export const updateFtsBlockedNodes = (state: FtsState) => {
  if (state.lastNodeId === NODE_ID_UNKNOWN) {
    // An FTS at the unknown node is effectively removed from the factory, so release its nodes.
    FactoryLayoutService.releaseAllNodes(state.serialNumber);
  } else if (state.actionState?.state === State.FINISHED && state.actionState.command === FtsCommandType.DOCK) {
    const orderManagement = OrderManagement.getInstance();
    if (
      orderManagement.isOrderActionRunning(state.orderId, state.actionState.id) ||
      (!orderManagement.getActiveOrder(state.orderId) &&
        FtsPairingStates.getInstance().getLastFinishedDockId(state.serialNumber) !== state.actionState.id)
    ) {
      // Delete all blocked nodes when the FTS is docked.
      // Only do that once when a specific docking action is finished.
      FactoryLayoutService.releaseAllNodesExcept(state.serialNumber, state.lastNodeId);
    }
    FtsPairingStates.getInstance().setLastFinishedDockId(state.serialNumber, state.actionState.id);
  } else {
    FactoryLayoutService.releaseNodesBefore(state.serialNumber, state.lastNodeId);
  }
};

/**
 * Handle the FTS state. If the FTS is in a reset state, the order will be reset and the FTS will be positioned at
 * UNKNOWN. The user needs to re-dock the FTS to the DPS in order to use it again.
 * If not the availability of the FTS will be updated.
 * @param state The FTS state
 */
export const handleFtsState = async (state: FtsState): Promise<void> => {
  console.debug('FTS_STATE received: ', JSON.stringify(state, null, 2));
  handleChargingUpdate(state);
  const tempResetContain = isResetContained(state);
  if (tempResetContain.isResetContained) {
    console.log(`FTS_AVAIL: FTS ${state.serialNumber} is in reset state. Resetting order.`);
    FactoryLayoutService.releaseAllNodes(state.serialNumber);
    return handleResetWarning(tempResetContain.resetErrors, state.serialNumber);
  } else {
    console.log(`FTS_AVAIL: update FTS availability for ${state.serialNumber}`);
    updateFtsBlockedNodes(state);
    const ftsAvail = await updateFtsAvailability(state);
    await retriggerChargeOrders();
    // only re-trigger fts commands if the FTS is ready to accept a new one
    if (ftsAvail === AvailableState.READY) {
      const batteryIsLow: boolean = isBatteryLow(state);
      if (batteryIsLow) {
        console.debug(`FTS BATTERY: battery is low. Drive to charger if config enables it`);
      }
      const chargingDisabled: boolean = config.ftsCharge.disabled;
      const hasChargerAvailable: boolean = checkChargerAvailability();
      if (batteryIsLow && !chargingDisabled) {
        if (!hasChargerAvailable) {
          console.debug(`FTS BATTERY: No charger is ready. Trying to free chargers.`);
          await resetBusyChargersThatAreEmpty();
        }
        console.debug(`FTS BATTERY: Triggering Charge order.`);
        await triggerChargeOrderForFts(state.serialNumber);
      } else {
        if (chargingDisabled) {
          console.debug(`FTS BATTERY: Charging is disabled. Do not drive to charger.`);
        }
        console.debug(`ORDER_MANAGEMENT: re-trigger navigation steps, FTS ${state.serialNumber} is READY again.`);
        await OrderManagement.getInstance().retriggerFTSSteps();
      }
    }
    // FITEFF22-607: Always move FTS away from chargers
    await freeBlockedChargers(true);
    return Promise.resolve();
  }
};

/**
 * Send an instant action to the FTS to clear the load handler. This will result in the FTS being available again.
 */
export const sendClearLoadFtsInstantAction = async (
  orderId: string,
  serialNumber: string,
  loadDropped = false,
  workpieceId?: string,
): Promise<void> => {
  const topic = getFtsTopic(serialNumber, FtsTopic.INSTANT_ACTION);
  const loadingBay = workpieceId ? FtsPairingStates.getInstance().getLoadingBayForOrder(serialNumber, orderId) : undefined;
  const workpieceType = OrderManagement.getInstance().getWorkpieceType(orderId);

  console.debug(
    `Sending clear load handler instant action for FTS ${serialNumber} with load dropped ${loadDropped} and workpiece ${workpieceId} to topic ${topic}`,
  );
  const instantAction: InstantAction = {
    serialNumber,
    timestamp: new Date(),
    actions: [
      {
        actionId: randomUUID(),
        actionType: InstantActions.CLEAR_LOAD_HANDLER,
        metadata: {
          loadDropped,
          loadType: workpieceType,
          loadId: workpieceId,
          loadPosition: loadingBay,
        },
      },
    ],
  };

  clearLoadingBay(loadDropped, serialNumber, orderId);

  const mqttClient = getMqttClient();

  return mqttClient.publish(topic, JSON.stringify(instantAction));
};

/**
 * Send an instant action to the FTS to reset it and force a re-pairing.
 */
export const sendResetFtsInstantAction = async (serialNumber: string): Promise<void> => {
  const topic = getFtsTopic(serialNumber, FtsTopic.INSTANT_ACTION);

  console.debug(`Sending reset instant action for FTS ${serialNumber} to topic ${topic}`);
  const instantAction: InstantAction = {
    serialNumber,
    timestamp: new Date(),
    actions: [
      {
        actionId: randomUUID(),
        actionType: InstantActions.RESET,
      },
    ],
  };
  const ftsPairingStates = FtsPairingStates.getInstance();
  ftsPairingStates.resetLoadingBay(serialNumber);
  await ftsPairingStates.updateAvailability(serialNumber, AvailableState.BLOCKED, undefined, NODE_ID_UNKNOWN);

  const mqttClient = getMqttClient();

  return mqttClient.publish(topic, JSON.stringify(instantAction), { qos: 2 });
};
