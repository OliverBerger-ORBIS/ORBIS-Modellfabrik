import { Injectable } from '@angular/core';
import { map, Observable, shareReplay } from 'rxjs';
import { CcuTopic } from '../../common/protocol';
import {
  FactoryLayout,
  FactoryNode,
  FactoryRoadFlat,
  FtsPairedModule,
  PairedModule,
  PairingState,
  RoadDirection,
} from '../../common/protocol/ccu';
import { Module, ModuleType } from '../../common/protocol/module';
import { TypedMqttService } from '../futurefactory.service';
import { StatesService } from './states.service';
import { getPayload } from '../utils/rx.utils';

export type FactoryTileId = string;
export type FactoryTile = {
  type: string;
  x: number;
  y: number;
  id: string;
};
export type FactoryRoadTile = FactoryTile & {
  type: 'ROAD';
  road: { [T in RoadDirection]?: FactoryTileId };
};
export type FactoryModuleTile = FactoryTile & {
  type: 'MODULE';
  direction: RoadDirection;
  intersection?: FactoryTileId;
  moduleType: ModuleType;
  connected: boolean;
  placeholder?: boolean;
};
export type FactoryGridLayout = Array<FactoryModuleTile | FactoryRoadTile>;

/** Defines the modules, that are twice the size of a regular module */
export const largeModules = [ModuleType.HBW, ModuleType.DPS];

@Injectable({
  providedIn: 'root',
})
export class FactoryLayoutService {
  readonly currentGridLayout$: Observable<FactoryGridLayout>;
  readonly pairedModules$: Observable<Array<PairedModule>>;
  readonly pairedFTS$: Observable<Array<FtsPairedModule>>;
  readonly pairingState$: Observable<PairingState>;

  // directions to update, in clockwise order. The order is used for the module connection
  private readonly DIRECTION_UPDATES: Array<{
    direction: RoadDirection;
    inverse: RoadDirection;
    xDiff: number;
    yDiff: number;
  }> = [
    {
      direction: RoadDirection.NORTH,
      inverse: RoadDirection.SOUTH,
      xDiff: 0,
      yDiff: -1,
    },
    {
      direction: RoadDirection.EAST,
      inverse: RoadDirection.WEST,
      xDiff: 1,
      yDiff: 0,
    },
    {
      direction: RoadDirection.SOUTH,
      inverse: RoadDirection.NORTH,
      xDiff: 0,
      yDiff: 1,
    },
    {
      direction: RoadDirection.WEST,
      inverse: RoadDirection.EAST,
      xDiff: -1,
      yDiff: 0,
    },
  ];

  constructor(private mqtt: TypedMqttService, private factoryStateService: StatesService) {
    this.currentGridLayout$ = this.mqtt
      .subscribe<FactoryLayout>(CcuTopic.LAYOUT)
      .pipe(
        getPayload(),
        map((layout) => this.layoutToGridLayout(layout)),
        shareReplay(1)
      );

    this.pairingState$ = this.factoryStateService.pairingState$;
    this.pairedModules$ = this.factoryStateService.pairedModules$;
    this.pairedFTS$ = this.factoryStateService.pairedTransports$;
  }

  public getInverseDirection(direction: RoadDirection): RoadDirection {
    switch (direction) {
      case RoadDirection.EAST:
        return RoadDirection.WEST;
      case RoadDirection.WEST:
        return RoadDirection.EAST;
      case RoadDirection.NORTH:
        return RoadDirection.SOUTH;
      case RoadDirection.SOUTH:
        return RoadDirection.NORTH;
    }
  }

  public isLargeModule(moduleType: ModuleType): boolean {
    return largeModules.includes(moduleType);
  }

  /**
   * convert the layout to a grid layout and assign coordinates to all elements
   * @param layout
   */
  public layoutToGridLayout(
    layout: FactoryLayout
  ): Array<FactoryModuleTile | FactoryRoadTile> {
    const { modules, intersections, roads } = layout;
    const road_tiles = this.createPositionedRoadTiles(intersections, roads);
    const module_tiles = this.createModuleTiles(modules);
    this.positionModuleTiles(module_tiles, road_tiles, roads);

    const allTiles: Array<FactoryModuleTile | FactoryRoadTile> = [
      ...Array.from(road_tiles.values()),
      ...Array.from(module_tiles.values()),
    ];
    this.moveToPositivePositions(allTiles);

    return allTiles;
  }

  /**
   * Moves the grid positions of a collection of tiles into positive values. The tiles are moved in-place
   * @param allTiles
   * @private
   */
  private moveToPositivePositions(
    allTiles: Array<FactoryModuleTile | FactoryRoadTile>
  ) {
    // get the minimum x and y values and offset the values into positive space
    const minimums = allTiles.reduce(
      (minimums, tile) => {
        minimums.x = tile.x < minimums.x ? tile.x : minimums.x;
        minimums.y = tile.y < minimums.y ? tile.y : minimums.y;
        return minimums;
      },
      { x: 0, y: 0 }
    );
    allTiles.forEach((tile) => {
      tile.x = tile.x - minimums.x;
      tile.y = tile.y - minimums.y;
    });
  }

