import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChangeDetectorRef } from '@angular/core';
import { BehaviorSubject, of } from 'rxjs';
import { HbwStockGridComponent } from '../hbw-stock-grid.component';
import { InventoryStateService } from '../../../services/inventory-state.service';
import { EnvironmentService } from '../../../services/environment.service';
import { MessageMonitorService } from '../../../services/message-monitor.service';
import type { InventoryOverviewState, InventorySlotState, StockSnapshot } from '@omf3/entities';

jest.mock('../../../mock-dashboard', () => {
  return {
    getDashboardController: jest.fn(() => ({
      streams: {
        inventoryOverview$: new BehaviorSubject({
          slots: {},
          availableCounts: {},
          reservedCounts: {},
          lastUpdated: '',
        }),
      },
    })),
  };
});

describe('HbwStockGridComponent', () => {
  let component: HbwStockGridComponent;
  let fixture: ComponentFixture<HbwStockGridComponent>;
  let inventoryStateService: jest.Mocked<InventoryStateService>;
  let environmentService: jest.Mocked<EnvironmentService>;
  let messageMonitorService: jest.Mocked<MessageMonitorService>;

  const createEmptyInventoryState = (): InventoryOverviewState => ({
    slots: {
      A1: { location: 'A1', workpiece: null },
      A2: { location: 'A2', workpiece: null },
      A3: { location: 'A3', workpiece: null },
      B1: { location: 'B1', workpiece: null },
      B2: { location: 'B2', workpiece: null },
      B3: { location: 'B3', workpiece: null },
      C1: { location: 'C1', workpiece: null },
      C2: { location: 'C2', workpiece: null },
      C3: { location: 'C3', workpiece: null },
    },
    availableCounts: { BLUE: 0, WHITE: 0, RED: 0 },
    reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
    lastUpdated: '',
  });

  beforeEach(async () => {
    const inventoryStateMock = {
      getState$: jest.fn(() => new BehaviorSubject<InventoryOverviewState | null>(createEmptyInventoryState())),
      getSnapshot: jest.fn(() => null),
      setState: jest.fn(),
      clear: jest.fn(),
    } as unknown as InventoryStateService;

    const environmentServiceMock = {
      current: { key: 'mock' },
      environment$: new BehaviorSubject({ key: 'mock' }),
    } as unknown as EnvironmentService;

    const messageMonitorMock = {
      getLastMessage: jest.fn(() => of({ valid: false, payload: null })),
    } as unknown as MessageMonitorService;

    await TestBed.configureTestingModule({
      imports: [HbwStockGridComponent],
      providers: [
        { provide: InventoryStateService, useValue: inventoryStateMock },
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: MessageMonitorService, useValue: messageMonitorMock },
        { provide: ChangeDetectorRef, useValue: { markForCheck: jest.fn() } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HbwStockGridComponent);
    component = fixture.componentInstance;
    inventoryStateService = TestBed.inject(InventoryStateService) as any;
    environmentService = TestBed.inject(EnvironmentService) as any;
    messageMonitorService = TestBed.inject(MessageMonitorService) as any;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display empty slots', (done) => {
    fixture.detectChanges();
    
    component.inventorySlots$.subscribe((slots) => {
      expect(slots).toHaveLength(9);
      expect(slots[0].location).toBe('A1');
      expect(slots[0].workpiece).toBeNull();
      done();
    });
  });

  it('should display workpiece icons when slots are filled', (done) => {
    const filledState: InventoryOverviewState = {
      slots: {
        A1: { location: 'A1', workpiece: { id: 'wp1', type: 'BLUE', state: 'RAW' } },
        A2: { location: 'A2', workpiece: { id: 'wp2', type: 'WHITE', state: 'PROCESSED' } },
        A3: { location: 'A3', workpiece: null },
        B1: { location: 'B1', workpiece: null },
        B2: { location: 'B2', workpiece: null },
        B3: { location: 'B3', workpiece: null },
        C1: { location: 'C1', workpiece: null },
        C2: { location: 'C2', workpiece: null },
        C3: { location: 'C3', workpiece: null },
      },
      availableCounts: { BLUE: 1, WHITE: 0, RED: 0 },
      reservedCounts: { BLUE: 0, WHITE: 0, RED: 0 },
      lastUpdated: '',
    };

    (inventoryStateService.getState$ as jest.Mock).mockReturnValue(new BehaviorSubject(filledState));
    
    fixture.detectChanges();
    
    component.inventorySlots$.subscribe((slots) => {
      expect(slots[0].workpiece?.type).toBe('BLUE');
      expect(slots[1].workpiece?.type).toBe('WHITE');
      expect(component.getSlotIcon(slots[0])).not.toBe(component.emptySlotIcon);
      done();
    });
  });

  it('should apply correct CSS class for reserved workpieces', () => {
    const slot: InventorySlotState = {
      location: 'A1',
      workpiece: { id: 'wp1', type: 'BLUE', state: 'RESERVED' },
    };

    const cssClass = component.getSlotClass(slot);
    expect(cssClass).toBe('hbw-stock-grid__slot--reserved');
  });

  it('should generate correct tooltip text', () => {
    const slot: InventorySlotState = {
      location: 'A1',
      workpiece: { id: 'wp-123', type: 'BLUE', state: 'RAW' },
    };

    const tooltip = component.getSlotTooltip(slot);
    expect(tooltip).toContain('A1');
    expect(tooltip).toContain('wp-123');
    expect(tooltip).toContain('RAW');
  });

  it('should return empty slot icon for empty slots', () => {
    const slot: InventorySlotState = {
      location: 'A1',
      workpiece: null,
    };

    const icon = component.getSlotIcon(slot);
    expect(icon).toBe(component.emptySlotIcon);
  });

  describe('Layout and styling', () => {
    it('should render slot labels in template', () => {
      fixture.detectChanges();
      
      const compiled = fixture.nativeElement;
      const slotLabels = compiled.querySelectorAll('.hbw-stock-grid__slot-label');
      
      expect(slotLabels.length).toBe(9); // 3x3 grid = 9 slots
      expect(slotLabels[0].textContent).toBe('A1');
    });

    it('should render slots with location labels', () => {
      fixture.detectChanges();
      
      const compiled = fixture.nativeElement;
      const slots = compiled.querySelectorAll('.hbw-stock-grid__slot');
      
      expect(slots.length).toBe(9); // 3x3 grid = 9 slots
    });

    it('should render grid container', () => {
      fixture.detectChanges();
      
      const compiled = fixture.nativeElement;
      const grid = compiled.querySelector('.hbw-stock-grid');
      
      expect(grid).toBeTruthy();
    });
  });
});
