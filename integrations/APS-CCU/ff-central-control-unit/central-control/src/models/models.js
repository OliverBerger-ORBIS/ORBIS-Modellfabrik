"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FTSNotReadyError = exports.ControllerNotReadyError = void 0;
class ControllerNotReadyError extends Error {
    constructor(deviceType, moduleType, customMessage) {
        super(`Controller is not ready for deviceType ${deviceType}${moduleType ? ` and moduleType ${moduleType}` : ''}${customMessage ? ` message ${customMessage}` : ''}`);
        this.name = 'ControllerNotReadyError';
    }
}
exports.ControllerNotReadyError = ControllerNotReadyError;
class FTSNotReadyError extends ControllerNotReadyError {
    constructor(customMessage) {
        super('FTS', undefined, customMessage);
        this.name = 'FTSNotReadyError';
    }
}
exports.FTSNotReadyError = FTSNotReadyError;
