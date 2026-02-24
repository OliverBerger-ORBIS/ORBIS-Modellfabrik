"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.updateOrderWorkpieceId = exports.updateFtsLoadHandler = exports.clearLoadingBay = exports.handleModuleAvailability = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../common/protocol");
const ccu_1 = require("../../../../common/protocol/ccu");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const calibration_1 = require("../calibration/calibration");
const helper_1 = require("../fts/helper");
const order_management_1 = require("../order/management/order-management");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const pairing_states_1 = require("../pairing/pairing-states");
const state_1 = require("../state");
const cloud_stock_1 = require("./cloud-stock");
exports.TOPICS = [(0, protocol_1.getModuleTopic)(protocol_1.ANY_SERIAL, protocol_1.ModuleTopic.STATE)];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
/**
 * Check if a module has an active load.
 * An active load is a load without a defined position
 */
const hasActiveLoad = (state) => {
    if (!state.loads || state.loads.length === 0) {
        return false;
    }
    return state.loads.some(load => !load.loadPosition);
};
const isInstantAction = (actionState) => {
    return Object.values(vda_1.InstantActions).includes(actionState.command);
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
const handleModuleAvailability = async (state) => {
    const pairingInstance = pairing_states_1.PairingStates.getInstance();
    const error = (0, state_1.getVdaErrorsLogLevel)(state.errors);
    const isLoadedWithWorkpiece = hasActiveLoad(state);
    console.debug(`MODULE_AVAIL: update module availability for ${state.serialNumber}:
      error (${error === state_1.LogLevel.ERROR}) 
      paused (${state.paused})
      loaded (${isLoadedWithWorkpiece})
      orderId (${state.orderId})
      orderUpdateId (${state.orderUpdateId})
      actionState (${JSON.stringify(state.actionState ?? {})})`);
    if (error === state_1.LogLevel.ERROR || state.paused) {
        console.debug(`MODULE_AVAIL: update module availability for ${state.serialNumber} to BLOCKED because of 
      error (${error === state_1.LogLevel.ERROR}) or 
      paused (${state.paused})`);
        await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.BLOCKED);
    }
    else if (isLoadedWithWorkpiece) {
        /*
         This condition was (!!state.loads && state.loads.length > 0).
         The new condition differs in that it does ignore any load with a defined position.
         This defines a load with a missing position as a load that is in production on the module.
         That will skip loads stored in the HBW, which is desired and makes the special casing for pick commands unnecessary.
         */
        if (!state.actionState) {
            if (pairingInstance.getModuleType(state.serialNumber) === module_1.ModuleType.DPS) {
                // The DPS can have an active workpiece without an action when it is processing input
                // In that case it is only ready for the orderId it is processing
                if (state.orderId) {
                    await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.READY, state.orderId);
                }
                else {
                    await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.BUSY);
                }
            }
            else {
                // having a loaded active workpiece without an action state is an error that requires user intervention
                await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.BLOCKED);
            }
            return;
        }
        // instantActions do not have to be ignored.
        // This might temporarily mark a module busy for an order, but the finished actions will release it.
        // A temporary mark as ready, but waiting for a specific order does not matter either.
        // That specific order will not have an action ready that can be sent to the module until it publishes an updated state.
        if (state.actionState.state === vda_1.State.FINISHED) {
            await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.READY, state.orderId);
        }
        else {
            await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.BUSY, state.orderId);
            return;
        }
    }
    else {
        // if no active load is on the module, then it can be assumed ready when no errors or a running action are present
        if (state.actionState) {
            if (vda_1.passiveInstantActions.includes(state.actionState.command)) {
                return;
            }
            if ((!isInstantAction(state.actionState) && state.actionState.state !== vda_1.State.FINISHED) ||
                state.actionState.state === vda_1.State.RUNNING) {
                await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.BUSY, state.orderId);
            }
            else {
                await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.READY);
            }
        }
        else {
            await pairingInstance.updateAvailability(state.serialNumber, ccu_1.AvailableState.READY);
        }
    }
};
exports.handleModuleAvailability = handleModuleAvailability;
const clearLoadingBay = (loadRemoved, ftsSerialNumber, orderId) => {
    if (!loadRemoved || !orderId) {
        return;
    }
    console.debug(`Clearing loading bay for FTS ${ftsSerialNumber} and order ${orderId}`);
    fts_pairing_states_1.FtsPairingStates.getInstance().clearLoadingBay(ftsSerialNumber, orderId);
};
exports.clearLoadingBay = clearLoadingBay;
const updateFtsLoadHandler = async (state) => {
    if (!state.orderId) {
        return Promise.resolve();
    }
    if (!state.actionState) {
        return Promise.resolve();
    }
    const actionState = state.actionState;
    if (actionState.state !== vda_1.State.FINISHED) {
        return Promise.resolve();
    }
    if (actionState.command !== module_1.ModuleCommandType.PICK.toString() && actionState.command !== module_1.ModuleCommandType.DROP.toString()) {
        return Promise.resolve();
    }
    const loadRemovedFromFts = actionState.command === module_1.ModuleCommandType.PICK.toString();
    const workpieceId = order_management_1.OrderManagement.getInstance().getWorkpieceId(state.orderId);
    const ftsSerialNumber = fts_pairing_states_1.FtsPairingStates.getInstance().getFtsSerialNumberForOrderId(state.orderId);
    if (!workpieceId || !ftsSerialNumber) {
        console.debug(`No workpiece or FTS serial number found for order ${state.orderId} workpiece: ${workpieceId} FTS: ${ftsSerialNumber}`);
        return Promise.resolve();
    }
    return (0, helper_1.sendClearLoadFtsInstantAction)(state.orderId, ftsSerialNumber, loadRemovedFromFts, workpieceId);
};
exports.updateFtsLoadHandler = updateFtsLoadHandler;
/**
 * Update the workpieceId if a new workpiece has been fetched for the order
 * @param state
 */
