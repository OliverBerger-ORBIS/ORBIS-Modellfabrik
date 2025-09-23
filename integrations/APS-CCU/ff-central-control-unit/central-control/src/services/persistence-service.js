"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PersistenceService = void 0;
const helpers_1 = require("../helpers");
class PersistenceService {
    static async init(storageLocation) {
        this.storageLocation = storageLocation;
        if (this.storageLocation) {
            return this.load();
        }
        return undefined;
    }
    /**
     * Loads the data from the storage location on the disc.
     */
    static async load() {
        if (!this.storageLocation) {
            return undefined;
        }
        try {
            const value = await (0, helpers_1.readJsonFile)(this.storageLocation);
            return value;
        }
        catch (error) {
            console.error('Error while loading file: ' + this.storageLocation, error);
        }
    }
    /**
     * Persists the provided data to the storage location on the disc.
     */
    static async persist(data) {
        if (!this.storageLocation) {
            return;
        }
        try {
            await (0, helpers_1.writeJsonFile)(this.storageLocation, data);
        }
        catch (error) {
            console.error('Error while saving file: ' + this.storageLocation, error);
        }
    }
}
exports.PersistenceService = PersistenceService;
