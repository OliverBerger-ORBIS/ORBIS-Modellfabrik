"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const json_revivers_1 = require("../../../../common/util/json.revivers");
const protocol_1 = require("../../../../common/protocol");
const ccu_1 = require("../../../../common/protocol/ccu");
const production_1 = require("../production/production");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const cloud_stock_1 = require("../production/cloud-stock");
const order_management_1 = require("../order/management/order-management");
const helper_1 = require("../fts/helper");
const pairing_states_1 = require("../pairing/pairing-states");
const module_1 = require("../../../../common/protocol/module");
const charge_1 = require("../fts/charge");
const mqtt_1 = require("../../mqtt/mqtt");
const factory_layout_service_1 = require("../layout/factory-layout-service");
const park_1 = require("../park");
const current_errors_service_1 = __importDefault(require("../current-errors/current-errors.service"));
exports.TOPICS = [protocol_1.CcuTopic.SET_RESET];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
/**
 * Handle messages to reset the factory to an empty state
 *
 * - No orders pending
 * - No Workpieces in HBW or FTS
 * - No FTS within the layout
 * @param message
 */
const handleMessage = async (message) => {
    const reset = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    if (reset?.timestamp) {
        // clear all orders, including history
        await order_management_1.OrderManagement.getInstance().reinitialize();
        // clear storage, if requested by user
        if (reset?.withStorage) {
            // clear local stock cache
            await (0, cloud_stock_1.clearStock)();
            // clear stock from all connected HBWs
            await (0, production_1.clearHBWContents)();
        }
        // clear queue of FTS waiting for charger
        (0, charge_1.clearChargerQueue)();
        // clear blocked node list since all FTS must be re-docked to the DPS anyway
        factory_layout_service_1.FactoryLayoutService.releaseAllNodes();
        // send a reset to all fts
        const ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
        for (const fts of ftsPairingStates.getAll()) {
            current_errors_service_1.default.getInstance().removeError(fts.serialNumber);
            await (0, helper_1.sendResetFtsInstantAction)(fts.serialNumber);
        }
        (0, park_1.clearAllParkRequests)();
        // send a reset to all modules
        const pairingStates = pairing_states_1.PairingStates.getInstance();
        for (const mod of pairingStates.getAll()) {
            if (mod.subType === module_1.ModuleType.CHRG) {
                await pairing_states_1.PairingStates.getInstance().updateAvailability(mod.serialNumber, ccu_1.AvailableState.READY);
            }
            else {
                current_errors_service_1.default.getInstance().removeError(mod.serialNumber);
                await (0, production_1.sendResetModuleInstantAction)(mod.serialNumber);
            }
        }
        // reset node-red-flows
        await (0, mqtt_1.getMqttClient)().publish(protocol_1.CcuTopic.GLOBAL, JSON.stringify({ type: 'reset' }), { qos: 2 });
    }
};
exports.handleMessage = handleMessage;
