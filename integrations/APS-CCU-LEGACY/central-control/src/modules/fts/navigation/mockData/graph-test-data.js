"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BLOCKED_NODES_NO_PATH = exports.EXPECTED_BLOCKED_ADJACENCY_MATRIX = exports.BLOCKED_NODES = exports.EXPECTED_ADJACENCY_MATRIX = exports.EXPECTED_GRAPH = exports.EXPEXTED_EDGE_NUMBER = exports.EXPEXTED_NODE_NUMBER = exports.edges = exports.edge10 = exports.edge9 = exports.edge8 = exports.edge7 = exports.edge6 = exports.edge5 = exports.edge4 = exports.edge2 = exports.edge1 = exports.intersections = exports.intersection4 = exports.intersection3 = exports.intersection2 = exports.intersection1 = exports.modules = exports.moduleDrill = exports.moduleMILL = exports.moduleAIQS = exports.moduleHBW = exports.moduleDps = void 0;
const module_1 = require("../../../../../../common/protocol/module");
const factory_layout_service_1 = require("../../../layout/factory-layout-service");
const ccu_1 = require("../../../../../../common/protocol/ccu");
exports.moduleDps = { type: module_1.ModuleType.DPS, serialNumber: 'DPS-1' };
exports.moduleHBW = { type: module_1.ModuleType.HBW, serialNumber: 'HBW-1' };
exports.moduleAIQS = { type: module_1.ModuleType.AIQS, serialNumber: 'AIQS-1' };
exports.moduleMILL = { type: module_1.ModuleType.MILL, serialNumber: 'MILL-1' };
exports.moduleDrill = { type: module_1.ModuleType.DRILL, serialNumber: 'DRILL-1' };
exports.modules = [exports.moduleDps, exports.moduleHBW, exports.moduleAIQS, exports.moduleMILL, exports.moduleDrill];
exports.intersection1 = { id: '1' };
exports.intersection2 = { id: '2' };
exports.intersection3 = { id: '3' };
exports.intersection4 = { id: '4' };
exports.intersections = [exports.intersection1, exports.intersection2, exports.intersection3, exports.intersection4];
exports.edge1 = {
    from: factory_layout_service_1.FactoryLayoutService.getModuleNode(exports.moduleDps),
    to: exports.intersection1,
    length: 320,
    direction: ccu_1.RoadDirection.NORTH,
};
exports.edge2 = {
    from: exports.intersection1,
    to: factory_layout_service_1.FactoryLayoutService.getModuleNode(exports.moduleAIQS),
    length: 320,
    direction: ccu_1.RoadDirection.WEST,
};
exports.edge4 = {
    from: exports.intersection1,
    to: exports.intersection2,
    length: 400,
    direction: ccu_1.RoadDirection.EAST,
};
exports.edge5 = {
    from: exports.intersection2,
    to: factory_layout_service_1.FactoryLayoutService.getModuleNode(exports.moduleHBW),
    length: 320,
    direction: ccu_1.RoadDirection.SOUTH,
};
exports.edge6 = {
    from: exports.intersection2,
    to: factory_layout_service_1.FactoryLayoutService.getModuleNode(exports.moduleMILL),
    length: 320,
    direction: ccu_1.RoadDirection.EAST,
};
exports.edge7 = {
    from: exports.intersection3,
    to: factory_layout_service_1.FactoryLayoutService.getModuleNode(exports.moduleDrill),
    length: 320,
    direction: ccu_1.RoadDirection.NORTH,
};
exports.edge8 = {
    from: exports.intersection2,
    to: exports.intersection3,
    length: 400,
    direction: ccu_1.RoadDirection.NORTH,
};
exports.edge9 = {
    from: exports.intersection3,
    to: exports.intersection4,
    length: 400,
    direction: ccu_1.RoadDirection.WEST,
};
exports.edge10 = {
    from: exports.intersection4,
    to: exports.intersection1,
    length: 300,
    direction: ccu_1.RoadDirection.SOUTH,
};
exports.edges = [exports.edge1, exports.edge2, exports.edge4, exports.edge5, exports.edge6, exports.edge7, exports.edge8, exports.edge9, exports.edge10];
/**
 * The sum of the number of intersections and modules
 */
exports.EXPEXTED_NODE_NUMBER = 9;
/**
 * The number of edges this graph should generate, double all edges that are unidirectional
 */
exports.EXPEXTED_EDGE_NUMBER = 18;
/**
 * Graph visual representation
 *
 *                     DRILL
 *                      |
 *                      |
 *              4 ----- 3
 *              |       |
 *              |       |
 *    AIQS ---- 1 ----- 2 ----- MILL
 *              |       |
 *              |       |
 *             DPS --- HBW
 */
