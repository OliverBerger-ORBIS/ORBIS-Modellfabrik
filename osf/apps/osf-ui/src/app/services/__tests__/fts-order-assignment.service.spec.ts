import { TestBed } from '@angular/core/testing';
import { BehaviorSubject, of } from 'rxjs';
import { FtsOrderAssignmentService } from '../fts-order-assignment.service';
import { MessageMonitorService } from '../message-monitor.service';
import { ShopfloorMappingService } from '../shopfloor-mapping.service';

describe('FtsOrderAssignmentService', () => {
  let service: FtsOrderAssignmentService;
  const lastMessageSubjects = new Map<string, BehaviorSubject<unknown | null>>();
  const historyByTopic = new Map<string, unknown[]>();

  beforeEach(() => {
    lastMessageSubjects.clear();
    historyByTopic.clear();

    const messageMonitorMock = {
      getLastMessage: (topic: string) => {
        if (!lastMessageSubjects.has(topic)) {
          lastMessageSubjects.set(topic, new BehaviorSubject<unknown | null>(null));
        }
        return lastMessageSubjects.get(topic)!.asObservable();
      },
      getHistory: (topic: string) => {
        return (historyByTopic.get(topic) ?? []) as Array<{ valid: boolean; payload: unknown }>;
      },
    };

    TestBed.configureTestingModule({
      providers: [
        FtsOrderAssignmentService,
        {
          provide: MessageMonitorService,
          useValue: messageMonitorMock,
        },
        {
          provide: ShopfloorMappingService,
          useValue: {
            getAgvOptions: () => [
              { serial: '5iO4', label: 'AGV-1' },
              { serial: 'leJ4', label: 'AGV-2' },
            ],
          },
        },
      ],
    });
    service = TestBed.inject(FtsOrderAssignmentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return null when no assignment', () => {
    expect(service.getFtsSerialForStep('order-1', 'step-1')).toBeNull();
  });

  it('should return ftsSerial when assignment from fts order message', (done) => {
    const payload = {
      orderId: 'order-1',
      nodes: [{ id: 'n1', action: { type: 'DOCK', id: 'step-1' } }],
    };
    historyByTopic.set('fts/v1/ff/5iO4/order', [{ valid: true, payload }]);
    const subj = lastMessageSubjects.get('fts/v1/ff/5iO4/order');
    subj?.next({ valid: true, payload });

    service.getFtsSerialForStep$('order-1', 'step-1').subscribe((serial) => {
      expect(serial).toBe('5iO4');
      done();
    });
  });

  it('should use last node with action.id when multiple nodes', (done) => {
    const payload = {
      orderId: 'order-2',
      nodes: [
        { id: 'n1', action: { type: 'PASS', id: 'prev' } },
        { id: 'n2', action: { type: 'DOCK', id: 'step-nav' } },
      ],
    };
    historyByTopic.set('fts/v1/ff/leJ4/order', [{ valid: true, payload }]);
    lastMessageSubjects.get('fts/v1/ff/leJ4/order')?.next({ valid: true, payload });

    service.getFtsSerialForStep$('order-2', 'step-nav').subscribe((serial) => {
      expect(serial).toBe('leJ4');
      done();
    });
  });
});
