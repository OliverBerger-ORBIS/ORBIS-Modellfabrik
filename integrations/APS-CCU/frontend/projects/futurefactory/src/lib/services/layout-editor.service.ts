import { Injectable, OnDestroy } from '@angular/core';
import { GridsterItem } from 'angular-gridster2';
import { BehaviorSubject, combineLatest, map, Observable, shareReplay, startWith, Subject, } from 'rxjs';
import { FactoryLayout, PairedModule, RoadDirection, } from '../../common/protocol/ccu';
import { ModuleType } from '../../common/protocol/module';
import { FactoryGridLayout, FactoryLayoutService, FactoryModuleTile, FactoryRoadTile, } from './factory-layout.service';

export interface GridItem extends GridsterItem {
  tile: FactoryModuleTile | FactoryRoadTile;
}

/** length of the docking path to a module in mm */
const DOCKING_ROAD_LENGTH = 380;
/** length of the docking path for the charger in mm */
const CHARGER_ROAD_LENGTH = 430;
/** length of the road between intersections in mm */
const ROAD_LENGTH = 360;

@Injectable({
  providedIn: 'root',
})
export class LayoutEditorService implements OnDestroy {
  // next direction in clockwise order
  private readonly NEXT_DIRECTIONS_CLOCKWISE: Record<
    RoadDirection,
    RoadDirection
  > = {
    [RoadDirection.NORTH]: RoadDirection.EAST,
    [RoadDirection.EAST]: RoadDirection.SOUTH,
    [RoadDirection.SOUTH]: RoadDirection.WEST,
    [RoadDirection.WEST]: RoadDirection.NORTH,
  };
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

  private readonly EXTRA_TILE_OFFSETS_FOR_MODULES: Record<
    string,
    {
      [key in RoadDirection]: { x: number; y: number, cols: number, rows: number };
    }
  > = {
    [ModuleType.DPS]: {
      [RoadDirection.NORTH]: { x: 0, y: 0, cols: 2, rows: 1 },
      [RoadDirection.EAST]: { x: 0, y: 0, cols:  1, rows: 2 },
      [RoadDirection.SOUTH]: { x: -1, y: 0, cols: 2, rows: 1 },
      [RoadDirection.WEST]: { x: 0, y: -1, cols: 1, rows: 2 },
    },
    [ModuleType.HBW]: {
      [RoadDirection.NORTH]: { x: -1, y: 0, cols: 2, rows: 1 },
      [RoadDirection.EAST]: { x: 0, y: -1, cols:  1, rows: 2 },
      [RoadDirection.SOUTH]: { x: 0, y: 0, cols: 2, rows: 1 },
      [RoadDirection.WEST]: { x: 0, y: 0, cols: 1, rows: 2 },
    },
  };

  private grid: GridItem[] = [];
  private _modified = false;

  public get modified() {
    return this._modified;
  }

  private destroyed$ = new Subject<void>();
  private gridSubject: BehaviorSubject<GridItem[]> = new BehaviorSubject<
    GridItem[]
  >([]);
  readonly editorGrid$: Observable<GridItem[]> =
    this.gridSubject.asObservable();
  private baseLayout: FactoryGridLayout = [];

  readonly availableModules$: Observable<PairedModule[]>;

  constructor(private layoutService: FactoryLayoutService) {
    // internal subscription to always update the grid
    this.layoutService.currentGridLayout$.subscribe((layout) => {
      this.baseLayout = layout; // store layout for grid reset
      this.updateEditorGrid(layout);
    });
    this.availableModules$ = this._getAvailableModules(
      this.layoutService.pairedModules$.pipe(startWith([])),
      this.editorGrid$,
      this.layoutService.currentGridLayout$
    );
  }

  ngOnDestroy(): void {
    this.destroyed$.next();
    this.destroyed$.complete();
  }

