import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { firstValueFrom, of, shareReplay } from 'rxjs';
import {
  AvailableState,
  PairedModule,
  RoadDirection,
} from '../../common/protocol/ccu';
import { ModuleType } from '../../common/protocol/module';
import {
  FactoryGridLayout,
  FactoryLayoutService,
} from './factory-layout.service';
import { GridItem, LayoutEditorService } from './layout-editor.service';

const FACTORY_TEST_LAYOUT = {
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
    {
      id: '5',
    },
    {
      id: '6',
    },
  ],
  modules: [
    {
      serialNumber: 'kBix',
      type: 'DPS',
    },
    {
      serialNumber: 'yBix',
      type: 'HBW',
    },
    {
      serialNumber: '4Cjx',
      type: 'AIQS',
    },
    {
      serialNumber: 'ctxw',
      type: 'MILL',
    },
    {
      serialNumber: 'CHRG1',
      type: 'CHRG',
    },
  ],
  roads: [
    {
      direction: 'NORTH',
      from: '1',
      length: 360,
      to: '2',
    },
    {
      direction: 'NORTH',
      from: '3',
      length: 360,
      to: '4',
    },
    {
      direction: 'EAST',
      from: '3',
      length: 360,
      to: '1',
    },
    {
      direction: 'NORTH',
      from: '4',
      length: 360,
      to: '5',
    },
    {
      direction: 'EAST',
      from: '4',
      length: 360,
      to: '2',
    },
    {
      direction: 'EAST',
      from: '6',
      length: 360,
      to: '4',
    },
    {
      direction: 'NORTH',
      from: 'kBix',
      length: 380,
      to: '1',
    },
    {
      direction: 'NORTH',
      from: 'yBix',
      length: 380,
      to: '3',
    },
    {
      direction: 'EAST',
      from: '4Cjx',
      length: 380,
      to: '3',
    },
    {
      direction: 'SOUTH',
      from: 'ctxw',
      length: 380,
      to: '5',
    },
    {
      direction: 'WEST',
      from: 'CHRG1',
      length: 430,
      to: '2',
    },
  ],
};

const FACTORY_GRID_LAYOUT: FactoryGridLayout = [
  {
    id: '1',
    road: {
      NORTH: '2',
      SOUTH: 'kBix',
      WEST: '3',
    },
    type: 'ROAD',
    x: 2,
    y: 3,
  },
  {
    id: '2',
    road: {
      EAST: 'CHRG1',
      SOUTH: '1',
      WEST: '4',
    },
    type: 'ROAD',
    x: 2,
    y: 2,
  },
  {
    id: '3',
    road: {
      EAST: '1',
      NORTH: '4',
      SOUTH: 'yBix',
      WEST: '4Cjx',
    },
    type: 'ROAD',
    x: 1,
    y: 3,
  },
  {
    id: '4',
    road: {
      EAST: '2',
      NORTH: '5',
      SOUTH: '3',
      WEST: '6',
    },
    type: 'ROAD',
    x: 1,
    y: 2,
  },
  {
    id: '5',
    road: {
      NORTH: 'ctxw',
      SOUTH: '4',
    },
    type: 'ROAD',
    x: 1,
    y: 1,
  },
  {
    id: '6',
    road: {
      EAST: '4',
    },
    type: 'ROAD',
    x: 0,
    y: 2,
  },
  {
    connected: false,
    direction: RoadDirection.NORTH,
    id: 'kBix',
    intersection: '1',
    moduleType: ModuleType.DPS,
    type: 'MODULE',
    x: 2,
    y: 4,
  },
  {
    connected: false,
    direction: RoadDirection.NORTH,
    id: 'yBix',
    intersection: '3',
    moduleType: ModuleType.HBW,
    type: 'MODULE',
    x: 1,
    y: 4,
  },
  {
    connected: false,
    direction: RoadDirection.EAST,
    id: '4Cjx',
    intersection: '3',
    moduleType: ModuleType.AIQS,
    type: 'MODULE',
    x: 0,
    y: 3,
  },
  {
    connected: false,
    direction: RoadDirection.SOUTH,
    id: 'ctxw',
    intersection: '5',
    moduleType: ModuleType.MILL,
    type: 'MODULE',
    x: 1,
    y: 0,
  },
  {
    connected: false,
    direction: RoadDirection.WEST,
    id: 'CHRG1',
    intersection: '2',
    moduleType: ModuleType.CHRG,
    type: 'MODULE',
    x: 3,
    y: 2,
  },
];

