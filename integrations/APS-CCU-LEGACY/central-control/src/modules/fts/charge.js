"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.clearChargerQueue = exports.sendStopChargingInstantAction = exports.sendChargingNavigationRequest = exports.triggerChargeOrderForFts = exports.freeBlockedChargers = exports.resetBusyChargersThatAreEmpty = exports.retriggerChargeOrders = exports.handleChargingUpdate = exports.isBatteryLow = exports.FTS_WAITING_FOR_RECHARGE = void 0;
const fts_1 = require("../../../../common/protocol/fts");
const navigator_service_1 = require("./navigation/navigator-service");
const pairing_states_1 = require("../pairing/pairing-states");
const module_1 = require("../../../../common/protocol/module");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const ccu_1 = require("../../../../common/protocol/ccu");
const node_crypto_1 = require("node:crypto");
const navigation_1 = require("./navigation/navigation");
const mqtt_1 = require("../../mqtt/mqtt");
const protocol_1 = require("../../../../common/protocol");
const factory_layout_service_1 = require("../layout/factory-layout-service");
const config_1 = __importDefault(require("../../config"));
const vda_1 = require("../../../../common/protocol/vda");
const general_config_service_1 = require("../../services/config/general-config-service");
exports.FTS_WAITING_FOR_RECHARGE = new Set();
/**
 * Check if the FTS battery is low and should be recharged
 * @param state
 */
const isBatteryLow = (state) => {
    // battery is nominal 8.4V. The FTS fails at less than 8.4V
    // maybe there should be a boost converter from 8.4 to 9V, so we can use the nominal battery voltage?
    // isNaN check returns true if the value is null so we need to check for null first
    if (state.batteryState?.percentage != null && !isNaN(state.batteryState?.percentage)) {
        return state.batteryState.percentage <= general_config_service_1.GeneralConfigService.config.ftsSettings.chargeThresholdPercent;
    }
    return false;
};
exports.isBatteryLow = isBatteryLow;
/**
 * Handle updating the FTS charge status and the charger availability
 * @param state
 */
const handleChargingUpdate = (state) => {
    const ftsPairingState = fts_pairing_states_1.FtsPairingStates.getInstance();
    const pairingState = pairing_states_1.PairingStates.getInstance();
    if (!state.batteryState?.charging && ftsPairingState.isCharging(state.serialNumber)) {
        if (state.orderId) {
            pairingState.clearModuleForOrder(state.orderId);
        }
    }
    ftsPairingState.updateCharge(state.serialNumber, state.batteryState?.charging ?? false, state.batteryState?.currentVoltage ?? 0, state.batteryState?.percentage);
};
exports.handleChargingUpdate = handleChargingUpdate;
/**
 * Retrigger charging orders that could not be issued due to path problems, or missing chargers
 */
const retriggerChargeOrders = async () => {
    for (const serial of exports.FTS_WAITING_FOR_RECHARGE) {
        await (0, exports.triggerChargeOrderForFts)(serial);
    }
};
exports.retriggerChargeOrders = retriggerChargeOrders;
/**
 * Mark busy chargers, that have no FTS on them, as ready again
 */
const resetBusyChargersThatAreEmpty = async () => {
    const pairingStates = pairing_states_1.PairingStates.getInstance();
    const ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
    const modules = pairingStates.getAllPaired(module_1.ModuleType.CHRG);
    for (const charger of modules) {
        if (charger.serialNumber && charger.available === ccu_1.AvailableState.BUSY) {
            const fts = ftsPairingStates.getFtsAtPosition(charger.serialNumber);
            if (!fts) {
                await pairingStates.updateAvailability(charger.serialNumber, ccu_1.AvailableState.READY);
            }
        }
    }
};
exports.resetBusyChargersThatAreEmpty = resetBusyChargersThatAreEmpty;
/**
 * If there are FTS waiting to charge, try to free up a charger blocked by a ready fts if that is possible.
 *
 * @param force free chargers even if it is not necessary, do not let an FTS idle on a charger
 */
const freeBlockedChargers = async (force = false) => {
    if (!force && !exports.FTS_WAITING_FOR_RECHARGE.size) {
        return;
    }
    const ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
    const modules = pairing_states_1.PairingStates.getInstance().getAllReady(module_1.ModuleType.CHRG);
    for (const blocked of modules) {
        try {
            if (ftsPairingStates.getFtsAtPosition(blocked.serialNumber)) {
                await (0, navigation_1.sendClearModuleNodeNavigationRequest)(blocked.serialNumber);
                return;
            }
        }
        catch {
            console.log(`FTS CHARGE: Freeing of module ${blocked.serialNumber} failed, trying next module.`);
        }
    }
};
exports.freeBlockedChargers = freeBlockedChargers;
/**
 * Verifies if charging command is enabled by config {@link config.ftsCharge.enabled}.
 * If it is not enabled, prints an info and aborts any further actions
 *
 * If it is enabled, it checks if a charging order can be issued:
 * - FTS must be ready
 * - A READY charger module must be in the layout
 * - The position of the FTS must be known
 * - A valid path to the charger must exist (this also takes blocked nodes into consideration)
 *
 * If any of the checks fail, the serialnumber is queued and a retry will be issued on FTS state change
 * @param serialNumber The FTS serial number to trigger the charge order for
 * @param forceCharge If true, the charge order will be issued even if the automatic charging is disabled.
 * All other checks (charger available, FTS ready, ...) still apply. This is used for manual triggered loading
 * via the UI.
 */
