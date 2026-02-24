"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BasePairingStates = void 0;
const ccu_1 = require("../../../../common/protocol/ccu");
const vda_1 = require("../../../../common/protocol/vda");
const factsheets_1 = require("../factsheets/factsheets");
class BasePairingStates {
    /**
     * Get a PairedModule for a given serial number. undefined if no module is paired.
     * @param serialNumber the serial number of the module
     */
    get(serialNumber) {
        return this.getKnownModules().get(serialNumber)?.state;
    }
    /**
     * Returns all paired DeviceTypes
     */
    getAll() {
        return Array.from(this.getKnownModules().values()).map(data => data.state);
    }
    /**
     * Returns the factsheet for the module with the given serial number. undefined if no factsheet is available.
     * @param serialNumber
     */
    getFactsheet(serialNumber) {
        return this.getKnownModules().get(serialNumber)?.factsheet;
    }
    /**
     * Clears all known modules.
     */
    reset() {
        this.getKnownModules().clear();
    }
    /**
     * update the connection state of a device type
     * @param conn the connection state
     */
    async update(conn) {
        this.initializePairingStateObject(conn.serialNumber);
        // this will not be null, because we will initialze it in the line above
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const data = this.getKnownModules().get(conn.serialNumber);
        const lastConnState = data.connection?.connectionState;
        data.connection = conn;
        data.state.connected = conn.connectionState === vda_1.ConnectionState.ONLINE;
        data.state.ip = conn.connectionState === vda_1.ConnectionState.ONLINE ? conn.ip : undefined;
        data.state.version = conn.version;
        console.log('updated state', JSON.stringify(data.state));
        if (data.state.connected) {
            data.state.lastSeen = new Date();
            if (!data.factsheet || (lastConnState && lastConnState !== vda_1.ConnectionState.ONLINE)) {
                await (0, factsheets_1.requestFactsheet)(data.state);
            }
        }
        else {
            data.state.available = ccu_1.AvailableState.BLOCKED;
        }
    }
    /**
     * Mark a module as being in the calibration mode
     * @param serialNumber
     * @param calibrating is the caliration mode active?
     */
    setCalibrating(serialNumber, calibrating) {
        this.initializePairingStateObject(serialNumber);
        // this will not be null, because we will initialze it in the line above
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        this.getKnownModules().get(serialNumber).state.calibrating = calibrating;
    }
    /**
     * Initialize a pairing state if necessary
     */
    initializePairingStateObject(serialNumber) {
        if (this.getKnownModules().has(serialNumber)) {
            return;
        }
        this.getKnownModules().set(serialNumber, {
            state: {
                serialNumber: serialNumber,
                type: this.getType(),
                connected: false,
                available: ccu_1.AvailableState.BLOCKED,
            },
        });
    }
}
exports.BasePairingStates = BasePairingStates;
