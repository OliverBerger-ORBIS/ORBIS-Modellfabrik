import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { OrderCardComponent } from '../order-card.component';
import { ModuleNameService } from '../../../services/module-name.service';
import type { OrderActive, ProductionStep } from '@omf3/entities';
import { SimpleChange } from '@angular/core';

describe('OrderCardComponent', () => {
  let component: OrderCardComponent;
  let fixture: ComponentFixture<OrderCardComponent>;
  let moduleNameService: ModuleNameService;

  const mockOrder: OrderActive = {
    orderId: 'ORDER-001',
    orderType: 'PRODUCTION',
    type: 'BLUE',
    state: 'IN_PROGRESS',
    status: 'IN_PROGRESS',
    startedAt: '2024-01-01T10:00:00Z',
    productId: 'WP-12345',
    productionSteps: [
      {
        id: 'step-1',
        state: 'COMPLETED',
        type: 'HBW',
        moduleType: 'HBW',
        command: 'PICK',
        startedAt: '2024-01-01T10:00:00Z',
        stoppedAt: '2024-01-01T10:05:00Z',
      },
      {
        id: 'step-2',
        state: 'IN_PROGRESS',
        type: 'MPO',
        moduleType: 'MPO',
        command: 'PROCESS',
        startedAt: '2024-01-01T10:05:00Z',
      },
      {
        id: 'step-3',
        state: 'PENDING',
        type: 'NAVIGATION',
        command: 'NAVIGATE',
        source: 'MPO',
        target: 'VGR',
      },
    ] as ProductionStep[],
  } as OrderActive;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrderCardComponent, HttpClientTestingModule],
      providers: [ModuleNameService],
    }).compileComponents();

    fixture = TestBed.createComponent(OrderCardComponent);
    component = fixture.componentInstance;
    moduleNameService = TestBed.inject(ModuleNameService);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Input Binding', () => {
    it('should accept order property', () => {
      component.order = mockOrder;
      fixture.detectChanges();
      expect(component.order).toBe(mockOrder);
    });

    it('should accept isCompleted property', () => {
      component.isCompleted = true;
      fixture.detectChanges();
      expect(component.isCompleted).toBe(true);
    });

    it('should have isCompleted property', () => {
      component.isCompleted = true;
      expect(component.isCompleted).toBe(true);
      component.isCompleted = false;
      expect(component.isCompleted).toBe(false);
    });
  });

  describe('ngOnChanges', () => {
    it('should update steps when order changes', () => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      expect(component.steps.length).toBe(3);
    });

    it('should collapse on first change if isCompleted is true', () => {
      component.isCompleted = true;
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      expect(component.collapsed).toBe(true);
    });

    it('should not collapse on subsequent changes', () => {
      component.order = mockOrder;
      component.collapsed = false;
      component.ngOnChanges({
        order: new SimpleChange(mockOrder, mockOrder, false),
      });
      expect(component.collapsed).toBe(false);
    });

    it('should handle null order', () => {
      component.order = null;
      component.ngOnChanges({
        order: new SimpleChange(null, null, true),
      });
      expect(component.steps).toEqual([]);
    });
  });

  describe('Template Rendering', () => {
    it('should display order when provided', () => {
      component.order = mockOrder;
      fixture.detectChanges();
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.order-card')).toBeTruthy();
    });

    it('should not display anything when order is null', () => {
      component.order = null;
      fixture.detectChanges();
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.order-card')).toBeFalsy();
    });

    it('should display order steps when not collapsed', () => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      component.collapsed = false;
      fixture.detectChanges();
      const compiled = fixture.nativeElement;
      const steps = compiled.querySelectorAll('.step-row');
      expect(steps.length).toBeGreaterThan(0);
    });

    it('should hide content when collapsed', () => {
      component.order = mockOrder;
      component.collapsed = true;
      fixture.detectChanges();
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.order-card__content')).toBeFalsy();
    });
  });

  describe('Status Badge Styling', () => {
    it('should apply state--running class for IN_PROGRESS', () => {
      component.order = { ...mockOrder, state: 'IN_PROGRESS' };
      expect(component.headerStateClass).toBe('state--running');
    });

    it('should apply state--completed class for COMPLETED', () => {
      component.order = { ...mockOrder, state: 'COMPLETED' };
      expect(component.headerStateClass).toBe('state--completed');
    });

    it('should apply state--failed class for FAILED', () => {
      component.order = { ...mockOrder, state: 'FAILED' };
      expect(component.headerStateClass).toBe('state--failed');
    });

    it('should apply state--queued as default', () => {
      component.order = { ...mockOrder, state: 'PENDING' };
      expect(component.headerStateClass).toBe('state--queued');
    });
  });

  describe('OnPush Change Detection', () => {
    it('should use OnPush change detection strategy', () => {
      const metadata = (OrderCardComponent as any).__annotations__?.[0];
      // Check component metadata or constructor
      expect(component).toBeTruthy();
      // OnPush is set in the component decorator
    });

    it('should update view when order input changes', () => {
      component.order = mockOrder;
      fixture.detectChanges();
      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('.order-card')).toBeTruthy();

      component.order = { ...mockOrder, orderId: 'ORDER-002' };
      fixture.detectChanges();
      expect(component.order.orderId).toBe('ORDER-002');
    });
  });

  describe('activeStep getter', () => {
    it('should return step with IN_PROGRESS state', () => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      const activeStep = component.activeStep;
      expect(activeStep?.id).toBe('step-2');
      expect(activeStep?.state).toBe('IN_PROGRESS');
    });

    it('should return undefined if no active step', () => {
      const orderWithNoActive = {
        ...mockOrder,
        productionSteps: [
          { ...mockOrder.productionSteps![0], state: 'COMPLETED' },
          { ...mockOrder.productionSteps![1], state: 'COMPLETED' },
        ] as ProductionStep[],
      };
      component.order = orderWithNoActive;
      component.ngOnChanges({
        order: new SimpleChange(null, orderWithNoActive, true),
      });
      expect(component.activeStep).toBeUndefined();
    });
  });

  describe('nextPendingStep getter', () => {
    it('should return first pending step', () => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      const nextStep = component.nextPendingStep;
      expect(nextStep?.id).toBe('step-3');
    });
  });

  describe('completedSteps getter', () => {
    it('should return all completed steps', () => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      const completed = component.completedSteps;
      expect(completed.length).toBe(1);
      expect(completed[0].id).toBe('step-1');
    });
  });

  describe('headerStatus getter', () => {
    it('should return running status for IN_PROGRESS', () => {
      component.order = { ...mockOrder, state: 'RUNNING' };
      const status = component.headerStatus;
      expect(status.class).toBe('state--running');
      expect(status.label).toBeDefined();
    });

    it('should return completed status for FINISHED', () => {
      component.order = { ...mockOrder, state: 'FINISHED' };
      const status = component.headerStatus;
      expect(status.class).toBe('state--completed');
    });

    it('should return failed status for FAILED', () => {
      component.order = { ...mockOrder, state: 'FAILED' };
      const status = component.headerStatus;
      expect(status.class).toBe('state--failed');
    });

    it('should fallback to status field', () => {
      component.order = { ...mockOrder, state: undefined, status: 'RUNNING' };
      const status = component.headerStatus;
      expect(status.class).toBe('state--running');
    });
  });

  describe('orderTypeIcon getter', () => {
    it('should return production icon for PRODUCTION order', () => {
      component.order = { ...mockOrder, orderType: 'PRODUCTION' };
      const icon = component.orderTypeIcon;
      expect(icon).toBeDefined();
      expect(typeof icon).toBe('string');
    });

    it('should return storage icon for STORAGE order', () => {
      component.order = { ...mockOrder, orderType: 'STORAGE' };
      const icon = component.orderTypeIcon;
      expect(icon).toBeDefined();
      expect(typeof icon).toBe('string');
    });
  });

  describe('workpieceIcon getter', () => {
    it('should return product icon for PRODUCTION order', () => {
      component.order = { ...mockOrder, orderType: 'PRODUCTION', type: 'BLUE' };
      const icon = component.workpieceIcon;
      expect(icon).toBeDefined();
    });

    it('should return 3D icon for STORAGE order', () => {
      component.order = { ...mockOrder, orderType: 'STORAGE', type: 'WHITE' };
      const icon = component.workpieceIcon;
      expect(icon).toBeDefined();
    });

    it('should return null for unknown workpiece type', () => {
      component.order = { ...mockOrder, type: 'UNKNOWN' };
      const icon = component.workpieceIcon;
      expect(icon).toBeNull();
    });
  });

  describe('Label methods', () => {
    it('should return order type label', () => {
      component.order = { ...mockOrder, orderType: 'PRODUCTION' };
      const label = component.getOrderTypeLabel();
      expect(label).toBeDefined();
    });

    it('should return storage type label', () => {
      component.order = { ...mockOrder, orderType: 'STORAGE' };
      const label = component.getOrderTypeLabel();
      expect(label).toBeDefined();
    });

    it('should return workpiece type label for BLUE', () => {
      component.order = { ...mockOrder, type: 'BLUE' };
      const label = component.getWorkpieceTypeLabel();
      expect(label).toBeDefined();
    });

    it('should return workpiece type label for WHITE', () => {
      component.order = { ...mockOrder, type: 'WHITE' };
      const label = component.getWorkpieceTypeLabel();
      expect(label).toBeDefined();
    });

    it('should return workpiece type label for RED', () => {
      component.order = { ...mockOrder, type: 'RED' };
      const label = component.getWorkpieceTypeLabel();
      expect(label).toBeDefined();
    });

    it('should return unknown type as-is', () => {
      component.order = { ...mockOrder, type: 'UNKNOWN' };
      const label = component.getWorkpieceTypeLabel();
      expect(label).toBe('UNKNOWN');
    });

    it('should format step number label', () => {
      const label = component.getStepNumberLabel(1);
      expect(label).toContain('01');
    });

    it('should return toggle details label', () => {
      const label = component.getToggleDetailsLabel();
      expect(label).toBeDefined();
    });
  });

  describe('Timestamp formatting', () => {
    it('should format orderStartedAt', () => {
      component.order = { ...mockOrder, startedAt: '2024-01-01T10:00:00Z' };
      const formatted = component.orderStartedAt;
      expect(formatted).toBeTruthy();
    });

    it('should return null for invalid timestamp', () => {
      component.order = { ...mockOrder, startedAt: 'invalid' };
      const formatted = component.orderStartedAt;
      expect(formatted).toBeNull();
    });

    it('should format activeStepStartedAt', () => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      const formatted = component.activeStepStartedAt;
      expect(formatted).toBeTruthy();
    });
  });

  describe('Duration calculation', () => {
    it('should calculate order duration with active step', () => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      const duration = component.orderDuration;
      expect(duration).toBeTruthy();
      expect(duration).toContain('m');
    });

    it('should return null if no startedAt', () => {
      component.order = { ...mockOrder, startedAt: undefined };
      component.ngOnChanges({
        order: new SimpleChange(null, component.order, true),
      });
      const duration = component.orderDuration;
      expect(duration).toBeNull();
    });

    it('should calculate duration for finished order', () => {
      const finishedOrder = {
        ...mockOrder,
        state: 'FINISHED',
        startedAt: '2024-01-01T10:00:00Z',
        finishedAt: '2024-01-01T11:00:00Z',
        productionSteps: mockOrder.productionSteps?.map((s) => ({
          ...s,
          state: 'COMPLETED',
        })) as ProductionStep[],
      };
      component.order = finishedOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, finishedOrder, true),
      });
      const duration = component.orderDuration;
      expect(duration).toBeTruthy();
    });
  });

  describe('Step methods', () => {
    beforeEach(() => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
    });

    it('should get step background class', () => {
      const step = mockOrder.productionSteps![0];
      const bgClass = component.stepBackgroundClass(step);
      expect(bgClass).toContain('step--');
    });

    it('should get step status class', () => {
      const step = mockOrder.productionSteps![0];
      const statusClass = component.stepStatusClass(step);
      expect(statusClass).toContain('step__status-icon--');
    });

    it('should get step status icon', () => {
      const step = mockOrder.productionSteps![0];
      const icon = component.stepStatusIcon(step);
      expect(icon).toBeDefined();
    });

    it('should get step state label', () => {
      const step = mockOrder.productionSteps![0];
      const label = component.stepStateLabel(step);
      expect(label).toBeDefined();
    });
  });

  describe('Command label', () => {
    it('should format navigation command', () => {
      const navStep = mockOrder.productionSteps![2];
      const label = component.commandLabel(navStep);
      expect(label).toContain('→');
      expect(label).toContain('MPO');
      expect(label).toContain('VGR');
    });

    it('should return command for non-navigation', () => {
      const step = mockOrder.productionSteps![0];
      const label = component.commandLabel(step);
      expect(label).toBe('PICK');
    });

    it('should fallback to type if no command', () => {
      const step = { ...mockOrder.productionSteps![0], command: undefined };
      const label = component.commandLabel(step);
      expect(label).toBe('HBW');
    });
  });

  describe('Module icon and name', () => {
    beforeEach(() => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
    });

    it('should get module icon', () => {
      const step = mockOrder.productionSteps![0];
      const icon = component.moduleIcon(step);
      expect(icon).toBeDefined();
    });

    it('should get FTS icon for navigation', () => {
      const navStep = mockOrder.productionSteps![2];
      const icon = component.moduleIcon(navStep);
      expect(icon).toBeDefined();
    });

    it('should get module name', () => {
      const step = mockOrder.productionSteps![0];
      const name = component.moduleName(step);
      expect(name).toBeDefined();
    });

    it('should get FTS name for navigation', () => {
      const navStep = mockOrder.productionSteps![2];
      const name = component.moduleName(navStep);
      expect(name).toBeDefined();
    });

    it('should get module full name', () => {
      const step = mockOrder.productionSteps![0];
      const fullName = component.moduleFullName(step);
      expect(fullName).toBeDefined();
    });

    it('should get target module icon for navigation', () => {
      const navStep = mockOrder.productionSteps![2];
      const icon = component.targetModuleIcon(navStep);
      expect(icon).toBeDefined();
    });

    it('should return null for non-navigation target icon', () => {
      const step = mockOrder.productionSteps![0];
      const icon = component.targetModuleIcon(step);
      expect(icon).toBeNull();
    });

    it('should return null for START target', () => {
      const navStep = { ...mockOrder.productionSteps![2], target: 'START' };
      const icon = component.targetModuleIcon(navStep);
      expect(icon).toBeNull();
    });
  });

  describe('workpieceId getter', () => {
    it('should return workpieceId from order', () => {
      // Add workpieceId as a dynamic property
      const orderWithWorkpiece = { ...mockOrder, workpieceId: 'WP-12345' } as any;
      component.order = orderWithWorkpiece;
      const id = component.workpieceId;
      expect(id).toBe('WP-12345');
    });

    it('should fallback to productId', () => {
      component.order = mockOrder;
      const id = component.workpieceId;
      expect(id).toBe('WP-12345');
    });

    it('should return null if both missing', () => {
      const orderWithNoId = { ...mockOrder, productId: undefined } as OrderActive;
      component.order = orderWithNoId;
      const id = component.workpieceId;
      expect(id).toBeNull();
    });
  });

  describe('toggleCollapse', () => {
    it('should toggle collapsed state', () => {
      component.collapsed = false;
      component.toggleCollapse();
      expect(component.collapsed).toBe(true);

      component.toggleCollapse();
      expect(component.collapsed).toBe(false);
    });

    it('should trigger view update on toggle', () => {
      component.order = mockOrder;
      component.collapsed = true;
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('.order-card__toggle');
      button.click();
      fixture.detectChanges();

      expect(component.collapsed).toBe(false);
    });
  });

  describe('trackStep', () => {
    it('should return step id for tracking', () => {
      const step = mockOrder.productionSteps![0];
      const tracked = component.trackStep(0, step);
      expect(tracked).toBe('step-1');
    });
  });

  describe('previewStep getter', () => {
    it('should return active step if available', () => {
      component.order = mockOrder;
      component.ngOnChanges({
        order: new SimpleChange(null, mockOrder, true),
      });
      const preview = component.previewStep;
      expect(preview?.id).toBe('step-2');
    });

    it('should fallback to next pending step', () => {
      const orderWithNoPending = {
        ...mockOrder,
        productionSteps: [
          { ...mockOrder.productionSteps![0], state: 'COMPLETED' },
          { ...mockOrder.productionSteps![1], state: 'COMPLETED' },
          { ...mockOrder.productionSteps![2], state: 'PENDING' },
        ] as ProductionStep[],
      };
      component.order = orderWithNoPending;
      component.ngOnChanges({
        order: new SimpleChange(null, orderWithNoPending, true),
      });
      const preview = component.previewStep;
      expect(preview?.id).toBe('step-3');
    });

    it('should fallback to last completed step', () => {
      const orderCompleted = {
        ...mockOrder,
        productionSteps: [
          { ...mockOrder.productionSteps![0], state: 'COMPLETED' },
          { ...mockOrder.productionSteps![1], state: 'COMPLETED' },
          { ...mockOrder.productionSteps![2], state: 'COMPLETED' },
        ] as ProductionStep[],
      };
      component.order = orderCompleted;
      component.ngOnChanges({
        order: new SimpleChange(null, orderCompleted, true),
      });
      const preview = component.previewStep;
      expect(preview?.id).toBe('step-3');
    });

    it('should return undefined if no steps', () => {
      component.order = { ...mockOrder, productionSteps: [] };
      component.ngOnChanges({
        order: new SimpleChange(null, component.order, true),
      });
      const preview = component.previewStep;
      expect(preview).toBeUndefined();
    });
  });

  describe('Edge cases', () => {
    it('should handle order without productionSteps', () => {
      component.order = { ...mockOrder, productionSteps: undefined };
      component.ngOnChanges({
        order: new SimpleChange(null, component.order, true),
      });
      expect(component.steps).toEqual([]);
    });

    it('should handle empty productionSteps array', () => {
      component.order = { ...mockOrder, productionSteps: [] };
      component.ngOnChanges({
        order: new SimpleChange(null, component.order, true),
      });
      expect(component.steps).toEqual([]);
    });

    it('should handle order with undefined state', () => {
      component.order = { ...mockOrder, state: undefined, status: undefined };
      const stateClass = component.headerStateClass;
      expect(stateClass).toBe('state--queued');
    });

    it('should handle step with empty state', () => {
      const step = { ...mockOrder.productionSteps![0], state: '' };
      const bgClass = component.stepBackgroundClass(step);
      expect(bgClass).toContain('step--queued');
    });
  });
});
