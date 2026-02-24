"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EXPECTED_ROUTE_DPS_MILL = exports.EXPECTED_OFFICE_GRAPH = exports.office_edges = exports.office_intersections = exports.office_modules = void 0;
const module_1 = require("../../../../../../common/protocol/module");
const factory_layout_service_1 = require("../../../layout/factory-layout-service");
const ccu_1 = require("../../../../../../common/protocol/ccu");
const moduleDPS = { type: module_1.ModuleType.DPS, serialNumber: 'kBix' };
const moduleHBW = { type: module_1.ModuleType.HBW, serialNumber: 'yBix' };
const moduleAIQS = { type: module_1.ModuleType.AIQS, serialNumber: '4Cjx' };
const moduleMILL = { type: module_1.ModuleType.MILL, serialNumber: 'ctxw' };
const moduleDRILL = { type: module_1.ModuleType.DRILL, serialNumber: 'xULx' };
exports.office_modules = [moduleDPS, moduleHBW, moduleAIQS, moduleMILL, moduleDRILL];
const intersection1 = { id: '1' };
const intersection2 = { id: '2' };
const intersection3 = { id: '3' };
const intersection4 = { id: '4' };
const intersection5 = { id: '5' };
const intersection6 = { id: '6' };
exports.office_intersections = [
    intersection1,
    intersection2,
    intersection3,
    intersection4,
    intersection5,
    intersection6,
];
const edge1 = {
    from: factory_layout_service_1.FactoryLayoutService.getModuleNode(moduleDPS),
    to: intersection1,
    length: 320,
    direction: ccu_1.RoadDirection.NORTH,
};
const edge2 = {
    from: intersection1,
    to: intersection2,
    length: 400,
    direction: ccu_1.RoadDirection.NORTH,
};
const edge3 = {
    from: intersection1,
    to: intersection3,
    length: 400,
    direction: ccu_1.RoadDirection.WEST,
};
const edge4 = {
    from: intersection2,
    to: factory_layout_service_1.FactoryLayoutService.getModuleNode(moduleDRILL),
    length: 320,
    direction: ccu_1.RoadDirection.EAST,
};
const edge5 = {
    from: intersection2,
    to: intersection4,
    length: 400,
    direction: ccu_1.RoadDirection.WEST,
};
const edge6 = {
    from: intersection3,
    to: factory_layout_service_1.FactoryLayoutService.getModuleNode(moduleHBW),
    length: 320,
    direction: ccu_1.RoadDirection.SOUTH,
};
const edge7 = {
    from: intersection3,
    to: factory_layout_service_1.FactoryLayoutService.getModuleNode(moduleAIQS),
    length: 320,
    direction: ccu_1.RoadDirection.WEST,
};
const edge8 = {
    from: intersection3,
    to: intersection4,
    length: 400,
    direction: ccu_1.RoadDirection.NORTH,
};
const edge9 = {
    from: intersection4,
    to: intersection6,
    length: 400,
    direction: ccu_1.RoadDirection.WEST,
};
const edge11 = {
    from: intersection4,
    to: intersection5,
    length: 400,
    direction: ccu_1.RoadDirection.NORTH,
};
const edge12 = {
    from: intersection5,
    to: factory_layout_service_1.FactoryLayoutService.getModuleNode(moduleMILL),
    length: 320,
    direction: ccu_1.RoadDirection.NORTH,
};
exports.office_edges = [edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, edge9, edge11, edge12];
exports.EXPECTED_OFFICE_GRAPH = {
    nodes: [
        {
            id: 'kBix',
            module: {
                type: 'DPS',
                serialNumber: 'kBix',
            },
        },
        {
            id: 'yBix',
            module: {
                type: 'HBW',
                serialNumber: 'yBix',
            },
        },
        {
            id: '4Cjx',
            module: {
                type: 'AIQS',
                serialNumber: '4Cjx',
            },
        },
        {
            id: 'ctxw',
            module: {
                type: 'MILL',
                serialNumber: 'ctxw',
            },
        },
        {
            id: 'xULx',
            module: {
                type: 'DRILL',
                serialNumber: 'xULx',
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
        {
            id: '5',
        },
        {
            id: '6',
        },
    ],
    edges: [
        {
            from: {
                id: 'kBix',
                module: {
                    type: 'DPS',
                    serialNumber: 'kBix',
                },
            },
            to: {
                id: '1',
            },
            length: 320,
            direction: 'NORTH',
        },
        {
            from: {
                id: '1',
            },
            to: {
                id: '2',
            },
            length: 400,
            direction: 'NORTH',
        },
        {
            from: {
                id: '1',
            },
            to: {
                id: '3',
            },
            length: 400,
            direction: 'WEST',
        },
        {
            from: {
                id: '2',
            },
            to: {
                id: 'xULx',
                module: {
                    type: 'DRILL',
                    serialNumber: 'xULx',
                },
            },
            length: 320,
            direction: 'EAST',
        },
        {
            from: {
                id: '2',
            },
            to: {
                id: '4',
            },
            length: 400,
            direction: 'WEST',
        },
        {
            from: {
                id: '3',
            },
            to: {
                id: 'yBix',
                module: {
                    type: 'HBW',
                    serialNumber: 'yBix',
                },
            },
            length: 320,
            direction: 'SOUTH',
        },
        {
            from: {
                id: '3',
            },
            to: {
                id: '4Cjx',
                module: {
                    type: 'AIQS',
                    serialNumber: '4Cjx',
                },
            },
            length: 320,
            direction: 'WEST',
        },
        {
            from: {
                id: '3',
            },
            to: {
                id: '4',
            },
            length: 400,
            direction: 'NORTH',
        },
        {
            from: {
                id: '4',
            },
            to: {
                id: '6',
            },
            length: 400,
            direction: 'WEST',
        },
        {
            from: {
                id: '4',
            },
            to: {
                id: '5',
            },
            length: 400,
            direction: 'NORTH',
        },
        {
            from: {
                id: '5',
            },
            to: {
                id: 'ctxw',
                module: {
                    type: 'MILL',
                    serialNumber: 'ctxw',
                },
            },
            length: 320,
            direction: 'NORTH',
        },
        {
            length: 320,
            direction: 'SOUTH',
            from: {
                id: '1',
            },
            to: {
                id: 'kBix',
                module: {
                    type: 'DPS',
                    serialNumber: 'kBix',
                },
            },
        },
        {
            length: 400,
            direction: 'SOUTH',
            from: {
                id: '2',
            },
            to: {
                id: '1',
            },
        },
        {
            length: 400,
            direction: 'EAST',
            from: {
                id: '3',
            },
            to: {
                id: '1',
            },
        },
        {
            length: 320,
            direction: 'WEST',
            from: {
                id: 'xULx',
                module: {
                    type: 'DRILL',
                    serialNumber: 'xULx',
                },
            },
            to: {
                id: '2',
            },
        },
        {
            length: 400,
            direction: 'EAST',
            from: {
                id: '4',
            },
            to: {
                id: '2',
            },
        },
        {
            length: 320,
            direction: 'NORTH',
            from: {
                id: 'yBix',
                module: {
                    type: 'HBW',
                    serialNumber: 'yBix',
                },
            },
            to: {
                id: '3',
            },
        },
        {
            length: 320,
            direction: 'EAST',
            from: {
                id: '4Cjx',
                module: {
                    type: 'AIQS',
                    serialNumber: '4Cjx',
                },
            },
            to: {
                id: '3',
            },
        },
        {
            length: 400,
            direction: 'SOUTH',
            from: {
                id: '4',
            },
            to: {
                id: '3',
            },
        },
        {
            length: 400,
            direction: 'EAST',
            from: {
                id: '6',
            },
            to: {
                id: '4',
            },
        },
        {
            length: 400,
            direction: 'SOUTH',
            from: {
                id: '5',
            },
            to: {
                id: '4',
            },
        },
        {
            length: 320,
            direction: 'SOUTH',
            from: {
                id: 'ctxw',
                module: {
                    type: 'MILL',
                    serialNumber: 'ctxw',
                },
            },
            to: {
                id: '5',
            },
        },
    ],
};
exports.EXPECTED_ROUTE_DPS_MILL = {
    timestamp: '2023-03-22T16:24:46.730Z',
    orderId: 'testOrderId',
    orderUpdateId: 4,
    nodes: [
        {
            id: 'kBix',
            linkedEdges: ['kBix-1'],
        },
        {
            id: '1',
            linkedEdges: ['kBix-1', '1-2'],
            action: {
                id: 'ebe3c241-9059-4e3e-a6b2-da4ce98b79c3',
                type: 'PASS',
            },
        },
        {
            id: '2',
            linkedEdges: ['1-2', '2-4'],
            action: {
                id: '43fe9815-5187-4ae4-95ce-c3fbd0356ae3',
                type: 'TURN',
                metadata: {
                    direction: 'LEFT',
                },
            },
        },
        {
            id: '4',
            linkedEdges: ['2-4', '4-5'],
            action: {
                id: '30082ab7-57a8-483f-a7f2-69b1af14f12a',
                type: 'TURN',
                metadata: {
                    direction: 'RIGHT',
                },
            },
        },
        {
            id: '5',
            linkedEdges: ['4-5', '5-ctxw'],
            action: {
                id: '30082ab7-57a8-483f-a7f2-69b1af14f12c',
                type: 'PASS',
            },
        },
        {
            id: 'ctxw',
            linkedEdges: ['5-ctxw'],
            action: {
                type: 'DOCK',
                id: '1a22afae-74c8-4d4b-adf9-bf8d87e0126b',
            },
        },
    ],
    edges: [
        {
            id: 'kBix-1',
            length: 320,
            linkedNodes: ['kBix', '1'],
        },
        {
            id: '1-2',
            length: 400,
            linkedNodes: ['1', '2'],
        },
        {
            id: '2-4',
            length: 400,
            linkedNodes: ['2', '4'],
        },
        {
            id: '4-5',
            length: 400,
            linkedNodes: ['4', '5'],
        },
        {
            id: '5-ctxw',
            length: 320,
            linkedNodes: ['5', 'ctxw'],
        },
    ],
    serialNumber: 'FTS-1',
};
