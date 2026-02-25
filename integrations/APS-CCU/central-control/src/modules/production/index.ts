import { IClientSubscribeOptions } from 'async-mqtt';
import { ANY_SERIAL, getModuleTopic, ModuleTopic } from '../../../../common/protocol';
import { AvailableState } from '../../../../common/protocol/ccu';
import { ModuleCommandType, ModuleState, ModuleType } from '../../../../common/protocol/module';
import { ActionState, InstantActions, passiveInstantActions, State } from '../../../../common/protocol/vda';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { updateModuleCalibrationState } from '../calibration/calibration';
import { sendClearLoadFtsInstantAction } from '../fts/helper';
import { OrderManagement } from '../order/management/order-management';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { PairingStates } from '../pairing/pairing-states';
import { addModuleLogEntry, getVdaErrorsLogLevel, LogLevel } from '../state';
import { handleStock } from './cloud-stock';

export const TOPICS: string[] = [getModuleTopic(ANY_SERIAL, ModuleTopic.STATE)];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

/**
 * Check if a module has an active load.
 * An active load is a load without a defined position
 */
const hasActiveLoad = (state: ModuleState): boolean => {
  if (!state.loads || state.loads.length === 0) {
    return false;
  }
  return state.loads.some(load => !load.loadPosition);
};

const isInstantAction = <T extends InstantActions | ModuleCommandType>(actionState: ActionState<T>) => {
  return Object.values(InstantActions).includes(actionState.command as InstantActions);
};

/**
 * Updates the availability of a module.
 * A module has these availability states in this order
 * - BLOCKED occurs when the module sends a paused state, a fatal error or has a loaded workpiece, but no actionState
 * - BUSY when the module currently has an actionState that has not FINISHED.
 * - READY, but only for a specific order when the module has a finished action state and a workpiece is loaded
 * - READY for any new order when the module has no actionState, or a FINISHED actionState without any loaded workpiece
 * @param state
 */
export const handleModuleAvailability = async (state: ModuleState): Promise<void> => {
  const pairingInstance = PairingStates.getInstance();
  const error = getVdaErrorsLogLevel(state.errors);
  const isLoadedWithWorkpiece = hasActiveLoad(state);

  console.debug(
    `MODULE_AVAIL: update module availability for ${state.serialNumber}:
      error (${error === LogLevel.ERROR}) 
      paused (${state.paused})
      loaded (${isLoadedWithWorkpiece})
      orderId (${state.orderId})
      orderUpdateId (${state.orderUpdateId})
      actionState (${JSON.stringify(state.actionState ?? {})})`,
  );

  if (error === LogLevel.ERROR || state.paused) {
    console.debug(
      `MODULE_AVAIL: update module availability for ${state.serialNumber} to BLOCKED because of 
      error (${error === LogLevel.ERROR}) or 
      paused (${state.paused})`,
    );
    await pairingInstance.updateAvailability(state.serialNumber, AvailableState.BLOCKED);
  } else if (isLoadedWithWorkpiece) {
    /*
     This condition was (!!state.loads && state.loads.length > 0).
     The new condition differs in that it does ignore any load with a defined position.
     This defines a load with a missing position as a load that is in production on the module.
     That will skip loads stored in the HBW, which is desired and makes the special casing for pick commands unnecessary.
     */
    if (!state.actionState) {
      const moduleType = pairingInstance.getModuleType(state.serialNumber);
      if (moduleType === ModuleType.DPS) {
        // The DPS can have an active workpiece without an action when it is processing input
        // In that case it is only ready for the orderId it is processing
        if (state.orderId) {
          await pairingInstance.updateAvailability(state.serialNumber, AvailableState.READY, state.orderId);
        } else {
          await pairingInstance.updateAvailability(state.serialNumber, AvailableState.BUSY);
        }
      } else if (moduleType === ModuleType.HBW) {
        // HBW: Loads with loadPosition are stored in warehouse, not "active". Treat as READY.
        // (isLoadedWithWorkpiece should be false for stored loads; this guards against timing/parsing edge cases)
        const allStored = state.loads?.every(load => !!load.loadPosition) ?? true;
        if (allStored) {
          await pairingInstance.updateAvailability(state.serialNumber, AvailableState.READY);
        } else {
          await pairingInstance.updateAvailability(state.serialNumber, AvailableState.BLOCKED);
        }
      } else if (moduleType !== undefined) {
        // Other modules: having a loaded active workpiece without an action state is an error
        await pairingInstance.updateAvailability(state.serialNumber, AvailableState.BLOCKED);
      } else if (state.loads?.every(load => !!load.loadPosition)) {
        // moduleType unknown (e.g. state before factsheet): if all loads stored, treat as READY (likely HBW mock)
        await pairingInstance.updateAvailability(state.serialNumber, AvailableState.READY);
      } else {
        // moduleType unknown with active load (no position): error requiring user intervention (original fallback)
        await pairingInstance.updateAvailability(state.serialNumber, AvailableState.BLOCKED);
      }
      return;
    }
    // instantActions do not have to be ignored.
    // This might temporarily mark a module busy for an order, but the finished actions will release it.
    // A temporary mark as ready, but waiting for a specific order does not matter either.
    // That specific order will not have an action ready that can be sent to the module until it publishes an updated state.

    if (state.actionState.state === State.FINISHED) {
      await pairingInstance.updateAvailability(state.serialNumber, AvailableState.READY, state.orderId);
    } else {
      await pairingInstance.updateAvailability(state.serialNumber, AvailableState.BUSY, state.orderId);
      return;
    }
  } else {
    // if no active load is on the module, then it can be assumed ready when no errors or a running action are present
    if (state.actionState) {
      if (passiveInstantActions.includes(state.actionState.command as InstantActions)) {
        return;
      }
      if (
        (!isInstantAction(state.actionState) && state.actionState.state !== State.FINISHED) ||
        state.actionState.state === State.RUNNING
      ) {
        await pairingInstance.updateAvailability(state.serialNumber, AvailableState.BUSY, state.orderId);
      } else {
        await pairingInstance.updateAvailability(state.serialNumber, AvailableState.READY);
      }
    } else {
      await pairingInstance.updateAvailability(state.serialNumber, AvailableState.READY);
    }
  }
};

