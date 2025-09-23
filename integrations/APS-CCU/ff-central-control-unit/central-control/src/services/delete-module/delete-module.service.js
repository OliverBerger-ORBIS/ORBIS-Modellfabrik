"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const protocol_1 = require("../../../../common/protocol");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const helpers_1 = require("../../helpers");
const pairing_states_1 = require("../../modules/pairing/pairing-states");
class DeleteModuleService {
    constructor(mqtt) {
        this.mqtt = mqtt;
        this.listenToMessages();
        void this.subscribeToTopics();
    }
    static initialize(mqtt) {
        if (!DeleteModuleService.instance) {
            console.debug('Intialize the DeleteModuleService');
            DeleteModuleService.instance = new DeleteModuleService(mqtt);
            console.debug('DeleteModuleService ready');
        }
    }
    listenToMessages() {
        this.mqtt.on('message', async (topic, message) => {
            if ((0, helpers_1.matchTopics)(DeleteModuleService.TOPICS, topic)) {
                await this.handleDeleteModuleRequest(message.toString());
            }
        });
    }
    async subscribeToTopics() {
        const subscriptions = await this.mqtt.subscribe(DeleteModuleService.TOPICS, { qos: 2 });
        console.log('DeleteModuleService:', subscriptions);
    }
    /**
     * Based on the received message, the module will be deleted from the CCU
     * and all topics will be cleared.
     * @param message The message containing the serial number of the module to delete.
     */
    async handleDeleteModuleRequest(message) {
        if (!message) {
            // ignore empty message
            return;
        }
        const { serialNumber } = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
        if (!serialNumber) {
            // invalid serial number received, ignoring message
            return;
        }
        const publishOptions = { qos: 1, retain: true };
        const emptyMessage = Buffer.from('');
        const topicsToRemove = [
            protocol_1.ModuleTopic.STATE,
            protocol_1.ModuleTopic.ORDER,
            protocol_1.ModuleTopic.CONNECTION,
            protocol_1.ModuleTopic.FACTSHEET,
            protocol_1.ModuleTopic.INSTANT_ACTION,
        ];
        for (const topic of topicsToRemove) {
            await this.mqtt.publish((0, protocol_1.getModuleTopic)(serialNumber, topic), emptyMessage, publishOptions);
        }
        await this.mqtt.publish(`${protocol_1.ModuleTopic.ROOT}/${serialNumber}`, emptyMessage, publishOptions);
        await pairing_states_1.PairingStates.getInstance().removeKnownModule(serialNumber);
    }
}
DeleteModuleService.TOPICS = [protocol_1.CcuTopic.DELETE_MODULE];
exports.default = DeleteModuleService;