  /**
   * Determine the list of modules to show in the list
   * @param modules$
   * @param editorGrid$
   * @param currentGridLayout$
   * @private
   */
  _getAvailableModules(
    modules$: Observable<PairedModule[]>,
    editorGrid$: Observable<GridItem[]>,
    currentGridLayout$: Observable<FactoryGridLayout>
  ): Observable<PairedModule[]> {
    // This method is not marked as private to be able to test it directly.

    const availableModules$ = combineLatest([
      modules$,
      editorGrid$,
      currentGridLayout$,
    ]).pipe(
      map(([mods, grid, currentGridLayout]) => {
        const modulesInLayout = currentGridLayout.filter(
          (mod): mod is FactoryModuleTile => mod.type === 'MODULE'
        );
        const modules = [...mods];
        for (const module of modulesInLayout) {
          // add modules that are
          if (
            !modules.find((checkMod) => checkMod.serialNumber === module.id)
          ) {
            modules.push({
              type: 'MODULE',
              subType: module.moduleType,
              connected: false,
              serialNumber: module.id,
            });
          }
        }
        return modules.filter(
          (mod) =>
            mod.type === 'MODULE' &&
            !grid.find((item) => item.tile.id === mod.serialNumber)
        );
      }),
      shareReplay(1)
    );

    return availableModules$;
  }

  public isLargeModule(moduleType: ModuleType): boolean {
    return this.layoutService.isLargeModule(moduleType);
  }

  public hasGridItemId(id: string): boolean {
    return this.grid.find(item => item.tile.id === id) != undefined;
  }

  /**
   * Add all elements that are part of the currently used factory layout and remove all others
   * @param layout
   */
  updateEditorGrid(layout: FactoryGridLayout) {
    if (this._modified) {
      return;
    }
    // first remove all deleted elements
    this.grid = this.grid.filter(item => layout.find(tile => tile.id === item.tile.id))
    // then fill in the changed or added elements
    for (const tile of layout) {
      const gridItem = this.grid.find((item) => item.tile.id === tile.id);
      let offX = 0, offY = 0, rows = 1, cols = 1;
      if (tile.type === 'MODULE') {
        const modifiers = this.EXTRA_TILE_OFFSETS_FOR_MODULES[tile.moduleType]?.[tile.direction];
        if (modifiers) {
          offX = modifiers.x;
          offY = modifiers.y;
          rows = modifiers.rows;
          cols = modifiers.cols;
        }
      }
      if (!gridItem) {
        this.grid.push({
          tile: JSON.parse(JSON.stringify(tile)), // deep copy
          x: tile.x + offX,
          y: tile.y + offY,
          rows: rows,
          cols: cols,
          resizeEnabled: false,
        });
      } else {
        // move existing items
        gridItem.tile = JSON.parse(JSON.stringify(tile)); // deep copy
        gridItem.x = tile.x + offX;
        gridItem.y = tile.y + offY;
        gridItem.rows = rows;
        gridItem.cols = cols;
      }
    }
    this.moveToPositiveCoordinates(this.grid);
    this.gridSubject.next(this.grid);
  }

  private moveToPositiveCoordinates(grid: GridItem[]) {
    const minX = grid.reduce((minimum, item) => Math.min(item.x, minimum), 0 );
    const minY = grid.reduce((minimum, item) => Math.min(item.y, minimum), 0 );
    for (const item of grid) {
      item.x -= minX;
      item.y -= minY;
      item.tile.x -= minX;
      item.tile.y -= minY;
    }
  }

  resetLayout() {
    this.grid = [];
    this._modified = false;
    this.updateEditorGrid(this.baseLayout);
  }

  getNextId(): string {
    const ids = this.grid
      .filter((item) => item.tile.type === 'ROAD')
      .map((item) => Number(item.tile.id));
    if (!ids.length) {
      return '1';
    }
    return String(Math.max(...ids) + 1);
  }

  private getGridItemAtTilePosition(x: number, y: number): GridItem | undefined {
    return this.grid.find((item) => item.tile.x === x && item.tile.y === y);
  }
  private hasOverlappingItem(needle: GridItem) {
    return this.grid.find(item => (! ((item.x >= (needle.x + needle.cols) ||
        (item.x + item.cols) <= needle.x ||
        item.y >= (needle.y + needle.rows) ||
          (item.y + item.rows) <= needle.y))) && needle !== item )
  }

  public deleteGridItem(changed: GridItem) {
    this._modified = true;
    this.clearItemAssociations(changed);
    this.grid = this.grid.filter((item) => item !== changed);
    this.gridSubject.next(this.grid);
  }

  private clearItemAssociations(changed: GridItem) {
    // delete old associations
    for (const item of this.grid) {
      if (
        item !== changed &&
        item.tile.type === 'MODULE' &&
        item.tile.intersection === changed.tile.id
      ) {
        item.tile.intersection = undefined;
      } else if (item !== changed && item.tile.type === 'ROAD') {
        const roads = item.tile.road;
        for (const dir of Object.keys(roads) as RoadDirection[]) {
          if (roads[dir] === changed.tile.id) {
            roads[dir] = undefined;
          }
        }
      }
    }
  }

