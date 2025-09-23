"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.sendResetFtsInstantAction = exports.sendClearLoadFtsInstantAction = exports.handleFtsState = exports.updateFtsBlockedNodes = exports.checkChargerAvailability = exports.handleResetWarning = exports.updateFtsAvailability = exports.getLastModuleSerialNumber = void 0;
const node_crypto_1 = require("node:crypto");
const protocol_1 = require("../../../../common/protocol");
const ccu_1 = require("../../../../common/protocol/ccu");
const fts_1 = require("../../../../common/protocol/fts");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const config_1 = __importDefault(require("../../config"));
const mqtt_1 = require("../../mqtt/mqtt");
const factory_layout_service_1 = require("../layout/factory-layout-service");
const order_management_1 = require("../order/management/order-management");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const pairing_states_1 = require("../pairing/pairing-states");
const production_1 = require("../production");
const production_2 = require("../production/production");
const state_1 = require("../state");
const charge_1 = require("./charge");
const current_errors_service_1 = __importDefault(require("../current-errors/current-errors.service"));
/**
 * Determine the last module serial number for the FTS based on the last finished action
 * @param state
 */
const getLastModuleSerialNumber = (state) => {
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
        console.debug(`FTS_AVAIL: last module is undefined because of no action state found and last node id is not non-numeric: ${state.lastNodeId}`);
        return undefined;
    }
    // if the FTS is not driving and there is an action, use it to determine the position
    if (state.actionState.state !== vda_1.State.FINISHED) {
        console.debug(`FTS_AVAIL: last module is undefined because of action is: ${state.actionState.state}`);
        return undefined;
    }
    const targetModuleType = order_management_1.OrderManagement.getInstance().getTargetModuleTypeForNavActionId(state.actionState.id);
    if (!targetModuleType) {
        console.debug(`FTS_AVAIL: last module is undefined because target module type was not found for action id: ${state.actionState.id}`);
        return undefined;
    }
    const targetModule = pairing_states_1.PairingStates.getInstance().getForModuleType(targetModuleType, state.orderId);
    if (!targetModule) {
        console.debug(`FTS_AVAIL: last module is undefined because target module was not found for action id: ${state.actionState.id} and type: ${targetModuleType}`);
        return undefined;
    }
    console.debug(`FTS_AVAIL: last module is ${targetModule.serialNumber}`);
    return targetModule.serialNumber;
};
exports.getLastModuleSerialNumber = getLastModuleSerialNumber;
const updateFtsAvailability = async (state) => {
    const pairings = fts_pairing_states_1.FtsPairingStates.getInstance();
    // errors of type warning do not make the FTS unavailable.
    const error = (0, state_1.getVdaErrorsLogLevel)(state.errors);
    if (error === state_1.LogLevel.ERROR || state.paused || state.lastNodeId == fts_1.NODE_ID_UNKNOWN) {
        console.debug(`FTS_AVAIL: update FTS availability for ${state.serialNumber} to BLOCKED because of error (${error === state_1.LogLevel.ERROR}) or paused (${state.paused}) or unknown node (${state.lastNodeId == fts_1.NODE_ID_UNKNOWN})`);
        await pairings.updateAvailability(state.serialNumber, ccu_1.AvailableState.BLOCKED, state.orderId, state.lastNodeId);
        return ccu_1.AvailableState.BLOCKED;
    }
    const lastModuleSerialNumber = (0, exports.getLastModuleSerialNumber)(state);
    if (state.driving || state.waitingForLoadHandling) {
        console.debug(`FTS_AVAIL: update FTS availability for ${state.serialNumber} to BUSY because of driving or waiting for load handler with last module serial number: ${lastModuleSerialNumber}`);
        await pairings.updateAvailability(state.serialNumber, ccu_1.AvailableState.BUSY, state.orderId, state.lastNodeId, lastModuleSerialNumber);
        return ccu_1.AvailableState.BUSY;
    }
    else if (!state.actionState || state.actionState.state === vda_1.State.FINISHED) {
        // Ready if the FTS has no actionState, this can only happen if the FTS has been started. Or if the action is finished
        console.debug(`FTS_AVAIL: update FTS availability for ${state.serialNumber} to READY, last module serial number: ${lastModuleSerialNumber}`);
        await pairings.updateAvailability(state.serialNumber, ccu_1.AvailableState.READY, undefined, state.lastNodeId, lastModuleSerialNumber);
        return ccu_1.AvailableState.READY;
    }
    else {
        // If the FTS is not driving and the action is not finished, it is busy
        console.debug(`FTS_AVAIL: update FTS availability for ${state.serialNumber} to BUSY because action is not finished, last module serial number: ${lastModuleSerialNumber}`);
        await pairings.updateAvailability(state.serialNumber, ccu_1.AvailableState.BUSY, state.orderId, state.lastNodeId, lastModuleSerialNumber);
        return ccu_1.AvailableState.BUSY;
    }
};
exports.updateFtsAvailability = updateFtsAvailability;
const handleResetWarning = async (resetWarnings, serialNumber) => {
    const management = order_management_1.OrderManagement.getInstance();
    const pairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
    for (const e of resetWarnings) {
        if (e.errorType === fts_1.FtsErrors.RESET) {
            current_errors_service_1.default.getInstance().removeError(serialNumber);
            // reset orders for loaded workpieces
            const orderIds = pairingStates.getLoadedOrderIds(serialNumber);
            pairingStates.resetLoadingBay(serialNumber);
            for (const id of orderIds) {
                pairing_states_1.PairingStates.getInstance().clearModuleForOrder(id);
                await management.resetOrder(id);
            }
            // Update readiness of the FTS and set the last docked module to UNKNOWN
            console.log(`FTS_AVAIL: update FTS availability for ${serialNumber} to BLOCKED after reset at position UNKNOWN`);
            await pairingStates.updateAvailability(serialNumber, ccu_1.AvailableState.READY, undefined, fts_1.NODE_ID_UNKNOWN, fts_1.NODE_ID_UNKNOWN);
            // always reset the current order, even if there is no workpiece loaded
            const orderId = e.errorReferences?.find(r => r.referenceKey === 'orderId')?.referenceValue;
            if (!orderId) {
                console.debug(`FTS Reset without associated orderId`);
                continue;
            }
            console.debug(`FTS Reset for order ${orderId}`);
            // completely reset the module of the active order in case it knew about the order
            const module = pairing_states_1.PairingStates.getInstance().getModuleForOrder(orderId);
            if (module && module.subType !== module_1.ModuleType.HBW && module.subType !== module_1.ModuleType.CHRG) {
                current_errors_service_1.default.getInstance().removeError(module.serialNumber);
                await (0, production_2.sendResetModuleInstantAction)(module.serialNumber);
                pairing_states_1.PairingStates.getInstance().clearModuleForOrder(orderId);
            }
            await management.resetOrder(orderId);
        }
    }
};
exports.handleResetWarning = handleResetWarning;
const isResetContained = (state) => {
    const resetErrors = state.errors?.filter(e => e.errorType === fts_1.FtsErrors.RESET) || [];
    return {
        isResetContained: resetErrors.length > 0,
        resetErrors,
    };
};
/**
 * Checks the paired modules for a charger and returns true if a charger is available and ready to be used.
 * @returns true if a charger is available and ready to be used
 */
