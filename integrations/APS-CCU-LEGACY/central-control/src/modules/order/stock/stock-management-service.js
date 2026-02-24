"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.StockManagementService = void 0;
const pairing_states_1 = require("../../pairing/pairing-states");
const module_1 = require("../../../../../common/protocol/module");
const fts_pairing_states_1 = require("../../pairing/fts-pairing-states");
class StockManagementService {
    /**
     * Reinitialize the stock management
     */
    static reset() {
        this.clearStock();
        this.reservations = [];
        this.bayReservations = [];
        this.warehouseStorageBays.clear();
        this.activatedWarehouses.clear();
    }
    /**
     * Reinitialize the stock reservations
     */
    static removeAllReservations() {
        this.reservations = [];
        this.bayReservations = [];
    }
    /**
     * Check if there is a workpiece available for an order.
     *
     * @param type
     * @param unpreferredHbwSerials if set, the availability of other warehouses is checked first and the ones in this list are checked last
     *                              with the first warehouse in the list being the most unpreferred and being checked last
     * @returns serialNumber of the hbw where the workpiece can be reserved or undefined
     */
    static stockAvailable(type, unpreferredHbwSerials) {
        const reservationsForType = this.reservations.filter(reserve => reserve.type === type);
        if (reservationsForType.length >= this.stock[type]) {
            return undefined;
        }
        let warehouses = Array.from(this.activatedWarehouses);
        if (unpreferredHbwSerials) {
            warehouses = warehouses.filter(hbwSerial => !unpreferredHbwSerials.has(hbwSerial));
            warehouses.push(...Array.from(unpreferredHbwSerials).reverse());
        }
        for (const hbwSerial of warehouses) {
            const specificReserve = reservationsForType.filter(reserve => reserve.hbwSerial === hbwSerial);
            const specificAmount = (this.warehouseStock.get(hbwSerial) || []).filter(load => load.loadType === type);
            if (specificReserve.length < specificAmount.length) {
                return hbwSerial;
            }
        }
        return undefined;
    }
    /**
     * Check if there is a workpiece reserved for an order.
     *
     * @param orderId
     * @returns the hbw serial if there is a reserved workpiece, otherwise undefined
     */
    static hasReservedWorkpiece(orderId) {
        return this.reservations.find(reserve => reserve.orderId === orderId)?.hbwSerial;
    }
    /**
     * Tries to reserve a stocked workpiece for an order.
     * Does nothing If the workpiece is already reserved for the order.
     *
     * @param orderId
     * @param type
     * @returns the hbw serial if a workpiece could be reserved, otherwise undefined
     */
    static reserveWorkpiece(orderId, type) {
        const existing = this.reservations.find(reserve => reserve.orderId === orderId);
        if (existing && type !== existing.type) {
            throw new Error('Cannot reserve two different workpieces for an order');
        }
        else if (existing) {
            return existing.hbwSerial;
        }
        // when there are multiple FTS paired to the factory, try to reserve a workpiece in a different warehouse than the previous one
        // this enables the factory to utilize multiple FTS in parallel right from the start
        // if there is only one HBW, this will not have any effect, because the unpreferred HBWs will be still be checked - just last
        // and if there is only one HWB, it does not matter which one is last
        const hasMultipleFts = fts_pairing_states_1.FtsPairingStates.getInstance().getAll().length > 1;
        const unpreferredHbwSerials = new Set();
        if (hasMultipleFts && this.reservations.length > 0) {
            const reservationsBackwards = [...this.reservations].reverse();
            for (const previousReservation of reservationsBackwards) {
                unpreferredHbwSerials.add(previousReservation.hbwSerial);
            }
        }
        const available = this.stockAvailable(type, unpreferredHbwSerials);
        if (!available) {
            return undefined;
        }
        this.reservations.push({
            hbwSerial: available,
            type: type,
            orderId: orderId,
        });
        return available;
    }
    /**
     * Get the first warehouse id that has a reservation for an order
     *
     * @param orderId
     * @returns serialNumber of the chosen warehouse or undefined if none available
     */
    static getReservedWarehouse(orderId) {
        const baySerial = this.bayReservations.find(reserve => reserve.orderId === orderId)?.hbwSerial;
        if (baySerial) {
            return baySerial;
        }
        return this.reservations.find(reserve => reserve.orderId === orderId)?.hbwSerial;
    }
    /**
     * Removes a reservation if the workpiece has been taken or the order has been cancelled
     * @param orderId
     */
    static removeReservation(orderId) {
        this.reservations = this.reservations.filter(reserve => reserve.orderId !== orderId);
        this.bayReservations = this.bayReservations.filter(reserve => reserve.orderId !== orderId);
    }
    /**
     * Set the available stock as reported by the storage module
     * @param hbwSerial
     * @param loads
     */
    static setStock(hbwSerial, loads) {
        this.warehouseStock.set(hbwSerial, loads);
        this.updateStockAmount();
    }
    static updateStockAmount() {
        for (const type of Object.keys(this.stock)) {
            this.stock[type] = 0;
        }
        for (const hbwSerial of this.activatedWarehouses) {
            for (const load of this.warehouseStock.get(hbwSerial) || []) {
                this.stock[load.loadType] += 1;
            }
        }
    }
    /**
     * Tries to reserve an empty bay for a workpiece for an order.
     * Does nothing If the bay is already reserved for the order.
     *
     * @param orderId
     * @param type
     * @returns true if a bay could be reserved, otherwise false
     * @throws Error if a reservation for a different type already exists
     */
    static reserveEmptyBay(orderId, type) {
        const existing = this.bayReservations.find(reserve => reserve.orderId === orderId);
        if (existing && type !== existing.type) {
            throw new Error('Cannot reserve empty loading bays for two different workpieces for an order');
        }
        else if (existing) {
            return existing.hbwSerial;
        }
        const available = this.emptyBayAvailable(type);
        if (!available) {
            return undefined;
        }
        this.bayReservations.push({
            type: type,
            orderId: orderId,
            hbwSerial: available,
        });
        return available;
    }
    /**
     * Check if there is an empty bay reserved for an order.
     *
     * @param orderId
     * @returns true if a workpiece could be reserved, otherwise false
     */
    static hasReservedEmptyBay(orderId) {
        return this.bayReservations.some(reserve => reserve.orderId === orderId);
    }
    /**
     * Check if there is an empty bay available for the workpiece of an order.
     *
     * @param type
     * @returns {string | undefined} the serial number of the HBW that has a free slot or undefined if nothing is available
     */
    static emptyBayAvailable(type) {
        const reservationsForType = this.bayReservations.filter(reserve => reserve.type === type);
        for (const warehouse of this.activatedWarehouses) {
            const baysForType = this.warehouseStorageBays.get(warehouse)?.[type] || 0;
            const reservations = reservationsForType.filter(reserve => reserve.hbwSerial === warehouse);
            const stockOfType = this.warehouseStock.get(warehouse)?.filter(stock => stock.loadType === type) || [];
            const baysFree = baysForType - stockOfType.length;
            if (reservations.length < baysFree) {
                return warehouse;
            }
        }
    }
    /**
     * Set the available storage bays as reported by the storage module
     * @param hbwSerial
     * @param sets
     */
    static setBays(hbwSerial, sets) {
        const stock = {
            RED: 0,
            BLUE: 0,
            WHITE: 0,
        };
        for (const set of sets) {
            stock[set.loadType] += Math.floor(set.maxAmount || 1);
        }
        this.warehouseStorageBays.set(hbwSerial, stock);
    }
    /**
     * Update storage bay information for a module
     * @param serialNumber the module
     */
    static updateBaysFromModule(serialNumber) {
        const pairingState = pairing_states_1.PairingStates.getInstance();
        const module = pairingState.get(serialNumber);
        if (module?.type === 'MODULE' && module.subType === module_1.ModuleType.HBW && module.connected) {
            // The module disconnecting is currently ignored.
            const factsheet = pairingState.getFactsheet(serialNumber);
            if (factsheet?.loadSpecification?.loadSets) {
                StockManagementService.setBays(serialNumber, factsheet.loadSpecification.loadSets);
            }
        }
    }
    static clearStock() {
        this.warehouseStock.clear();
        this.updateStockAmount();
    }
    static getWarehouses() {
        return [...this.activatedWarehouses.values()];
    }
    static setWarehouses(warehouses) {
        this.activatedWarehouses = new Set(warehouses);
    }
    static getStock() {
        const storedLoads = new Array();
        const assignedReservations = this.getReservationsCounts();
        for (const warehouse of this.activatedWarehouses) {
            const loads = [...(this.warehouseStock.get(warehouse) || [])];
            // Sort loads by timestamp in ascending order (oldest first)
            loads.sort((a, b) => (a.loadTimestamp || 0) - (b.loadTimestamp || 0));
            for (const load of loads) {
                const is_reserved = assignedReservations[warehouse]?.[load.loadType] > 0;
                if (is_reserved) {
                    assignedReservations[warehouse][load.loadType] -= 1;
                }
                const stored = {
                    hbwSerial: warehouse,
                    workpiece: load,
                    reserved: is_reserved,
                };
                storedLoads.push(stored);
            }
        }
        return storedLoads;
    }
    static getReservationsCounts() {
        const assignedReservations = {};
        for (const warehouse of this.activatedWarehouses) {
            assignedReservations[warehouse] = {
                RED: 0,
                BLUE: 0,
                WHITE: 0,
            };
        }
        for (const reservation of this.reservations) {
            if (assignedReservations[reservation.hbwSerial]) {
                assignedReservations[reservation.hbwSerial][reservation.type] += 1;
            }
        }
        return assignedReservations;
    }
}
exports.StockManagementService = StockManagementService;
/**
 * The list of reserved stock items
 * @private
 */
StockManagementService.reservations = new Array();
/**
 * The list of reserved empty bays
 * @private
 */
StockManagementService.bayReservations = new Array();
/**
 * The stored stock per warehouse
 * @private
 */
StockManagementService.warehouseStock = new Map();
/**
 * The warehouses that are configured in the factory layout
 * @private
 */
StockManagementService.activatedWarehouses = new Set();
StockManagementService.stock = {
    RED: 0,
    WHITE: 0,
    BLUE: 0,
};
StockManagementService.warehouseStorageBays = new Map();
