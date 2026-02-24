"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getLog = exports.addModuleLogEntry = exports.addFtsLogEntry = exports.addOrderLogEntry = exports.addLogEntry = exports.getVdaErrorsLogLevel = exports.LogLevel = void 0;
const protocol_1 = require("../../../../common/protocol");
const config_1 = __importDefault(require("../../config"));
const mqtt_1 = require("../../mqtt/mqtt");
var LogLevel;
(function (LogLevel) {
    LogLevel["INFO"] = "INFO";
    LogLevel["WARNING"] = "WARNING";
    LogLevel["ERROR"] = "ERROR";
})(LogLevel = exports.LogLevel || (exports.LogLevel = {}));
const log = new Array();
/**
 * Returns the most critical error level of a list of errors.
 *
 * VdaErrors are either fatal errors or warnings.
 * Having at least one fatal error results in an `ERROR` log level
 * If we have any non-fatal errors, those must of level `WARNING`.
 * Having no errors results in the `INFO` level.
 */
const getVdaErrorsLogLevel = (errors) => {
    if (errors?.find(e => e['errorLevel'] === 'FATAL')) {
        return LogLevel.ERROR;
    }
    else if (errors?.length) {
        return LogLevel.WARNING;
    }
    else {
        return LogLevel.INFO;
    }
};
exports.getVdaErrorsLogLevel = getVdaErrorsLogLevel;
const addLogEntry = async (entry) => {
    log.push(entry);
    if (config_1.default.mqtt.debug) {
        await (0, mqtt_1.getMqttClient)().publish(protocol_1.CcuTopic.LOG, JSON.stringify(log), { qos: 1, retain: true });
    }
    else {
        console.log('MQTT debug is disabled, not publishing log entry');
    }
};
exports.addLogEntry = addLogEntry;
const addOrderLogEntry = async (order) => await (0, exports.addLogEntry)({
    type: 'ORDER',
    timestamp: order.timestamp,
    orderId: order.orderId,
    level: LogLevel.INFO,
});
exports.addOrderLogEntry = addOrderLogEntry;
const addFtsLogEntry = async (state) => await (0, exports.addLogEntry)({
    type: 'FTS',
    serialNumber: state.serialNumber,
    timestamp: state.timestamp,
    orderId: state.orderId,
    level: (0, exports.getVdaErrorsLogLevel)(state.errors),
    state: state,
});
exports.addFtsLogEntry = addFtsLogEntry;
const addModuleLogEntry = async (state) => await (0, exports.addLogEntry)({
    type: 'MODULE',
    serialNumber: state.serialNumber,
    timestamp: state.timestamp,
    orderId: state.orderId,
    level: (0, exports.getVdaErrorsLogLevel)(state.errors),
    state: state,
});
exports.addModuleLogEntry = addModuleLogEntry;
exports.getLog = log;
