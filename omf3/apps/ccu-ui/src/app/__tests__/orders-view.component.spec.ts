import { ComponentFixture, TestBed } from '@angular/core/testing';
import { OrdersViewComponent } from '../orders-view.component';
import { of } from 'rxjs';
import type { OrderActive } from '@omf3/entities';

describe('OrdersViewComponent', () => {
  let component: OrdersViewComponent;
  let fixture: ComponentFixture<OrdersViewComponent>;

  const mockOrders: OrderActive[] = [
    {
      orderId: 'order-1',
      productId: 'PROD-001',
      quantity: 5,
      status: 'running',
    },
    {
      orderId: 'order-2',
      productId: 'PROD-002',
      quantity: 10,
      status: 'queued',
    },
  ];

  const mockCounts = {
    running: 1,
    queued: 1,
    completed: 0,
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrdersViewComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(OrdersViewComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display orders from stream', () => {
    component.orders$ = of(mockOrders);
    component.counts$ = of(mockCounts);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const orderItems = compiled.querySelectorAll('li');
    expect(orderItems.length).toBe(2);
  });

  it('should display order details', () => {
    component.orders$ = of(mockOrders);
    component.counts$ = of(mockCounts);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const firstOrder = compiled.querySelector('li');
    expect(firstOrder?.textContent).toContain('order-1');
    expect(firstOrder?.textContent).toContain('PROD-001');
    expect(firstOrder?.textContent).toContain('5');
  });

  it('should display status badges', () => {
    component.orders$ = of(mockOrders);
    component.counts$ = of(mockCounts);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const badges = compiled.querySelectorAll('.status-badges .badge');
    expect(badges.length).toBe(3);
    expect(compiled.textContent).toContain('Running: 1');
    expect(compiled.textContent).toContain('Queued: 1');
    expect(compiled.textContent).toContain('Completed: 0');
  });

  it('should handle empty orders list', () => {
    component.orders$ = of([]);
    component.counts$ = of({ running: 0, queued: 0, completed: 0 });
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyMessage = compiled.querySelector('.empty');
    expect(emptyMessage).toBeTruthy();
    expect(emptyMessage?.textContent).toContain('No active orders');
  });

  it('should display order status', () => {
    component.orders$ = of(mockOrders);
    component.counts$ = of(mockCounts);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const pills = compiled.querySelectorAll('.pill');
    expect(pills.length).toBe(2);
    expect(pills[0]?.textContent).toContain('running');
    expect(pills[1]?.textContent).toContain('queued');
  });

  it('should update when orders stream changes', () => {
    component.orders$ = of([]);
    component.counts$ = of({ running: 0, queued: 0, completed: 0 });
    fixture.detectChanges();

    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.empty')).toBeTruthy();

    // Create new component instance with new streams
    fixture = TestBed.createComponent(OrdersViewComponent);
    component = fixture.componentInstance;
    component.orders$ = of(mockOrders);
    component.counts$ = of(mockCounts);
    fixture.detectChanges();

    compiled = fixture.nativeElement as HTMLElement;
    const orderItems = compiled.querySelectorAll('li');
    expect(orderItems.length).toBe(2);
  });

  describe('Edge Cases', () => {
    it('should handle orders with missing orderId', () => {
      const ordersWithMissingId: OrderActive[] = [
        {
          productId: 'PROD-001',
          quantity: 5,
          status: 'running',
        } as OrderActive,
      ];

      component.orders$ = of(ordersWithMissingId);
      component.counts$ = of({ running: 1, queued: 0, completed: 0 });
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('PROD-001');
    });

    it('should handle orders with null/undefined values', () => {
      const ordersWithNulls: OrderActive[] = [
        {
          orderId: 'order-1',
          productId: undefined,
          quantity: undefined,
          status: undefined,
        } as OrderActive,
      ];

      component.orders$ = of(ordersWithNulls);
      component.counts$ = of({ running: 0, queued: 0, completed: 0 });
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('order-1');
    });

    it('should handle very large order lists', () => {
      const largeOrderList: OrderActive[] = Array.from({ length: 100 }, (_, i) => ({
        orderId: `order-${i}`,
        productId: `PROD-${i}`,
        quantity: i,
        status: i % 2 === 0 ? 'running' : 'queued',
      }));

      component.orders$ = of(largeOrderList);
      component.counts$ = of({ running: 50, queued: 50, completed: 0 });
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      const orderItems = compiled.querySelectorAll('li');
      expect(orderItems.length).toBe(100);
    });

    it('should handle counts with negative values', () => {
      component.orders$ = of(mockOrders);
      component.counts$ = of({ running: -1, queued: -1, completed: -1 });
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      // Component should still render, even with invalid counts
      expect(compiled).toBeTruthy();
    });

    it('should handle counts with very large values', () => {
      component.orders$ = of(mockOrders);
      component.counts$ = of({ running: 999999, queued: 999999, completed: 999999 });
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('999999');
    });

    it('should handle orders with special characters in IDs', () => {
      const ordersWithSpecialChars: OrderActive[] = [
        {
          orderId: 'order-!@#$%^&*()',
          productId: 'PROD-<>?:"{}|',
          quantity: 5,
          status: 'running',
        },
      ];

      component.orders$ = of(ordersWithSpecialChars);
      component.counts$ = of({ running: 1, queued: 0, completed: 0 });
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.textContent).toContain('order-!@#$%^&*()');
    });

    it('should handle orders with empty strings', () => {
      const ordersWithEmptyStrings: OrderActive[] = [
        {
          orderId: '',
          productId: '',
          quantity: 0,
          status: '',
        },
      ];

      component.orders$ = of(ordersWithEmptyStrings);
      component.counts$ = of({ running: 0, queued: 0, completed: 0 });
      fixture.detectChanges();

      const compiled = fixture.nativeElement as HTMLElement;
      // Component should still render
      expect(compiled).toBeTruthy();
    });
  });
});

