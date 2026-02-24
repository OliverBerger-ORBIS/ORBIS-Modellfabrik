import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { BehaviorSubject, EMPTY } from 'rxjs';
import { CcuTopic } from '../../../common/protocol';
import { FactoryLayout, RoadDirection } from '../../../common/protocol/ccu';
import { ModuleType } from '../../../common/protocol/module';
import { TypedMqttService } from '../../futurefactory.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { FactoryLayoutService } from '../../services/factory-layout.service';
import { OrderStatesService } from '../../services/order-states.service';
import { StatesService } from '../../services/states.service';
import { FactoryLayoutComponent } from './factory-layout.component';

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

describe('FactoryLayoutComponent', () => {
  let component: FactoryLayoutComponent;
  let fixture: ComponentFixture<FactoryLayoutComponent>;
  let hasRunningOrdersSubject: BehaviorSubject<boolean>;
  let typedMqttService: jest.Mocked<TypedMqttService>;
  let statesService: jest.Mocked<StatesService>;

  beforeEach(async () => {
    hasRunningOrdersSubject = new BehaviorSubject<boolean>(false);
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [FactoryLayoutComponent],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: jest.fn(() => EMPTY),
          publish: jest.fn(),
        }),
        MockProvider(OrderStatesService, {
          hasRunningOrders$: hasRunningOrdersSubject.asObservable(),
        }),
        MockProvider(StatesService, {
          pairingState$: EMPTY,
          pairedModules$: EMPTY,
          pairedTransports$: EMPTY,
        }),
      ],
    }).compileComponents();

    typedMqttService = TestBed.inject(
      TypedMqttService
    ) as jest.Mocked<TypedMqttService>;
    statesService = TestBed.inject(StatesService) as jest.Mocked<StatesService>;

    fixture = TestBed.createComponent(FactoryLayoutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the component', () => {
    expect(fixture).toMatchSnapshot();
  });

  it('should save the layout, if no order is running', async () => {
    await component.saveLayout();
    expect(typedMqttService.publish).toHaveBeenCalledWith(
      CcuTopic.SET_LAYOUT,
      expect.any(Object)
    );
  });

  it("shouldn't save the layout, if an order is running", async () => {
    hasRunningOrdersSubject.next(true);
    await component.saveLayout();
    expect(typedMqttService.publish).not.toHaveBeenCalledWith(
      CcuTopic.SET_LAYOUT,
      expect.any(Object)
    );
  });

  it('should create a grid from the given layout', () => {
    const editor = new FactoryLayoutService(typedMqttService, statesService);
    const grid = editor.layoutToGridLayout(FACTORY_TEST_LAYOUT);
    expect(grid).toEqual(EXPECTED_FACTORY_GRID_LAYOUT);
  });
});
