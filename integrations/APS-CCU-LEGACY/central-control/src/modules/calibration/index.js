"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const json_revivers_1 = require("../../../../common/util/json.revivers");
const protocol_1 = require("../../../../common/protocol");
const pairing_states_1 = require("../pairing/pairing-states");
const calibration_1 = require("./calibration");
exports.TOPICS = [protocol_1.CcuTopic.SET_MODULE_CALIBRATION];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
/**
 * Handle messages to dynamically configure module specific settings
 * @param message
 */
const handleMessage = async (message) => {
    // TODO: FITEFF22-373 errors with the message format should be handled better
    const calibration = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    const modState = pairing_states_1.PairingStates.getInstance();
    if (modState.get(calibration.serialNumber)) {
        console.debug(`CALIBRATION: Send calibration action to: ${calibration.serialNumber}`);
        return (0, calibration_1.sendCalibrationInstantAction)(calibration);
    }
};
exports.handleMessage = handleMessage;
