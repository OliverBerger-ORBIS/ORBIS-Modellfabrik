"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const json_revivers_1 = require("../../../../../common/util/json.revivers");
const protocol_1 = require("../../../../../common/protocol");
const fts_pairing_states_1 = require("../../pairing/fts-pairing-states");
const charge_1 = require("../charge");
exports.TOPICS = [protocol_1.CcuTopic.SET_CHARGE];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
/**
 * Handle messages to charge an FTS
 * @param message
 */
const handleMessage = async (message) => {
    const chargeRequest = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    if (!chargeRequest?.serialNumber) {
        console.error('Charge request is not valid');
        return;
    }
    const startCharge = chargeRequest.charge;
    const ftsSerialNumber = chargeRequest.serialNumber;
    const ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
    const fts = ftsPairingStates.get(ftsSerialNumber);
    if (fts == undefined) {
        console.error(`FTS with serial number ${ftsSerialNumber} is not paired`);
        return;
    }
    const isCharging = ftsPairingStates.isCharging(ftsSerialNumber);
    console.log(`Start charging: ${startCharge}, is charging: ${isCharging}, serialNumber: ${ftsSerialNumber}`);
    if (startCharge && !isCharging) {
        return (0, charge_1.triggerChargeOrderForFts)(ftsSerialNumber, true);
    }
    else if (!startCharge && isCharging) {
        return (0, charge_1.sendStopChargingInstantAction)(ftsSerialNumber);
    }
    // fallthrough when state of fts does not match the request, e.g. fts should go to charge but is already charging
    // Do not crash the CCU, just log the error because this should not happen, unless the interface is used manually
    console.error(`FTS with serial number ${ftsSerialNumber} is already charging: ${isCharging} and should not be charged: ${startCharge}`);
};
exports.handleMessage = handleMessage;
