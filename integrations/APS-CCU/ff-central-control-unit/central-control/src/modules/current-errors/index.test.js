"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const current_errors_service_1 = __importDefault(require("./current-errors.service"));
const index_1 = require("./index");
describe('handleCurrentErrorsMessage', () => {
    let addErrorSpy;
    let removeErrorSpy;
    beforeEach(() => {
        jest.restoreAllMocks();
        addErrorSpy = jest.spyOn(current_errors_service_1.default.getInstance(), 'addError');
        removeErrorSpy = jest.spyOn(current_errors_service_1.default.getInstance(), 'removeError');
    });
    it('should ignore empty message', async () => {
        await (0, index_1.handleCurrentErrorsMessage)('');
        expect(addErrorSpy).not.toHaveBeenCalled();
    });
    it('should ignore message with missing serialNumber', async () => {
        await (0, index_1.handleCurrentErrorsMessage)('{}');
        expect(addErrorSpy).not.toHaveBeenCalled();
    });
    it('should not try to add errors for message with missing errors', async () => {
        await (0, index_1.handleCurrentErrorsMessage)('{"serialNumber":"123"}');
        expect(addErrorSpy).not.toHaveBeenCalled();
    });
    it('should delete errors for a message without errors', async () => {
        await (0, index_1.handleCurrentErrorsMessage)('{"serialNumber":"123"}');
        expect(removeErrorSpy).toHaveBeenCalled();
    });
    it('should not delete errors for a message with errors', async () => {
        await (0, index_1.handleCurrentErrorsMessage)('{"serialNumber":"123", "errors": [{"errorType": "TEST_error", "errorLevel": "WARNING"}]}');
        expect(removeErrorSpy).not.toHaveBeenCalled();
    });
});
