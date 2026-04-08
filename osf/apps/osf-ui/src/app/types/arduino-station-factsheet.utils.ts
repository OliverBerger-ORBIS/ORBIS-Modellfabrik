import type {
  ArduinoStationFactsheet,
  ArduinoStationThresholdDraft,
  ArduinoStationThresholds,
} from './arduino-station-factsheet.types';

const DEFAULTS: ArduinoStationThresholdDraft = {
  dhtTempWarn: 30,
  dhtTempDanger: 35,
  dhtHumWarn: 60,
  dhtHumDanger: 85,
  gasWarn: 500,
  gasDanger: 750,
  flameRaw: 25,
  mpuMagnitudeYellow: 18500,
  mpuMagnitudeRed: 26500,
};

export function isArduinoStationFactsheet(payload: unknown): payload is ArduinoStationFactsheet {
  if (!payload || typeof payload !== 'object') {
    return false;
  }
  const o = payload as Record<string, unknown>;
  return (
    typeof o['sketchVersion'] === 'string' &&
    typeof o['stationId'] === 'string' &&
    typeof o['configTopic'] === 'string' &&
    Array.isArray(o['sensors']) &&
    o['thresholds'] !== undefined &&
    typeof o['thresholds'] === 'object'
  );
}

/** Merge partial MQTT `thresholds` with sketch defaults (Environmental Data tab, mock without factsheet). */
export function draftFromThresholdsOnly(t: ArduinoStationThresholds | undefined | null): ArduinoStationThresholdDraft {
  const d = defaultArduinoThresholdDraft();
  if (!t) {
    return d;
  }
  return {
    dhtTempWarn: t.dhtTempWarn ?? d.dhtTempWarn,
    dhtTempDanger: t.dhtTempDanger ?? d.dhtTempDanger,
    dhtHumWarn: t.dhtHumWarn ?? d.dhtHumWarn,
    dhtHumDanger: t.dhtHumDanger ?? d.dhtHumDanger,
    gasWarn: t.gasWarn ?? d.gasWarn,
    gasDanger: t.gasDanger ?? d.gasDanger,
    flameRaw: t.flameRaw ?? d.flameRaw,
    mpuMagnitudeYellow: t.mpuMagnitudeYellow ?? d.mpuMagnitudeYellow,
    mpuMagnitudeRed: t.mpuMagnitudeRed ?? d.mpuMagnitudeRed,
  };
}

export function draftFromFactsheet(fs: ArduinoStationFactsheet): ArduinoStationThresholdDraft {
  return draftFromThresholdsOnly(fs.thresholds);
}

export function defaultArduinoThresholdDraft(): ArduinoStationThresholdDraft {
  return { ...DEFAULTS };
}

export function buildArduinoConfigPayload(draft: ArduinoStationThresholdDraft): Record<string, unknown> {
  return {
    thresholds: { ...draft },
  };
}
