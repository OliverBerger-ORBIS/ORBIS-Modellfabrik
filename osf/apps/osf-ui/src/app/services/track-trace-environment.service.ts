import { Injectable, inject } from '@angular/core';
import { Observable, merge, timer, combineLatest } from 'rxjs';
import { distinctUntilChanged, filter, map, pairwise, shareReplay, take, withLatestFrom } from 'rxjs/operators';
import type { Bme680Snapshot, LdrSnapshot } from '@osf/entities';
import { MessageMonitorService } from './message-monitor.service';

/** Row in Track & Trace “Environment / sensors” column */
export interface TrackTraceEnvironmentRow {
  id: string;
  label: string;
  value: string;
  variant: 'normal' | 'warn' | 'alarm';
}

export interface TrackTraceEnvironmentSnapshot {
  rows: TrackTraceEnvironmentRow[];
  hasAlarm: boolean;
  updatedAt: string;
}

interface VibrationPayload {
  vibrationLevel?: 'green' | 'yellow' | 'red';
  vibrationDetected?: boolean;
  magnitude?: number;
  impulseCount?: number;
  timestamp?: string;
}

interface Dht11Payload {
  temperature?: number;
  humidity?: number;
  timestamp?: string;
}

interface FlamePayload {
  flameDetected?: boolean;
  rawValue?: number;
  timestamp?: string;
}

interface GasPayload {
  gasDetected?: boolean;
  gasLevel?: number;
  rawValue?: number;
  timestamp?: string;
}

const BME680_TOPIC = '/j1/txt/1/i/bme680';
const LDR_TOPIC = '/j1/txt/1/i/ldr';
const DHT11_TOPIC = 'osf/arduino/temperature/dht11-1/state';
const VIB_MPU_TOPIC = 'osf/arduino/vibration/mpu6050-1/state';
const VIB_SW420_TOPIC = 'osf/arduino/vibration/sw420-1/state';
const FLAME_TOPIC = 'osf/arduino/flame/flame-1/state';
const GAS_TOPIC = 'osf/arduino/gas/mq2-1/state';

const SAMPLE_MS = 30_000;

function parseJson<T>(payload: unknown): T | null {
  if (payload == null) {
    return null;
  }
  if (typeof payload === 'object') {
    return payload as T;
  }
  if (typeof payload === 'string') {
    try {
      return JSON.parse(payload) as T;
    } catch {
      return null;
    }
  }
  return null;
}

/**
 * Live environment snapshot for Track & Trace (UC-01 Live Demo).
 * Combines shopfloor-adjacent MQTT sensor topics: ~30s routine refresh, immediate emit on alarm edges.
 */
@Injectable({ providedIn: 'root' })
export class TrackTraceEnvironmentService {
  private readonly messageMonitor = inject(MessageMonitorService);

  /** Snapshot stream for the third Track & Trace column */
  readonly snapshot$: Observable<TrackTraceEnvironmentSnapshot>;