  /**
   * Positions and connects the module tiles in the road grid according to the given road connections.
   * Connections are performed in-place, road tiles and module tiles are modified.
   * @param module_tiles - The modules to connect
   * @param road_tiles - The road tiles to connect the modules to
   * @param roads - The road connections for the modules
   * @private
   */
  private positionModuleTiles(
    module_tiles: Map<string, FactoryModuleTile>,
    road_tiles: Map<string, FactoryRoadTile>,
    roads: FactoryRoadFlat[]
  ): void {
    // connect the modules to the road tiles
    for (const edge of roads) {
      const fromModule = module_tiles.get(edge.from);
      const toModule = module_tiles.get(edge.to);
      if (fromModule) {
        const toNode = road_tiles.get(edge.to);
        if (fromModule && toNode) {
          fromModule.direction = edge.direction;
          fromModule.intersection = toNode.id;
          const inverseDirectionUpdate = this.DIRECTION_UPDATES.find(
            (update) => update.inverse === edge.direction
          );
          if (inverseDirectionUpdate) {
            fromModule.x = toNode.x + inverseDirectionUpdate.xDiff;
            fromModule.y = toNode.y + inverseDirectionUpdate.yDiff;
            toNode.road[inverseDirectionUpdate.direction] = fromModule.id;
          }
        }
      } else if (toModule) {
        const fromNode = road_tiles.get(edge.from);
        if (toModule && fromNode) {
          const directionUpdate = this.DIRECTION_UPDATES.find(
            (update) => update.direction === edge.direction
          );
          if (directionUpdate) {
            toModule.x = fromNode.x + directionUpdate.xDiff;
            toModule.y = fromNode.y + directionUpdate.yDiff;
            toModule.direction = directionUpdate.inverse;
          }
          fromNode.road[edge.direction] = toModule.id;
          toModule.intersection = fromNode.id;
        }
      }
    }
  }

  /**
   * Create module tiles from a list of modules
   * @param modules
   * @private
   */
  private createModuleTiles(modules: Module[]): Map<string, FactoryModuleTile> {
    // Add the connected modules to the grid
    const module_tiles = new Map<string, FactoryModuleTile>();
    modules.forEach((n) =>
      module_tiles.set(n.serialNumber, {
        type: 'MODULE',
        id: n.serialNumber,
        x: 0,
        y: 0,
        direction: n.type === ModuleType.DPS ? RoadDirection.WEST : RoadDirection.EAST,
        connected: false,
        moduleType: n.type,
        placeholder: n.placeholder,
      })
    );
    return module_tiles;
  }

  /**
   * Create road tiles from a list of intersections and connect them using the given roads
   *
   * This function expects that all intersections are connected to a single road network.
   * The behaviour is undefined when the list contains unconnected intersections
   * @param intersections
   * @param roads
   * @private
   */
  private createPositionedRoadTiles(
    intersections: FactoryNode[],
    roads: FactoryRoadFlat[]
  ): Map<string, FactoryRoadTile> {
    const visited = new Set<string>();
    const road_tiles = new Map<string, FactoryRoadTile>();
    if (!intersections.length) {
      return road_tiles;
    }
    intersections.forEach((n) =>
      road_tiles.set(n.id, {
        type: 'ROAD',
        id: n.id,
        x: 0,
        y: 0,
        road: {},
      })
    );

    // create connections for the road grid
    for (const edge of roads) {
      const fromNode = road_tiles.get(edge.from);
      const toNode = road_tiles.get(edge.to);
      if (fromNode && toNode) {
        fromNode.road[edge.direction] = toNode.id;
        toNode.road[this.getInverseDirection(edge.direction)] = fromNode.id;
      }
    }
    // assume all road tiles are connected
    // walk through all nodes starting from the first
    let start = intersections[0].id;
    const stack: Array<FactoryRoadTile> = [road_tiles.get(start)!];

    // Traverse the graph using depth-first search to calculate the positions
    while (stack.length > 0) {
      const activeNode = stack.pop()!;

      for (const direction of this.DIRECTION_UPDATES) {
        const nodeid = activeNode.road[direction.direction];
        if (nodeid && !visited.has(nodeid)) {
          visited.add(nodeid);
          const connectedNode = road_tiles.get(nodeid);
          if (connectedNode) {
            connectedNode.x = activeNode.x + direction.xDiff;
            connectedNode.y = activeNode.y + direction.yDiff;
            stack.push(connectedNode);
          }
        }
      }
    }
    return road_tiles;
  }
}
