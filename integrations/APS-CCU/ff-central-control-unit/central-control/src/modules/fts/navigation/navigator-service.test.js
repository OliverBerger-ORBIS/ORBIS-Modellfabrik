"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/* eslint-disable prettier/prettier */
const factory_layout_service_1 = require("../../layout/factory-layout-service");
const static_office_factory_data_1 = require("./mockData/static-office-factory-data");
const navigator_service_1 = require("./navigator-service");
const graph_test_data_1 = require("./mockData/graph-test-data");
const fts_1 = require("../../../../../common/protocol/fts");
describe('TestNavigator', () => {
    beforeEach(async () => {
        await factory_layout_service_1.FactoryLayoutService.initialize();
    });
    afterEach(() => {
        factory_layout_service_1.FactoryLayoutService.destroy();
    });
    it('should setup a graph properly with the provided modules and edges input', () => {
        // This test assumes a fixed ordering of test modules -> if you re-sort them, this will fail
        const factoryGraph = factory_layout_service_1.FactoryLayoutService.generateGraph(graph_test_data_1.modules, graph_test_data_1.intersections, graph_test_data_1.edges);
        expect(factoryGraph).toBeDefined();
        expect(factoryGraph.nodes).toBeDefined();
        expect(factoryGraph.edges).toBeDefined();
        expect(factoryGraph.nodes.length).toBe(graph_test_data_1.EXPEXTED_NODE_NUMBER);
        expect(factoryGraph.edges.length).toBe(graph_test_data_1.EXPEXTED_EDGE_NUMBER);
        expect(factoryGraph).toEqual(graph_test_data_1.EXPECTED_GRAPH);
    });
    it('should build the adjacent matrix correctly ', () => {
        // This test assumes a fixed ordering of test modules -> if you re-sort them, this will fail
        const factoryGraph = factory_layout_service_1.FactoryLayoutService.generateGraph(graph_test_data_1.modules, graph_test_data_1.intersections, graph_test_data_1.edges);
        const adjacencyMatrix = navigator_service_1.NavigatorService.buildAdjacencyMatrix(factoryGraph);
        expect(adjacencyMatrix).toBeDefined();
        expect(adjacencyMatrix.length).toBe(graph_test_data_1.EXPEXTED_NODE_NUMBER);
        expect(adjacencyMatrix).toEqual(graph_test_data_1.EXPECTED_ADJACENCY_MATRIX);
    });
    it('should build the adjacent matrix correctly with a blocked node', () => {
        // This test assumes a fixed ordering of test modules -> if you re-sort them, this will fail
        const factoryGraph = factory_layout_service_1.FactoryLayoutService.generateGraph(graph_test_data_1.modules, graph_test_data_1.intersections, graph_test_data_1.edges);
        const adjacencyMatrix = navigator_service_1.NavigatorService.buildAdjacencyMatrix(factoryGraph, graph_test_data_1.BLOCKED_NODES);
        expect(adjacencyMatrix).toBeDefined();
        expect(adjacencyMatrix.length).toBe(graph_test_data_1.EXPEXTED_NODE_NUMBER);
        expect(adjacencyMatrix).toEqual(graph_test_data_1.EXPECTED_BLOCKED_ADJACENCY_MATRIX);
    });
    it('should calculate the shortest path between two nodes', () => {
        // This test assumes a fixed ordering of test modules -> if you re-sort them, this will fail
        const factoryGraph = factory_layout_service_1.FactoryLayoutService.generateGraph(graph_test_data_1.modules, graph_test_data_1.intersections, graph_test_data_1.edges);
        const adjacencyMatrix = navigator_service_1.NavigatorService.buildAdjacencyMatrix(factoryGraph);
        const shortestPath = navigator_service_1.NavigatorService.findShortestPath(adjacencyMatrix, 0, 4);
        expect(shortestPath).toBeDefined();
        // Sum of the lengths of the edges that are expected to be used.
        expect(shortestPath?.distance).toBe(320 + 320 + 300 + 400);
        const nodeIds = shortestPath?.path;
        expect(nodeIds).toBeDefined();
        expect(nodeIds).toEqual([0, 5, 8, 7, 4]);
    });
    it('should calculate the shortest path between two nodes with a blocked node', () => {
        // This test assumes a fixed ordering of test modules -> if you re-sort them, this will fail
        const factoryGraph = factory_layout_service_1.FactoryLayoutService.generateGraph(graph_test_data_1.modules, graph_test_data_1.intersections, graph_test_data_1.edges);
        const adjacencyMatrix = navigator_service_1.NavigatorService.buildAdjacencyMatrix(factoryGraph, graph_test_data_1.BLOCKED_NODES);
        const shortestPath = navigator_service_1.NavigatorService.findShortestPath(adjacencyMatrix, 0, 4);
        expect(shortestPath).toBeDefined();
        // Sum of the lengths of the edges that are expected to be used.
        expect(shortestPath?.distance).toBe(320 + 320 + 400 + 400);
        const nodeIds = shortestPath?.path;
        expect(nodeIds).toBeDefined();
        expect(nodeIds).toEqual([0, 5, 6, 7, 4]);
    });
    it('should return no path between two nodes when all connections are blocked', () => {
        // This test assumes a fixed ordering of test modules -> if you re-sort them, this will fail
        const factoryGraph = factory_layout_service_1.FactoryLayoutService.generateGraph(graph_test_data_1.modules, graph_test_data_1.intersections, graph_test_data_1.edges);
        const adjacencyMatrix = navigator_service_1.NavigatorService.buildAdjacencyMatrix(factoryGraph, graph_test_data_1.BLOCKED_NODES_NO_PATH);
        const shortestPath = navigator_service_1.NavigatorService.findShortestPath(adjacencyMatrix, 0, 4);
        expect(shortestPath).toBeNull();
    });
    it('should generate the FTS Order with no turn before docking', () => {
        // Test specific setup, since we need the factoryLayoutService in a specific state
        factory_layout_service_1.FactoryLayoutService.graph = factory_layout_service_1.FactoryLayoutService.generateGraph(graph_test_data_1.modules, graph_test_data_1.intersections, graph_test_data_1.edges);
        // This test assumes a fixed ordering of test modules -> if you re-sort them, this will fail
        const actionId = 'Test-Action';
        const serialNumber = 'FTS-1';
        const orderUpdateId = 4;
        const orderId = 'testOrderId';
        const ftsOrder = navigator_service_1.NavigatorService.getFTSOrder('HBW-1', 'DRILL-1', orderId, orderUpdateId, serialNumber, actionId);
        expect(ftsOrder).toBeDefined();
        expect(ftsOrder.orderId).toBe(orderId);
        expect(ftsOrder.orderUpdateId).toBe(orderUpdateId);
        expect(ftsOrder.serialNumber).toBe(serialNumber);
        const orderNodes = ftsOrder.nodes;
        expect(orderNodes).toBeDefined();
        expect(orderNodes.length).toBe(4);
        const startNode = orderNodes[0];
        expect(startNode.id).toBe('HBW-1');
        expect(startNode.action?.type).toBeUndefined();
        const firstNode = orderNodes[1];
        expect(firstNode.id).toBe('2');
        expect(firstNode.action?.type).toBe(fts_1.FtsCommandType.PASS);
        const secondNode = orderNodes[2];
        expect(secondNode.id).toBe('3');
        expect(secondNode.action?.type).toBe(fts_1.FtsCommandType.PASS);
        const thirdNode = orderNodes[3];
        expect(thirdNode.id).toBe('DRILL-1');
        expect(thirdNode.action?.type).toBe(fts_1.FtsCommandType.DOCK);
        expect(ftsOrder.edges).toBeDefined();
        const lastNodeAction = orderNodes[orderNodes.length - 1].action;
        expect(lastNodeAction).toBeDefined();
        expect(ftsOrder.edges.length).toBe(3);
        expect(lastNodeAction?.type).toBe(fts_1.FtsCommandType.DOCK);
        expect(lastNodeAction?.id).toBe(actionId);
    });
    it('should generate the FTS Order', () => {
        // Test specific setup, since we need the factoryLayoutService in a specific state
        factory_layout_service_1.FactoryLayoutService.graph = factory_layout_service_1.FactoryLayoutService.generateGraph(graph_test_data_1.modules, graph_test_data_1.intersections, graph_test_data_1.edges);
        // This test assumes a fixed ordering of test modules -> if you re-sort them, this will fail
        const actionId = 'Test-Action';
        const serialNumber = 'FTS-1';
        const orderUpdateId = 4;
        const orderId = 'testOrderId';
        const ftsOrder = navigator_service_1.NavigatorService.getFTSOrder('DPS-1', 'DRILL-1', orderId, orderUpdateId, serialNumber, actionId);
        expect(ftsOrder).toBeDefined();
        expect(ftsOrder.orderId).toBe(orderId);
        expect(ftsOrder.orderUpdateId).toBe(orderUpdateId);
        expect(ftsOrder.serialNumber).toBe(serialNumber);
        const orderNodes = ftsOrder.nodes;
        expect(orderNodes).toBeDefined();
        expect(orderNodes.length).toBe(5);
        const startNode = orderNodes[0];
        expect(startNode.id).toBe('DPS-1');
        expect(startNode.action?.type).toBeUndefined();
        const firstNode = orderNodes[1];
        expect(firstNode.id).toBe('1');
        expect(firstNode.action?.type).toBe(fts_1.FtsCommandType.PASS);
        const secondNode = orderNodes[2];
        expect(secondNode.id).toBe('4');
        expect(secondNode.action?.type).toBe(fts_1.FtsCommandType.TURN);
        const thirdNode = orderNodes[3];
        expect(thirdNode.id).toBe('3');
        expect(thirdNode.action?.type).toBe(fts_1.FtsCommandType.TURN);
        const fourthNode = orderNodes[4];
        expect(fourthNode.id).toBe('DRILL-1');
        expect(fourthNode.action?.type).toBe(fts_1.FtsCommandType.DOCK);
        expect(ftsOrder.edges).toBeDefined();
        const lastNodeAction = orderNodes[orderNodes.length - 1].action;
        expect(lastNodeAction).toBeDefined();
        expect(ftsOrder.edges.length).toBe(4);
        expect(lastNodeAction?.type).toBe(fts_1.FtsCommandType.DOCK);
        expect(lastNodeAction?.id).toBe(actionId);
    });
    it('should find the path from DPS to MILL and convert it to an FTS order', () => {
        // Test specific setup, since we need the factoryLayoutService in a specific state
        factory_layout_service_1.FactoryLayoutService.graph = factory_layout_service_1.FactoryLayoutService.generateGraph(static_office_factory_data_1.office_modules, static_office_factory_data_1.office_intersections, static_office_factory_data_1.office_edges);
        const actionId = 'Test-Action';
        const serialNumber = 'FTS-1';
        const orderUpdateId = 4;
        const orderId = 'testOrderId';
        const ftsOrder = navigator_service_1.NavigatorService.getFTSOrder(static_office_factory_data_1.office_modules[0].serialNumber, static_office_factory_data_1.office_modules[3].serialNumber, orderId, orderUpdateId, serialNumber, actionId);
        console.log('FTS ORDER', JSON.stringify(ftsOrder, null, 2));
        expect(ftsOrder).toBeDefined();
        expect(ftsOrder.orderId).toBe(orderId);
        expect(ftsOrder.orderUpdateId).toBe(orderUpdateId);
        expect(ftsOrder.serialNumber).toBe(serialNumber);
        expect(ftsOrder.nodes).toBeDefined();
        expect(ftsOrder.nodes.length).toBe(6);
        expect(ftsOrder.edges).toBeDefined();
        expect(ftsOrder.edges.length).toBe(5);
        const expectedNodes = static_office_factory_data_1.EXPECTED_ROUTE_DPS_MILL.nodes;
        expect(ftsOrder.nodes[0].action?.type).toBe(expectedNodes[0].action?.type);
        expect(ftsOrder.nodes[0].id).toBe(expectedNodes[0].id);
        expect(ftsOrder.nodes[1].action?.type).toBe(expectedNodes[1].action?.type);
        expect(ftsOrder.nodes[1].action?.metadata?.direction).toBe(expectedNodes[1].action?.metadata?.direction);
        expect(ftsOrder.nodes[2].action?.type).toBe(expectedNodes[2].action?.type);
        expect(ftsOrder.nodes[2].action?.metadata?.direction).toBe(expectedNodes[2].action?.metadata?.direction);
        expect(ftsOrder.nodes[3].action?.type).toBe(expectedNodes[3].action?.type);
        const orderNodes = ftsOrder.nodes;
        const lastNodeAction = orderNodes[orderNodes.length - 1].action;
        expect(lastNodeAction).toBeDefined();
        expect(lastNodeAction?.type).toBe(fts_1.FtsCommandType.DOCK);
        expect(lastNodeAction?.id).toBe(actionId);
    });
    it('should find the path from DPS to HBW and convert it to an FTS order', () => {
        // Test specific setup, since we need the factoryLayoutService in a specific state
        factory_layout_service_1.FactoryLayoutService.graph = factory_layout_service_1.FactoryLayoutService.generateGraph(static_office_factory_data_1.office_modules, static_office_factory_data_1.office_intersections, static_office_factory_data_1.office_edges);
        const actionId = 'Test-Action';
        const serialNumber = 'FTS-1';
        const orderUpdateId = 4;
        const orderId = 'testOrderId';
        const ftsOrder = navigator_service_1.NavigatorService.getFTSOrder(static_office_factory_data_1.office_modules[0].serialNumber, static_office_factory_data_1.office_modules[1].serialNumber, orderId, orderUpdateId, serialNumber, actionId);
        console.log('FTS ORDER', JSON.stringify(ftsOrder, null, 2));
        expect(ftsOrder).toBeDefined();
        expect(ftsOrder.orderId).toBe(orderId);
        expect(ftsOrder.orderUpdateId).toBe(orderUpdateId);
        expect(ftsOrder.serialNumber).toBe(serialNumber);
        expect(ftsOrder.nodes).toBeDefined();
        expect(ftsOrder.nodes.length).toBe(4);
        expect(ftsOrder.edges).toBeDefined();
        expect(ftsOrder.edges.length).toBe(3);
        const orderNodes = ftsOrder.nodes;
        // we turn and dock on the same node
        const lastTurnNode = orderNodes[orderNodes.length - 2].action;
        const lastNodeAction = orderNodes[orderNodes.length - 1].action;
        expect(lastNodeAction).toBeDefined();
        expect(lastTurnNode).toBeDefined();
        expect(lastTurnNode?.type).toBe(fts_1.FtsCommandType.TURN);
        expect(lastNodeAction?.type).toBe(fts_1.FtsCommandType.DOCK);
        expect(lastTurnNode?.id).not.toBe(lastNodeAction?.id); // random id vs. action id
        // different node since we changed navigation nodes in FITEFF22-499
        expect(orderNodes[orderNodes.length - 2].id).not.toBe(orderNodes[orderNodes.length - 1].id);
        expect(lastNodeAction?.id).toBe(actionId);
    });
    it('should find the zero-length path for identical start and target', () => {
        const moduleIndex = 0;
        factory_layout_service_1.FactoryLayoutService.graph = factory_layout_service_1.FactoryLayoutService.generateGraph(static_office_factory_data_1.office_modules, static_office_factory_data_1.office_intersections, static_office_factory_data_1.office_edges);
        const path = navigator_service_1.NavigatorService.getFTSPath(static_office_factory_data_1.office_modules[moduleIndex].serialNumber, static_office_factory_data_1.office_modules[moduleIndex].serialNumber, 'ftsSerial');
        expect(path).toEqual({
            path: [moduleIndex],
            distance: 0,
        });
    });
    it('should find the path from DPS to HBW', () => {
        // Test specific setup, since we need the factoryLayoutService in a specific state
        factory_layout_service_1.FactoryLayoutService.graph = factory_layout_service_1.FactoryLayoutService.generateGraph(static_office_factory_data_1.office_modules, static_office_factory_data_1.office_intersections, static_office_factory_data_1.office_edges);
        const serialNumber = 'FTS-1';
        const ftsPath = navigator_service_1.NavigatorService.getFTSPath(static_office_factory_data_1.office_modules[0].serialNumber, static_office_factory_data_1.office_modules[1].serialNumber, serialNumber);
        expect(ftsPath).toBeDefined();
        if (!ftsPath) {
            return;
        }
        expect(ftsPath.path[0]).toEqual(0); // source is module at index 0
        expect(ftsPath.path[ftsPath.path.length - 1]).toEqual(1); // target is module at index 1
        expect(ftsPath.distance).toEqual(1040); // sum of all edge lengths used in the path
    });
});
