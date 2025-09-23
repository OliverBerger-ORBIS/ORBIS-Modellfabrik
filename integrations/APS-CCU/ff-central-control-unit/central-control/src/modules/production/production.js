"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.sendCancelStorageOrder = exports.sendAnnounceDpsOutput = exports.sendResetModuleInstantAction = exports.clearHBWContents = exports.sendProductionCommand = void 0;
const mqtt_1 = require("../../mqtt/mqtt");
const protocol_1 = require("../../../../common/protocol");
const module_1 = require("../../../../common/protocol/module");
const ccu_1 = require("../../../../common/protocol/ccu");
const pairing_states_1 = require("../pairing/pairing-states");
const models_1 = require("../../models/models");
const vda_1 = require("../../../../common/protocol/vda");
const node_crypto_1 = require("node:crypto");
const convertProductionType = (prodStep, orderId, orderUpdateId, pairedModule, metadata) => {
    return {
        timestamp: new Date(),
        serialNumber: pairedModule.serialNumber,
        orderId,
        orderUpdateId,
        action: {
            id: prodStep.id,
            command: prodStep.command,
            metadata,
        },
    };
};
/**
 * sends the production command to a module and return the chosen module serialNumber
 * @param productionStep
 * @param orderId
 * @param orderUpdateId
 * @param pairedModule
 * @param metadata
 */
const sendProductionCommand = async (productionStep, orderId, orderUpdateId, pairedModule, metadata) => {
    // sanity check
    const serialNumber = pairedModule.serialNumber;
    if (!pairing_states_1.PairingStates.getInstance().isReadyForOrder(serialNumber, orderId)) {
        throw new models_1.ControllerNotReadyError('MODULE', productionStep.moduleType);
    }
    const command = convertProductionType(productionStep, orderId, orderUpdateId, pairedModule, metadata);
    const mqtt = (0, mqtt_1.getMqttClient)();
    return mqtt
        .publish((0, protocol_1.getModuleTopic)(serialNumber, protocol_1.ModuleTopic.ORDER), JSON.stringify(command))
        .then(() => console.debug(`command published: ${productionStep.command}`))
        .catch(err => console.error(`command not published: ${productionStep.command}`, err));
};
exports.sendProductionCommand = sendProductionCommand;
/**
 * Sends a SET_STORAGE instant action to the given module that clears all stored workpieces
 * @param serialNumber
 */
const sendEmptySetStorageAction = async (serialNumber) => {
    const instantAction = {
        timestamp: new Date(),
        serialNumber: serialNumber,
        actions: [
            {
                actionType: vda_1.InstantActions.SET_STORAGE,
                actionId: (0, node_crypto_1.randomUUID)(),
                metadata: {
                    contents: {},
                },
            },
        ],
    };
    if (instantAction.actions[0]?.metadata && 'contents' in instantAction.actions[0].metadata) {
        for (const position of Object.values(module_1.StorageModuleBayPosition)) {
            instantAction.actions[0].metadata.contents[position] = {};
        }
    }
    const mqtt = (0, mqtt_1.getMqttClient)();
    return mqtt.publish((0, protocol_1.getModuleTopic)(serialNumber, protocol_1.ModuleTopic.INSTANT_ACTION), JSON.stringify(instantAction));
};
/**
 * Clear the contents of all storage modules to a new empty state.
 */
const clearHBWContents = async () => {
    const modules = pairing_states_1.PairingStates.getInstance()
        .getAll()
        .filter(mod => mod.subType === module_1.ModuleType.HBW);
    for (const mod of modules) {
        await sendEmptySetStorageAction(mod.serialNumber);
    }
};
exports.clearHBWContents = clearHBWContents;
/**
 * Send an instant action to the FTS to reset it and force a re-pairing.
 */
const sendResetModuleInstantAction = async (serialNumber) => {
    const topic = (0, protocol_1.getModuleTopic)(serialNumber, protocol_1.ModuleTopic.INSTANT_ACTION);
    console.debug(`Sending reset instant action for Module ${serialNumber} to topic ${topic}`);
    const instantAction = {
        serialNumber,
        timestamp: new Date(),
        actions: [
            {
                actionId: (0, node_crypto_1.randomUUID)(),
                actionType: vda_1.InstantActions.RESET,
            },
        ],
    };
    const pairingStates = pairing_states_1.PairingStates.getInstance();
    await pairingStates.updateAvailability(serialNumber, ccu_1.AvailableState.BLOCKED);
    const mqttClient = (0, mqtt_1.getMqttClient)();
    return mqttClient.publish(topic, JSON.stringify(instantAction), { qos: 2 });
};
exports.sendResetModuleInstantAction = sendResetModuleInstantAction;
/**
 * Send an instant action to the DPS to announce a PICK command to output a workpice.
 * The DPS will then abort running input processes that have not been published and wait for the PICK command.
 * @param serialNumber
 * @param orderId
 * @param workpiece
 */
const sendAnnounceDpsOutput = async (serialNumber, orderId, workpiece) => {
    const topic = (0, protocol_1.getModuleTopic)(serialNumber, protocol_1.ModuleTopic.INSTANT_ACTION);
    console.debug(`Sending announceOutput instant action for Module ${serialNumber} to topic ${topic}`);
    const instantAction = {
        serialNumber,
        timestamp: new Date(),
        actions: [
            {
                actionId: (0, node_crypto_1.randomUUID)(),
                actionType: vda_1.InstantActions.ANNOUNCE_OUTPUT,
                metadata: {
                    orderId: orderId,
                    type: workpiece,
                },
            },
        ],
    };
    const mqttClient = (0, mqtt_1.getMqttClient)();
    return mqttClient.publish(topic, JSON.stringify(instantAction), { qos: 2 });
};
exports.sendAnnounceDpsOutput = sendAnnounceDpsOutput;
/**
 * Send an instant action to the DPS to cancel the storage order for a loaded workpiece.
 * The DPS will then cancel the order and discard the workpiece to NIO.
 * @param serialNumber
 */
const sendCancelStorageOrder = async (serialNumber) => {
    const topic = (0, protocol_1.getModuleTopic)(serialNumber, protocol_1.ModuleTopic.INSTANT_ACTION);
    console.debug(`Sending cancelStorageOrder instant action for Module ${serialNumber} to topic ${topic}`);
    const instantAction = {
        serialNumber,
        timestamp: new Date(),
        actions: [
            {
                actionId: (0, node_crypto_1.randomUUID)(),
                actionType: vda_1.InstantActions.CANCEL_STORAGE_ORDER,
            },
        ],
    };
    const mqttClient = (0, mqtt_1.getMqttClient)();
    return mqttClient.publish(topic, JSON.stringify(instantAction), { qos: 2 });
};
exports.sendCancelStorageOrder = sendCancelStorageOrder;
