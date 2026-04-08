import {
  buildArduinoConfigPayload,
  draftFromFactsheet,
  draftFromThresholdsOnly,
  isArduinoStationFactsheet,
} from '../arduino-station-factsheet.utils';
import type { ArduinoStationFactsheet } from '../arduino-station-factsheet.types';

describe('arduino-station-factsheet.utils', () => {
  it('isArduinoStationFactsheet accepts valid payload', () => {
    const fs: ArduinoStationFactsheet = {
      sketchVersion: '1.1.8',
      stationId: 'sensor-station-1',
      configTopic: 'osf/arduino/station/config',
      thresholds: { dhtTempWarn: 30 },
      sensors: [],
    };
    expect(isArduinoStationFactsheet(fs)).toBe(true);
  });

  it('buildArduinoConfigPayload nests thresholds', () => {
    const p = buildArduinoConfigPayload({
      dhtTempWarn: 31,
      dhtTempDanger: 35,
      dhtHumWarn: 60,
      dhtHumDanger: 85,
      gasWarn: 500,
      gasDanger: 750,
      flameRaw: 25,
      mpuMagnitudeYellow: 18000,
      mpuMagnitudeRed: 26000,
    });
    expect(p).toEqual({
      thresholds: {
        dhtTempWarn: 31,
        dhtTempDanger: 35,
        dhtHumWarn: 60,
        dhtHumDanger: 85,
        gasWarn: 500,
        gasDanger: 750,
        flameRaw: 25,
        mpuMagnitudeYellow: 18000,
        mpuMagnitudeRed: 26000,
      },
    });
  });

  it('draftFromFactsheet merges missing threshold fields with defaults', () => {
    const fs = {
      sketchVersion: '1.0.0',
      stationId: 'x',
      configTopic: 'osf/arduino/station/config',
      thresholds: { dhtTempWarn: 28 },
      sensors: [],
    } as ArduinoStationFactsheet;
    const d = draftFromFactsheet(fs);
    expect(d.dhtTempWarn).toBe(28);
    expect(d.dhtTempDanger).toBe(35);
  });

  it('draftFromThresholdsOnly uses defaults when null/undefined', () => {
    const a = draftFromThresholdsOnly(null);
    const b = draftFromThresholdsOnly(undefined);
    expect(a.dhtTempWarn).toBe(b.dhtTempWarn);
    expect(a.dhtTempDanger).toBe(35);
  });

  it('draftFromThresholdsOnly merges partial MQTT thresholds', () => {
    const d = draftFromThresholdsOnly({ dhtTempWarn: 22, mpuMagnitudeYellow: 19000 });
    expect(d.dhtTempWarn).toBe(22);
    expect(d.dhtTempDanger).toBe(35);
    expect(d.mpuMagnitudeYellow).toBe(19000);
  });
});
