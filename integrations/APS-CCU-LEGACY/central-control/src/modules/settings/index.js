"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const json_revivers_1 = require("../../../../common/util/json.revivers");
const pairing_1 = require("../pairing");
const protocol_1 = require("../../../../common/protocol");
const pairing_states_1 = require("../pairing/pairing-states");
exports.TOPICS = [protocol_1.CcuTopic.SET_MODULE_DURATION];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
/**
 * Handle messages to dynamically configure module specific settings
 * @param message
 */
const handleMessage = async (message) => {
    // TODO: FITEFF22-373 errors with the message format should be handled better
    const duration = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    const modState = pairing_states_1.PairingStates.getInstance();
    if (modState.get(duration.serialNumber)) {
        console.debug(`Handle setting duration for: ${duration.serialNumber}`);
        modState.updateDuration(duration.serialNumber, duration.duration);
    }
    return (0, pairing_1.publishPairingState)();
};
exports.handleMessage = handleMessage;
