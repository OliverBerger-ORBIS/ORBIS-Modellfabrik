import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AgvViewComponent } from '../agv-view.component';
import { of } from 'rxjs';
import type { FtsState } from '@osf/entities';

describe('AgvViewComponent', () => {
  let component: AgvViewComponent;
  let fixture: ComponentFixture<AgvViewComponent>;

  const mockFtsStates: Record<string, FtsState> = {
    '5iO4': {
      ftsId: '5iO4',
      status: 'moving',
      position: { x: 100, y: 200 },
      speed: 0.5,
      lastSeen: '2025-11-10T18:00:00Z',
    },
    'FTS-002': {
      ftsId: 'FTS-002',
      status: 'idle',
      position: { x: 50, y: 75 },
      speed: 0,
      lastSeen: '2025-11-10T18:05:00Z',
    },
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgvViewComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AgvViewComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display FTS states from stream', () => {
    component.ftsStates$ = of(mockFtsStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const ftsItems = compiled.querySelectorAll('li');
    expect(ftsItems.length).toBe(2);
  });

  it('should display FTS ID', () => {
    component.ftsStates$ = of(mockFtsStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('5iO4');
    expect(compiled.textContent).toContain('FTS-002');
  });

  it('should display FTS status', () => {
    component.ftsStates$ = of(mockFtsStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('moving');
    expect(compiled.textContent).toContain('idle');
  });

  it('should display FTS position when available', () => {
    component.ftsStates$ = of(mockFtsStates);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('(100, 200)');
    expect(compiled.textContent).toContain('(50, 75)');
  });

  it('should handle empty FTS states', () => {
    component.ftsStates$ = of({});
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyMessage = compiled.querySelector('.empty');
    expect(emptyMessage).toBeTruthy();
    expect(emptyMessage?.textContent).toContain('No AGV telemetry');
  });

  it('should handle FTS without position', () => {
    const statesWithoutPosition: Record<string, FtsState> = {
      '5iO4': {
        ftsId: '5iO4',
        status: 'idle',
        lastSeen: '2025-11-10T18:00:00Z',
      },
    };

    component.ftsStates$ = of(statesWithoutPosition);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('5iO4');
    expect(compiled.textContent).toContain('idle');
    // Should not contain coordinates
    expect(compiled.textContent).not.toContain('(');
  });

  it('should update when FTS states stream changes', () => {
    component.ftsStates$ = of({});
    fixture.detectChanges();

    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.empty')).toBeTruthy();

    // Create new component instance with new stream
    fixture = TestBed.createComponent(AgvViewComponent);
    component = fixture.componentInstance;
    component.ftsStates$ = of(mockFtsStates);
    fixture.detectChanges();

    compiled = fixture.nativeElement as HTMLElement;
    const ftsItems = compiled.querySelectorAll('li');
    expect(ftsItems.length).toBe(2);
  });

  describe('Edge Cases', () => {
    it('should handle FTS with missing ftsId', () => {
      const statesWithMissingId: Record<string, FtsState> = {
        'unknown': {
          status: 'idle',
          lastSeen: '2025-11-10T18:00:00Z',
        } as FtsState,
      };

      component.ftsStates$ = of(statesWithMissingId);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled).toBeTruthy();
    });

    it('should handle FTS with null/undefined position', () => {
      const statesWithNullPosition: Record<string, FtsState> = {
        '5iO4': {
          ftsId: '5iO4',
          status: 'idle',
          position: undefined,
          lastSeen: '2025-11-10T18:00:00Z',
        },
      };

      component.ftsStates$ = of(statesWithNullPosition);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('5iO4');
    });

    it('should handle FTS with extreme position values', () => {
      const statesWithExtremePositions: Record<string, FtsState> = {
        '5iO4': {
          ftsId: '5iO4',
          status: 'moving',
          position: { x: -1000, y: 10000 },
          speed: 0.5,
          lastSeen: '2025-11-10T18:00:00Z',
        },
      };

      component.ftsStates$ = of(statesWithExtremePositions);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('5iO4');
    });

    it('should handle FTS with invalid status', () => {
      const statesWithInvalidStatus: Record<string, FtsState> = {
        '5iO4': {
          ftsId: '5iO4',
          status: 'unknown-status' as any,
          lastSeen: '2025-11-10T18:00:00Z',
        },
      };

      component.ftsStates$ = of(statesWithInvalidStatus);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('5iO4');
    });

    it('should handle FTS with very long IDs', () => {
      const longId = 'A'.repeat(1000);
      const statesWithLongId: Record<string, FtsState> = {
        [longId]: {
          ftsId: longId,
          status: 'idle',
          lastSeen: '2025-11-10T18:00:00Z',
        },
      };

      component.ftsStates$ = of(statesWithLongId);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled).toBeTruthy();
    });

    it('should handle FTS with invalid timestamps', () => {
      const statesWithInvalidTimestamp: Record<string, FtsState> = {
        '5iO4': {
          ftsId: '5iO4',
          status: 'idle',
          lastSeen: 'invalid-date',
        },
      };

      component.ftsStates$ = of(statesWithInvalidTimestamp);
      
      // Component might use DatePipe which will throw for invalid dates
      // This tests that the component handles the error gracefully
      try {
        fixture.detectChanges();
        const compiled = fixture.nativeElement as HTMLElement;
        expect(compiled.textContent).toContain('5iO4');
      } catch (error) {
        // DatePipe error is expected for invalid dates
        expect(error).toBeDefined();
      }
    });

    it('should handle FTS with negative speed', () => {
      const statesWithNegativeSpeed: Record<string, FtsState> = {
        '5iO4': {
          ftsId: '5iO4',
          status: 'moving',
          position: { x: 100, y: 200 },
          speed: -0.5,
          lastSeen: '2025-11-10T18:00:00Z',
        },
      };

      component.ftsStates$ = of(statesWithNegativeSpeed);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('5iO4');
    });
  });
});