  /**
   * After a tile has been moved, update its connections
   * @param changed
   */
  updateMovedGridItem(changed: GridItem) {
    this._modified = true;
    changed.tile.x = changed.x;
    changed.tile.y = changed.y;
    if (changed.tile.type === 'MODULE') {
      const modifiers = this.EXTRA_TILE_OFFSETS_FOR_MODULES[changed.tile.moduleType]?.[changed.tile.direction];
      if (modifiers) {
        changed.tile.x -= modifiers.x;
        changed.tile.y -= modifiers.y;
      }
    }

    // delete old associations
    this.clearItemAssociations(changed);

    // create new associations
    if (changed.tile.type === 'ROAD') {
      this.rebuildConnectionsForRoad(changed);
    } else if (changed.tile.type === 'MODULE') {
      this.rebuildConnectionsForModule(changed);
    }
    this.moveToPositiveCoordinates(this.grid);
    this.gridSubject.next(this.grid);
  }

  /**
   * Connects a module to a road tile
   * @param changed
   * @private
   */
  private rebuildConnectionsForModule(changed: GridItem) {
    if (changed.tile.type !== 'MODULE') {
      return;
    }
    changed.tile.intersection = undefined;
    const lastDirection = changed.tile.direction;
    const startIndex = Math.max(
      0,
      this.DIRECTION_UPDATES.findIndex(
        (update) => update.direction === lastDirection
      )
    );

    for (
      let i = 0;
      i < this.DIRECTION_UPDATES.length && !changed.tile.intersection;
      ++i
    ) {
      // loop through the complete array starting at any chosen index
      const update =
        this.DIRECTION_UPDATES[
          (i + startIndex) % this.DIRECTION_UPDATES.length
        ];
      // road connection is moved along the x or y axis depending on the large module type
      let xPos = changed.tile.x + update.xDiff;
      let yPos = changed.tile.y + update.yDiff;
      const item = this.getGridItemAtTilePosition(xPos, yPos);

      if (item && item.tile.type === 'ROAD') {
        changed.tile.direction = update.direction;
        const modifiers = this.EXTRA_TILE_OFFSETS_FOR_MODULES[changed.tile.moduleType]?.[update.direction];
        if (modifiers) {
          changed.x = changed.tile.x + modifiers.x;
          changed.y = changed.tile.y + modifiers.y;
          changed.rows = modifiers.rows;
          changed.cols = modifiers.cols;
          console.log(modifiers)
        }
        if (!this.hasOverlappingItem(changed)) {
          changed.tile.intersection = item.tile.id;
          item.tile.road[update.inverse] = changed.tile.id;
        }
        break;
      }
    }
  }

  /**
   * Connects a road tile to all neighboring tiles.
   * @param changed
   * @private
   */
  private rebuildConnectionsForRoad(changed: GridItem) {
    if (changed.tile.type !== 'ROAD') {
      return;
    }
    changed.tile.road['NORTH'] = undefined;
    changed.tile.road['EAST'] = undefined;
    changed.tile.road['SOUTH'] = undefined;
    changed.tile.road['WEST'] = undefined;
    for (const update of this.DIRECTION_UPDATES) {
      const item = this.getGridItemAtTilePosition(
        changed.tile.x + update.xDiff,
        changed.tile.y + update.yDiff
      );
      if (item) {
        changed.tile.road[update.direction] = item.tile.id;
        if (item.tile.type === 'ROAD') {
          item.tile.road[update.inverse] = changed.tile.id;
        } else if (item.tile.type === 'MODULE' && !item.tile.intersection) {
          const modifiers = this.EXTRA_TILE_OFFSETS_FOR_MODULES[item.tile.moduleType]?.[update.inverse];
          const oldX = item.x;
          const oldY = item.y;
          const oldRows = item.rows;
          const oldCols = item.cols;
          if (modifiers) {
            item.x = item.tile.x + modifiers.x;
            item.y = item.tile.y + modifiers.y;
            item.rows = modifiers.rows;
            item.cols = modifiers.cols;
            console.log(modifiers)
          }
          if (this.hasOverlappingItem(item)) {
            item.x = oldX
            item.y = oldY
            item.rows = oldRows
            item.cols = oldCols
          } else {
            item.tile.direction = update.inverse;
            item.tile.intersection = changed.tile.id;
          }
        }
      }
    }
  }

