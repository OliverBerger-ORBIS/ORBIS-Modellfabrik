import { Module, ModuleType } from '../../../../../../common/protocol/module';
import { FactoryLayoutService, FactoryRoad } from '../../../layout/factory-layout-service';
import { FactoryNode, RoadDirection } from '../../../../../../common/protocol/ccu';

export const moduleDps = { type: ModuleType.DPS, serialNumber: 'DPS-1' };
export const moduleHBW = { type: ModuleType.HBW, serialNumber: 'HBW-1' };
export const moduleAIQS = { type: ModuleType.AIQS, serialNumber: 'AIQS-1' };
export const moduleMILL = { type: ModuleType.MILL, serialNumber: 'MILL-1' };
export const moduleDrill = { type: ModuleType.DRILL, serialNumber: 'DRILL-1' };

export const modules: Module[] = [moduleDps, moduleHBW, moduleAIQS, moduleMILL, moduleDrill];

export const intersection1 = { id: '1' };
export const intersection2 = { id: '2' };
export const intersection3 = { id: '3' };
export const intersection4 = { id: '4' };

export const intersections: FactoryNode[] = [intersection1, intersection2, intersection3, intersection4];

export const edge1: FactoryRoad = {
  from: FactoryLayoutService.getModuleNode(moduleDps),
  to: intersection1,
  length: 320,
  direction: RoadDirection.NORTH,
};
export const edge2 = {
  from: intersection1,
  to: FactoryLayoutService.getModuleNode(moduleAIQS),
  length: 320,
  direction: RoadDirection.WEST,
};
export const edge4 = {
  from: intersection1,
  to: intersection2,
  length: 400,
  direction: RoadDirection.EAST,
};
export const edge5 = {
  from: intersection2,
  to: FactoryLayoutService.getModuleNode(moduleHBW),
  length: 320,
  direction: RoadDirection.SOUTH,
};
export const edge6 = {
  from: intersection2,
  to: FactoryLayoutService.getModuleNode(moduleMILL),
  length: 320,
  direction: RoadDirection.EAST,
};
export const edge7 = {
  from: intersection3,
  to: FactoryLayoutService.getModuleNode(moduleDrill),
  length: 320,
  direction: RoadDirection.NORTH,
};
export const edge8 = {
  from: intersection2,
  to: intersection3,
  length: 400,
  direction: RoadDirection.NORTH,
};
export const edge9 = {
  from: intersection3,
  to: intersection4,
  length: 400,
  direction: RoadDirection.WEST,
};
export const edge10 = {
  from: intersection4,
  to: intersection1,
  length: 300,
  direction: RoadDirection.SOUTH,
};
export const edges: FactoryRoad[] = [edge1, edge2, edge4, edge5, edge6, edge7, edge8, edge9, edge10];

/**
 * The sum of the number of intersections and modules
 */
export const EXPEXTED_NODE_NUMBER = 9;
/**
 * The number of edges this graph should generate, double all edges that are unidirectional
 */
export const EXPEXTED_EDGE_NUMBER = 18;

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
export const EXPECTED_GRAPH = {
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

export const EXPECTED_ADJACENCY_MATRIX = [
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

export const BLOCKED_NODES = new Set('4');
export const EXPECTED_BLOCKED_ADJACENCY_MATRIX = [
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

export const BLOCKED_NODES_NO_PATH = new Set(['4', '2']);
