import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, of, throwError } from 'rxjs';
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
    icon_sizing_rules: { by_role: { default: 0.75, intersection: 0.5 } },
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
      {
        id: 'orbis-cell',
        name: 'ORBIS',
        role: 'company',
        position: { x: 10, y: 80 },
        size: { w: 40, h: 20 },
        show_name: true,
      },
      {
        id: 'dsp-cell',
        name: 'DSP',
        role: 'software',
        position: { x: 60, y: 80 },
        size: { w: 40, h: 20 },
        show_name: true,
      },
    ],
  } as any;

  beforeEach(async () => {
    rotation$.next('none');
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

  afterEach(() => {
    localStorage.removeItem('shopfloor-preview-scale');
    localStorage.removeItem('shopfloor-config-scale');
    localStorage.removeItem('OSF.shopfloorScale.shopfloor');
    localStorage.removeItem('OSF.shopfloorScale.agv');
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

  it('zooms in/out, persists scale, and resetZoom restores the default', () => {
    const start = component.currentScale;
    component.zoomIn();
    expect(component.currentScale).toBeCloseTo(start + component.scaleStep);
    expect(component.canZoomOut).toBe(true);
    expect(localStorage.getItem('shopfloor-config-scale')).toBe(String(component.currentScale));

    component.zoomOut();
    expect(component.currentScale).toBeCloseTo(start);

    component.resetZoom();
    expect(component.currentScale).toBe(component.scale);
    expect(localStorage.getItem('shopfloor-config-scale')).toBeNull();
  });

  it('migrates legacy config zoom into a scoped storage key', () => {
    localStorage.setItem('shopfloor-config-scale', '1.2');
    component.scaleStorageScope = 'shopfloor';
    component.ngOnChanges({
      scaleStorageScope: new SimpleChange(null, 'shopfloor', false),
    });
    expect(component.currentScale).toBe(1.2);
    expect(localStorage.getItem('OSF.shopfloorScale.shopfloor')).toBe('1.2');
  });

  it('maps availability colors and unknown flags', () => {
    expect(component.getModuleBackgroundColor(undefined)).toBeUndefined();
    expect(component.getModuleBackgroundColor('READY')).toContain('status-success');
    expect(component.getModuleBackgroundColor('BUSY')).toContain('status-warning');
    expect(component.getModuleBackgroundColor('BLOCKED')).toContain('status-error');
    expect(component.getModuleBackgroundColor('Unknown')).toContain('orbis-grey');
    expect(component.getModuleBackgroundColor('IDLE' as never)).toBeUndefined();
    expect(component.isUnknownAvailability(undefined)).toBe(false);
    expect(component.isUnknownAvailability('Unknown')).toBe(true);
    expect(component.isUnknownAvailability('unknown')).toBe(true);
  });

  it('builds fixed-cell transforms for rotation and highlight', () => {
    expect(component.getFixedCellTransform({ cellRotationDeg: 0, highlighted: false } as never)).toBeNull();
    expect(component.getFixedCellTransform({ cellRotationDeg: 180, highlighted: false } as never)).toBe(
      'rotate(180deg)'
    );
    expect(component.getFixedCellTransform({ cellRotationDeg: 180, highlighted: true } as never)).toContain(
      'scale(1.02)'
    );
  });

  it('derives info and badge labels from step and order', () => {
    component.infoText = undefined;
    component.activeStep = null;
    expect(component.infoLabel).toBe('');

    component.activeStep = { type: 'NAVIGATION', source: 'HBW', target: 'DRILL' } as never;
    expect(component.infoLabel).toBe('HBW → DRILL');

    component.infoText = 'Custom';
    expect(component.infoLabel).toBe('Custom');

    component.badgeText = undefined;
    component.order = { orderType: 'STORAGE' } as never;
    component.activeStep = { type: 'PRODUCTION' } as never;
    expect(component.badgeLabel.toUpperCase()).toContain('STORAGE');

    component.activeStep = { type: 'NAVIGATION' } as never;
    expect(component.badgeLabel).toBe('FTS');
  });

  it('emits selection only when selection is enabled', () => {
    const selected = jest.spyOn(component.cellSelected, 'emit');
    const dbl = jest.spyOn(component.cellDoubleClicked, 'emit');
    const event = { stopPropagation: jest.fn() } as unknown as Event;
    const module = { id: 'hbw-cell' } as never;

    component.selectionEnabled = false;
    component.onModuleActivate(module, event);
    component.onModuleDouble(module, event);
    expect(selected).not.toHaveBeenCalled();
    expect(dbl).not.toHaveBeenCalled();

    component.selectionEnabled = true;
    component.onModuleActivate(module, event);
    component.onModuleDouble(module, event);
    component.onFixedActivate({ id: 'ix-1' } as never, event);
    expect(selected).toHaveBeenCalledWith({ id: 'hbw-cell', kind: 'module' });
    expect(dbl).toHaveBeenCalledWith({ id: 'hbw-cell', kind: 'module' });
    expect(selected).toHaveBeenCalledWith({ id: 'ix-1', kind: 'fixed' });
    expect(event.stopPropagation).toHaveBeenCalled();
  });

  it('rotates the view model when the rotation service emits cw90', () => {
    const before = component.viewModel as { width: number; height: number };
    expect(before.width).toBeGreaterThan(before.height);

    rotation$.next('cw90');
    const after = component.viewModel as { width: number; height: number };
    expect(after.width).toBe(before.height);
    expect(after.height).toBe(before.width);
  });

  it('converts hex colors and falls back for invalid values', () => {
    const hexToRgb = (component as unknown as { hexToRgb: (hex: string) => string }).hexToRgb;
    expect(hexToRgb.call(component, '#154194')).toBe('21, 65, 148');
    expect(hexToRgb.call(component, 'not-a-color')).toBe('249, 115, 22');
  });

  it('returns null for a busy station lookup when the status map is empty', () => {
    component.moduleStatusMap = null;
    const pick = (component as unknown as { pickFirstBusyStationSerial: (vm: unknown) => string | null })
      .pickFirstBusyStationSerial;
    expect(pick.call(component, { modules: [{ id: 'hbw-cell' }], fixedPositions: [] })).toBeNull();
  });

  it('renders ORBIS/DSP fixed cells and keeps canvas size on rot180', () => {
    const vm = component.viewModel as {
      width: number;
      height: number;
      fixedPositions: Array<{ id: string; labelPosition?: string; showLabel: boolean }>;
    };
    expect(vm.fixedPositions.map((cell) => cell.id)).toEqual(expect.arrayContaining(['orbis-cell', 'dsp-cell']));
    const dsp = vm.fixedPositions.find((cell) => cell.id === 'dsp-cell');
    expect(dsp?.labelPosition).toBe('right');
    expect(dsp?.showLabel).toBe(false);

    rotation$.next('rot180');
    const after = component.viewModel as { width: number; height: number };
    expect(after.width).toBe(vm.width);
    expect(after.height).toBe(vm.height);
  });

  it('places FTS overlays and rotates them with ccw90', () => {
    component.ftsPositions = [{ serial: '5iO4', x: 50, y: 40, color: '#f97316' }];
    component.showFtsOverlay = true;
    component.ngOnChanges({
      ftsPositions: new SimpleChange(null, component.ftsPositions, false),
    });
    const before = component.viewModel as { ftsOverlays: Array<{ x: number; y: number }> };
    expect(before.ftsOverlays.length).toBe(1);

    rotation$.next('ccw90');
    const after = component.viewModel as { ftsOverlays: Array<{ x: number; y: number }> };
    expect(after.ftsOverlays.length).toBe(1);
    expect(after.ftsOverlays[0].x).not.toBe(before.ftsOverlays[0].x);
  });

  it('resolves route refs, paths and midpoints', () => {
    const api = component as unknown as {
      resolveNodeRef: (value?: string) => string | null;
      findRoutePath: (start: string, target: string) => string[] | null;
      findRoadBetween: (a: string, b: string) => unknown;
      computeRouteMidpoint: (segments: Array<{ x1: number; y1: number; x2: number; y2: number }>) => {
        x: number;
        y: number;
      } | null;
      getRoleScale: (role: string) => number;
      isOrbisBrandFixedCell: (id: string, label: string) => boolean;
    };

    expect(api.resolveNodeRef.call(component, undefined)).toBeNull();
    expect(api.resolveNodeRef.call(component, 'serial:SVR3QA0022')).toBe('serial:SVR3QA0022');
    expect(api.findRoutePath.call(component, 'serial:SVR3QA0022', 'serial:SVR4H76530')?.length).toBeGreaterThan(1);
    expect(api.findRoutePath.call(component, 'serial:SVR3QA0022', 'serial:missing')).toBeNull();
    expect(api.findRoadBetween.call(component, 'serial:SVR3QA0022', 'intersection:1')).toBeTruthy();
    expect(api.computeRouteMidpoint.call(component, [])).toBeNull();
    expect(api.computeRouteMidpoint.call(component, [{ x1: 0, y1: 0, x2: 10, y2: 0 }])).toEqual({ x: 5, y: 0 });
    expect(api.getRoleScale.call(component, 'intersection')).toBe(0.5);
    expect(api.isOrbisBrandFixedCell.call(component, 'orbis-cell', 'ORBIS')).toBe(true);
    expect(api.isOrbisBrandFixedCell.call(component, 'other', 'MILL')).toBe(false);
  });

  it('loads colored SVG content and swallows HTTP errors', async () => {
    const http = (component as unknown as { http: { get: jest.Mock } }).http;
    const loadSvgWithColor = (
      component as unknown as {
        loadSvgWithColor: (path: string, color: string) => Promise<unknown>;
      }
    ).loadSvgWithColor;
    const loadSvgWithGreenFill = (
      component as unknown as { loadSvgWithGreenFill: (path: string) => Promise<unknown> }
    ).loadSvgWithGreenFill;

    http.get.mockReturnValue(of('<svg fill="#154194"></svg>'));
    await expect(loadSvgWithColor.call(component, '/fts.svg', '#22c55e')).resolves.toBeTruthy();
    await expect(loadSvgWithGreenFill.call(component, '/fts.svg')).resolves.toBeTruthy();

    const error = jest.spyOn(console, 'error').mockImplementation(() => undefined);
    http.get.mockReturnValue(throwError(() => new Error('missing svg')));
    await expect(loadSvgWithColor.call(component, '/missing.svg', '#22c55e')).resolves.toBeUndefined();
    error.mockRestore();
  });

  it('clamps zoom at max and ignores invalid stored scales', () => {
    component.currentScale = component.maxScale;
    expect(component.canZoomIn).toBe(false);
    component.zoomIn();
    expect(component.currentScale).toBe(component.maxScale);

    localStorage.setItem('shopfloor-config-scale', 'not-a-number');
    expect(
      (component as unknown as { loadSavedScale: (key: string) => number | null }).loadSavedScale.call(
        component,
        'shopfloor-config-scale'
      )
    ).toBeNull();
  });

  it('formats START/END navigation and module-type info labels', () => {
    component.infoText = undefined;
    component.activeStep = { type: 'NAVIGATION', source: 'START', target: 'END' } as never;
    expect(component.infoLabel).toContain('→');
    component.activeStep = { type: 'PRODUCTION', moduleType: 'DRILL' } as never;
    expect(component.infoLabel).toContain('DRILL');
  });
});

describe('ShopfloorPreview interaction (Coverage C)', () => {
  let fixture: ComponentFixture<ShopfloorPreviewComponent>;
  let component: ShopfloorPreviewComponent;
  const rotation$ = new BehaviorSubject<'none' | 'cw90' | 'ccw90' | 'rot180'>('none');

  const layoutConfig = {
    metadata: { canvas: { width: 200, height: 120 } },
    scaling: { default_percent: 60 },
    icon_sizing_rules: { by_role: { default: 0.75, intersection: 0.5 } },
    parsed_roads: [],
    modules_by_serial: { SVR3QA0022: { cell_id: 'hbw-cell' } },
    intersection_map: {},
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
        id: 'mill-cell',
        name: 'MILL',
        role: 'module',
        serial: 'SVR3QA2091',
        position: { x: 100, y: 20 },
        size: { w: 40, h: 40 },
        show_name: true,
      },
    ],
  } as const;

  beforeEach(async () => {
    rotation$.next('none');
    await TestBed.configureTestingModule({
      imports: [ShopfloorPreviewComponent],
      providers: [
        { provide: HttpClient, useValue: { get: jest.fn(() => of('<svg/>')) } },
        {
          provide: ModuleNameService,
          useValue: {
            getModuleFullName: (key: string) => key,
            getModuleDisplayName: (key: string) => ({ fullName: key, shortName: key }),
          },
        },
        { provide: ShopfloorMappingService, useValue: { initializeLayout: jest.fn(), getAgvColor: jest.fn(() => '#f97316') } },
        { provide: ShopfloorLayoutService, useValue: { config$: of(layoutConfig) } },
        { provide: ShopfloorRotationService, useValue: { current: 'none' as const, rotation$: rotation$.asObservable() } },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(ShopfloorPreviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('applies highlightModulesOverride to rendered module cells', () => {
    component.highlightModulesOverride = ['hbw-cell'];
    component.ngOnChanges({
      highlightModulesOverride: new SimpleChange(null, component.highlightModulesOverride, false),
    });
    const vm = component.viewModel as { modules: Array<{ id: string; highlighted: boolean }> };
    const hbw = vm.modules.find((m) => m.id === 'hbw-cell');
    const mill = vm.modules.find((m) => m.id === 'mill-cell');
    expect(hbw?.highlighted).toBe(true);
    expect(mill?.highlighted).toBe(false);
  });

  it('marks current position modules from override list', () => {
    component.currentPositionModulesOverride = ['serial:SVR3QA2091'];
    component.ngOnChanges({
      currentPositionModulesOverride: new SimpleChange(null, component.currentPositionModulesOverride, false),
    });
    const vm = component.viewModel as { modules: Array<{ id: string; isCurrentPosition?: boolean }> };
    const mill = vm.modules.find((m) => m.id === 'mill-cell');
    expect(mill?.isCurrentPosition).toBe(true);
  });

  it('emits viewportChanged when zoom changes', () => {
    const viewportSpy = jest.spyOn(component.viewportChanged, 'emit');
    component.zoomIn();
    expect(viewportSpy).toHaveBeenCalledWith(
      expect.objectContaining({ widthPx: expect.any(Number), heightPx: expect.any(Number), scale: expect.any(Number) })
    );
  });

  it('schedules follow-scroll when followActiveStation is enabled', () => {
    const schedule = jest.spyOn(
      component as unknown as { scheduleFollowActiveStationScroll: () => void },
      'scheduleFollowActiveStationScroll'
    );
    component.moduleStatusMap = new Map([
      ['hbw-cell', { availability: 'BUSY', connected: true } as never],
    ]);
    component.followActiveStation = true;
    component.ngOnChanges({
      moduleStatusMap: new SimpleChange(null, component.moduleStatusMap, false),
      followActiveStation: new SimpleChange(false, true, false),
    });
    expect(schedule).toHaveBeenCalled();
  });
});