const checkChargerAvailability = () => {
    const pairedChargers = pairing_states_1.PairingStates.getInstance().getAllReady(module_1.ModuleType.CHRG);
    return pairedChargers.length > 0;
};
exports.checkChargerAvailability = checkChargerAvailability;
/**
 * Updates the blocked nodes for a given FTS state.
 * If the lastNodeId is NODE_ID_UNKNOWN, releases all nodes associated with the FTS.
 * If the FTS sends a completed docking action that has not been handled,
 *    releases all nodes except the lastNodeId.
 * Otherwise, releases nodes before the lastNodeId.
 */
const updateFtsBlockedNodes = (state) => {
    if (state.lastNodeId === fts_1.NODE_ID_UNKNOWN) {
        // An FTS at the unknown node is effectively removed from the factory, so release its nodes.
        factory_layout_service_1.FactoryLayoutService.releaseAllNodes(state.serialNumber);
    }
    else if (state.actionState?.state === vda_1.State.FINISHED && state.actionState.command === fts_1.FtsCommandType.DOCK) {
        const orderManagement = order_management_1.OrderManagement.getInstance();
        if (orderManagement.isOrderActionRunning(state.orderId, state.actionState.id) ||
            (!orderManagement.getActiveOrder(state.orderId) &&
                fts_pairing_states_1.FtsPairingStates.getInstance().getLastFinishedDockId(state.serialNumber) !== state.actionState.id)) {
            // Delete all blocked nodes when the FTS is docked.
            // Only do that once when a specific docking action is finished.
            factory_layout_service_1.FactoryLayoutService.releaseAllNodesExcept(state.serialNumber, state.lastNodeId);
        }
        fts_pairing_states_1.FtsPairingStates.getInstance().setLastFinishedDockId(state.serialNumber, state.actionState.id);
    }
    else {
        factory_layout_service_1.FactoryLayoutService.releaseNodesBefore(state.serialNumber, state.lastNodeId);
    }
};
exports.updateFtsBlockedNodes = updateFtsBlockedNodes;
/**
 * Handle the FTS state. If the FTS is in a reset state, the order will be reset and the FTS will be positioned at
 * UNKNOWN. The user needs to re-dock the FTS to the DPS in order to use it again.
 * If not the availability of the FTS will be updated.
 * @param state The FTS state
 */