exports.EXPECTED_GRAPH = {
    edges: [
        {
            direction: 'NORTH',
            from: {
                id: 'DPS-1',
                module: {
                    serialNumber: 'DPS-1',
                    type: 'DPS',
                },
            },
            length: 320,
            to: {
                id: '1',
            },
        },
        {
            direction: 'WEST',
            from: {
                id: '1',
            },
            length: 320,
            to: {
                id: 'AIQS-1',
                module: {
                    serialNumber: 'AIQS-1',
                    type: 'AIQS',
                },
            },
        },
        {
            direction: 'EAST',
            from: {
                id: '1',
            },
            length: 400,
            to: {
                id: '2',
            },
        },
        {
            direction: 'SOUTH',
            from: {
                id: '2',
            },
            length: 320,
            to: {
                id: 'HBW-1',
                module: {
                    serialNumber: 'HBW-1',
                    type: 'HBW',
                },
            },
        },
        {
            direction: 'EAST',
            from: {
                id: '2',
            },
            length: 320,
            to: {
                id: 'MILL-1',
                module: {
                    serialNumber: 'MILL-1',
                    type: 'MILL',
                },
            },
        },
        {
            direction: 'NORTH',
            from: {
                id: '3',
            },
            length: 320,
            to: {
                id: 'DRILL-1',
                module: {
                    serialNumber: 'DRILL-1',
                    type: 'DRILL',
                },
            },
        },
        {
            direction: 'NORTH',
            from: {
                id: '2',
            },
            length: 400,
            to: {
                id: '3',
            },
        },
        {
            direction: 'WEST',
            from: {
                id: '3',
            },
            length: 400,
            to: {
                id: '4',
            },
        },
        {
            direction: 'SOUTH',
            from: {
                id: '4',
            },
            length: 300,
            to: {
                id: '1',
            },
        },
        {
            direction: 'SOUTH',
            from: {
                id: '1',
            },
            length: 320,
            to: {
                id: 'DPS-1',
                module: {
                    serialNumber: 'DPS-1',
                    type: 'DPS',
                },
            },
        },
        {
            direction: 'EAST',
            from: {
                id: 'AIQS-1',
                module: {
                    serialNumber: 'AIQS-1',
                    type: 'AIQS',
                },
            },
            length: 320,
            to: {
                id: '1',
            },
        },
        {
            direction: 'WEST',
            from: {
                id: '2',
            },
            length: 400,
            to: {
                id: '1',
            },
        },
        {
            direction: 'NORTH',
            from: {
                id: 'HBW-1',
                module: {
                    serialNumber: 'HBW-1',
                    type: 'HBW',
                },
            },
            length: 320,
            to: {
                id: '2',
            },
        },
        {
            direction: 'WEST',
            from: {
                id: 'MILL-1',
                module: {
                    serialNumber: 'MILL-1',
                    type: 'MILL',
                },
            },
            length: 320,
            to: {
                id: '2',
            },
        },
        {
            direction: 'SOUTH',
            from: {
                id: 'DRILL-1',
                module: {
                    serialNumber: 'DRILL-1',
                    type: 'DRILL',
                },
            },
            length: 320,
            to: {
                id: '3',
            },
        },
        {
            direction: 'SOUTH',
            from: {
                id: '3',
            },
            length: 400,
            to: {
                id: '2',
            },
        },
        {
            direction: 'EAST',
            from: {
                id: '4',
            },
            length: 400,
            to: {
                id: '3',
            },
        },
        {
            direction: 'NORTH',
            from: {
                id: '1',
            },
            length: 300,
            to: {
                id: '4',
            },
        },
    ],
    nodes: [
        {
            id: 'DPS-1',
            module: {
                serialNumber: 'DPS-1',
                type: 'DPS',
            },
        },
        {
            id: 'HBW-1',
            module: {
                serialNumber: 'HBW-1',
                type: 'HBW',
            },
        },
        {
            id: 'AIQS-1',
            module: {
                serialNumber: 'AIQS-1',
                type: 'AIQS',
            },
        },
        {
            id: 'MILL-1',
            module: {
                serialNumber: 'MILL-1',
                type: 'MILL',
            },
        },
        {
            id: 'DRILL-1',
            module: {
                serialNumber: 'DRILL-1',
                type: 'DRILL',
            },
        },
        {
            id: '1',
        },
        {
            id: '2',
        },
        {
            id: '3',
        },
        {
            id: '4',
        },
    ],
};
exports.EXPECTED_ADJACENCY_MATRIX = [
    [0, Infinity, Infinity, Infinity, Infinity, 320, Infinity, Infinity, Infinity],
    [Infinity, 0, Infinity, Infinity, Infinity, Infinity, 320, Infinity, Infinity],
    [Infinity, Infinity, 0, Infinity, Infinity, 320, Infinity, Infinity, Infinity],
    [Infinity, Infinity, Infinity, 0, Infinity, Infinity, 320, Infinity, Infinity],
    [Infinity, Infinity, Infinity, Infinity, 0, Infinity, Infinity, 320, Infinity],
    [320, Infinity, 320, Infinity, Infinity, 0, 400, Infinity, 300],
    [Infinity, 320, Infinity, 320, Infinity, 400, 0, 400, Infinity],
    [Infinity, Infinity, Infinity, Infinity, 320, Infinity, 400, 0, 400],
    [Infinity, Infinity, Infinity, Infinity, Infinity, 300, Infinity, 400, 0],
];
exports.BLOCKED_NODES = new Set('4');
exports.EXPECTED_BLOCKED_ADJACENCY_MATRIX = [
    [0, Infinity, Infinity, Infinity, Infinity, 320, Infinity, Infinity, Infinity],
    [Infinity, 0, Infinity, Infinity, Infinity, Infinity, 320, Infinity, Infinity],
    [Infinity, Infinity, 0, Infinity, Infinity, 320, Infinity, Infinity, Infinity],
    [Infinity, Infinity, Infinity, 0, Infinity, Infinity, 320, Infinity, Infinity],
    [Infinity, Infinity, Infinity, Infinity, 0, Infinity, Infinity, 320, Infinity],
    [320, Infinity, 320, Infinity, Infinity, 0, 400, Infinity, Infinity],
    [Infinity, 320, Infinity, 320, Infinity, 400, 0, 400, Infinity],
    [Infinity, Infinity, Infinity, Infinity, 320, Infinity, 400, 0, Infinity],
    [Infinity, Infinity, Infinity, Infinity, Infinity, Infinity, Infinity, Infinity, 0],
];
exports.BLOCKED_NODES_NO_PATH = new Set(['4', '2']);