export const clearLoadingBay = (loadRemoved: boolean, ftsSerialNumber: string, orderId: string | undefined): void => {
  if (!loadRemoved || !orderId) {
    return;
  }

  console.debug(`Clearing loading bay for FTS ${ftsSerialNumber} and order ${orderId}`);
  FtsPairingStates.getInstance().clearLoadingBay(ftsSerialNumber, orderId);
};

export const updateFtsLoadHandler = async (state: ModuleState): Promise<void> => {
  if (!state.orderId) {
    return Promise.resolve();
  }
  if (!state.actionState) {
    return Promise.resolve();
  }

  const actionState = state.actionState;
  if (actionState.state !== State.FINISHED) {
    return Promise.resolve();
  }

  if (actionState.command !== ModuleCommandType.PICK.toString() && actionState.command !== ModuleCommandType.DROP.toString()) {
    return Promise.resolve();
  }

  const loadRemovedFromFts = actionState.command === ModuleCommandType.PICK.toString();
  const workpieceId = OrderManagement.getInstance().getWorkpieceId(state.orderId);
  const ftsSerialNumber = FtsPairingStates.getInstance().getFtsSerialNumberForOrderId(state.orderId);

  if (!workpieceId || !ftsSerialNumber) {
    console.debug(`No workpiece or FTS serial number found for order ${state.orderId} workpiece: ${workpieceId} FTS: ${ftsSerialNumber}`);
    return Promise.resolve();
  }

  return sendClearLoadFtsInstantAction(state.orderId, ftsSerialNumber, loadRemovedFromFts, workpieceId);
};

/**
 * Update the workpieceId if a new workpiece has been fetched for the order
 * @param state
 */
export const updateOrderWorkpieceId = (state: ModuleState): void => {
  if (!state.actionState) {
    return;
  }

  const actionState = state.actionState;
  if (actionState.state !== State.FINISHED) {
    return;
  }

  // only a DROP command can introduce a new workpiece
  if (actionState.command !== ModuleCommandType.DROP.toString()) {
    return;
  }

  // a new workpiece can only be received from the HBW
  const moduleType = PairingStates.getInstance().getModuleType(state.serialNumber);
  if (moduleType !== ModuleType.HBW) {
    return;
  }

  const orderManagement = OrderManagement.getInstance();
  const oldWorkpieceId = orderManagement.getWorkpieceId(state.orderId);
  const newWorkpieceId = actionState.result;
  console.debug(`PRODUCTION_HANDLER: Handle workpieceId update for orderId ${state.orderId} from ${oldWorkpieceId} to ${newWorkpieceId}`);
  // only update when the HBW does send a new ID
  if (newWorkpieceId && oldWorkpieceId !== newWorkpieceId) {
    orderManagement.updateOrderWorkpieceId(state.orderId, newWorkpieceId);
  }
};

export const handleMessage = async (message: string): Promise<void> => {
  if (!message) {
    // ignoring empty message
    return;
  }
  console.log('Message:', message);
  const state = JSON.parse(message, jsonIsoDateReviver) as ModuleState;
  await addModuleLogEntry(state);
  await handleModuleAvailability(state);
  // detect the module calibration and publish the calibration data correctly
  await updateModuleCalibrationState(state);
  await handleStock(state);
  const ignoredCommands: (InstantActions | ModuleCommandType | undefined)[] = [InstantActions.SET_STATUS_LED];
  if (
    state?.actionState?.state == State.FINISHED &&
    state?.actionState?.id?.length > 0 &&
    !ignoredCommands.includes(state.actionState?.command)
  ) {
    updateOrderWorkpieceId(state);
    await updateFtsLoadHandler(state);
    return OrderManagement.getInstance().handleActionUpdate(
      state.orderId,
      state.actionState.id,
      state.actionState.state,
      state.actionState.result,
    );
  }
  // When receiving a state update from a module, simply retry all queued module as well as FTS steps
  // If no steps are queued, try to look for a new order
  return OrderManagement.getInstance().resumeOrders();
};
