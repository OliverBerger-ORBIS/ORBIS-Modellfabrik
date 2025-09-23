"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.NavigatorService = void 0;
const node_crypto_1 = require("node:crypto");
const ccu_1 = require("../../../../../common/protocol/ccu");
const fts_1 = require("../../../../../common/protocol/fts");
const config_1 = __importDefault(require("../../../config"));
const factory_layout_service_1 = require("../../layout/factory-layout-service");
const model_1 = require("../model");
/**
 * Responsible for calculating the shortest path between two nodes in the factory layout graph
 * and converting said path into a FTS order that can be directly published to the mqtt broker.
 */
class NavigatorService {
    /**
     * Calculates the shortest path between two nodes in the factory layout graph.
     * Then converts this path to a data structure that can be directly executed by the FTS
     *
     * The provided orderId, orderUpdateId and serialNumber are used to reference a specific order for
     * which this FTS order is generated.
     *
     * @param startNodeId
     * @param targetNodeId
     * @param serialNumber
     */
    static getFTSPath(startNodeId, targetNodeId, serialNumber) {
        /*
         * TODO: We might need to performance optimize this method at some point
         * For each request to the method, the graph configuration is parsed and
         * the adjacency matrix is calculated. There is no caching implemented yet.
         */
        const graph = factory_layout_service_1.FactoryLayoutService.graph;
        const start = graph.nodes.findIndex(node => node.id === startNodeId);
        const target = graph.nodes.findIndex(node => node.id === targetNodeId);
        if (start < 0 || target < 0) {
            return null;
        }
        if (start === target) {
            return {
                path: [start],
                distance: 0,
            };
        }
        let blocked = new Set();
        if (config_1.default.routing.disableNodeBlocking) {
            console.warn('Node blocking disabled by config. This may lead to a crash if multiple FTS are driving on the layout');
        }
        else {
            console.debug('Getting blocked nodes for fts ID: ', serialNumber);
            blocked = factory_layout_service_1.FactoryLayoutService.getBlockedNodeIds(serialNumber);
        }
        console.debug('BLOCKED nodes:', blocked);
        const adjacencyMatrix = NavigatorService.buildAdjacencyMatrix(graph, blocked);
        console.debug('MATRIX', adjacencyMatrix);
        return NavigatorService.findShortestPath(adjacencyMatrix, start, target);
    }
    /**
     * Calculates the shortest path between two nodes in the factory layout graph.
     * Then converts this path to a data structure that can be directly executed by the FTS
     *
     * The provided orderId, orderUpdateId and serialNumber are used to reference a specific order for
     * which this FTS order is generated.
     *
     * @param startNodeId
     * @param targetNodeId
     * @param orderId
     * @param orderUpdateId
     * @param serialNumber
     * @param actionId
     */
    static getFTSOrder(startNodeId, targetNodeId, orderId, orderUpdateId, serialNumber, actionId) {
        const graph = factory_layout_service_1.FactoryLayoutService.graph;
        const path = NavigatorService.getFTSPath(startNodeId, targetNodeId, serialNumber);
        if (!path) {
            throw new Error('No path found, possibly all routes are blocked by other FTS');
        }
        if (path.distance == 0) {
            // FTS is already at the target node, we need to issue the order to
            //  reposition the FTS to a different loading bay
            return {
                timestamp: new Date(),
                orderId,
                orderUpdateId,
                nodes: [
                    {
                        id: targetNodeId,
                        linkedEdges: [],
                        action: {
                            type: fts_1.FtsCommandType.DOCK,
                            id: actionId,
                        },
                    },
                ],
                edges: [],
                serialNumber,
            };
        }
        console.debug('PATH', JSON.stringify(path, null, 2));
        return NavigatorService.convertPathToOrder(graph, path.path, orderId, orderUpdateId, serialNumber, actionId);
    }
    static buildAdjacencyMatrix(graph, blocked) {
        // create an empty adjacency matrix with all values set to Infinity
        const adjacencyMatrix = Array(graph.nodes.length)
            .fill(null)
            .map(() => Array(graph.nodes.length).fill(Infinity));
        // set the diagonal values to 0
        for (let i = 0; i < graph.nodes.length; i++) {
            adjacencyMatrix[i][i] = 0;
        }
        // populate the adjacency matrix with edge lengths
        for (const edge of graph.edges) {
            if (blocked && (blocked.has(edge.from.id) || blocked.has(edge.to.id))) {
                // do not add connections to blocked nodes
                continue;
            }
            const fromIndex = graph.nodes.findIndex(node => node.id === edge.from.id);
            const toIndex = graph.nodes.findIndex(node => node.id === edge.to.id);
            // set the value in the adjacency matrix to the edge length
            console.log('FROM Node', graph.nodes[fromIndex], fromIndex);
            adjacencyMatrix[fromIndex][toIndex] = edge.length;
        }
        return adjacencyMatrix;
    }
    /**
     * This code uses a priority queue to keep track of the vertices with the shortest distance from the start vertex.
     * It initializes all distances to Infinity, except for the start vertex which is set to 0.
     * Then it iteratively explores the neighbors of the vertices with the shortest distance until all vertices have been visited.
     * The distances array returned by the function will contain the shortest distance from the start vertex to each vertex in the graph.
     *
     * To find the path with the lowest weight, we can modify the function to keep track of the previous vertex that led to the shortest distance to each vertex.
     * Then, we can trace back the path from the target vertex to the start vertex by following the previous vertices. Here's the modified code:
     *
     * It's important to ensure that the graph doesn't contain negative cycles before running Dijkstra's algorithm.
     */
    static findShortestPath(adjacencyMatrix, start, target) {
        const distances = new Array(adjacencyMatrix.length).fill(Infinity);
        const visited = new Array(adjacencyMatrix.length).fill(false);
        const previous = new Array(adjacencyMatrix.length).fill(null);
        distances[start] = 0;
        while (!visited[target]) {
            let currNode = null;
            let shortestDistance = Infinity;
            for (let i = 0; i < adjacencyMatrix.length; i++) {
                if (!visited[i] && distances[i] < shortestDistance) {
                    currNode = i;
                    shortestDistance = distances[i];
                }
            }
            if (currNode === null) {
                break;
            }
            visited[currNode] = true;
            for (let i = 0; i < adjacencyMatrix[currNode].length; i++) {
                const weight = adjacencyMatrix[currNode][i];
                if (weight !== 0) {
                    const distance = shortestDistance + weight;
                    if (distance < distances[i]) {
                        distances[i] = distance;
                        previous[i] = currNode;
                    }
                }
            }
        }
        if (target === null) {
            return null;
        }
        const path = [];
        let currentNode = target;
        while (currentNode !== null) {
            path.unshift(currentNode);
            currentNode = previous[currentNode];
        }
        // return null if no valid path to the target exists
        if (distances[target] === null || distances[target] === Infinity) {
            return null;
        }
        return { path, distance: distances[target] };
    }
    /**
     * Based on the input graph and the calculated path (sequence of nodes), this function generates
     * the respective FTS order.
     * To do so, it infers rotation commands based on the edge directions.
     *
     * @param graph The active factory layout graph, which was used to generate the path
     * @param path the calculated path (sequence of nodes)
     * @param orderId
     * @param orderUpdateId
     * @param serialNumber
     * @param actionId The action ID used to queue the next order after the FTS order is completed
     */
    static convertPathToOrder(graph, path, orderId, orderUpdateId, serialNumber, actionId) {
        if (path.length < 2) {
            throw new Error('Path must contain at least two nodes');
        }
        if (NavigatorService.hasDuplicates(path)) {
            throw new Error('Path must not contain duplicate nodes, could indicate a cycle in the graph');
        }
        const nodes = [];
        const edges = [];
        // Add all edges to the order
        for (let j = 0; j < path.length - 1; j++) {
            const startNodeIndex = path[j];
            const startNode = graph.nodes[startNodeIndex];
            const endNodeIndex = path[j + 1];
            const endNode = graph.nodes[endNodeIndex];
            const edge = factory_layout_service_1.FactoryLayoutService.findEdgeBetweenNodes(graph.edges, startNode, endNode);
            if (!edge) {
                throw new Error('No edge found between nodes: ' + startNode.id + ' and ' + endNode.id + '');
            }
            const edgeId = startNode.id + '-' + endNode.id;
            edges.push({
                id: edgeId,
                length: edge.length,
                linkedNodes: [startNode.id, endNode.id],
            });
        }
        const initialPositionNode = graph.nodes[path[0]];
        /**
         * Adds the initial node from with the fts starts the navigation. No Action to execute here
         * since direction is already known because the FTS is docked to the module in a specific direction
         */
        nodes.push({
            id: initialPositionNode.id,
            linkedEdges: NavigatorService.getLinkedEdges(edges, initialPositionNode),
        });
        // We only list nodes where we need to execute a action, this excludes the start and end node
        for (let i = 1; i < path.length - 1; i++) {
            const startNodeIndex = path[i - 1];
            const startNode = graph.nodes[startNodeIndex];
            const actionNodeIndex = path[i];
            const actionNode = graph.nodes[actionNodeIndex];
            // This is a list which is used by the FTS to verify that the FTS order is valid. It contains
            // all edges, that are connected to the node
            const linkedEdges = NavigatorService.getLinkedEdges(edges, actionNode);
            const targetNodeIndex = path[i + 1];
            const targetNode = graph.nodes[targetNodeIndex];
            // This is an intersection node, so we need to infer the action that needs to be executed by the FTS
            const inboundEdge = factory_layout_service_1.FactoryLayoutService.findEdgeBetweenNodes(graph.edges, startNode, actionNode);
            const outboundEdge = factory_layout_service_1.FactoryLayoutService.findEdgeBetweenNodes(graph.edges, actionNode, targetNode);
            if (!inboundEdge || !outboundEdge) {
                throw new Error('Action node ' + actionNode.id + ' is not connected to the previous and next node');
            }
            const nodeAction = NavigatorService.inferIntersectionNodeAction(inboundEdge, outboundEdge);
            // this is an actual module, so we only can dock to this.
            if ('module' in targetNode) {
                console.log('Found a module in path, docking to it');
                // Before docking, we need to check if we face the proper direction
                if (nodeAction.type === fts_1.FtsCommandType.TURN || nodeAction.type === fts_1.FtsCommandType.PASS) {
                    console.log(`Adding another action before docking: ${nodeAction.type}`);
                    nodes.push({
                        id: actionNode.id,
                        linkedEdges,
                        action: nodeAction,
                    });
                }
                nodes.push({
                    id: targetNode.id,
                    linkedEdges: NavigatorService.getLinkedEdges(edges, targetNode),
                    action: {
                        type: fts_1.FtsCommandType.DOCK,
                        id: actionId,
                    },
                });
                // The navigation path directly ends on the next module, no mather if there are more path-entries that follow
                break;
            }
            // This is a normal intersection node, so we need to add the action to the order
            nodes.push({
                id: actionNode.id,
                linkedEdges,
                action: nodeAction,
            });
        }
        return {
            timestamp: new Date(),
            orderId,
            orderUpdateId,
            nodes,
            edges,
            serialNumber,
        };
    }
    /**
     * Based on the provided inbound and outbound edge, this function infers the action that needs to be executed
     * at the intersection node.
     * This function assumes that the inbound and outbound edge are connected to the intersection node. If this is not
     * the case, unexpected behavior might occur.
     *
     * @param inboundEdge the ingoing edge to the intersection node
     * @param outboundEdge the outgoing edge from the intersection node
     */
    static inferIntersectionNodeAction(inboundEdge, outboundEdge) {
        // If both edges have the same direction, we need to pass the intersection without any additional actions
        const type = inboundEdge.direction === outboundEdge.direction ? fts_1.FtsCommandType.PASS : fts_1.FtsCommandType.TURN;
        const action = {
            id: (0, node_crypto_1.randomUUID)(),
            type,
        };
        // If we need to turn, we need to infer the direction by checking the inbound and outbound edge directions
        if (type === fts_1.FtsCommandType.TURN) {
            const direction = NavigatorService.inferTurnDirectionFromRoadDirections(inboundEdge.direction, outboundEdge.direction);
            action.metadata = {
                direction: direction,
            };
        }
        return action;
    }
    /**
     * Based on the provided inbound and outbound edge directions, this function infers the turn direction
     * for the FTS.
     * This function assumes that the inbound and outbound edge are connected to the intersection node and the
     * edges are only orthogonal to each other. If this is not the case, unexpected behavior might occur.
     *
     * @param inboundDirection The direction of the inbound edge
     * @param outboundDirection The direction of the outbound edge
     */
    static inferTurnDirectionFromRoadDirections(inboundDirection, outboundDirection) {
        let direction = null;
        if (inboundDirection === ccu_1.RoadDirection.NORTH) {
            if (outboundDirection === ccu_1.RoadDirection.EAST) {
                direction = model_1.Direction.RIGHT;
            }
            else if (outboundDirection === ccu_1.RoadDirection.WEST) {
                direction = model_1.Direction.LEFT;
            }
            else {
                throw new Error('Invalid outbound edge direction: ' + outboundDirection);
            }
        }
        else if (inboundDirection === ccu_1.RoadDirection.SOUTH) {
            if (outboundDirection === ccu_1.RoadDirection.EAST) {
                direction = model_1.Direction.LEFT;
            }
            else if (outboundDirection === ccu_1.RoadDirection.WEST) {
                direction = model_1.Direction.RIGHT;
            }
            else {
                throw new Error('Invalid outbound edge direction: ' + outboundDirection);
            }
        }
        else if (inboundDirection === ccu_1.RoadDirection.EAST) {
            if (outboundDirection === ccu_1.RoadDirection.NORTH) {
                direction = model_1.Direction.LEFT;
            }
            else if (outboundDirection === ccu_1.RoadDirection.SOUTH) {
                direction = model_1.Direction.RIGHT;
            }
            else {
                throw new Error('Invalid outbound edge direction: ' + outboundDirection);
            }
        }
        else if (inboundDirection === ccu_1.RoadDirection.WEST) {
            if (outboundDirection === ccu_1.RoadDirection.NORTH) {
                direction = model_1.Direction.RIGHT;
            }
            else if (outboundDirection === ccu_1.RoadDirection.SOUTH) {
                direction = model_1.Direction.LEFT;
            }
            else {
                throw new Error('Invalid outbound edge direction: ' + outboundDirection);
            }
        }
        if (!direction) {
            throw new Error('Invalid inbound edge direction: ' + inboundDirection);
        }
        return direction;
    }
    /**
     * Extracts all edges from the provided list that are connected to the provided node
     */
    static getLinkedEdges(edges, node) {
        return edges.filter(edge => edge.linkedNodes.includes(node.id)).map(edge => edge.id);
    }
    static hasDuplicates(path) {
        for (let i = 0; i < path.length; i++) {
            if (path.indexOf(path[i]) !== i) {
                return true;
            }
        }
        return false;
    }
}
exports.NavigatorService = NavigatorService;
