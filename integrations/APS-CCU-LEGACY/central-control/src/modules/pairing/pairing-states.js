"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PairingStates = void 0;
/* eslint-disable @typescript-eslint/no-non-null-assertion */
const ccu_1 = require("../../../../common/protocol/ccu");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const base_pairing_states_1 = require("./base-pairing-states");
const index_1 = require("./index");
const config_1 = __importDefault(require("../../config"));
class PairingStates extends base_pairing_states_1.BasePairingStates {
    constructor() {
        super();
        // TODO FITEFF22-347 do we need to store the last pairing date and last communication date?
        this.type = 'MODULE';
        this.knownModules = new Map();
    }
    getKnownModules() {
        if (config_1.default.mqtt.debug) {
            (0, index_1.sendKnownModules)(Object.fromEntries(this.knownModules)).catch(e => {
                // do not crash if we cannot publish the known modules, this is only for debugging
                console.error(e);
            });
        }
        return this.knownModules;
    }
    static getInstance() {
        if (!PairingStates.instance) {
            PairingStates.instance = new PairingStates();
        }
        return PairingStates.instance;
    }
    /**
     * returns a PairedModule if a module of ModuleType is ready for the given orderId.
     * The readiness is determined by:
     * <ul>
     *   <li>a module is connected and no order is currently execution on it --> a PairedModule is returned</li>
     *   <li>a module is connected, but an order is present on it.
     *    <br>
     *    <ul>
     *      <li>the order has not the same id as orderId --> undefined since the module is not ready</li>
     *      <li>
     *        <ul>
     *          <li>the state of the order != State.FINISHED --> undefined since the module is not ready</li>
     *          <li>the state of the order == State.FINISHED --> a PairedModule is returned as it is in a ready state to receive an order update for the given orderId</li>
     *        </ul>
     *      </li>
     *      <li>the order has the same id as orderId and has a status != State.FINISHED --> undefined since the module is not ready</li>
     *      <li>the order has the same id as orderId and has a status != State.FINISHED --> undefined since the module is not ready</li>
     *    </ul>
     *   </li>
     *   <li>the module is of the given type</li>
     *   </ul>
     * @param moduleType the module type to look for
     * @param orderId the order id to determine if the module is ready for an order.
     */
    getReadyForModuleType(moduleType, orderId) {
        const allReady = this.getAllReadyModuleData('MODULE').filter(data => data.factsheet?.typeSpecification.moduleClass === moduleType);
        console.log(`Found ready modules for ${moduleType}: ${allReady?.length || 0}`);
        return this.findModuleForOrder(allReady, orderId);
    }
    findModuleForOrder(modules, orderId) {
        let pairedMod = undefined;
        for (const mod of modules) {
            if (mod.orderId != undefined && mod.orderId !== orderId) {
                console.log(`Module ${mod.state.serialNumber} is not ready for orderID: ${orderId} 
        because it is already assigned to order ${mod.orderId}`);
                continue;
            }
            pairedMod = mod.state;
            if (mod.orderId === orderId) {
                // Early exit if we have a direct math on the order ID
                return mod.state;
            }
        }
        return pairedMod;
    }
    /**
     * Get the module currently assigned to the order
     * @param orderId
     * @param moduleType
     */
    getModuleForOrder(orderId, moduleType) {
        return this.getAllReadyModuleData('MODULE').find(data => {
            const orderIDMatches = data.orderId === orderId;
            const typeMatches = moduleType === undefined || data.state.subType === moduleType;
            console.log(`Finding module for order: ${orderId} ${moduleType} -> Results: ${orderIDMatches} ${typeMatches}`);
            return orderIDMatches && typeMatches;
        })?.state;
    }
    /**
     * Return if the module is ready to receive an order with the given orderid.
     * @param serialNumber
     * @param orderId
     */
    isReadyForOrder(serialNumber, orderId) {
        const data = this.getKnownModules().get(serialNumber);
        return data != undefined && this.isReady(serialNumber) && (!data.orderId || data.orderId === orderId);
    }
    /**
     * Get a paired module for a given type. This does not check if the module is ready to accept a new order. if this is needed use getReadyForModuleType.
     * Returns undefined if no module of the given type is paired and connected
     * @param moduleType the type the paired module should have
     * @param [orderId] reuse the module for the given orderId if possible
     */
    getForModuleType(moduleType, orderId) {
        const moduls = this.getAllPairedModuleData()
            .filter(module => module.state.connected)
            .filter(module => module.factsheet?.typeSpecification.moduleClass === moduleType);
        if (!orderId) {
            return moduls[0]?.state;
        }
        return this.findModuleForOrder(moduls, orderId);
    }
    getAllPairedModuleData() {
        return Array.from(this.knownModules.values()).filter(m => m.state.type === 'MODULE' && m.state.pairedSince);
    }
    getAllReadyModuleData(type) {
        return this.getAllPairedModuleData().filter(data => data.state?.type === type && data.state?.available === ccu_1.AvailableState.READY && data.state?.connected);
    }
    getAllReady(type) {
        return this.getAllReadyModuleData('MODULE')
            .map(data => data.state)
            .filter(state => state.subType === type);
    }
    getAllPaired(type) {
        return this.getAllPairedModuleData()
            .map(data => data.state)
            .filter(state => state.subType === type);
    }
    /**
     * Checks if a module is ready to receive an order or an order update
     * A module is ready if it is connected and paired and its state is READY.
     *
     * It does not indicate if the module can receive any new order or
     * only order updates for a specific order.
     * @param serialNumber
     */
    isReady(serialNumber) {
        const state = this.knownModules.get(serialNumber)?.state;
        if (!state || !state.connected || !state.pairedSince) {
            return false;
        }
        return state.available === ccu_1.AvailableState.READY;
    }
    updateFacts(facts) {
        this.initializePairingStateObject(facts.serialNumber);
        const data = this.knownModules.get(facts.serialNumber);
        data.factsheet = facts;
        data.state.subType = data.factsheet.typeSpecification.moduleClass;
        data.state.hasCalibration =
            undefined != data.factsheet.protocolFeatures?.moduleActions?.find(a => a.actionType === vda_1.InstantActions.CALIBRATION_START);
        // set default productionDuration if it is still missing.
        if (!data.state.productionDuration && !module_1.SUPPORT_MODULES.has(data.state.subType) && data.state.subType !== module_1.ModuleType.AIQS) {
            data.state.productionDuration = module_1.MODULE_DEFAULT_PRODUCTION_DURATION;
        }
        if (data.state.connected) {
            data.state.lastSeen = new Date();
        }
    }
    async updateAvailability(serialNumber, avail, orderId) {
        this.initializePairingStateObject(serialNumber);
        const data = this.knownModules.get(serialNumber);
        console.log(`PAIRING: updateAvailability ${serialNumber} ${avail} ${orderId}`);
        data.state.available = avail;
        data.state.assigned = !!orderId;
        data.orderId = orderId;
        await (0, index_1.publishPairingState)();
    }
    getType() {
        return this.type;
    }
    /**
     * Remove the module lock to a specific order, so all orders are accepted again
     * @param orderId
     */
    clearModuleForOrder(orderId) {
        for (const module of this.knownModules.values()) {
            if (module.orderId !== orderId) {
                continue;
            }
            module.orderId = undefined;
            module.state.assigned = false;
            module.state.available = ccu_1.AvailableState.READY;
        }
    }
    /**
     * Replace the paired modules with a new set of modules
     * This is used to set the paired modules from the modules configured in the layout
     *
     * @param modules all paired modules
     */
    setPairedModules(modules) {
        const pairedIds = new Set(modules.map(module => module.serialNumber));
        // delete pairing for removed modules
        for (const [moduleId, module] of this.knownModules.entries()) {
            if (!pairedIds.has(moduleId)) {
                module.state.pairedSince = undefined;
            }
        }
        // add pairing for added modules
        for (const module of modules) {
            this.initializePairingStateObject(module.serialNumber);
            const state = this.knownModules.get(module.serialNumber).state;
            if (!state.subType) {
                state.subType = module.type;
            }
            // set default productionDuration if it is still missing.
            if (!state.productionDuration && !module_1.SUPPORT_MODULES.has(module.type) && module.type !== module_1.ModuleType.AIQS) {
                state.productionDuration = module_1.MODULE_DEFAULT_PRODUCTION_DURATION;
            }
            if (!state.pairedSince) {
                state.pairedSince = new Date();
            }
            if (module.type === module_1.ModuleType.CHRG) {
                state.connected = true;
                if (state.available !== ccu_1.AvailableState.BUSY) {
                    state.available = ccu_1.AvailableState.READY;
                }
            }
        }
    }
    /**
     * Updates the production duration for a given module.
     *
     * @param {string} serialNumber - The serial number of the module to update.
     * @param {number} duration - The new production duration.
     */
    updateDuration(serialNumber, duration) {
        const state = this.get(serialNumber);
        console.debug(`Setting duration for ${serialNumber} to ${duration}`);
        if (state && state.subType && !module_1.SUPPORT_MODULES.has(state.subType) && state.productionDuration !== undefined) {
            state.productionDuration = duration;
        }
    }
    /**
     * Get the module type for a module by serial number
     * The module type is known only after the module has successfully sent its factsheet.
     *
     * @param serialNumber
     */
    getModuleType(serialNumber) {
        return this.getFactsheet(serialNumber)?.typeSpecification.moduleClass;
    }
    /**
     * Removes a module from the known modules by serial number.
     * @param {string} serialNumber - The serial number of the module to remove.
     */
    async removeKnownModule(serialNumber) {
        if (this.getKnownModules().has(serialNumber)) {
            this.getKnownModules().delete(serialNumber);
        }
        await (0, index_1.publishPairingState)();
    }
}
exports.PairingStates = PairingStates;
