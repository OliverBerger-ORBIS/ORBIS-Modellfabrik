"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_LAYOUT = void 0;
const ccu_1 = require("../../../../../common/protocol/ccu");
const module_1 = require("../../../../../common/protocol/module");
exports.DEFAULT_LAYOUT = {
    modules: [
        {
            type: module_1.ModuleType.HBW,
            serialNumber: 'HBW-MISSING',
            placeholder: true,
        },
        {
            type: module_1.ModuleType.DRILL,
            serialNumber: 'DRILL-MISSING',
            placeholder: true,
        },
        {
            type: module_1.ModuleType.MILL,
            serialNumber: 'MILL-MISSING',
            placeholder: true,
        },
        {
            type: module_1.ModuleType.DPS,
            serialNumber: 'DPS-MISSING',
            placeholder: true,
        },
        {
            type: module_1.ModuleType.AIQS,
            serialNumber: 'AIQS-MISSING',
            placeholder: true,
        },
        {
            type: module_1.ModuleType.CHRG,
            serialNumber: 'CHRG0',
        },
    ],
    intersections: [
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
    roads: [
        {
            length: 360,
            from: '1',
            to: '2',
            direction: ccu_1.RoadDirection.EAST,
        },
        {
            length: 360,
            from: '3',
            to: '1',
            direction: ccu_1.RoadDirection.NORTH,
        },
        {
            length: 360,
            from: '3',
            to: '4',
            direction: ccu_1.RoadDirection.EAST,
        },
        {
            length: 360,
            from: '4',
            to: '2',
            direction: ccu_1.RoadDirection.NORTH,
        },
        {
            direction: ccu_1.RoadDirection.EAST,
            from: 'HBW-MISSING',
            to: '1',
            length: 380,
        },
        {
            direction: ccu_1.RoadDirection.EAST,
            from: 'DRILL-MISSING',
            to: '3',
            length: 380,
        },
        {
            direction: ccu_1.RoadDirection.SOUTH,
            from: 'MILL-MISSING',
            to: '1',
            length: 380,
        },
        {
            direction: ccu_1.RoadDirection.WEST,
            from: 'DPS-MISSING',
            to: '2',
            length: 380,
        },
        {
            direction: ccu_1.RoadDirection.SOUTH,
            from: 'AIQS-MISSING',
            to: '2',
            length: 380,
        },
        {
            direction: ccu_1.RoadDirection.WEST,
            from: 'CHRG0',
            to: '4',
            length: 430,
        },
    ],
};
