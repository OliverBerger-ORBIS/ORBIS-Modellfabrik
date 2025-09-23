"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderFlowService = void 0;
const module_1 = require("../../../../../common/protocol/module");
const helpers_1 = require("../../../helpers");
const protocol_1 = require("../../../../../common/protocol");
const node_crypto_1 = require("node:crypto");
const ccu_1 = require("../../../../../common/protocol/ccu");
const mqtt_1 = require("../../../mqtt/mqtt");
class OrderFlowService {
    /**
     * Initialize the order flows with the given file used for persistence.
     * This should be called before connecting to mqtt.
     * @param filename
     */
    static async initialize(filename) {
        console.debug('Initialize the Order Flows Service');
        if (this.filename) {
            return;
        }
        this.filename = filename;
        // setup default flows
        this.flows = this.getDefaultFlows();
        await this.reloadFlows();
        console.debug('Order Flows Service initialized');
    }
    /**
     * The default flows as used in the sample factory
     */
    static getDefaultFlows() {
        return {
            BLUE: { steps: [module_1.ModuleType.MILL, module_1.ModuleType.DRILL, module_1.ModuleType.AIQS] },
            RED: { steps: [module_1.ModuleType.MILL, module_1.ModuleType.AIQS] },
            WHITE: { steps: [module_1.ModuleType.DRILL, module_1.ModuleType.AIQS] },
        };
    }
    /**
     * Converts a production flow to a complete production definition.
     * A flow consists of the production steps without fetching the workpiece and delivery
     * @param flow The module flow
     * @param depenendActionId optionally an actionid that has to be finished first
     * @private
     */
    static convertFlowToDefinition(flow, depenendActionId) {
        const definition = {
            navigationSteps: [],
            productionSteps: [],
        };
        // start by driving to HBW and getting the workpiece
        const navigateFromStart = this.getNavigationStep((0, node_crypto_1.randomUUID)(), module_1.ModuleType.START, module_1.ModuleType.HBW, depenendActionId);
        definition.navigationSteps?.push(navigateFromStart);
        const getWorkpieceStep = this.getOrderManufactureStep((0, node_crypto_1.randomUUID)(), module_1.ModuleType.HBW, module_1.ModuleCommandType.DROP, navigateFromStart.id);
        definition.productionSteps.push(getWorkpieceStep);
        // add all production steps: navigate -> pick -> produce -> drop
        let prevStep = getWorkpieceStep;
        for (const mod of flow.steps) {
            const navigate = this.getNavigationStep((0, node_crypto_1.randomUUID)(), prevStep.moduleType, mod, prevStep.id);
            definition.navigationSteps?.push(navigate);
            const pick = this.getOrderManufactureStep((0, node_crypto_1.randomUUID)(), mod, module_1.ModuleCommandType.PICK, navigate.id);
            definition.productionSteps.push(pick);
            let produce;
            const action = module_1.MODULE_COMMAND_MAP[mod];
            if (action) {
                produce = this.getOrderManufactureStep((0, node_crypto_1.randomUUID)(), mod, action, pick.id);
                definition.productionSteps.push(produce);
            }
            const drop = this.getOrderManufactureStep((0, node_crypto_1.randomUUID)(), mod, module_1.ModuleCommandType.DROP, produce?.id ?? pick.id);
            definition.productionSteps.push(drop);
            prevStep = drop;
        }
        // end by dropping the workpiece at the DPS and staying there
        const navigateToDps = this.getNavigationStep((0, node_crypto_1.randomUUID)(), prevStep.moduleType, module_1.ModuleType.DPS, prevStep.id);
        definition.navigationSteps?.push(navigateToDps);
        const dpsStep = this.getOrderManufactureStep((0, node_crypto_1.randomUUID)(), module_1.ModuleType.DPS, module_1.ModuleCommandType.PICK, navigateToDps.id);
        definition.productionSteps.push(dpsStep);
        return definition;
    }
    /**
     * Reload flows from the persistent file.
     *
     * Flows will be merged on top of the existing flows.
     * An existing flow will be kept if the file does not contain a valid flow for that workpiece type.
     * An empty flow is valid
     */
    static async reloadFlows() {
        try {
            const newFlows = await (0, helpers_1.readJsonFile)(this.filename);
            // load new valid flows and merge them with the existing flows.
            for (const [item, flow] of Object.entries(newFlows)) {
                const wp = item;
                if ('steps' in flow && Array.isArray(flow.steps)) {
                    this.flows[wp] = flow;
                }
                else {
                    console.debug(`OrderFlowService: Ignoring invalid flow for ${wp}: `, flow);
                }
            }
        }
        catch (e) {
            console.debug(`OrderFlowService: Error reading flows from file ${this.filename}: `, e);
        }
    }
    /**
     * Save flows to the persistence file,
     */
    static async saveFlows() {
        try {
            await (0, helpers_1.writeJsonFile)(this.filename, this.flows);
        }
        catch (e) {
            console.debug(`OrderFlowService: Error saving flows to file ${this.filename}: `, e);
        }
    }
    static getFlows() {
        return JSON.parse(JSON.stringify(this.flows));
    }
    /**
     * Set new flows.
     * @param flows The new production flows
     */
    static setFlows(flows) {
        for (const [item, flow] of Object.entries(flows)) {
            const wp = item;
            if ('steps' in flow && Array.isArray(flow.steps)) {
                this.flows[wp] = flow;
            }
            else {
                console.debug(`OrderFlowService: Ignoring invalid flow for ${wp}: `, flow);
            }
        }
    }
    /**
     * Publish flow information to the mqtt topic {@link CcuTopic.FLOWS} if a connection exists
     */
    static async publishFlows() {
        const mqtt = (0, mqtt_1.getMqttClient)();
        if (mqtt) {
            return mqtt.publish(protocol_1.CcuTopic.FLOWS, JSON.stringify(this.flows), { qos: 1, retain: true });
        }
    }
    /**
     * Get a production definition for a workpiece type that has been defined with a flow
     * @param type
     * @param dependentActionId Optionally the id of an action that has to be finished before this production starts
     */
    static getProductionDefinition(type, dependentActionId) {
        const flow = this.flows[type] || { steps: [] };
        return this.convertFlowToDefinition(flow, dependentActionId);
    }
    /**
     * Returns a list of all production steps that are required to store a new workpiece
     *
     * 1) Drive the FTS to the input module
     * 2) Unload the workpiece onto the FTS
     * 3) Drive the FTS to the HighBayStorage
     * 4) Load the workpiece from the FTS into the HighBayStorage
     *
     */
    static getStorageProductionDefinition() {
        // Drive from starting point to the input module
        const startToDPS = this.getNavigationStep((0, node_crypto_1.randomUUID)(), module_1.ModuleType.START, module_1.ModuleType.DPS);
        // load classified workpiece onto fts from input module
        const unloadWorkpieceFromDPS = this.getOrderManufactureStep((0, node_crypto_1.randomUUID)(), module_1.ModuleType.DPS, module_1.ModuleCommandType.DROP, startToDPS.id);
        // Drive from input module to the storage module
        const dpsToHBW = this.getNavigationStep((0, node_crypto_1.randomUUID)(), module_1.ModuleType.DPS, module_1.ModuleType.HBW, unloadWorkpieceFromDPS.id);
        // load classified workpiece onto fts from input module
        const storeWorkpiece = this.getOrderManufactureStep((0, node_crypto_1.randomUUID)(), module_1.ModuleType.HBW, module_1.ModuleCommandType.PICK, dpsToHBW.id);
        // Stay at the last module
        return {
            navigationSteps: [startToDPS, dpsToHBW],
            productionSteps: [unloadWorkpieceFromDPS, storeWorkpiece],
        };
    }
    /**
     * Helper method to generate a navigation command in one line
     */
    static getNavigationStep(actionId, source, target, dependentActionId) {
        return {
            id: actionId,
            type: 'NAVIGATION',
            state: ccu_1.OrderState.ENQUEUED,
            source,
            target,
            dependentActionId,
        };
    }
    /**
     * Helper method to generate a production command in one line
     */
    static getOrderManufactureStep(id, moduleType, command, dependentActionId) {
        return {
            id,
            type: 'MANUFACTURE',
            dependentActionId,
            state: ccu_1.OrderState.ENQUEUED,
            command,
            moduleType,
        };
    }
}
exports.OrderFlowService = OrderFlowService;
OrderFlowService.flows = {};
