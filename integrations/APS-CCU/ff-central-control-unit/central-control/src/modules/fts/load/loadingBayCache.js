"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LoadingBayCache = exports.LoadingBayOccupiedError = void 0;
class LoadingBayOccupiedError extends Error {
    constructor(serialNumber, position) {
        super(`The loading bay for FTS ${serialNumber} and position ${position} is already occupied`);
        this.name = 'LoadingBayOccupiedError';
    }
}
exports.LoadingBayOccupiedError = LoadingBayOccupiedError;
class LoadingBayCache {
    static getInstance() {
        if (!LoadingBayCache.instance) {
            LoadingBayCache.instance = new LoadingBayCache();
        }
        return LoadingBayCache.instance;
    }
    constructor() {
        this.loadingBayCache = new Map();
    }
    initLoadingBayForFTS(serialNumber) {
        this.loadingBayCache.set(serialNumber, {
            '1': undefined,
            '2': undefined,
            '3': undefined,
        });
    }
    /**
     * Returns the loading bay for the given serial number.
     * @param serialNumber the serial number of the FTS
     */
    getLoadingBayForFTS(serialNumber) {
        if (!this.loadingBayCache.has(serialNumber)) {
            this.initLoadingBayForFTS(serialNumber);
        }
        return this.loadingBayCache.get(serialNumber);
    }
    getLoadingBayForOrder(serialNumber, orderId) {
        if (!this.loadingBayCache.has(serialNumber)) {
            return undefined;
        }
        const loadingBays = this.loadingBayCache.get(serialNumber);
        if (!loadingBays) {
            return undefined;
        }
        const positions = Object.keys(loadingBays);
        for (const position of positions) {
            if (loadingBays[position] === orderId) {
                return position;
            }
        }
        return undefined;
    }
    /**
     * Sets the loading bay for the given serial number.
     * @param serialNumber the serial number of the FTS
     * @param loadPosition the loading bay
     * @param orderId the order associated with the loading bay
     * @throws LoadingBayOccupiedError if the loading bay is already occupied
     */
    setLoadingBay(serialNumber, loadPosition, orderId) {
        if (!this.loadingBayCache.has(serialNumber)) {
            this.initLoadingBayForFTS(serialNumber);
        }
        const loadingBays = this.loadingBayCache.get(serialNumber);
        if (loadingBays.hasOwnProperty(loadPosition) && loadingBays[loadPosition]) {
            if (loadingBays[loadPosition] !== orderId) {
                throw new LoadingBayOccupiedError(serialNumber, loadPosition);
            }
        }
        loadingBays[loadPosition] = orderId;
    }
    /**
     * Clears the loading bay for the given serial number and order.
     * @param serialNumber the serial number of the FTS
     * @param orderId the id of the order
     */
    clearLoadingBayForOrder(serialNumber, orderId) {
        if (!this.loadingBayCache.has(serialNumber)) {
            this.initLoadingBayForFTS(serialNumber);
        }
        const loadingBays = this.loadingBayCache.get(serialNumber);
        if (!loadingBays) {
            return;
        }
        const positions = Object.keys(loadingBays);
        for (const position of positions) {
            if (loadingBays[position] === orderId) {
                loadingBays[position] = undefined;
            }
        }
        console.log(loadingBays);
    }
    resetLoadingBayForFts(serialNumber) {
        if (!this.loadingBayCache.has(serialNumber)) {
            return;
        }
        this.loadingBayCache.set(serialNumber, {
            '1': undefined,
            '2': undefined,
            '3': undefined,
        });
    }
    reset() {
        this.loadingBayCache.clear();
    }
}
exports.LoadingBayCache = LoadingBayCache;