  constructor() {
    const bme680$ = this.messageMonitor.getLastMessage<unknown>(BME680_TOPIC).pipe(
      map((m) => (m?.valid ? parseJson<Bme680Snapshot>(m.payload) : null))
    );
    const ldr$ = this.messageMonitor.getLastMessage<unknown>(LDR_TOPIC).pipe(
      map((m) => (m?.valid ? parseJson<LdrSnapshot>(m.payload) : null))
    );
    const dht11$ = this.messageMonitor.getLastMessage<unknown>(DHT11_TOPIC).pipe(
      map((m) => (m?.valid ? parseJson<Dht11Payload>(m.payload) : null))
    );
    const mpu$ = this.messageMonitor.getLastMessage<unknown>(VIB_MPU_TOPIC).pipe(
      map((m) => (m?.valid ? parseJson<VibrationPayload>(m.payload) : null))
    );
    const sw420$ = this.messageMonitor.getLastMessage<unknown>(VIB_SW420_TOPIC).pipe(
      map((m) => (m?.valid ? parseJson<VibrationPayload>(m.payload) : null))
    );
    const flame$ = this.messageMonitor.getLastMessage<unknown>(FLAME_TOPIC).pipe(
      map((m) => (m?.valid ? parseJson<FlamePayload>(m.payload) : null))
    );
    const gas$ = this.messageMonitor.getLastMessage<unknown>(GAS_TOPIC).pipe(
      map((m) => (m?.valid ? parseJson<GasPayload>(m.payload) : null))
    );

    const live$ = combineLatest({
      bme680: bme680$,
      ldr: ldr$,
      dht11: dht11$,
      mpu: mpu$,
      sw420: sw420$,
      flame: flame$,
      gas: gas$,
    }).pipe(shareReplay({ bufferSize: 1, refCount: false }));

    const periodic$ = timer(SAMPLE_MS, SAMPLE_MS).pipe(withLatestFrom(live$), map(([, snap]) => snap));

    const alarm$ = live$.pipe(
      map((s) => ({ snap: s, alarm: this.hasEnvironmentAlarm(s) })),
      pairwise(),
      filter(([p, c]) => p.alarm !== c.alarm),
      map(([, c]) => c.snap)
    );

    this.snapshot$ = merge(live$.pipe(take(1)), periodic$, alarm$).pipe(
      map((snap) => this.buildSnapshot(snap)),
      distinctUntilChanged(
        (a, b) => a.hasAlarm === b.hasAlarm && this.rowsSig(a) === this.rowsSig(b)
      ),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  private rowsSig(s: TrackTraceEnvironmentSnapshot): string {
    return s.rows.map((r) => `${r.id}:${r.value}:${r.variant}`).join('|');
  }

  hasEnvironmentAlarm(s: {
    mpu: VibrationPayload | null;
    sw420: VibrationPayload | null;
    flame: FlamePayload | null;
    gas: GasPayload | null;
  }): boolean {
    const mpuAlarm = s.mpu?.vibrationLevel === 'red' || s.mpu?.vibrationDetected === true;
    const swAlarm =
      s.sw420?.vibrationLevel === 'red' ||
      s.sw420?.vibrationDetected === true ||
      (s.sw420?.vibrationLevel === 'yellow' && s.sw420?.vibrationDetected);
    const flameAlarm = s.flame?.flameDetected === true;
    const gasAlarm = s.gas?.gasDetected === true || (s.gas?.gasLevel ?? 0) >= 2;
    return Boolean(mpuAlarm || swAlarm || flameAlarm || gasAlarm);
  }

  private buildSnapshot(s: {
    bme680: Bme680Snapshot | null;
    ldr: LdrSnapshot | null;
    dht11: Dht11Payload | null;
    mpu: VibrationPayload | null;
    sw420: VibrationPayload | null;
    flame: FlamePayload | null;
    gas: GasPayload | null;
  }): TrackTraceEnvironmentSnapshot {
    const rows: TrackTraceEnvironmentRow[] = [];
    const alarm = this.hasEnvironmentAlarm(s);

    const t = s.bme680?.ts ?? s.ldr?.ts ?? s.dht11?.timestamp ?? s.mpu?.timestamp ?? new Date().toISOString();

    const bmeRh = s.bme680?.h ?? s.bme680?.rh;
    if (s.bme680 && (s.bme680.t != null || bmeRh != null)) {
      const parts: string[] = [];
      if (s.bme680.t != null) {
        parts.push(`${s.bme680.t.toFixed(1)}°C`);
      }
      if (bmeRh != null) {
        parts.push(`${bmeRh.toFixed(0)}% RH`);
      }
      if (s.bme680.iaq != null) {
        parts.push(`IAQ ${Math.round(s.bme680.iaq)}`);
      }
      rows.push({
        id: 'bme680',
        label: 'BME680',
        value: parts.length ? parts.join(' · ') : '—',
        variant: 'normal',
      });
    }

    if (s.ldr && (s.ldr.br != null || s.ldr.ldr != null)) {
      const lux = s.ldr.br ?? s.ldr.ldr;
      rows.push({
        id: 'ldr',
        label: 'Ambient light',
        value: lux != null ? `${Math.round(lux)}` : '—',
        variant: 'normal',
      });
    }

    if (s.dht11 && (s.dht11.temperature != null || s.dht11.humidity != null)) {
      const p: string[] = [];
      if (s.dht11.temperature != null) {
        p.push(`${s.dht11.temperature.toFixed(1)}°C`);
      }
      if (s.dht11.humidity != null) {
        p.push(`${s.dht11.humidity.toFixed(0)}% RH`);
      }
      rows.push({
        id: 'dht11',
        label: 'DHT11',
        value: p.join(' · ') || '—',
        variant: 'normal',
      });
    }

    const mpuLevel = s.mpu?.vibrationLevel;
    const mpuVariant: TrackTraceEnvironmentRow['variant'] =
      mpuLevel === 'red' ? 'alarm' : mpuLevel === 'yellow' ? 'warn' : 'normal';
    if (s.mpu && (mpuLevel || s.mpu.magnitude != null || s.mpu.vibrationDetected != null)) {
      const mag = s.mpu.magnitude != null ? `mag ${s.mpu.magnitude.toFixed(2)}` : '';
      rows.push({
        id: 'vib-mpu',
        label: 'Vibration (MPU-6050)',
        value: [mpuLevel?.toUpperCase() ?? '—', mag].filter(Boolean).join(' · '),
        variant: mpuVariant,
      });
    }

    const swLevel = s.sw420?.vibrationLevel;
    const swVariant: TrackTraceEnvironmentRow['variant'] =
      s.sw420?.vibrationDetected === true || swLevel === 'red'
        ? 'alarm'
        : swLevel === 'yellow'
          ? 'warn'
          : 'normal';
    if (s.sw420) {
      rows.push({
        id: 'vib-sw420',
        label: 'Vibration (SW-420)',
        value: s.sw420.vibrationDetected ? 'DETECTED' : swLevel?.toUpperCase() ?? '—',
        variant: swVariant,
      });
    }

    if (s.flame && (s.flame.flameDetected != null || s.flame.rawValue != null)) {
      rows.push({
        id: 'flame',
        label: 'Flame',
        value: s.flame.flameDetected ? 'ALARM' : s.flame.rawValue != null ? `raw ${s.flame.rawValue}` : '—',
        variant: s.flame.flameDetected ? 'alarm' : 'normal',
      });
    }

    if (s.gas && (s.gas.gasDetected != null || s.gas.rawValue != null || s.gas.gasLevel != null)) {
      const lvl = s.gas.gasLevel ?? 0;
      const variant: TrackTraceEnvironmentRow['variant'] =
        s.gas.gasDetected === true || lvl >= 2 ? 'alarm' : lvl >= 1 ? 'warn' : 'normal';
      let gasValue = '—';
      if (s.gas.gasDetected === true) {
        gasValue = 'DETECTED';
      } else if (s.gas.gasDetected === false && s.gas.rawValue == null) {
        gasValue = 'clear';
      } else if (s.gas.rawValue != null) {
        gasValue = `raw ${s.gas.rawValue}`;
      }
      if (lvl > 0) {
        gasValue = gasValue === '—' ? `L${lvl}` : `${gasValue} · L${lvl}`;
      }
      rows.push({
        id: 'gas',
        label: 'Gas (MQ-2)',
        value: gasValue,
        variant,
      });
    }

    if (rows.length === 0) {
      rows.push({
        id: 'empty',
        label: '',
        value: '',
        variant: 'normal',
      });
    }

    return {
      rows,
      hasAlarm: alarm,
      updatedAt: typeof t === 'string' ? t : new Date().toISOString(),
    };
  }
}