  addItem(item: GridItem) {
    this.grid = [...this.grid, item];
    this.updateMovedGridItem(item);
  }

  /**
   * Rotates the direction a module uses to connect to a road clockwise.
   * @param item
   */
  rotateModuleConnection(item: GridItem) {
    console.log("olditem", item)
    if (item.tile.type === 'MODULE') {
      const oldDirection = item.tile.direction;
      const directionIndex = this.DIRECTION_UPDATES.findIndex(
        (update) => update.direction === oldDirection
      );
      const nextIndex = (directionIndex + 1) % this.DIRECTION_UPDATES.length;
      item.tile.direction = this.DIRECTION_UPDATES[nextIndex].direction;
      const modifier = this.EXTRA_TILE_OFFSETS_FOR_MODULES[item.tile.moduleType]?.[item.tile.direction];
      if (modifier) {
        item.rows = modifier.rows;
        item.cols = modifier.cols;
        item.x = item.tile.x + modifier.x;
        item.y = item.tile.y + modifier.y;
      }
      console.log(modifier)
      console.log(item)
      // rotate the tile by switching the rows and cols

      this.updateMovedGridItem(item);
    }
  }

  public convertGridLayoutToLayout(grid: FactoryGridLayout): FactoryLayout {
    const layout: FactoryLayout = { modules: [], intersections: [], roads: [] };
    for (const tile of grid) {
      switch (tile.type) {
        case 'MODULE':
          layout.modules.push({
            type: tile.moduleType,
            serialNumber: tile.id,
            placeholder: tile.placeholder
          });
          if (tile.intersection) {
            layout.roads.push({
              direction: tile.direction,
              from: tile.id,
              to: tile.intersection,
              length: (tile.moduleType === ModuleType.CHRG ? CHARGER_ROAD_LENGTH : DOCKING_ROAD_LENGTH),
            });
          }
          break;
        case 'ROAD':
          layout.intersections.push({
            id: tile.id,
          });
          // only add NORTH and EAST connections to other intersections to avoid duplicates
          for (const update of this.DIRECTION_UPDATES) {
            if (
              update.direction === RoadDirection.NORTH ||
              update.direction === RoadDirection.EAST
            ) {
              const targetId = tile.road[update.direction];
              if (targetId) {
                const target = grid.find(
                  (value) => value.id === tile.road[update.direction]
                );
                // do not add connections to modules, that is done from the module side
                if (target && target.type !== 'MODULE') {
                  layout.roads.push({
                    length: ROAD_LENGTH,
                    from: tile.id,
                    to: targetId,
                    direction: update.direction,
                  });
                }
              }
            }
          }
          break;
      }
    }
    return layout;
  }

  public async getNewGridLayout(): Promise<FactoryGridLayout> {
    return this.convertGridToGridLayout(this.grid);
  }
  public convertGridToGridLayout(grid: Array<GridItem>): FactoryGridLayout {
    return grid.map((item) => item.tile);
  }

  /**
   * Verifies all modules are connected to an intersection and there is only a single network that connects all tiles
   * @param grid
   */
  public validateGridLayout(grid: FactoryGridLayout): boolean {
    const notVisited = new Set(grid.map((tile) => tile.id));
    if (notVisited.size) {
      const stack: Array<string> = [grid[0].id];
      while (stack.length) {
        const activeId = stack.pop();
        const activeTile = grid.find((tile) => tile.id === activeId);
        if (!activeId || !activeTile || !notVisited.has(activeTile.id)) {
          continue;
        }
        notVisited.delete(activeTile.id);
        switch (activeTile.type) {
          case 'ROAD':
            for (const update of this.DIRECTION_UPDATES) {
              const id = activeTile.road[update.direction];
              if (id && notVisited.has(id)) {
                stack.push(id);
              }
            }
            break;
          case 'MODULE':
            const id = activeTile.intersection;
            if (!id) {
              return false; // a module has to be connected
            } else if (notVisited.has(id)) {
              stack.push(id);
            }
            break;
        }
      }
    }
    // starting from the first tile all tiles have to be reachable
    return notVisited.size === 0;
  }

  /**
   * Notify the service that the layout has been saved and the next layout update will be accepted
   */
  public setLayoutSaved() {
    this._modified = false;
  }
}