const handleFtsState = async (state) => {
    console.debug('FTS_STATE received: ', JSON.stringify(state, null, 2));
    (0, charge_1.handleChargingUpdate)(state);
    const tempResetContain = isResetContained(state);
    if (tempResetContain.isResetContained) {
        console.log(`FTS_AVAIL: FTS ${state.serialNumber} is in reset state. Resetting order.`);
        factory_layout_service_1.FactoryLayoutService.releaseAllNodes(state.serialNumber);
        return (0, exports.handleResetWarning)(tempResetContain.resetErrors, state.serialNumber);
    }
    else {
        console.log(`FTS_AVAIL: update FTS availability for ${state.serialNumber}`);
        (0, exports.updateFtsBlockedNodes)(state);
        const ftsAvail = await (0, exports.updateFtsAvailability)(state);
        await (0, charge_1.retriggerChargeOrders)();
        // only re-trigger fts commands if the FTS is ready to accept a new one
        if (ftsAvail === ccu_1.AvailableState.READY) {
            const batteryIsLow = (0, charge_1.isBatteryLow)(state);
            if (batteryIsLow) {
                console.debug(`FTS BATTERY: battery is low. Drive to charger if config enables it`);
            }
            const chargingDisabled = config_1.default.ftsCharge.disabled;
            const hasChargerAvailable = (0, exports.checkChargerAvailability)();
            if (batteryIsLow && !chargingDisabled) {
                if (!hasChargerAvailable) {
                    console.debug(`FTS BATTERY: No charger is ready. Trying to free chargers.`);
                    await (0, charge_1.resetBusyChargersThatAreEmpty)();
                }
                console.debug(`FTS BATTERY: Triggering Charge order.`);
                await (0, charge_1.triggerChargeOrderForFts)(state.serialNumber);
            }
            else {
                if (chargingDisabled) {
                    console.debug(`FTS BATTERY: Charging is disabled. Do not drive to charger.`);
                }
                console.debug(`ORDER_MANAGEMENT: re-trigger navigation steps, FTS ${state.serialNumber} is READY again.`);
                await order_management_1.OrderManagement.getInstance().retriggerFTSSteps();
            }
        }
        // FITEFF22-607: Always move FTS away from chargers
        await (0, charge_1.freeBlockedChargers)(true);
        return Promise.resolve();
    }
};
exports.handleFtsState = handleFtsState;
/**
 * Send an instant action to the FTS to clear the load handler. This will result in the FTS being available again.
 */
const sendClearLoadFtsInstantAction = async (orderId, serialNumber, loadDropped = false, workpieceId) => {
    const topic = (0, protocol_1.getFtsTopic)(serialNumber, protocol_1.FtsTopic.INSTANT_ACTION);
    const loadingBay = workpieceId ? fts_pairing_states_1.FtsPairingStates.getInstance().getLoadingBayForOrder(serialNumber, orderId) : undefined;
    const workpieceType = order_management_1.OrderManagement.getInstance().getWorkpieceType(orderId);
    console.debug(`Sending clear load handler instant action for FTS ${serialNumber} with load dropped ${loadDropped} and workpiece ${workpieceId} to topic ${topic}`);
    const instantAction = {
        serialNumber,
        timestamp: new Date(),
        actions: [
            {
                actionId: (0, node_crypto_1.randomUUID)(),
                actionType: vda_1.InstantActions.CLEAR_LOAD_HANDLER,
                metadata: {
                    loadDropped,
                    loadType: workpieceType,
                    loadId: workpieceId,
                    loadPosition: loadingBay,
                },
            },
        ],
    };
    (0, production_1.clearLoadingBay)(loadDropped, serialNumber, orderId);
    const mqttClient = (0, mqtt_1.getMqttClient)();
    return mqttClient.publish(topic, JSON.stringify(instantAction));
};
exports.sendClearLoadFtsInstantAction = sendClearLoadFtsInstantAction;
/**
 * Send an instant action to the FTS to reset it and force a re-pairing.
 */
const sendResetFtsInstantAction = async (serialNumber) => {
    const topic = (0, protocol_1.getFtsTopic)(serialNumber, protocol_1.FtsTopic.INSTANT_ACTION);
    console.debug(`Sending reset instant action for FTS ${serialNumber} to topic ${topic}`);
    const instantAction = {
        serialNumber,
        timestamp: new Date(),
        actions: [
            {
                actionId: (0, node_crypto_1.randomUUID)(),
                actionType: vda_1.InstantActions.RESET,
            },
        ],
    };
    const ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
    ftsPairingStates.resetLoadingBay(serialNumber);
    await ftsPairingStates.updateAvailability(serialNumber, ccu_1.AvailableState.BLOCKED, undefined, fts_1.NODE_ID_UNKNOWN);
    const mqttClient = (0, mqtt_1.getMqttClient)();
    return mqttClient.publish(topic, JSON.stringify(instantAction), { qos: 2 });
};
exports.sendResetFtsInstantAction = sendResetFtsInstantAction;
