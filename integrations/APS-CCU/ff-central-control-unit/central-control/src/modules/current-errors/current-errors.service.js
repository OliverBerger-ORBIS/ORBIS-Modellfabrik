"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
class CurrentErrorsService {
    constructor() {
        this.currentErrors = new Map();
    }
    static getInstance() {
        if (!CurrentErrorsService.instance) {
            CurrentErrorsService.instance = new CurrentErrorsService();
        }
        return CurrentErrorsService.instance;
    }
    hasError(serialNumber) {
        return this.currentErrors.has(serialNumber);
    }
    getAllCurrentErrors() {
        const currentErrors = [];
        for (const [serialNumber, errors] of this.currentErrors.entries()) {
            currentErrors.push({ serialNumber, errors: errors });
        }
        return currentErrors;
    }
    getError(serialNumber) {
        return this.currentErrors.get(serialNumber) ?? null;
    }
    addError(serialNumber, error) {
        const existing = this.currentErrors.get(serialNumber);
        const newErrors = Array.isArray(error) ? [...error] : [error];
        this.currentErrors.set(serialNumber, existing ? [...existing, ...newErrors] : newErrors);
    }
    removeError(serialNumber) {
        this.currentErrors.delete(serialNumber);
    }
}
exports.default = CurrentErrorsService;
