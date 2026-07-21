import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { SimpleChange } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ShopfloorPreviewComponent } from './shopfloor-preview.component';
import { ModuleNameService } from '../../services/module-name.service';
import { ShopfloorMappingService } from '../../services/shopfloor-mapping.service';
import { ShopfloorLayoutService } from '../../services/shopfloor-layout.service';
import { ShopfloorRotationService } from '../../services/shopfloor-rotation.service';

describe('ShopfloorPreviewComponent', () => {
  let fixture: ComponentFixture<ShopfloorPreviewComponent>;
  let component: ShopfloorPreviewComponent;

  const rotation$ = new BehaviorSubject<'none' | 'cw90' | 'ccw90' | 'rot180'>('none');

  const layoutConfig = {
    metadata: { canvas: { width: 200, height: 120 } },
    scaling: { default_percent: 60 },
    icon_sizing_rules: { by_role: { default: 0.75 } },
    parsed_roads: [
      {
        from: { ref: 'serial:SVR3QA0022', center: { x: 40, y: 40 } },
        to: { ref: 'intersection:1', center: { x: 100, y: 40 } },
        length: 60,
        direction: 'EAST',
      },
      {
        from: { ref: 'intersection:1', center: { x: 100, y: 40 } },
        to: { ref: 'serial:SVR4H76530', center: { x: 160, y: 40 } },
        length: 60,
        direction: 'EAST',
      },
    ],
    modules_by_serial: {
      SVR3QA0022: { cell_id: 'hbw-cell' },
      SVR4H76530: { cell_id: 'aiqs-cell' },
    },
    intersection_map: {
      '1': 'ix-1',
    },
    cells: [
      {
        id: 'hbw-cell',
        name: 'HBW',
        role: 'module',
        serial: 'SVR3QA0022',
        position: { x: 20, y: 20 },
        size: { w: 40, h: 40 },
        show_name: true,
      },
      {
        id: 'aiqs-cell',
        name: 'AIQS',
        role: 'module',
        serial: 'SVR4H76530',
        position: { x: 140, y: 20 },
        size: { w: 40, h: 40 },
        show_name: true,
      },
      {
        id: 'ix-1',
        name: 'I1',
        role: 'intersection',
        position: { x: 95, y: 35 },
        size: { w: 10, h: 10 },
      },
    ],
  } as any;

  beforeEach(async () => {
    const httpMock = {
      get: jest.fn(() => of('<svg/>')),
    };
    const moduleNameMock = {
      getModuleFullName: (key: string) => key,
      getModuleDisplayName: (key: string) => ({ fullName: key, shortName: key }),
    };
    const mappingMock = {
      initializeLayout: jest.fn(),
      getAgvColor: jest.fn(() => '#f97316'),
    };
    const layoutServiceMock = {
      config$: of(layoutConfig),
    };
    const rotationMock = {
      current: 'none' as const,
      rotation$: rotation$.asObservable(),
    };

    await TestBed.configureTestingModule({
      imports: [ShopfloorPreviewComponent],
      providers: [
        { provide: HttpClient, useValue: httpMock },
        { provide: ModuleNameService, useValue: moduleNameMock },
        { provide: ShopfloorMappingService, useValue: mappingMock },
        { provide: ShopfloorLayoutService, useValue: layoutServiceMock },
        { provide: ShopfloorRotationService, useValue: rotationMock },
      ],
    })
      .compileComponents();

    fixture = TestBed.createComponent(ShopfloorPreviewComponent);
    component = fixture.componentInstance;
    component.order = null;
    fixture.detectChanges();
  });

  it('renders planned/traveled FTS layers and suppresses active route layer', () => {
    component.ftsRoutePlannedSegments = [{ x1: 10, y1: 10, x2: 50, y2: 10 }];
    component.ftsRouteTraveledSegments = [{ x1: 10, y1: 10, x2: 20, y2: 10 }];
    component.ngOnChanges({
      ftsRoutePlannedSegments: new SimpleChange(null, component.ftsRoutePlannedSegments, false),
      ftsRouteTraveledSegments: new SimpleChange(null, component.ftsRouteTraveledSegments, false),
    });

    const vm = component.viewModel as any;
    expect(vm.ftsPlannedRouteSegments?.length).toBe(1);
    expect(vm.ftsTraveledRouteSegments?.length).toBe(1);
    expect(vm.activeRouteSegments).toBeUndefined();
  });

  it('builds order active route when no FTS route layers are provided', () => {
    component.activeStep = {
      type: 'NAVIGATION',
      source: 'SVR3QA0022',
      target: 'SVR4H76530',
    } as any;
    component.ftsRoutePlannedSegments = null;
    component.ftsRouteTraveledSegments = null;
    component.ngOnChanges({
      activeStep: new SimpleChange(null, component.activeStep, false),
    });

    const vm = component.viewModel as any;
    expect(vm.activeRouteSegments?.length).toBeGreaterThan(0);
    expect(vm.ftsPlannedRouteSegments).toBeUndefined();
    expect(vm.ftsTraveledRouteSegments).toBeUndefined();
  });

  it('finds first BUSY station and skips duplicate follow-scroll target', () => {
    const anyComponent = component as any;
    component.moduleStatusMap = new Map([
      ['hbw-cell', { connected: true, availability: 'BUSY' }],
      ['aiqs-cell', { connected: true, availability: 'READY' }],
    ]) as any;

    const busy = anyComponent.pickFirstBusyStationSerial({
      modules: [{ id: 'aiqs-cell' }, { id: 'hbw-cell' }],
      fixedPositions: [],
    });
    expect(busy).toBe('hbw-cell');

    anyComponent.viewModel = { modules: [], fixedPositions: [] };
    anyComponent.lastFollowScrollSerial = 'hbw-cell';
    const spy = jest.fn();
    anyComponent.hostEl = {
      nativeElement: { querySelector: () => ({ scrollIntoView: spy }) },
    };
    anyComponent.pickFirstBusyStationSerial = () => 'hbw-cell';

    anyComponent.performFollowActiveStationScroll();
    expect(spy).not.toHaveBeenCalled();
  });
});
