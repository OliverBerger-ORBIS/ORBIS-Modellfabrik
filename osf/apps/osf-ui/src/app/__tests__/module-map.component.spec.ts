import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ModuleMapComponent } from '../module-map.component';
import { of } from 'rxjs';
import type { ModuleState } from '@osf/entities';

describe('ModuleMapComponent', () => {
  let component: ModuleMapComponent;
  let fixture: ComponentFixture<ModuleMapComponent>;

  const mockModuleStates: Record<string, ModuleState> = {
    'SVR3QA0022': {
      moduleId: 'SVR3QA0022',
      state: 'idle',
      lastSeen: '2025-11-10T18:00:00Z',
      details: {
        orderId: 'order-123',
      },
    },
    'SVR4H73275': {
      moduleId: 'SVR4H73275',
      state: 'working',
      lastSeen: '2025-11-10T18:05:00Z',
      details: {
        step: 'processing',
      },
    },
    'SVR4H76530': {
      moduleId: 'SVR4H76530',
      state: 'maintenance',
      lastSeen: '2025-11-10T18:10:00Z',
      details: {
        description: 'Maintenance required',
      },
    },
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModuleMapComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ModuleMapComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display module states from stream', () => {
    component.moduleStates$ = of(mockModuleStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const moduleItems = compiled.querySelectorAll('li');
    expect(moduleItems.length).toBe(3);
  });

  it('should display module IDs', () => {
    component.moduleStates$ = of(mockModuleStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('SVR3QA0022');
    expect(compiled.textContent).toContain('SVR4H73275');
    expect(compiled.textContent).toContain('SVR4H76530');
  });

  it('should display module states', () => {
    component.moduleStates$ = of(mockModuleStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('idle');
    expect(compiled.textContent).toContain('working');
    expect(compiled.textContent).toContain('maintenance');
  });

  it('should display module details (orderId)', () => {
    component.moduleStates$ = of(mockModuleStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('order-123');
  });

  it('should display module details (step)', () => {
    component.moduleStates$ = of(mockModuleStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('processing');
  });

  it('should display module details (description)', () => {
    component.moduleStates$ = of(mockModuleStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Maintenance required');
  });

  it('should handle empty module states', () => {
    component.moduleStates$ = of({});
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyMessage = compiled.querySelector('.empty');
    expect(emptyMessage).toBeTruthy();
    expect(emptyMessage?.textContent).toContain('Awaiting module telemetry');
  });

  it('should display timestamps when available', () => {
    component.moduleStates$ = of(mockModuleStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    // Timestamps should be displayed (format depends on locale)
    const timestamps = compiled.querySelectorAll('.timestamp');
    expect(timestamps.length).toBe(3);
  });

  it('should handle modules without details', () => {
    const statesWithoutDetails: Record<string, ModuleState> = {
      'SVR3QA0022': {
        moduleId: 'SVR3QA0022',
        state: 'idle',
        lastSeen: '2025-11-10T18:00:00Z',
      },
    };

    component.moduleStates$ = of(statesWithoutDetails);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('SVR3QA0022');
    expect(compiled.textContent).toContain('idle');
  });

  it('should update when module states stream changes', () => {
    component.moduleStates$ = of({});
    fixture.detectChanges();

    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.empty')).toBeTruthy();

    // Create new component instance with new stream
    fixture = TestBed.createComponent(ModuleMapComponent);
    component = fixture.componentInstance;
    component.moduleStates$ = of(mockModuleStates);
    fixture.detectChanges();

    compiled = fixture.nativeElement as HTMLElement;
    const moduleItems = compiled.querySelectorAll('li');
    expect(moduleItems.length).toBe(3);
  });

  describe('Edge Cases', () => {
    it('should handle modules with missing moduleId', () => {
      const statesWithMissingId: Record<string, ModuleState> = {
        'unknown': {
          state: 'idle',
          lastSeen: '2025-11-10T18:00:00Z',
        } as ModuleState,
      };

      component.moduleStates$ = of(statesWithMissingId);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled).toBeTruthy();
    });

    it('should handle modules with invalid state', () => {
      const statesWithInvalidState: Record<string, ModuleState> = {
        'SVR3QA0022': {
          moduleId: 'SVR3QA0022',
          state: 'unknown-state' as any,
          lastSeen: '2025-11-10T18:00:00Z',
        },
      };

      component.moduleStates$ = of(statesWithInvalidState);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('SVR3QA0022');
    });

    it('should handle modules with invalid timestamps', () => {
      const statesWithInvalidTimestamp: Record<string, ModuleState> = {
        'SVR3QA0022': {
          moduleId: 'SVR3QA0022',
          state: 'idle',
          lastSeen: 'invalid-date',
        },
      };

      component.moduleStates$ = of(statesWithInvalidTimestamp);
      
      // DatePipe will throw an error for invalid dates, which is expected behavior
      expect(() => {
        fixture.detectChanges();
      }).toThrow();
    });

    it('should handle modules with very long IDs', () => {
      const longId = 'A'.repeat(1000);
      const statesWithLongId: Record<string, ModuleState> = {
        [longId]: {
          moduleId: longId,
          state: 'idle',
          lastSeen: '2025-11-10T18:00:00Z',
        },
      };

      component.moduleStates$ = of(statesWithLongId);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled).toBeTruthy();
    });

    it('should handle modules with null details', () => {
      const statesWithNullDetails: Record<string, ModuleState> = {
        'SVR3QA0022': {
          moduleId: 'SVR3QA0022',
          state: 'idle',
          lastSeen: '2025-11-10T18:00:00Z',
          details: null as any,
        },
      };

      component.moduleStates$ = of(statesWithNullDetails);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('SVR3QA0022');
    });

    it('should handle modules with empty details object', () => {
      const statesWithEmptyDetails: Record<string, ModuleState> = {
        'SVR3QA0022': {
          moduleId: 'SVR3QA0022',
          state: 'idle',
          lastSeen: '2025-11-10T18:00:00Z',
          details: {},
        },
      };

      component.moduleStates$ = of(statesWithEmptyDetails);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('SVR3QA0022');
    });

    it('should handle modules with very large details objects', () => {
      const largeDetails: Record<string, any> = {};
      for (let i = 0; i < 1000; i++) {
        largeDetails[`key${i}`] = `value${i}`;
      }

      const statesWithLargeDetails: Record<string, ModuleState> = {
        'SVR3QA0022': {
          moduleId: 'SVR3QA0022',
          state: 'idle',
          lastSeen: '2025-11-10T18:00:00Z',
          details: largeDetails,
        },
      };

      component.moduleStates$ = of(statesWithLargeDetails);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('SVR3QA0022');
    });
  });
});

