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
      getTopics: () => [...historyByTopic.keys()],
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
              { serial: 'xkI4', label: 'AGV-2' },
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
    historyByTopic.set('fts/v1/ff/xkI4/order', [{ valid: true, payload }]);
    lastMessageSubjects.get('fts/v1/ff/xkI4/order')?.next({ valid: true, payload });

    service.getFtsSerialForStep$('order-2', 'step-nav').subscribe((serial) => {
      expect(serial).toBe('xkI4');
      done();
    });
  });

  it('should resolve assignment when layout empty (canonical dual-AGV fallback)', (done) => {
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [
        FtsOrderAssignmentService,
        {
          provide: MessageMonitorService,
          useValue: {
            getLastMessage: (topic: string) => {
              if (!lastMessageSubjects.has(topic)) {
                lastMessageSubjects.set(topic, new BehaviorSubject<unknown | null>(null));
              }
              return lastMessageSubjects.get(topic)!.asObservable();
            },
            getHistory: (topic: string) =>
              (historyByTopic.get(topic) ?? []) as Array<{ valid: boolean; payload: unknown }>,
            getTopics: () => [...historyByTopic.keys()],
          },
        },
        {
          provide: ShopfloorMappingService,
          useValue: { getAgvOptions: () => [] },
        },
      ],
    });
    const emptyLayoutService = TestBed.inject(FtsOrderAssignmentService);
    const payload = {
      orderId: 'order-dual',
      nodes: [{ id: 'n1', action: { type: 'DOCK', id: 'nav-step' } }],
    };
    historyByTopic.set('fts/v1/ff/xkI4/order', [{ valid: true, payload }]);
    lastMessageSubjects.get('fts/v1/ff/xkI4/order')?.next({ valid: true, payload });

    emptyLayoutService.getFtsSerialForStep$('order-dual', 'nav-step').subscribe((serial) => {
      expect(serial).toBe('xkI4');
      done();
    });
  });
});
