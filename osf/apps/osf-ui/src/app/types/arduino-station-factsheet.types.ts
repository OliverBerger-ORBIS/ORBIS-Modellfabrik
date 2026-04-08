/**
 * Payload for {@link OSF_ARDUINO_STATION_FACTSHEET_TOPIC} — Arduino publishes current
 * firmware-reported configuration and per-sensor capabilities (single MQTT topic).
 */
export interface ArduinoStationSensorCapability {
  readonly id: string;
  readonly label: string;
  readonly stateTopic: string;
  readonly capabilities?: {
    readonly thresholds?: Record<string, number>;
  };
}

export interface ArduinoStationFactsheet {
  readonly sketchVersion: string;
  readonly stationId: string;
  readonly configTopic: string;
  readonly thresholds: ArduinoStationThresholds;
  readonly sensors: readonly ArduinoStationSensorCapability[];
}

export interface ArduinoStationThresholds {
  readonly dhtTempWarn?: number;
  readonly dhtTempDanger?: number;
  readonly dhtHumWarn?: number;
  readonly dhtHumDanger?: number;
  readonly gasWarn?: number;
  readonly gasDanger?: number;
  readonly flameRaw?: number;
  readonly mpuMagnitudeYellow?: number;
  readonly mpuMagnitudeRed?: number;
}

/** Editable copy for Configuration tab (mutable draft before Apply). */
export type ArduinoStationThresholdDraft = {
  dhtTempWarn: number;
  dhtTempDanger: number;
  dhtHumWarn: number;
  dhtHumDanger: number;
  gasWarn: number;
  gasDanger: number;
  flameRaw: number;
  mpuMagnitudeYellow: number;
  mpuMagnitudeRed: number;
};
