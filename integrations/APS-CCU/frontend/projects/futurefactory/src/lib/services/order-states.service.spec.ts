import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { EMPTY, NEVER, Observable } from 'rxjs';
import { TestScheduler } from 'rxjs/testing';
import { TypedMqttService } from '../futurefactory.service';
import { OrderStatesService, STATE_TOPICS } from './order-states.service';
import { CcuTopic, OrderResponse } from '../../common/protocol';

describe('OrderStatesService', () => {
  const testScheduler = new TestScheduler((actual, expected) => {
    expect(actual).toEqual(expected);
  });
  let service: OrderStatesService;

  type Subscribe = (topic: string) => Observable<any>;
  const runTest = (subscribe: Subscribe) => {
    TestBed.configureTestingModule({
      providers: [MockProvider(TypedMqttService, { subscribe })],
    });
    return TestBed.inject(OrderStatesService);
  };

  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should be created', () => {
    service = runTest(() => EMPTY);
    expect(service).toBeTruthy();
  });

  describe('orderStatus$', () => {
    it("should emit empty object if messages don't have payload", () => {
      testScheduler.run(({ expectObservable, cold }) => {
        service = runTest((topic: string) =>
          cold('s', { s: { topic, payload: {} } })
        );
        const expectedMarble = '(sss)';
        const expectedValues = {
          s: {},
        };
        expectObservable(service.orderStatus$).toBe(
          expectedMarble,
          expectedValues
        );
      });
    });

    it('should emit status, if at least one message has payload', () => {
      testScheduler.run(({ expectObservable, cold }) => {
        const timestamp = new Date();
        service = runTest((topic: string) => {
          if (topic === STATE_TOPICS.order) {
            return cold('s', {
              s: {
                topic,
                payload: { orderId: '123', timestamp, type: 'WHITE' },
              },
            });
          }
          return cold('s', { s: { topic, payload: {} } });
        });
        const expectedMarble = '(ees)';
        const expectedValues = {
          e: {},
          s: {
            123: {
              current: 'Order created: 123 WHITE',
              log: [],
              lastTimestamp: timestamp,
            },
          },
        };
        expectObservable(service.orderStatus$).toBe(
          expectedMarble,
          expectedValues
        );
      });
    });

    it('should emit status, if all message have payload', () => {
      testScheduler.run(({ expectObservable, cold }) => {
        const timestamp = new Date();
        const topics = {
          [STATE_TOPICS.fts]: cold('m', {
            m: {
              topic: STATE_TOPICS.fts,
              payload: {
                orderId: '123',
                serialNumber: '123',
                actionState: {
                  command: 'IN_PROGRESS',
                  timestamp,
                  state: 'IN_PROGRESS',
                },
              },
            },
          }),
          [STATE_TOPICS.module]: cold('m', {
            m: {
              topic: STATE_TOPICS.module,
              payload: {
                orderId: '123',
                serialNumber: '123',
                actionState: {
                  command: 'IN_PROGRESS',
                  timestamp,
                  state: 'IN_PROGRESS',
                },
              },
            },
          }),
          [STATE_TOPICS.order]: cold('m', {
            m: {
              topic: STATE_TOPICS.order,
              payload: {
                orderId: '123',
                timestamp,
                type: 'WHITE',
              },
            },
          }),
        };
        service = runTest((topic: string) => topics[topic] ?? NEVER);
        const expectedMarble = '(abc)';
        const expectedValues = {
          a: {
            123: {
              current: 'FTS 123: IN_PROGRESS',
              log: [],
              lastTimestamp: timestamp,
            },
          },
          b: {
            123: {
              current: 'Module 123: IN_PROGRESS IN_PROGRESS',
              log: ['FTS 123: IN_PROGRESS'],
              lastTimestamp: timestamp,
            },
          },
          c: {
            123: {
              current: 'Order created: 123 WHITE',
              log: [
                'Module 123: IN_PROGRESS IN_PROGRESS',
                'FTS 123: IN_PROGRESS',
              ],
              lastTimestamp: timestamp,
            },
          },
        };
        expectObservable(service.orderStatus$).toBe(
          expectedMarble,
          expectedValues
        );
      });
    });

    describe("hasRunningOrders$", () => {
      it("should emit false if nothing is emitted", () => {
        testScheduler.run(({ expectObservable, cold }) => {
          service = runTest(() => NEVER);
          const expectedMarble = "f";
          const expectedValues = {
            f: false,
          };
          expectObservable(service.hasRunningOrders$).toBe(
            expectedMarble,
            expectedValues
          );
        });
      });

      it("should emit false if there are no orders", () => {
        testScheduler.run(({ expectObservable, cold }) => {
          const topics = {
            [CcuTopic.ACTIVE_ORDERS as string]: cold<OrderResponse[]>('p', {
              p: [],
            })
          };
          service = runTest((topic: string) => topics[topic] ?? NEVER);
          const expectedMarble = "(ff)";
          const expectedValues = {
            f: false,
          };
          expectObservable(service.hasRunningOrders$).toBe(
            expectedMarble,
            expectedValues
          );
        });
      });
    });
  });
});
