import fs from 'node:fs/promises';
import path from 'path';
import { RoadDirection } from '../../../../common/protocol/ccu';
import { ModuleType } from '../../../../common/protocol/module';
import config from '../../config';
import * as mqtt_spies from '../../mqtt/mqtt';
import {
  EXPECTED_OFFICE_GRAPH,
  office_edges,
  office_intersections,
  office_modules,
} from '../fts/navigation/mockData/static-office-factory-data';
import { PairingStates } from '../pairing/pairing-states';
import { FactoryLayoutService, FactoryNodeBlocker } from './factory-layout-service';
import { DEFAULT_LAYOUT } from './default_reset/default_layout';

const testLayout = {
  intersections: [{ id: '2' }],
  modules: [{ type: ModuleType.DRILL, serialNumber: 'xyzZ' }],
  roads: [{ direction: RoadDirection.SOUTH, length: 100, to: '2', from: 'xyzZ' }],
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
    } as unknown as mqtt_spies.AsyncMqttClient);
  });

  afterEach(() => {
    FactoryLayoutService.destroy();
    PairingStates.getInstance().reset();
    jest.clearAllMocks();
  });

  it('should generate the correct graph for the office factory', () => {
    const officeFactoryGraph = FactoryLayoutService.generateGraph(office_modules, office_intersections, office_edges);
    expect(officeFactoryGraph).toBeDefined();
    expect(officeFactoryGraph.nodes).toBeDefined();
    expect(officeFactoryGraph.edges).toBeDefined();
    expect(officeFactoryGraph.nodes.length).toBe(11); // 6 modules + 5 intersections
    expect(officeFactoryGraph.edges.length).toBe(22); // 11 edges times 2 (bidirectional)
    console.log('OFFICE GRAPH', JSON.stringify(officeFactoryGraph));
    console.log('EXPECTED OFFICE GRAPH', JSON.stringify(EXPECTED_OFFICE_GRAPH));
    expect(officeFactoryGraph).toEqual(EXPECTED_OFFICE_GRAPH);
  });

  it('should load and generate the office factory graph from a file', async () => {
    const factoryLayout = await FactoryLayoutService.loadLayoutFromJsonFile(path.join(config.storage.path, config.storage.layoutFile));
    expect(factoryLayout).not.toBeNull();
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const officeFactoryGraph = FactoryLayoutService.generateGraphFromJsonLayout(factoryLayout!);
    expect(officeFactoryGraph).toBeDefined();
    expect(officeFactoryGraph.nodes).toBeDefined();
    expect(officeFactoryGraph.edges).toBeDefined();
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const numOfModules = factoryLayout!.modules.length;
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const numOfIntersections = factoryLayout!.intersections.length;
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

    FactoryLayoutService.setLayout(layout);

    expect(FactoryLayoutService.graph).toEqual(expectedGraph);
    // no-explicit-any is needed here as layout is a private property
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    expect((FactoryLayoutService as any).layout).toEqual(testLayout);
  });

  it('should publish the layout correctly when an mqtt client exists', async () => {
    const layout = JSON.parse(JSON.stringify(testLayout));
    FactoryLayoutService.setLayout(layout);

    const publishSpy = jest.fn().mockImplementation(() => Promise.resolve());

    jest.spyOn(mqtt_spies, 'getMqttClient').mockReturnValue({
      publish: publishSpy,
    } as unknown as mqtt_spies.AsyncMqttClient);

    await FactoryLayoutService.publishLayout();
    expect(publishSpy).toHaveBeenLastCalledWith('ccu/state/layout', JSON.stringify(testLayout), { qos: 1, retain: true });
  });

  it('should initialize the graph with a file', async () => {
    const layoutJson = JSON.stringify(testLayout);
    jest.spyOn(fs, 'readFile').mockResolvedValue(layoutJson);

    await FactoryLayoutService.initialize('/foo/test.json');

    expect(fs.readFile).toHaveBeenCalledWith('/foo/test.json', expect.any(Object));
    expect(FactoryLayoutService.graph).toEqual(testGraph);
  });

  it('should reload a new file', async () => {
    const layoutJson = JSON.stringify(testLayout);
    jest.spyOn(fs, 'readFile').mockResolvedValue('{}');

    await FactoryLayoutService.initialize('/foo/test.json');
    expect(FactoryLayoutService.graph).toEqual(FactoryLayoutService.generateGraphFromJsonLayout(DEFAULT_LAYOUT));

    jest.spyOn(fs, 'readFile').mockResolvedValue(layoutJson);
    await FactoryLayoutService.reloadLayout();

    expect(fs.readFile).toHaveBeenCalledWith('/foo/test.json', expect.any(Object));
    expect(FactoryLayoutService.graph).toEqual(testGraph);
  });

  it('should save a layout', async () => {
    jest.spyOn(fs, 'readFile').mockResolvedValue('{}');
    jest.spyOn(fs, 'writeFile').mockResolvedValue();

    await FactoryLayoutService.initialize('/foo/test.json');
    expect(FactoryLayoutService.graph).toEqual(FactoryLayoutService.generateGraphFromJsonLayout(DEFAULT_LAYOUT));

    FactoryLayoutService.setLayout(testLayout);
    expect(FactoryLayoutService.graph).toEqual(testGraph);

    await FactoryLayoutService.saveLayout();

    expect(fs.writeFile).toHaveBeenCalledWith('/foo/test.json', JSON.stringify(testLayout, undefined, 2), expect.any(Object));
  });

  it('should block a node', async () => {
    await FactoryLayoutService.initialize();
    const nodeId = '12';
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: 'any',
    };

    FactoryLayoutService.blockNodeSequence([blocker]);

    expect(FactoryLayoutService.isNodeBlocked(nodeId)).toBe(true);
    expect(FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeId]));
  });

  it('should return nodes that are blocked by a different FTS', async () => {
    await FactoryLayoutService.initialize();
    const nodeId = '12';
    const nodeId2 = '2';
    const nodeId3 = '3';
    const ftsSerialNumber = 'FTS-1';
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber,
    };
    const blocker2: FactoryNodeBlocker = {
      nodeId: nodeId2,
      ftsSerialNumber: 'another',
    };
    const blocker3: FactoryNodeBlocker = {
      nodeId: nodeId3,
      ftsSerialNumber: 'any',
    };

    FactoryLayoutService.blockNodeSequence([blocker, blocker2, blocker3]);

    expect(FactoryLayoutService.isNodeBlocked(nodeId)).toBe(true);
    expect(FactoryLayoutService.isNodeBlocked(nodeId, ftsSerialNumber)).toBe(false);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2, ftsSerialNumber)).toBe(true);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2, ftsSerialNumber)).toBe(true);
    expect(FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeId, nodeId2, nodeId3]));
    expect(FactoryLayoutService.getBlockedNodeIds(ftsSerialNumber)).toEqual(new Set([nodeId2, nodeId3]));
  });

  it('should fail if a node has a preceding node that is missing', async () => {
    await FactoryLayoutService.initialize();
    const nodeId = '12';
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: 'any',
      afterNodeId: '2',
    };

    try {
      FactoryLayoutService.blockNodeSequence([blocker]);
    } catch (e) {
      expect(e).toEqual(Error('Node points to missing preceding node'));
    }
    expect.assertions(1);
  });

  it('should fail if a node is blocked by a different fts', async () => {
    await FactoryLayoutService.initialize();
    const nodeId = '12';
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: 'any',
    };
    const blocker2: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: 'another',
    };

    FactoryLayoutService.blockNodeSequence([blocker]);
    try {
      FactoryLayoutService.blockNodeSequence([blocker2]);
    } catch (e) {
      expect(e).toEqual(Error('Node already blocked by another FTS'));
    }
    expect.assertions(1);
  });

  it('should block a node sequence', async () => {
    await FactoryLayoutService.initialize();
    const nodeId = '12';
    const nodeId2 = '2';
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: 'any',
    };
    const blocker2: FactoryNodeBlocker = {
      nodeId: nodeId2,
      ftsSerialNumber: 'any',
      afterNodeId: nodeId,
    };

    FactoryLayoutService.blockNodeSequence([blocker, blocker2]);

    expect(FactoryLayoutService.isNodeBlocked(nodeId)).toBe(true);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
    expect(FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeId, nodeId2]));
  });

  it('should fail if an already blocked node refers to a different preceding node', async () => {
    await FactoryLayoutService.initialize();
    const nodeId = '12';
    const nodeId2 = '2';
    const nodeId3 = '3';
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: 'any',
    };
    const blocker2: FactoryNodeBlocker = {
      nodeId: nodeId2,
      ftsSerialNumber: 'any',
      afterNodeId: nodeId,
    };
    const blocker3: FactoryNodeBlocker = {
      nodeId: nodeId3,
      ftsSerialNumber: 'any',
    };
    const blocker2B: FactoryNodeBlocker = {
      nodeId: nodeId2,
      ftsSerialNumber: 'any',
      afterNodeId: nodeId3,
    };

    FactoryLayoutService.blockNodeSequence([blocker, blocker2]);

    try {
      FactoryLayoutService.blockNodeSequence([blocker3, blocker2B]);
    } catch (e) {
      expect(e).toEqual(Error('Node blocked with a different preceding node'));
    }
    expect.assertions(1);
  });

  it('should release a node', async () => {
    await FactoryLayoutService.initialize();
    const nodeId = '12';
    const nodeId2 = '2';
    const ftsSerial = 'fts';
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: ftsSerial,
    };
    const blocker2: FactoryNodeBlocker = {
      nodeId: nodeId2,
      ftsSerialNumber: ftsSerial,
      afterNodeId: nodeId,
    };

    FactoryLayoutService.blockNodeSequence([blocker, blocker2]);
    FactoryLayoutService.releaseNodesBefore(ftsSerial, nodeId2);

    expect(FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeId2]));
    expect(FactoryLayoutService.isNodeBlocked(nodeId)).toBe(false);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
  });

  it('should not release nodes ordered after the given node or unrelated nodes', async () => {
    await FactoryLayoutService.initialize();
    const nodeIdX = '6';
    const nodeId = '12';
    const nodeId2 = '2';
    const ftsSerial = 'fts';
    const blockerX: FactoryNodeBlocker = {
      nodeId: nodeIdX,
      ftsSerialNumber: ftsSerial,
    };
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: ftsSerial,
    };
    const blocker2: FactoryNodeBlocker = {
      nodeId: nodeId2,
      ftsSerialNumber: ftsSerial,
      afterNodeId: nodeId,
    };

    FactoryLayoutService.blockNodeSequence([blockerX, blocker, blocker2]);
    FactoryLayoutService.releaseNodesBefore(ftsSerial, nodeId2);

    expect(FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeIdX, nodeId2]));
    expect(FactoryLayoutService.isNodeBlocked(nodeIdX)).toBe(true);
    expect(FactoryLayoutService.isNodeBlocked(nodeId)).toBe(false);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
  });

  it('should release all nodes for an fts', async () => {
    await FactoryLayoutService.initialize();
    const nodeIdX = '6';
    const nodeId = '12';
    const nodeId2 = '2';
    const ftsSerial = 'fts';
    const blockerX: FactoryNodeBlocker = {
      nodeId: nodeIdX,
      ftsSerialNumber: 'someId',
    };
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: ftsSerial,
    };
    const blocker2: FactoryNodeBlocker = {
      nodeId: nodeId2,
      ftsSerialNumber: ftsSerial,
      afterNodeId: nodeId,
    };

    FactoryLayoutService.blockNodeSequence([blockerX, blocker, blocker2]);
    FactoryLayoutService.releaseAllNodes(ftsSerial);

    expect(FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeIdX]));
    expect(FactoryLayoutService.isNodeBlocked(nodeId)).toBe(false);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(false);
    expect(FactoryLayoutService.isNodeBlocked(nodeIdX)).toBe(true);
  });

  it('should not release nodes not belonging to the fts', async () => {
    await FactoryLayoutService.initialize();
    const nodeIdX = '6';
    const nodeId = '12';
    const nodeId2 = '2';
    const ftsSerial = 'fts';
    const blockerX: FactoryNodeBlocker = {
      nodeId: nodeIdX,
      ftsSerialNumber: 'someId',
    };
    const blocker: FactoryNodeBlocker = {
      nodeId,
      ftsSerialNumber: 'someId2',
    };
    const blocker2: FactoryNodeBlocker = {
      nodeId: nodeId2,
      ftsSerialNumber: 'someId2',
      afterNodeId: nodeId,
    };

    FactoryLayoutService.blockNodeSequence([blockerX, blocker, blocker2]);
    FactoryLayoutService.releaseAllNodes(ftsSerial);

    expect(FactoryLayoutService.getBlockedNodeIds()).toEqual(new Set([nodeIdX, nodeId, nodeId2]));
    expect(FactoryLayoutService.isNodeBlocked(nodeId)).toBe(true);
    expect(FactoryLayoutService.isNodeBlocked(nodeId2)).toBe(true);
    expect(FactoryLayoutService.isNodeBlocked(nodeIdX)).toBe(true);
  });
});