const FACTORY_EXPECTED_GRID = [
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'id': '1',
      'road': {
        'NORTH': '2',
        'SOUTH': 'kBix',
        'WEST': '3',
      },
      'type': 'ROAD',
      'x': 2,
      'y': 3,
    },
    'x': 2,
    'y': 3,
  },
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'id': '2',
      'road': {
        'EAST': 'CHRG1',
        'SOUTH': '1',
        'WEST': '4',
      },
      'type': 'ROAD',
      'x': 2,
      'y': 2,
    },
    'x': 2,
    'y': 2,
  },
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'id': '3',
      'road': {
        'EAST': '1',
        'NORTH': '4',
        'SOUTH': 'yBix',
        'WEST': '4Cjx',
      },
      'type': 'ROAD',
      'x': 1,
      'y': 3,
    },
    'x': 1,
    'y': 3,
  },
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'id': '4',
      'road': {
        'EAST': '2',
        'NORTH': '5',
        'SOUTH': '3',
        'WEST': '6',
      },
      'type': 'ROAD',
      'x': 1,
      'y': 2,
    },
    'x': 1,
    'y': 2,
  },
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'id': '5',
      'road': {
        'NORTH': 'ctxw',
        'SOUTH': '4',
      },
      'type': 'ROAD',
      'x': 1,
      'y': 1,
    },
    'x': 1,
    'y': 1,
  },
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'id': '6',
      'road': {
        'EAST': '4',
      },
      'type': 'ROAD',
      'x': 0,
      'y': 2,
    },
    'x': 0,
    'y': 2,
  },
  {
    'cols': 2,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'connected': false,
      'direction': 'NORTH',
      'id': 'kBix',
      'intersection': '1',
      'moduleType': 'DPS',
      'type': 'MODULE',
      'x': 2,
      'y': 4,
    },
    'x': 2,
    'y': 4,
  },
  {
    'cols': 2,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'connected': false,
      'direction': 'NORTH',
      'id': 'yBix',
      'intersection': '3',
      'moduleType': 'HBW',
      'type': 'MODULE',
      'x': 1,
      'y': 4,
    },
    'x': 0,
    'y': 4,
  },
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'connected': false,
      'direction': 'EAST',
      'id': '4Cjx',
      'intersection': '3',
      'moduleType': 'AIQS',
      'type': 'MODULE',
      'x': 0,
      'y': 3,
    },
    'x': 0,
    'y': 3,
  },
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'connected': false,
      'direction': 'SOUTH',
      'id': 'ctxw',
      'intersection': '5',
      'moduleType': 'MILL',
      'type': 'MODULE',
      'x': 1,
      'y': 0,
    },
    'x': 1,
    'y': 0,
  },
  {
    'cols': 1,
    'resizeEnabled': false,
    'rows': 1,
    'tile': {
      'connected': false,
      'direction': 'WEST',
      'id': 'CHRG1',
      'intersection': '2',
      'moduleType': 'CHRG',
      'type': 'MODULE',
      'x': 3,
      'y': 2,
    },
    'x': 3,
    'y': 2,
  },
];


