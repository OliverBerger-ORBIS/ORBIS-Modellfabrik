"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleMessage = exports.TOPIC_OPTIONS = exports.TOPICS = void 0;
const protocol_1 = require("../../../../../common/protocol");
const pairing_states_1 = require(".././pairing-states");
const mqtt_1 = require("../../../mqtt/mqtt");
const json_revivers_1 = require("../../../../../common/util/json.revivers");
const fts_pairing_states_1 = require(".././fts-pairing-states");
const vda_1 = require("../../../../../common/protocol/vda");
const node_crypto_1 = require("node:crypto");
const module_1 = require("../../../../../common/protocol/module");
exports.TOPICS = [protocol_1.CcuTopic.PAIRING_PAIR_FTS];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
/**
 * Send the initial docking action to pair the FTS.
 *
 * This tells the FTS it is standing in front of the DPS and it should dock there to get into a known position.
 * If no DPS is connected and available in the layout, do nothing.
 * @param fts
 */
const sendFtsInitialDockingInstantAction = async (fts) => {
    const dps = pairing_states_1.PairingStates.getInstance().getForModuleType(module_1.ModuleType.DPS);
    if (!dps) {
        console.error(`Could not find a DPS to initiate the FTS docking sequence for ${fts.serialNumber}`);
        return;
    }
    const action = {
        timestamp: new Date(),
        serialNumber: fts.serialNumber,
        actions: [
            {
                actionType: vda_1.InstantActions.FIND_INITIAL_DOCK_POSITION,
                actionId: (0, node_crypto_1.randomUUID)(),
                metadata: {
                    nodeId: dps.serialNumber,
                },
            },
        ],
    };
    return (0, mqtt_1.getMqttClient)().publish((0, protocol_1.getFtsTopic)(fts.serialNumber, protocol_1.FtsTopic.INSTANT_ACTION), JSON.stringify(action), { qos: 2 });
};
/**
 * Receives the request to pair an fts and position it docked to the DPS.
 * @param message
 */
const handleMessage = async (message) => {
    const request = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    const ftsState = fts_pairing_states_1.FtsPairingStates.getInstance();
    const fts = ftsState.get(request.serialNumber);
    if (fts?.connected && !fts?.pairedSince) {
        await sendFtsInitialDockingInstantAction(fts);
    }
};
exports.handleMessage = handleMessage;
