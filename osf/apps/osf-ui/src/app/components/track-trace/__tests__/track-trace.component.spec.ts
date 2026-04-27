import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { BehaviorSubject, of } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { TrackTraceComponent } from '../track-trace.component';
import { WorkpieceHistoryService } from '../../../services/workpiece-history.service';
import { ModuleNameService } from '../../../services/module-name.service';
import { EnvironmentService } from '../../../services/environment.service';
import { TrackTraceEnvironmentService } from '../../../services/track-trace-environment.service';
import type { WorkpieceHistory, OrderContext } from '../../../services/workpiece-history.service';

describe('TrackTraceComponent', () => {
  let component: TrackTraceComponent;
  let fixture: ComponentFixture<TrackTraceComponent>;
  let historyMap$: BehaviorSubject<Map<string, WorkpieceHistory>>;

  const createHistoryWithOrderStatus = (status: OrderContext['status']): WorkpieceHistory => ({
    workpieceId: 'wp-failed-test',
    workpieceType: 'RED',
    events: [],
    currentLocation: 'SVR4H73275',
    orders: [
      {
        orderId: 'order-1',
        orderType: 'PRODUCTION',
        status,
        customerOrderId: 'ERP-CO-X',
        customerId: 'CUST-1',
      },
    ],
  });

  beforeEach(async () => {
    historyMap$ = new BehaviorSubject(new Map<string, WorkpieceHistory>());

    const workpieceHistoryServiceMock = {
      initialize: jest.fn(),
      getHistory$: jest.fn(() => historyMap$.asObservable()),
    };

    const environmentServiceMock = {
      get current() {
        return { key: 'mock' as const };
      },
      environment$: new BehaviorSubject({ key: 'mock' as const, label: 'Mock', description: '', connection: { mqttHost: 'localhost', mqttPort: 1883 } }),
    };

    const trackTraceEnvironmentMock = {
      snapshot$: of({
        rows: [{ id: 'empty', label: '', value: '', variant: 'normal' as const }],
        hasAlarm: false,
        updatedAt: '2020-01-01T00:00:00.000Z',
      }),
    };

    await TestBed.configureTestingModule({
      imports: [TrackTraceComponent, FormsModule, HttpClientTestingModule],
      providers: [
        ModuleNameService,
        { provide: WorkpieceHistoryService, useValue: workpieceHistoryServiceMock },
        { provide: EnvironmentService, useValue: environmentServiceMock },
        { provide: TrackTraceEnvironmentService, useValue: trackTraceEnvironmentMock },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TrackTraceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Order Status FAILED/ERROR display', () => {
    it('should display Failed status when order has status ERROR', () => {
      const history = createHistoryWithOrderStatus('ERROR');
      historyMap$.next(new Map([['wp-failed-test', history]]));
      component.selectWorkpiece('wp-failed-test');
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      const failedLabel = el.querySelector('.status-failed');
      expect(failedLabel).toBeTruthy();
      expect(failedLabel?.textContent?.trim()).toMatch(/Failed|Fehlgeschlagen|Échoué/);
    });

    it('should display Failed status when order has status FAILED', () => {
      const history = createHistoryWithOrderStatus('FAILED');
      historyMap$.next(new Map([['wp-failed-test', history]]));
      component.selectWorkpiece('wp-failed-test');
      fixture.detectChanges();

      const el = fixture.nativeElement as HTMLElement;
      const failedLabel = el.querySelector('.status-failed');
      expect(failedLabel).toBeTruthy();
    });
  });
});