describe('LayoutEditorService', () => {
  let service: LayoutEditorService;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      providers: [
        MockProvider(FactoryLayoutService, {
          currentGridLayout$: of([]).pipe(shareReplay(1)),
          pairedModules$: of([]).pipe(shareReplay(1)),
        }),
      ],
    });
    service = TestBed.inject(LayoutEditorService);
  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });

  it('should create a grid from the given layout', () => {
    const layout = service.convertGridLayoutToLayout(FACTORY_GRID_LAYOUT);
    expect(layout).toEqual(FACTORY_TEST_LAYOUT);
  });

  it('should reject if a module is not connected', () => {
    const grid: FactoryGridLayout = [
      {
        type: 'MODULE',
        y: 2,
        x: 2,
        id: 'modid',
        moduleType: ModuleType.DRILL,
        direction: RoadDirection.EAST,
        connected: false,
      },
      { type: 'ROAD', y: 3, x: 1, id: '2', road: {} },
    ];

    expect(service.validateGridLayout(grid)).toBe(false);
  });

  it('should accept if all elements are connected', () => {
    const grid: FactoryGridLayout = [
      {
        type: 'MODULE',
        y: 2,
        x: 3,
        id: 'modid',
        moduleType: ModuleType.DRILL,
        direction: RoadDirection.EAST,
        connected: false,
        intersection: '2',
      },
      {
        type: 'ROAD',
        y: 2,
        x: 2,
        id: '2',
        road: { SOUTH: '1', EAST: 'modid' },
      },
      { type: 'ROAD', y: 3, x: 2, id: '1', road: { NORTH: '2' } },
    ];

    expect(service.validateGridLayout(grid)).toBe(true);
  });

  it('should accept if an element is not connected', () => {
    const grid: FactoryGridLayout = [
      {
        type: 'MODULE',
        y: 2,
        x: 3,
        id: 'modid',
        moduleType: ModuleType.DRILL,
        direction: RoadDirection.EAST,
        connected: false,
        intersection: '2',
      },
      { type: 'ROAD', y: 2, x: 2, id: '2', road: { EAST: 'modid' } },
      { type: 'ROAD', y: 3, x: 2, id: '1', road: {} },
    ];

    expect(service.validateGridLayout(grid)).toBe(false);
  });

  it('should add grid items', async () => {
    const expectedWithOne = [
      {
        cols: 1,
        rows: 1,
        tile: {
          id: '1',
          road: {},
          type: 'ROAD',
          x: 0,
          y: 0,
        },
        x: 0,
        y: 0,
      },
    ];
    const expectedWithTwo = [
      {
        cols: 1,
        rows: 1,
        tile: {
          id: '1',
          road: {
            EAST: '2',
          },
          type: 'ROAD',
          x: 0,
          y: 0,
        },
        x: 0,
        y: 0,
      },
      {
        cols: 1,
        rows: 1,
        tile: {
          id: '2',
          road: {
            WEST: '1',
          },
          type: 'ROAD',
          x: 1,
          y: 0,
        },
        x: 1,
        y: 0,
      },
    ];
    const newItem: GridItem = {
      tile: {
        type: 'ROAD',
        road: {},
        id: '1',
        x: 0,
        y: 0,
      },
      x: 0,
      y: 0,
      rows: 1,
      cols: 1,
    };
    service.addItem(newItem);
    await expect(firstValueFrom(service.editorGrid$)).resolves.toEqual(
      expectedWithOne
    );

    const newItem2: GridItem = {
      tile: {
        type: 'ROAD',
        road: {},
        id: '2',
        x: 1,
        y: 0,
      },
      x: 1,
      y: 0,
      rows: 1,
      cols: 1,
    };
    service.addItem(newItem2);
    await expect(firstValueFrom(service.editorGrid$)).resolves.toEqual(
      expectedWithTwo
    );
  });

  it('should generate the available modules from the paired modules and empty grids', async () => {
    const modules = of<PairedModule[]>([
      {
        type: 'MODULE',
        subType: ModuleType.HBW,
        available: AvailableState.BLOCKED,
        connected: false,
        serialNumber: 'serial',
      },
    ]);
    const expectedModules = [
      {
        available: 'BLOCKED',
        connected: false,
        serialNumber: 'serial',
        subType: 'HBW',
        type: 'MODULE',
      },
    ];
    const availableModules = await firstValueFrom(
      service._getAvailableModules(modules, of([]), of([]))
    );
    expect(availableModules).toEqual(expectedModules);
  });

  it('should convert the layout to a grid', async () => {
    service.updateEditorGrid(FACTORY_GRID_LAYOUT);
    await expect(firstValueFrom(service.editorGrid$)).resolves.toEqual(FACTORY_EXPECTED_GRID)
  })
});
