"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const module_1 = require("../../../../../common/protocol/module");
const order_flow_service_1 = require("./order-flow-service");
const crypt_spies = __importStar(require("node:crypto"));
const helpers_spies = __importStar(require("../../../helpers"));
const ccu_1 = require("../../../../../common/protocol/ccu");
let uuid_counter = 100000000000;
jest.mock('node:crypto');
describe('Test order flow parsing and definition generation', () => {
    beforeEach(() => {
        jest.spyOn(helpers_spies, 'writeJsonFile').mockResolvedValue();
        jest.spyOn(helpers_spies, 'readJsonFile').mockResolvedValue({});
        // mock uuids with sequential deterministic values
        jest.spyOn(crypt_spies, 'randomUUID').mockImplementation(() => {
            uuid_counter++;
            return `aabbccdd-eeee-ffff-1111-${uuid_counter}`;
        });
    });
    afterEach(() => {
        // no-explicit-any is needed here as the properties are private
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        order_flow_service_1.OrderFlowService['flows'] = {};
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        order_flow_service_1.OrderFlowService['filename'] = undefined;
        jest.restoreAllMocks();
        uuid_counter = 100000000000;
    });
    it('should convert a flow to an OrderDefinition', () => {
        const flow = { steps: [module_1.ModuleType.DRILL, module_1.ModuleType.AIQS] };
        const expectedDefinition = {
            navigationSteps: [
                {
                    id: 'aabbccdd-eeee-ffff-1111-100000000001',
                    source: 'START',
                    state: 'ENQUEUED',
                    target: 'HBW',
                    type: 'NAVIGATION',
                },
                {
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000002',
                    id: 'aabbccdd-eeee-ffff-1111-100000000003',
                    source: 'HBW',
                    state: 'ENQUEUED',
                    target: 'DRILL',
                    type: 'NAVIGATION',
                },
                {
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000006',
                    id: 'aabbccdd-eeee-ffff-1111-100000000007',
                    source: 'DRILL',
                    state: 'ENQUEUED',
                    target: 'AIQS',
                    type: 'NAVIGATION',
                },
                {
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000010',
                    id: 'aabbccdd-eeee-ffff-1111-100000000011',
                    source: 'AIQS',
                    state: 'ENQUEUED',
                    target: 'DPS',
                    type: 'NAVIGATION',
                },
            ],
            productionSteps: [
                {
                    command: 'DROP',
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000001',
                    id: 'aabbccdd-eeee-ffff-1111-100000000002',
                    moduleType: 'HBW',
                    state: 'ENQUEUED',
                    type: 'MANUFACTURE',
                },
                {
                    command: 'PICK',
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000003',
                    id: 'aabbccdd-eeee-ffff-1111-100000000004',
                    moduleType: 'DRILL',
                    state: 'ENQUEUED',
                    type: 'MANUFACTURE',
                },
                {
                    command: 'DRILL',
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000004',
                    id: 'aabbccdd-eeee-ffff-1111-100000000005',
                    moduleType: 'DRILL',
                    state: 'ENQUEUED',
                    type: 'MANUFACTURE',
                },
                {
                    command: 'DROP',
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000005',
                    id: 'aabbccdd-eeee-ffff-1111-100000000006',
                    moduleType: 'DRILL',
                    state: 'ENQUEUED',
                    type: 'MANUFACTURE',
                },
                {
                    command: 'PICK',
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000007',
                    id: 'aabbccdd-eeee-ffff-1111-100000000008',
                    moduleType: 'AIQS',
                    state: 'ENQUEUED',
                    type: 'MANUFACTURE',
                },
                {
                    command: 'CHECK_QUALITY',
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000008',
                    id: 'aabbccdd-eeee-ffff-1111-100000000009',
                    moduleType: 'AIQS',
                    state: 'ENQUEUED',
                    type: 'MANUFACTURE',
                },
                {
                    command: 'DROP',
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000009',
                    id: 'aabbccdd-eeee-ffff-1111-100000000010',
                    moduleType: 'AIQS',
                    state: 'ENQUEUED',
                    type: 'MANUFACTURE',
                },
                {
                    command: 'PICK',
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000011',
                    id: 'aabbccdd-eeee-ffff-1111-100000000012',
                    moduleType: 'DPS',
                    state: 'ENQUEUED',
                    type: 'MANUFACTURE',
                },
            ],
        };
        const definition = order_flow_service_1.OrderFlowService.convertFlowToDefinition(flow);
        expect(definition).toEqual(expectedDefinition);
    });
    it('should create a valid storage order definition', () => {
        const expectedStorageOrder = {
            navigationSteps: [
                {
                    id: 'aabbccdd-eeee-ffff-1111-100000000001',
                    source: module_1.ModuleType.START,
                    state: ccu_1.OrderState.ENQUEUED,
                    target: module_1.ModuleType.DPS,
                    type: 'NAVIGATION',
                },
                {
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000002',
                    id: 'aabbccdd-eeee-ffff-1111-100000000003',
                    source: module_1.ModuleType.DPS,
                    state: ccu_1.OrderState.ENQUEUED,
                    target: module_1.ModuleType.HBW,
                    type: 'NAVIGATION',
                },
            ],
            productionSteps: [
                {
                    command: module_1.ModuleCommandType.DROP,
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000001',
                    id: 'aabbccdd-eeee-ffff-1111-100000000002',
                    moduleType: module_1.ModuleType.DPS,
                    state: ccu_1.OrderState.ENQUEUED,
                    type: 'MANUFACTURE',
                },
                {
                    command: module_1.ModuleCommandType.PICK,
                    dependentActionId: 'aabbccdd-eeee-ffff-1111-100000000003',
                    id: 'aabbccdd-eeee-ffff-1111-100000000004',
                    moduleType: module_1.ModuleType.HBW,
                    state: ccu_1.OrderState.ENQUEUED,
                    type: 'MANUFACTURE',
                },
            ],
        };
        const definition = order_flow_service_1.OrderFlowService.getStorageProductionDefinition();
        expect(definition).toEqual(expectedStorageOrder);
    });
    it('should use the dependentActionId for the first navigation action if given', () => {
        const flow = { steps: [module_1.ModuleType.DRILL, module_1.ModuleType.AIQS] };
        const dependentActionId = '123456-1234-1234-1234-1234678';
        const definition = order_flow_service_1.OrderFlowService.convertFlowToDefinition(flow, dependentActionId);
        expect(definition).toHaveProperty('navigationSteps[0].dependentActionId', dependentActionId);
    });
    it('should reload a changed file', async () => {
        const flows = {
            RED: { steps: [module_1.ModuleType.AIQS] },
            WHITE: { steps: [module_1.ModuleType.DRILL] },
            BLUE: { steps: [module_1.ModuleType.DRILL, module_1.ModuleType.MILL] },
        };
        jest.spyOn(helpers_spies, 'readJsonFile').mockResolvedValue({});
        await order_flow_service_1.OrderFlowService.initialize('/foo/test.json');
        expect(order_flow_service_1.OrderFlowService.getFlows()).toEqual(order_flow_service_1.OrderFlowService.getDefaultFlows());
        jest.spyOn(helpers_spies, 'readJsonFile').mockResolvedValue(flows);
        await order_flow_service_1.OrderFlowService.reloadFlows();
        expect(helpers_spies.readJsonFile).toHaveBeenCalledWith('/foo/test.json');
        expect(order_flow_service_1.OrderFlowService.getFlows()).toEqual(flows);
    });
    it('should allow setting the flows', () => {
        const flows = {
            RED: { steps: [module_1.ModuleType.AIQS] },
            WHITE: { steps: [module_1.ModuleType.DRILL] },
            BLUE: { steps: [module_1.ModuleType.DRILL, module_1.ModuleType.MILL] },
        };
        expect(order_flow_service_1.OrderFlowService.getFlows()).toEqual({});
        order_flow_service_1.OrderFlowService.setFlows(flows);
        expect(order_flow_service_1.OrderFlowService.getFlows()).toEqual(flows);
    });
    it('should save the current flows', async () => {
        const flows = {
            RED: { steps: [module_1.ModuleType.AIQS] },
            WHITE: { steps: [module_1.ModuleType.DRILL] },
            BLUE: { steps: [module_1.ModuleType.DRILL, module_1.ModuleType.MILL] },
        };
        jest.spyOn(helpers_spies, 'writeJsonFile').mockResolvedValue();
        await order_flow_service_1.OrderFlowService.initialize('/foo/test.json');
        order_flow_service_1.OrderFlowService.setFlows(flows);
        await order_flow_service_1.OrderFlowService.saveFlows();
        expect(helpers_spies.writeJsonFile).toHaveBeenCalledWith('/foo/test.json', flows);
    });
});
