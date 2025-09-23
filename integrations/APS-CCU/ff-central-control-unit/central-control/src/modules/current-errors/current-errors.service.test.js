"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const current_errors_service_1 = __importDefault(require("./current-errors.service"));
describe('CurrentErrorsService', () => {
    const newErrors = [{ errorLevel: 'WARNING', errorType: 'TEST_error', timestamp: new Date() }];
    afterEach(() => {
        const currentErrors = current_errors_service_1.default.getInstance().getAllCurrentErrors();
        for (const current of currentErrors) {
            current_errors_service_1.default.getInstance().removeError(current.serialNumber);
        }
    });
    it('should add and return a single error', () => {
        current_errors_service_1.default.getInstance().addError('123', newErrors);
        const added = current_errors_service_1.default.getInstance().getError('123');
        expect(added).toEqual(newErrors);
    });
    it('should add and return a list of errors', () => {
        current_errors_service_1.default.getInstance().addError('123', newErrors[0]);
        const added = current_errors_service_1.default.getInstance().getError('123');
        expect(added).toEqual(newErrors);
    });
    it('should add an error to a list of existing errors', () => {
        const hasError = current_errors_service_1.default.getInstance().hasError('123');
        expect(hasError).toBeFalsy();
        current_errors_service_1.default.getInstance().addError('123', newErrors);
        const oneElement = current_errors_service_1.default.getInstance().getError('123');
        expect(oneElement).toEqual(newErrors);
        current_errors_service_1.default.getInstance().addError('123', newErrors[0]);
        const twoElements = current_errors_service_1.default.getInstance().getError('123');
        expect(twoElements).toEqual([newErrors[0], newErrors[0]]);
        current_errors_service_1.default.getInstance().addError('123', newErrors);
        const added = current_errors_service_1.default.getInstance().getError('123');
        expect(added).toEqual([newErrors[0], newErrors[0], newErrors[0]]);
    });
    it('should return null, if no error is found', () => {
        const added = current_errors_service_1.default.getInstance().getError('123');
        expect(added).toBeNull();
    });
    it('should add and remove and error', () => {
        current_errors_service_1.default.getInstance().addError('123', newErrors);
        const added = current_errors_service_1.default.getInstance().hasError('123');
        expect(added).toBeTruthy();
        current_errors_service_1.default.getInstance().removeError('123');
        const removed = current_errors_service_1.default.getInstance().hasError('123');
        expect(removed).toBeFalsy();
    });
    it('should add and return all errors', () => {
        current_errors_service_1.default.getInstance().addError('123', newErrors);
        const added = current_errors_service_1.default.getInstance().getAllCurrentErrors();
        expect(added).toEqual([{ serialNumber: '123', errors: newErrors }]);
    });
});
