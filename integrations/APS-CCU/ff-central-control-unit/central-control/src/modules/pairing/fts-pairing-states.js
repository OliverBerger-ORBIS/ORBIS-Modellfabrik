"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FtsPairingStates = void 0;
/* eslint-disable @typescript-eslint/no-non-null-assertion */
const loadingBayCache_1 = require("../fts/load/loadingBayCache");
const ccu_1 = require("../../../../common/protocol/ccu");
const fts_1 = require("../../../../common/protocol/fts");
const index_1 = require("./index");
const base_pairing_states_1 = require("./base-pairing-states");
const factory_layout_service_1 = require("../layout/factory-layout-service");
class FtsPairingStates extends base_pairing_states_1.BasePairingStates {
    constructor() {
        super();
        this.type = 'FTS';
        // TODO FITEFF22-347 do we need to store the previous FTS pairings?
        this.knownModules = new Map();
        this.loadingBayCache = loadingBayCache_1.LoadingBayCache.getInstance();
    }
    getKnownModules() {
        return this.knownModules;
    }
    static getInstance() {
        if (!FtsPairingStates.instance) {
            FtsPairingStates.instance = new FtsPairingStates();
        }
        return FtsPairingStates.instance;
    }
    isReady(serialNumber) {
        const state = this.knownModules.get(serialNumber)?.state;
        if (!state || !state.connected) {
            return false;
        }
        return state.available === ccu_1.AvailableState.READY;
    }
    isReadyForOrder(serialNumber, orderId) {
        const data = this.knownModules.get(serialNumber);
        if (!data?.state?.connected) {
            return false;
        }
        if (data.orderId && data.orderId !== orderId) {
            return false;
        }
        return data.state.available === ccu_1.AvailableState.READY;
    }
    updateFacts(facts) {
        this.initializePairingStateObject(facts.serialNumber);
        const data = this.knownModules.get(facts.serialNumber);
        data.factsheet = facts;
        if (data.state.connected) {
            data.state.lastSeen = new Date();
        }
    }
    /**
     * Update the availability of an FTS
     * @param serialNumber the serial number of the FTS
     * @param avail the available state
     * @param orderId the order id the FTS is reserved for
     * @param nodeId the id of the last node the FTS was at
     * @param lastModuleSerialNumber the id of the module the fts stops at
     * @param lastLoadPosition the load position the fts is docking with
     */
    async updateAvailability(serialNumber, avail, orderId, nodeId, lastModuleSerialNumber, lastLoadPosition) {
        this.initializePairingStateObject(serialNumber);
        const data = this.knownModules.get(serialNumber);
        data.state.available = avail;
        data.orderId = orderId;
        if (nodeId && nodeId !== data.state.lastNodeId) {
            console.debug(`${this.type} ${serialNumber} is now at position ${nodeId}`);
            data.state.lastNodeId = nodeId;
            if (nodeId === fts_1.NODE_ID_UNKNOWN) {
                data.state.pairedSince = undefined;
                data.state.lastModuleSerialNumber = fts_1.NODE_ID_UNKNOWN;
            }
            else if (data.state.lastNodeId === fts_1.NODE_ID_UNKNOWN) {
                factory_layout_service_1.FactoryLayoutService.blockNodeSequence([
                    {
                        ftsSerialNumber: serialNumber,
                        nodeId: nodeId,
                    },
                ]);
            }
        }
        if (lastModuleSerialNumber && lastModuleSerialNumber !== data.state.lastModuleSerialNumber) {
            console.debug(`${this.type} ${serialNumber} is now at module ${lastModuleSerialNumber}`);
            data.state.lastModuleSerialNumber = lastModuleSerialNumber;
            // mark an FTS as paired when we know where it is in the factory
            if (lastModuleSerialNumber !== fts_1.NODE_ID_UNKNOWN && !data.state.pairedSince) {
                data.state.pairedSince = new Date();
            }
            else if (lastModuleSerialNumber === fts_1.NODE_ID_UNKNOWN && data.state.pairedSince) {
                data.state.pairedSince = undefined;
            }
        }
        if (lastModuleSerialNumber && lastLoadPosition) {
            data.state.lastLoadPosition = lastLoadPosition;
        }
        else if ((lastModuleSerialNumber === fts_1.NODE_ID_UNKNOWN && !lastLoadPosition) || !data.state.lastLoadPosition) {
            data.state.lastLoadPosition = fts_1.LoadingBay.MIDDLE;
        }
        await (0, index_1.publishPairingState)();
    }
    /**
     * Update the battery voltage and charging state
     * @param serialNumber
     * @param charging
     * @param voltage
     * @param percentage
     */
    updateCharge(serialNumber, charging, voltage, percentage) {
        console.log('CHARGING:..' + charging + ' ' + serialNumber + ' ' + voltage);
        this.initializePairingStateObject(serialNumber);
        const data = this.knownModules.get(serialNumber);
        data.state.charging = charging;
        data.state.batteryVoltage = voltage;
        data.state.batteryPercentage = percentage;
    }
    isCharging(serialNumber) {
        return this.get(serialNumber)?.charging ?? false;
    }
    /**
     * Returns an FTS that can accept the order
     * The readiness is determined by:
     * <ul>
     *   <li>If an FTS is assigned to the order or it has the workpiece of the order and it is ready then it is returned</li>
     *   <li>If that assigned FTS is not ready, undefined is returned, for example it is waiting for a load update</li>
     *   <li>Any FTS that is ready and not assigned to an order is returned</li>
     *  </ul>
     * @returns FtsPairedModule or undefined if none is ready for the order
     */
    getReady(orderId) {
        if (orderId) {
            const fts = this.getForOrder(orderId);
            if (fts) {
                return this.isReady(fts.serialNumber) ? fts : undefined;
            }
        }
        const allReady = this.getAllReadyUnassigned();
        if (allReady.length === 0) {
            return undefined;
        }
        return allReady[0].state;
    }
    /**
     * Find the FTS that is assigned to the order or has a workpiece for the order
     * @param orderId
     */
    getForOrder(orderId) {
        for (const [serialNumber, fts] of this.knownModules) {
            // if an FTS is assigned to the order, use it.
            if (fts.orderId === orderId) {
                return fts.state;
            }
            // if an FTS has a load belonging to the order, use it.
            if (this.loadingBayCache.getLoadingBayForOrder(serialNumber, orderId)) {
                return fts.state;
            }
        }
        return undefined;
    }
    /**
     * gets a connected FTS that is assigned to an order.
     * @param orderId the order id
     */
    getFtsSerialNumberForOrderId(orderId) {
        const fts = Array.from(this.knownModules.values()).find(data => data.orderId === orderId && data.state.connected);
        return fts?.state.serialNumber ?? undefined;
    }
    /**
     * Get the data for all ready fts that are not assigned to an order
     */
    getAllReadyUnassigned() {
        return Array.from(this.knownModules.values()).filter(data => data.state?.available === ccu_1.AvailableState.READY && data.state?.connected && data.orderId == undefined);
    }
    setLoadingBay(serialNumber, loadPosition, orderId) {
        this.loadingBayCache.setLoadingBay(serialNumber, loadPosition, orderId);
    }
    getOpenloadingBay(serialNumber) {
        const loadingBays = this.loadingBayCache.getLoadingBayForFTS(serialNumber);
        const loadingBayIds = Object.keys(loadingBays);
        for (const position of loadingBayIds) {
            if (loadingBays.hasOwnProperty(position) && loadingBays[position] === undefined) {
                return position;
            }
        }
        return undefined;
    }
    getLoadedOrderIds(serialNumber) {
        const loadingBays = this.loadingBayCache.getLoadingBayForFTS(serialNumber);
        const orderIds = [];
        for (const load of Object.values(loadingBays)) {
            if (load) {
                orderIds.push(load);
            }
        }
        return orderIds;
    }
    isLoadingBayFree(serialNumber, bay) {
        const loadingBays = this.loadingBayCache.getLoadingBayForFTS(serialNumber);
        return loadingBays[bay] === undefined;
    }
    getLoadingBayForOrder(serialNumber, orderId) {
        return this.loadingBayCache.getLoadingBayForOrder(serialNumber, orderId);
    }
    clearLoadingBay(serialNumber, orderId) {
        this.loadingBayCache.clearLoadingBayForOrder(serialNumber, orderId);
    }
    resetLoadingBay(serialNumber) {
        this.loadingBayCache.resetLoadingBayForFts(serialNumber);
    }
    getType() {
        return this.type;
    }
    reset() {
        super.reset();
        this.loadingBayCache.reset();
    }
    /**
     * Checks if an FTS is waiting for a specific order at a given position.
     * @param orderId
     * @param targetSerialNumber
     */
    isFtsWaitingAtPosition(orderId, targetSerialNumber) {
        const fts = Array.from(this.knownModules.values()).find(paired => paired.state.lastModuleSerialNumber === targetSerialNumber);
        if (!fts) {
            return false;
        }
        const loadingBay = this.getLoadingBayForOrder(fts.state.serialNumber, orderId);
        return loadingBay !== undefined;
    }
    /**
     * Checks if an FTS is docked without an order waiting at a given position.
     * @param targetSerialNumber
     * @param [orderId] the orderId that has to be able to be accepted by the FTS
     */
    getFtsAtPosition(targetSerialNumber, orderId) {
        const fts = Array.from(this.knownModules.values()).find(paired => paired.state.connected &&
            paired.state.lastModuleSerialNumber === targetSerialNumber &&
            paired.state.available === ccu_1.AvailableState.READY);
        if (!fts) {
            return undefined;
        }
        if (orderId) {
            const loadingBay = this.getLoadingBayForOrder(fts.state.serialNumber, orderId);
            if (loadingBay !== undefined) {
                return undefined;
            }
            if (!fts.state.lastLoadPosition || !this.isLoadingBayFree(fts.state.serialNumber, fts.state.lastLoadPosition)) {
                return undefined;
            }
        }
        return fts.state;
    }
    getLastFinishedDockId(serialNumber) {
        return this.knownModules.get(serialNumber)?.lastFinishedActionId;
    }
    setLastFinishedDockId(serialNumber, actionId) {
        this.initializePairingStateObject(serialNumber);
        const data = this.knownModules.get(serialNumber);
        data.lastFinishedActionId = actionId;
    }
}
exports.FtsPairingStates = FtsPairingStates;