const triggerChargeOrderForFts = async (serialNumber, forceCharge = false) => {
    if (config_1.default.ftsCharge.disabled && !forceCharge) {
        console.info('FTS CHARGE: Disabled by config');
        return;
    }
    const ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
    exports.FTS_WAITING_FOR_RECHARGE.add(serialNumber);
    if (!ftsPairingStates.isReady(serialNumber) || ftsPairingStates.isCharging(serialNumber)) {
        console.warn(`FTS CHARGE: FTS ${serialNumber} not ready to navigate to charger`);
        return;
    }
    const modules = pairing_states_1.PairingStates.getInstance().getAllReady(module_1.ModuleType.CHRG);
    if (!modules.length) {
        console.warn(`FTS CHARGE: cannot navigate to charger for ${serialNumber}, no charger available`);
        return;
    }
    const fts = ftsPairingStates.get(serialNumber);
    if (!fts?.lastModuleSerialNumber) {
        console.warn('FTS CHARGE: cannot navigate from unknown last module for fts ' + serialNumber);
        return;
    }
    const paths = (0, navigation_1.getSortedModulePaths)(fts, modules);
    if (!paths?.length) {
        console.warn(`FTS CHARGE: cannot navigate to charger for ${serialNumber}, no charger or no path`);
        return;
    }
    try {
        await (0, exports.sendChargingNavigationRequest)(fts.serialNumber, paths[0].module.serialNumber);
        exports.FTS_WAITING_FOR_RECHARGE.delete(serialNumber);
    }
    catch (e) {
        console.warn(`FTS CHARGE: cannot send charging navigation to ${serialNumber}: `, e);
    }
};
exports.triggerChargeOrderForFts = triggerChargeOrderForFts;
/**
 * send the charging order
 * @param serialNumber
 * @param target
 */
const sendChargingNavigationRequest = async (serialNumber, target) => {
    // Is there an FTS ready to take the navigation Request?
    const ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
    const pairingStates = pairing_states_1.PairingStates.getInstance();
    const orderId = (0, node_crypto_1.randomUUID)();
    const fts = ftsPairingStates.get(serialNumber);
    if (!fts || !ftsPairingStates.isReady(serialNumber)) {
        return;
    }
    const chargeModule = pairingStates.get(target);
    if (!chargeModule || !pairingStates.isReady(target)) {
        throw new Error(`FTS CHARGE: The module ${target} is blocked`);
    }
    const startPosition = fts.lastModuleSerialNumber;
    if (!startPosition) {
        throw new Error(`FTS CHARGE: The start position for FTS ${serialNumber} is unknown`);
    }
    const targetPosition = chargeModule.serialNumber;
    const dockingMetadata = {
        loadPosition: fts_1.LoadingBay.MIDDLE,
        charge: true,
    };
    console.debug(`FTS CHARGE: Fts ${serialNumber} starts at position ${startPosition} to position ${targetPosition} to charge`);
    const newOrder = navigator_service_1.NavigatorService.getFTSOrder(startPosition, targetPosition, orderId, 0, serialNumber, (0, node_crypto_1.randomUUID)());
    console.debug(JSON.stringify(newOrder, null, 2));
    newOrder.nodes
        .filter(node => node.action?.type === fts_1.FtsCommandType.DOCK)
        .forEach(node => {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        node.action.metadata = dockingMetadata;
    });
    const mqtt = (0, mqtt_1.getMqttClient)();
    console.debug(`ORDER_MANAGEMENT: Publishing untracked charge order ${orderId} to ${(0, protocol_1.getFtsTopic)(serialNumber, protocol_1.FtsTopic.ORDER)}`);
    const blockedNodes = (0, navigation_1.getBlockedNodesForOrder)(newOrder);
    factory_layout_service_1.FactoryLayoutService.blockNodeSequence(blockedNodes);
    await mqtt.publish((0, protocol_1.getFtsTopic)(serialNumber, protocol_1.FtsTopic.ORDER), JSON.stringify(newOrder));
    await ftsPairingStates.updateAvailability(serialNumber, ccu_1.AvailableState.BUSY, orderId, fts.lastNodeId, fts.lastModuleSerialNumber, dockingMetadata.loadPosition);
    await pairingStates.updateAvailability(target, ccu_1.AvailableState.BUSY, orderId);
};
exports.sendChargingNavigationRequest = sendChargingNavigationRequest;
/**
 * Request the FTS to stop charging
 * @param serialNumber The serial number of the FTS to stop charging
 */
const sendStopChargingInstantAction = async (serialNumber) => {
    const isCharging = fts_pairing_states_1.FtsPairingStates.getInstance().isCharging(serialNumber);
    if (!isCharging) {
        console.warn(`FTS CHARGE: FTS ${serialNumber} can not stop charging: FTS is not charging`);
        return;
    }
    const stopCharging = {
        serialNumber,
        timestamp: new Date(),
        actions: [
            {
                actionId: (0, node_crypto_1.randomUUID)(),
                actionType: vda_1.InstantActions.STOP_CHARGING,
            },
        ],
    };
    await (0, mqtt_1.getMqttClient)().publish((0, protocol_1.getFtsTopic)(serialNumber, protocol_1.FtsTopic.INSTANT_ACTION), JSON.stringify(stopCharging));
};
exports.sendStopChargingInstantAction = sendStopChargingInstantAction;
const clearChargerQueue = () => {
    exports.FTS_WAITING_FOR_RECHARGE.clear();
};
exports.clearChargerQueue = clearChargerQueue;
