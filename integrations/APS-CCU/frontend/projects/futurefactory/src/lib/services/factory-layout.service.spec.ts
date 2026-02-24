import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { FactoryLayout, RoadDirection } from '../../common/protocol/ccu';
import { ModuleType } from '../../common/protocol/module';
import { TypedMqttService } from '../futurefactory.service';
import { FactoryLayoutService } from './factory-layout.service';
import { StatesService } from './states.service';

const FACTORY_TEST_LAYOUT: FactoryLayout = {
  modules: [
    {
      type: ModuleType.DPS,
      serialNumber: 'kBix',
    },
    {
      type: ModuleType.HBW,
      serialNumber: 'yBix',
    },
    {
      type: ModuleType.AIQS,
      serialNumber: '4Cjx',
    },
    {
      type: ModuleType.MILL,
      serialNumber: 'ctxw',
    },
    {
      type: ModuleType.DRILL,
      serialNumber: 'xULx',
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
    {
      id: '5',
    },
    {
      id: '6',
    },
  ],
  roads: [
    {
      from: 'kBix',
      to: '1',
      length: 320,
      direction: RoadDirection.NORTH,
    },
    {
      from: '1',
      to: '2',
      length: 400,
      direction: RoadDirection.NORTH,
    },
    {
      from: '1',
      to: '3',
      length: 400,
      direction: RoadDirection.WEST,
    },
    {
      from: '2',
      to: 'xULx',
      length: 320,
      direction: RoadDirection.EAST,
    },
    {
      from: '2',
      to: '4',
      length: 400,
      direction: RoadDirection.WEST,
    },
    {
      from: '3',
      to: 'yBix',
      length: 320,
      direction: RoadDirection.SOUTH,
    },
    {
      from: '3',
      to: '4Cjx',
      length: 320,
      direction: RoadDirection.WEST,
    },
    {
      from: '3',
      to: '4',
      length: 400,
      direction: RoadDirection.NORTH,
    },
    {
      from: '4',
      to: '6',
      length: 400,
      direction: RoadDirection.WEST,
    },
    {
      from: '4',
      to: '5',
      length: 400,
      direction: RoadDirection.NORTH,
    },
    {
      from: '5',
      to: 'ctxw',
      length: 320,
      direction: RoadDirection.NORTH,
    },
  ],
};
const EXPECTED_FACTORY_GRID_LAYOUT = [
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
      EAST: 'xULx',
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
    direction: 'NORTH',
    id: 'kBix',
    intersection: '1',
    moduleType: 'DPS',
    type: 'MODULE',
    x: 2,
    y: 4,
  },
  {
    connected: false,
    direction: 'NORTH',
    id: 'yBix',
    intersection: '3',
    moduleType: 'HBW',
    type: 'MODULE',
    x: 1,
    y: 4,
  },
  {
    connected: false,
    direction: 'EAST',
    id: '4Cjx',
    intersection: '3',
    moduleType: 'AIQS',
    type: 'MODULE',
    x: 0,
    y: 3,
  },
  {
    connected: false,
    direction: 'SOUTH',
    id: 'ctxw',
    intersection: '5',
    moduleType: 'MILL',
    type: 'MODULE',
    x: 1,
    y: 0,
  },
  {
    connected: false,
    direction: 'WEST',
    id: 'xULx',
    intersection: '2',
    moduleType: 'DRILL',
    type: 'MODULE',
    x: 3,
    y: 2,
  },
];

describe('FactoryLayoutService', () => {
  let service: FactoryLayoutService;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: jest.fn(() => EMPTY),
          publish: jest.fn(),
        }),
        MockProvider(StatesService, {
          pairingState$: EMPTY,
          pairedModules$: EMPTY,
          pairedTransports$: EMPTY,
        }),
      ],
    });
    service = TestBed.inject(FactoryLayoutService);
  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });

  it('should create a grid from the given layout', () => {
    const grid = service.layoutToGridLayout(FACTORY_TEST_LAYOUT);
    expect(grid).toEqual(EXPECTED_FACTORY_GRID_LAYOUT);
  });

  it('should create an empty grid for an empty layout', () => {
    const grid = service.layoutToGridLayout({
      roads: [],
      intersections: [],
      modules: [],
    });
    expect(grid).toEqual([]);
  });
});
