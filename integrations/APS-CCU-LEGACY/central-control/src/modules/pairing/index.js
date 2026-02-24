"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.calcStatusLEDFromPairingState = exports.sendPairingState = exports.publishPairingState = exports.sendKnownModules = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const node_crypto_1 = require("node:crypto");
const protocol_1 = require("../../../../common/protocol");
const ccu_1 = require("../../../../common/protocol/ccu");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const mqtt_1 = require("../../mqtt/mqtt");
const current_errors_service_1 = __importDefault(require("../current-errors/current-errors.service"));
const stock_management_service_1 = require("../order/stock/stock-management-service");
const fts_pairing_states_1 = require("./fts-pairing-states");
const pairing_states_1 = require("./pairing-states");
exports.TOPICS = [(0, protocol_1.getModuleTopic)(protocol_1.ANY_SERIAL, protocol_1.ModuleTopic.CONNECTION), (0, protocol_1.getFtsTopic)(protocol_1.ANY_SERIAL, protocol_1.FtsTopic.CONNECTION)];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
/**
 * Send the provided knownModules map to the ccu/pairing/known_modules topic for additional debug information.
 * @param knownModules the map of known modules, including their current state
 */
async function sendKnownModules(knownModules) {
    const mqtt = (0, mqtt_1.getMqttClient)();
    if (!mqtt) {
        return;
    }
    return mqtt.publish(protocol_1.CcuTopic.KNOWN_MODULES_STATE, JSON.stringify(knownModules), {
        qos: 2,
        retain: true,
    });
}
exports.sendKnownModules = sendKnownModules;
async function publishPairingState() {
    return sendPairingState(pairing_states_1.PairingStates.getInstance(), fts_pairing_states_1.FtsPairingStates.getInstance());
}
exports.publishPairingState = publishPairingState;
async function sendPairingState(modState, ftsState) {
    const mqtt = (0, mqtt_1.getMqttClient)();
    const pairingState = {
        modules: modState.getAll(),
        transports: ftsState.getAll(),
    };
    try {
        console.log('Calculating LED State');
        const module = pairing_states_1.PairingStates.getInstance().getForModuleType(module_1.ModuleType.DPS);
        if (module) {
            const ledInstantAction = (0, exports.calcStatusLEDFromPairingState)(pairingState, module.serialNumber);
            console.log('LED UPDATE', JSON.stringify(ledInstantAction));
            const topic = (0, protocol_1.getModuleTopic)(module.serialNumber, protocol_1.ModuleTopic.INSTANT_ACTION);
            await mqtt.publish(topic, JSON.stringify(ledInstantAction), { qos: 2 });
            console.log('Calculated LED State published');
        }
    }
    catch (e) {
        console.error('Error while updating LED State', e);
    }
    try {
        await mqtt.publish(protocol_1.CcuTopic.PAIRING_STATE, JSON.stringify(pairingState), {
            qos: 2,
            retain: true,
        });
    }
    catch (e) {
        console.error('Error while sending pairing state', e);
    }
}
exports.sendPairingState = sendPairingState;
/**
 * Based on the pairing state, this function determines the global state of the APS and wraps
 * it into an instant action which is used to turn the LEDs on/off on the connected DPS module.
 *
 * Gelb-Grün bedeutet, dass mindestens eine Station auf die Weitergabe eines Werkstücks wartet.
 * Grün bedeutet, alle Stationen befinden sich im Wartezustand.
 * Gelb bedeutet, dass mindestens eine Station aktiv ist.
 * Rot bedeutet einen Fehler, der im Dashboard via Reset gelöst werden muss. Bspw. ein Werkstück wurde nicht
 * an die Station übergeben oder ein FTS hat die Spur verloren
 *
 * @param pairingState
 * @param serialNumber
 */
const calcStatusLEDFromPairingState = (pairingState, serialNumber) => {
    // initiate instant action with green LED on indicating idle state
    const statusLeds = {
        green: false,
        red: false,
        yellow: false,
    };
    const ledInstantAction = {
        serialNumber,
        timestamp: new Date(),
        actions: [
            {
                actionId: (0, node_crypto_1.randomUUID)(),
                actionType: vda_1.InstantActions.SET_STATUS_LED,
                metadata: statusLeds,
            },
        ],
    };
    const allPairedModules = [...pairingState.modules, ...pairingState.transports].filter(mod => mod.pairedSince !== undefined);
    const currentErrors = current_errors_service_1.default.getInstance().getAllCurrentErrors();
    let overallBlocked = false;
    let overallBusy = false;
    let overallAssigned = false;
    for (const module of allPairedModules) {
        const hasError = currentErrors.some(error => error.serialNumber === module.serialNumber && (error.errors ?? []).some(err => err.errorLevel === 'FATAL'));
        const isChargingFts = module.type === 'FTS' && module.charging;
        if (module.available === ccu_1.AvailableState.BLOCKED && hasError && !isChargingFts) {
            overallBlocked = true;
            break; // Red is the highest prio, if there is one module with errors, then the LED is red in any case
        }
        if (!hasError && (module.available === ccu_1.AvailableState.BUSY || module.available === ccu_1.AvailableState.BLOCKED)) {
            overallBusy = true;
        }
        if (module.available === ccu_1.AvailableState.READY && module.assigned) {
            overallAssigned = true;
            // The DPS should be busy if it has a load.
            // Currently there is no good way to differentiate between busy input and waiting for FTS
            if (module.subType === module_1.ModuleType.DPS) {
                overallBusy = true;
            }
        }
    }
    if (overallBlocked) {
        statusLeds.red = true;
    }
    else if (overallBusy) {
        statusLeds.yellow = true;
    }
    else if (overallAssigned) {
        statusLeds.green = true;
    }
    else {
        statusLeds.green = true;
    }
    return ledInstantAction;
};
exports.calcStatusLEDFromPairingState = calcStatusLEDFromPairingState;
const handleMessage = async (message, topic) => {
    if (!message) {
        // ignoring empty message
        return;
    }
    console.log('handleMessage connection', message);
    const conn = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    const modState = pairing_states_1.PairingStates.getInstance();
    const ftsState = fts_pairing_states_1.FtsPairingStates.getInstance();
    if (topic.startsWith(protocol_1.ModuleTopic.ROOT)) {
        await modState.update(conn);
        stock_management_service_1.StockManagementService.updateBaysFromModule(conn.serialNumber);
    }
    else if (topic.startsWith(protocol_1.FtsTopic.ROOT)) {
        await ftsState.update(conn);
    }
    else {
        console.error('Unknown topic: ' + topic);
        return;
    }
    return sendPairingState(modState, ftsState);
};
exports.handleMessage = handleMessage;
