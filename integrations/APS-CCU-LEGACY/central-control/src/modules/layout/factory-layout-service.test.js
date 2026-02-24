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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const promises_1 = __importDefault(require("node:fs/promises"));
const path_1 = __importDefault(require("path"));
const ccu_1 = require("../../../../common/protocol/ccu");
const module_1 = require("../../../../common/protocol/module");
const config_1 = __importDefault(require("../../config"));
const mqtt_spies = __importStar(require("../../mqtt/mqtt"));
const static_office_factory_data_1 = require("../fts/navigation/mockData/static-office-factory-data");
const pairing_states_1 = require("../pairing/pairing-states");
const factory_layout_service_1 = require("./factory-layout-service");
const default_layout_1 = require("./default_reset/default_layout");
const testLayout = {
    intersections: [{ id: '2' }],
    modules: [{ type: module_1.ModuleType.DRILL, serialNumber: 'xyzZ' }],
    roads: [{ direction: ccu_1.RoadDirection.SOUTH, length: 100, to: '2', from: 'xyzZ' }],
};
const testGraph = {
    edges: [
        {
            direction: 'SOUTH',
            from: {
                id: 'xyzZ',
                module: {
                    serialNumber: 'xyzZ',
                    type: 'DRILL',
                },
            },
            length: 100,
            to: {
                id: '2',
            },
        },
        {
            direction: 'NORTH',
            from: {
                id: '2',
            },
            length: 100,
            to: {
                id: 'xyzZ',
                module: {
                    serialNumber: 'xyzZ',
                    type: 'DRILL',
                },
            },
        },
    ],
    nodes: [
        {
            id: 'xyzZ',
            module: {
                serialNumber: 'xyzZ',
                type: 'DRILL',
            },
        },
        {
            id: '2',
        },
    ],
};
describe('Test FactoryLayoutService', () => {
    beforeEach(() => {
        jest.spyOn(mqtt_spies, 'getMqttClient').mockReturnValue({
            publish: () => Promise.resolve(),
        });
    });
    afterEach(() => {
        factory_layout_service_1.FactoryLayoutService.destroy();
        pairing_states_1.PairingStates.getInstance().reset();
        jest.clearAllMocks();
    });
    it('should generate the correct graph for the office factory', () => {
        const officeFactoryGraph = factory_layout_service_1.FactoryLayoutService.generateGraph(static_office_factory_data_1.office_modules, static_office_factory_data_1.office_intersections, static_office_factory_data_1.office_edges);
        expect(officeFactoryGraph).toBeDefined();
        expect(officeFactoryGraph.nodes).toBeDefined();
        expect(officeFactoryGraph.edges).toBeDefined();
        expect(officeFactoryGraph.nodes.length).toBe(11); // 6 modules + 5 intersections
        expect(officeFactoryGraph.edges.length).toBe(22); // 11 edges times 2 (bidirectional)
        console.log('OFFICE GRAPH', JSON.stringify(officeFactoryGraph));
        console.log('EXPECTED OFFICE GRAPH', JSON.stringify(static_office_factory_data_1.EXPECTED_OFFICE_GRAPH));
        expect(officeFactoryGraph).toEqual(static_office_factory_data_1.EXPECTED_OFFICE_GRAPH);
    });
    it('should load and generate the office factory graph from a file', async () => {
        const factoryLayout = await factory_layout_service_1.FactoryLayoutService.loadLayoutFromJsonFile(path_1.default.join(config_1.default.storage.path, config_1.default.storage.layoutFile));
        expect(factoryLayout).not.toBeNull();
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const officeFactoryGraph = factory_layout_service_1.FactoryLayoutService.generateGraphFromJsonLayout(factoryLayout);
        expect(officeFactoryGraph).toBeDefined();
        expect(officeFactoryGraph.nodes).toBeDefined();
        expect(officeFactoryGraph.edges).toBeDefined();
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const numOfModules = factoryLayout.modules.length;
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const numOfIntersections = factoryLayout.intersections.length;
        const numberOfNodes = numOfModules + numOfIntersections;
        const numberOfEdges = numberOfNodes * 2; // bidirectional
        expect(officeFactoryGraph.nodes.length).toBe(numberOfNodes);
        expect(officeFactoryGraph.edges.length).toBe(numberOfEdges);
        console.log('OFFICE GRAPH', JSON.stringify(officeFactoryGraph, null, 2));
        // FIXME: this test fails because the office factory layout is not configured for the existing test setup
        // expect(officeFactoryGraph).toEqual(EXPECTED_OFFICE_GRAPH);
    });
    it('should set layout and graph correctly', () => {
        const layout = JSON.parse(JSON.stringify(testLayout));
        const expectedGraph = JSON.parse(JSON.stringify(testGraph));
        factory_layout_service_1.FactoryLayoutService.setLayout(layout);
        expect(factory_layout_service_1.FactoryLayoutService.graph).toEqual(expectedGraph);
        // no-explicit-any is needed here as layout is a private property
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        expect(factory_layout_service_1.FactoryLayoutService.layout).toEqual(testLayout);
    });
    it('should publish the layout correctly when an mqtt client exists', async () => {
        const layout = JSON.parse(JSON.stringify(testLayout));
        factory_layout_service_1.FactoryLayoutService.setLayout(layout);
        const publishSpy = jest.fn().mockImplementation(() => Promise.resolve());
        jest.spyOn(mqtt_spies, 'getMqttClient').mockReturnValue({
            publish: publishSpy,
        });
        await factory_layout_service_1.FactoryLayoutService.publishLayout();
        expect(publishSpy).toHaveBeenLastCalledWith('ccu/state/layout', JSON.stringify(testLayout), { qos: 1, retain: true });
    });
    it('should initialize the graph with a file', async () => {
        const layoutJson = JSON.stringify(testLayout);
        jest.spyOn(promises_1.default, 'readFile').mockResolvedValue(layoutJson);
        await factory_layout_service_1.FactoryLayoutService.initialize('/foo/test.json');
        expect(promises_1.default.readFile).toHaveBeenCalledWith('/foo/test.json', expect.any(Object));
        expect(factory_layout_service_1.FactoryLayoutService.graph).toEqual(testGraph);
    });
    it('should reload a new file', async () => {
        const layoutJson = JSON.stringify(testLayout);
        jest.spyOn(promises_1.default, 'readFile').mockResolvedValue('{}');
        await factory_layout_service_1.FactoryLayoutService.initialize('/foo/test.json');
        expect(factory_layout_service_1.FactoryLayoutService.graph).toEqual(factory_layout_service_1.FactoryLayoutService.generateGraphFromJsonLayout(default_layout_1.DEFAULT_LAYOUT));
        jest.spyOn(promises_1.default, 'readFile').mockResolvedValue(layoutJson);
        await factory_layout_service_1.FactoryLayoutService.reloadLayout();
        expect(promises_1.default.readFile).toHaveBeenCalledWith('/foo/test.json', expect.any(Object));
        expect(factory_layout_service_1.FactoryLayoutService.graph).toEqual(testGraph);
    });
    it('should save a layout', async () => {
        jest.spyOn(promises_1.default, 'readFile').mockResolvedValue('{}');
        jest.spyOn(promises_1.default, 'writeFile').mockResolvedValue();
        await factory_layout_service_1.FactoryLayoutService.initialize('/foo/test.json');
        expect(factory_layout_service_1.FactoryLayoutService.graph).toEqual(factory_layout_service_1.FactoryLayoutService.generateGraphFromJsonLayout(default_layout_1.DEFAULT_LAYOUT));
        factory_layout_service_1.FactoryLayoutService.setLayout(testLayout);
        expect(factory_layout_service_1.FactoryLayoutService.graph).toEqual(testGraph);
        await factory_layout_service_1.FactoryLayoutService.saveLayout();
        expect(promises_1.default.writeFile).toHaveBeenCalledWith('/foo/test.json', JSON.stringify(testLayout, undefined, 2), expect.any(Object));
    });
    it('should block a node', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeId = '12';
        const blocker = {
            nodeId,
            ftsSerialNumber: 'any',
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker]);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeId]));
    });
    it('should return nodes that are blocked by a different FTS', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeId = '12';
        const nodeId2 = '2';
        const nodeId3 = '3';
        const ftsSerialNumber = 'FTS-1';
        const blocker = {
            nodeId,
            ftsSerialNumber,
        };
        const blocker2 = {
            nodeId: nodeId2,
            ftsSerialNumber: 'another',
        };
        const blocker3 = {
            nodeId: nodeId3,
            ftsSerialNumber: 'any',
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker, blocker2, blocker3]);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId, ftsSerialNumber)).toBe(false);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2, ftsSerialNumber)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2, ftsSerialNumber)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeId, nodeId2, nodeId3]));
        expect(factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds(ftsSerialNumber)).toEqual(new Set([nodeId2, nodeId3]));
    });
    it('should fail if a node has a preceding node that is missing', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeId = '12';
        const blocker = {
            nodeId,
            ftsSerialNumber: 'any',
            afterNodeId: '2',
        };
        try {
            factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker]);
        }
        catch (e) {
            expect(e).toEqual(Error('Node points to missing preceding node'));
        }
        expect.assertions(1);
    });
    it('should fail if a node is blocked by a different fts', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeId = '12';
        const blocker = {
            nodeId,
            ftsSerialNumber: 'any',
        };
        const blocker2 = {
            nodeId,
            ftsSerialNumber: 'another',
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker]);
        try {
            factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker2]);
        }
        catch (e) {
            expect(e).toEqual(Error('Node already blocked by another FTS'));
        }
        expect.assertions(1);
    });
    it('should block a node sequence', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeId = '12';
        const nodeId2 = '2';
        const blocker = {
            nodeId,
            ftsSerialNumber: 'any',
        };
        const blocker2 = {
            nodeId: nodeId2,
            ftsSerialNumber: 'any',
            afterNodeId: nodeId,
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker, blocker2]);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeId, nodeId2]));
    });
    it('should fail if an already blocked node refers to a different preceding node', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeId = '12';
        const nodeId2 = '2';
        const nodeId3 = '3';
        const blocker = {
            nodeId,
            ftsSerialNumber: 'any',
        };
        const blocker2 = {
            nodeId: nodeId2,
            ftsSerialNumber: 'any',
            afterNodeId: nodeId,
        };
        const blocker3 = {
            nodeId: nodeId3,
            ftsSerialNumber: 'any',
        };
        const blocker2B = {
            nodeId: nodeId2,
            ftsSerialNumber: 'any',
            afterNodeId: nodeId3,
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker, blocker2]);
        try {
            factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker3, blocker2B]);
        }
        catch (e) {
            expect(e).toEqual(Error('Node blocked with a different preceding node'));
        }
        expect.assertions(1);
    });
    it('should release a node', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeId = '12';
        const nodeId2 = '2';
        const ftsSerial = 'fts';
        const blocker = {
            nodeId,
            ftsSerialNumber: ftsSerial,
        };
        const blocker2 = {
            nodeId: nodeId2,
            ftsSerialNumber: ftsSerial,
            afterNodeId: nodeId,
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blocker, blocker2]);
        factory_layout_service_1.FactoryLayoutService.releaseNodesBefore(ftsSerial, nodeId2);
        expect(factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeId2]));
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId)).toBe(false);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
    });
    it('should not release nodes ordered after the given node or unrelated nodes', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeIdX = '6';
        const nodeId = '12';
        const nodeId2 = '2';
        const ftsSerial = 'fts';
        const blockerX = {
            nodeId: nodeIdX,
            ftsSerialNumber: ftsSerial,
        };
        const blocker = {
            nodeId,
            ftsSerialNumber: ftsSerial,
        };
        const blocker2 = {
            nodeId: nodeId2,
            ftsSerialNumber: ftsSerial,
            afterNodeId: nodeId,
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blockerX, blocker, blocker2]);
        factory_layout_service_1.FactoryLayoutService.releaseNodesBefore(ftsSerial, nodeId2);
        expect(factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeIdX, nodeId2]));
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeIdX)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId)).toBe(false);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
    });
    it('should release all nodes for an fts', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeIdX = '6';
        const nodeId = '12';
        const nodeId2 = '2';
        const ftsSerial = 'fts';
        const blockerX = {
            nodeId: nodeIdX,
            ftsSerialNumber: 'someId',
        };
        const blocker = {
            nodeId,
            ftsSerialNumber: ftsSerial,
        };
        const blocker2 = {
            nodeId: nodeId2,
            ftsSerialNumber: ftsSerial,
            afterNodeId: nodeId,
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blockerX, blocker, blocker2]);
        factory_layout_service_1.FactoryLayoutService.releaseAllNodes(ftsSerial);
        expect(factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeIdX]));
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId)).toBe(false);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(false);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeIdX)).toBe(true);
    });
    it('should not release nodes not belonging to the fts', async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
        const nodeIdX = '6';
        const nodeId = '12';
        const nodeId2 = '2';
        const ftsSerial = 'fts';
        const blockerX = {
            nodeId: nodeIdX,
            ftsSerialNumber: 'someId',
        };
        const blocker = {
            nodeId,
            ftsSerialNumber: 'someId2',
        };
        const blocker2 = {
            nodeId: nodeId2,
            ftsSerialNumber: 'someId2',
            afterNodeId: nodeId,
        };
        factory_layout_service_1.FactoryLayoutService.blockNodeSequence([blockerX, blocker, blocker2]);
        factory_layout_service_1.FactoryLayoutService.releaseAllNodes(ftsSerial);
        expect(factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeIdX, nodeId, nodeId2]));
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
        expect(factory_layout_service_1.FactoryLayoutService.isNodeBlocked(nodeIdX)).toBe(true);
    });
});
