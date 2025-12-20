import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StockViewComponent } from '../stock-view.component';
import { of } from 'rxjs';

describe('StockViewComponent', () => {
  let component: StockViewComponent;
  let fixture: ComponentFixture<StockViewComponent>;

  const mockStock: Record<string, number> = {
    'PART-001': 10,
    'PART-002': 25,
    'PART-003': 5,
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StockViewComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(StockViewComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display stock levels from stream', () => {
    component.stockByPart$ = of(mockStock);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const rows = compiled.querySelectorAll('tbody tr');
    expect(rows.length).toBe(3);
  });

  it('should display part IDs and quantities', () => {
    component.stockByPart$ = of(mockStock);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('PART-001');
    expect(compiled.textContent).toContain('10');
    expect(compiled.textContent).toContain('PART-002');
    expect(compiled.textContent).toContain('25');
  });

  it('should handle empty stock', () => {
    component.stockByPart$ = of({});
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyMessage = compiled.querySelector('.empty');
    expect(emptyMessage).toBeTruthy();
    expect(emptyMessage?.textContent).toContain('No stock movements');
  });

  it('should display table headers', () => {
    component.stockByPart$ = of(mockStock);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const headers = compiled.querySelectorAll('thead th');
    expect(headers.length).toBe(2);
    expect(compiled.textContent).toContain('Part');
    expect(compiled.textContent).toContain('Quantity');
  });

  it('should update when stock stream changes', () => {
    component.stockByPart$ = of({});
    fixture.detectChanges();

    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.empty')).toBeTruthy();

    // Create new component instance with new stream
    fixture = TestBed.createComponent(StockViewComponent);
    component = fixture.componentInstance;
    component.stockByPart$ = of(mockStock);
    fixture.detectChanges();

    compiled = fixture.nativeElement as HTMLElement;
    const rows = compiled.querySelectorAll('tbody tr');
    expect(rows.length).toBe(3);
  });

  it('should handle zero quantities', () => {
    const stockWithZero: Record<string, number> = {
      'PART-001': 0,
      'PART-002': 5,
    };

    component.stockByPart$ = of(stockWithZero);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const rows = compiled.querySelectorAll('tbody tr');
    expect(rows.length).toBe(2);
    expect(compiled.textContent).toContain('PART-001');
    expect(compiled.textContent).toContain('0');
  });

  describe('Edge Cases', () => {
    it('should handle stock with negative quantities', () => {
      const stockWithNegative: Record<string, number> = {
        'PART-001': -5,
        'PART-002': 10,
      };

      component.stockByPart$ = of(stockWithNegative);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      const rows = compiled.querySelectorAll('tbody tr');
      expect(rows.length).toBe(2);
      expect(compiled.textContent).toContain('PART-001');
    });

    it('should handle stock with very large quantities', () => {
      const stockWithLargeQuantities: Record<string, number> = {
        'PART-001': 999999999,
        'PART-002': 1000000000,
      };

      component.stockByPart$ = of(stockWithLargeQuantities);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('PART-001');
    });

    it('should handle stock with special characters in part IDs', () => {
      const stockWithSpecialChars: Record<string, number> = {
        'PART-!@#$%': 10,
        'PART-<>?:"{}|': 20,
      };

      component.stockByPart$ = of(stockWithSpecialChars);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('PART-!@#$%');
    });

    it('should handle stock with empty part IDs', () => {
      const stockWithEmptyIds: Record<string, number> = {
        '': 10,
        'PART-002': 20,
      };

      component.stockByPart$ = of(stockWithEmptyIds);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      // Component should still render
      expect(compiled).toBeTruthy();
    });

    it('should handle stock with very long part IDs', () => {
      const longPartId = 'PART-' + 'A'.repeat(1000);
      const stockWithLongIds: Record<string, number> = {
        [longPartId]: 10,
      };

      component.stockByPart$ = of(stockWithLongIds);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled).toBeTruthy();
    });

    it('should handle stock with decimal quantities', () => {
      const stockWithDecimals: Record<string, number> = {
        'PART-001': 10.5,
        'PART-002': 20.75,
      };

      component.stockByPart$ = of(stockWithDecimals);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('PART-001');
    });

    it('should handle stock with NaN quantities', () => {
      const stockWithNaN: Record<string, number> = {
        'PART-001': NaN,
        'PART-002': 10,
      };

      component.stockByPart$ = of(stockWithNaN);
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      // Component should still render
      expect(compiled).toBeTruthy();
    });
  });
});