const updateOrderWorkpieceId = (state) => {
    if (!state.actionState) {
        return;
    }
    const actionState = state.actionState;
    if (actionState.state !== vda_1.State.FINISHED) {
        return;
    }
    // only a DROP command can introduce a new workpiece
    if (actionState.command !== module_1.ModuleCommandType.DROP.toString()) {
        return;
    }
    // a new workpiece can only be received from the HBW
    const moduleType = pairing_states_1.PairingStates.getInstance().getModuleType(state.serialNumber);
    if (moduleType !== module_1.ModuleType.HBW) {
        return;
    }
    const orderManagement = order_management_1.OrderManagement.getInstance();
    const oldWorkpieceId = orderManagement.getWorkpieceId(state.orderId);
    const newWorkpieceId = actionState.result;
    console.debug(`PRODUCTION_HANDLER: Handle workpieceId update for orderId ${state.orderId} from ${oldWorkpieceId} to ${newWorkpieceId}`);
    // only update when the HBW does send a new ID
    if (newWorkpieceId && oldWorkpieceId !== newWorkpieceId) {
        orderManagement.updateOrderWorkpieceId(state.orderId, newWorkpieceId);
    }
};
exports.updateOrderWorkpieceId = updateOrderWorkpieceId;
const handleMessage = async (message) => {
    if (!message) {
        // ignoring empty message
        return;
    }
    console.log('Message:', message);
    const state = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    await (0, state_1.addModuleLogEntry)(state);
    await (0, exports.handleModuleAvailability)(state);
    // detect the module calibration and publish the calibration data correctly
    await (0, calibration_1.updateModuleCalibrationState)(state);
    await (0, cloud_stock_1.handleStock)(state);
    const ignoredCommands = [vda_1.InstantActions.SET_STATUS_LED];
    if (state?.actionState?.state == vda_1.State.FINISHED &&
        state?.actionState?.id?.length > 0 &&
        !ignoredCommands.includes(state.actionState?.command)) {
        (0, exports.updateOrderWorkpieceId)(state);
        await (0, exports.updateFtsLoadHandler)(state);
        return order_management_1.OrderManagement.getInstance().handleActionUpdate(state.orderId, state.actionState.id, state.actionState.state, state.actionState.result);
    }
    // When receiving a state update from a module, simply retry all queued module as well as FTS steps
    // If no steps are queued, try to look for a new order
    return order_management_1.OrderManagement.getInstance().resumeOrders();
};
exports.handleMessage = handleMessage;
