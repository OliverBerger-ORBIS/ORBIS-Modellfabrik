import { TestBed } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';
import { take } from 'rxjs/operators';
import type { MonitoredMessage } from '../message-monitor.service';
import { MessageMonitorService } from '../message-monitor.service';
import { TrackTraceEnvironmentService } from '../track-trace-environment.service';

function monitored(payload: unknown, valid = true): MonitoredMessage {
  return {
    topic: 't',
    payload,
    timestamp: new Date().toISOString(),
    valid,
  };
}

describe('TrackTraceEnvironmentService', () => {
  let subjects: Record<string, BehaviorSubject<MonitoredMessage | null>>;

  const getSubject = (topic: string): BehaviorSubject<MonitoredMessage | null> => {
    if (!subjects[topic]) {
      subjects[topic] = new BehaviorSubject<MonitoredMessage | null>(null);
    }
    return subjects[topic];
  };

  beforeEach(() => {
    subjects = {};
    TestBed.configureTestingModule({
      providers: [
        TrackTraceEnvironmentService,
        {
          provide: MessageMonitorService,
          useValue: {
            getLastMessage: (topic: string) => getSubject(topic).asObservable(),
          },
        },
      ],
    });
  });

  it('should create', () => {
    expect(TestBed.inject(TrackTraceEnvironmentService)).toBeTruthy();
  });

  it('hasEnvironmentAlarm is true when MPU vibration level is red', () => {
    const svc = TestBed.inject(TrackTraceEnvironmentService);
    expect(
      svc.hasEnvironmentAlarm({
        mpu: { vibrationLevel: 'red' },
        sw420: null,
        flame: null,
        gas: null,
      })
    ).toBe(true);
  });

  it('emits empty snapshot when no MQTT payloads', (done) => {
    const svc = TestBed.inject(TrackTraceEnvironmentService);
    svc.snapshot$.pipe(take(1)).subscribe((snap) => {
      expect(snap.rows.some((r) => r.id === 'empty')).toBe(true);
      expect(snap.hasAlarm).toBe(false);
      done();
    });
  });

  it('emits alarm snapshot when SW-420 reports detection before first snapshot', (done) => {
    getSubject('osf/arduino/vibration/sw420-1/state').next(
      monitored(JSON.stringify({ vibrationDetected: true, vibrationLevel: 'red' }))
    );
    const svc = TestBed.inject(TrackTraceEnvironmentService);
    svc.snapshot$.pipe(take(1)).subscribe((snap) => {
      expect(snap.hasAlarm).toBe(true);
      const sw = snap.rows.find((r) => r.id === 'vib-sw420');
      expect(sw?.variant).toBe('alarm');
      done();
    });
  });
});
