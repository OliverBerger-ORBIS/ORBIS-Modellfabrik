"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.clearAllParkRequests = exports.clearParkRequest = exports.checkAndSendParkRequests = exports.handleMessage = exports.parkRequests = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const json_revivers_1 = require("../../../../common/util/json.revivers");
const protocol_1 = require("../../../../common/protocol");
const ccu_1 = require("../../../../common/protocol/ccu");
const pairing_states_1 = require("../pairing/pairing-states");
const module_1 = require("../../../../common/protocol/module");
const calibration_1 = require("../calibration/calibration");
exports.TOPICS = [protocol_1.CcuTopic.SET_PARK];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
exports.parkRequests = new Set();
/**
 * Handle messages to park the factory
 *
 * - Set all HBW, DPS in calibration mode
 * - Set all DPS, HBW in park position
 * @param message
 */
const handleMessage = async (message) => {
    const park = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    if (park?.timestamp) {
        // send a calibration/park to all modules
        const pairingStates = pairing_states_1.PairingStates.getInstance();
        const modulesDpsHbw = [...pairingStates.getAllPaired(module_1.ModuleType.DPS), ...pairingStates.getAllPaired(module_1.ModuleType.HBW)];
        for (const mod of modulesDpsHbw) {
            exports.parkRequests.add(mod.serialNumber);
            await (0, calibration_1.sendCalibrationInstantAction)({
                timestamp: new Date(),
                serialNumber: mod.serialNumber,
                command: ccu_1.ModuleCalibrationCommand.START,
                position: 'PARK',
            });
        }
    }
};
exports.handleMessage = handleMessage;
const checkAndSendParkRequests = async (serialNumber) => {
    if (!exports.parkRequests.has(serialNumber)) {
        return;
    }
    exports.parkRequests.delete(serialNumber);
    await (0, calibration_1.sendCalibrationInstantAction)({
        timestamp: new Date(),
        serialNumber: serialNumber,
        command: ccu_1.ModuleCalibrationCommand.SELECT,
        position: 'PARK',
    });
};
exports.checkAndSendParkRequests = checkAndSendParkRequests;
const clearParkRequest = (serialNumber) => {
    exports.parkRequests.delete(serialNumber);
};
exports.clearParkRequest = clearParkRequest;
const clearAllParkRequests = () => {
    exports.parkRequests.clear();
};
exports.clearAllParkRequests = clearAllParkRequests;
