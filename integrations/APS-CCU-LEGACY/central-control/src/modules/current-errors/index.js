"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleCurrentErrorsMessage = exports.CURRENT_ERRORS_TOPIC_OPTIONS = exports.CURRENT_ERRORS_TOPICS = void 0;
const protocol_1 = require("../../../../common/protocol");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const current_errors_service_1 = __importDefault(require("./current-errors.service"));
exports.CURRENT_ERRORS_TOPICS = [(0, protocol_1.getModuleTopic)(protocol_1.ANY_SERIAL, protocol_1.ModuleTopic.STATE), (0, protocol_1.getFtsTopic)(protocol_1.ANY_SERIAL, protocol_1.FtsTopic.STATE)];
exports.CURRENT_ERRORS_TOPIC_OPTIONS = {
    qos: 2,
};
const handleCurrentErrorsMessage = async (message) => {
    if (!message) {
        // ignore empty message
        return;
    }
    const actionState = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    if (!actionState.serialNumber || !actionState.errors) {
        // ignore message with missing serialNumber or errors
        if (actionState.serialNumber) {
            current_errors_service_1.default.getInstance().removeError(actionState.serialNumber);
        }
        return;
    }
    current_errors_service_1.default.getInstance().addError(actionState.serialNumber, actionState.errors);
};
exports.handleCurrentErrorsMessage = handleCurrentErrorsMessage;
