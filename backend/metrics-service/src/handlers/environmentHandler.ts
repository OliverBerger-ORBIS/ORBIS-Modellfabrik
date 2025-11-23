/**
 * Handler for /j1/txt/1/i/bme680 topic
 * Maps BME680 environment sensor data to InfluxDB measurement: environment
 */

import { Point } from '@influxdata/influxdb-client';
import { EnvironmentData } from '../types';
import { logger } from '../logger';

/**
 * Parse and create InfluxDB points from BME680 environment sensor messages
 * 
 * Measurement: environment
 * Tags: sensor_id, sensor_type
 * Fields: temperature, humidity, iaq, pressure, gas_resistance
 * Time: timestamp from payload or current time
 */
export function handleEnvironment(topic: string, payloadStr: string): Point[] {
  const points: Point[] = [];

  try {
    let data: EnvironmentData;
    const parsed = JSON.parse(payloadStr);

    // Handle nested payload structure
    if (parsed.payload) {
      if (typeof parsed.payload === 'string') {
        data = JSON.parse(parsed.payload);
      } else {
        data = parsed.payload;
      }
    } else {
      data = parsed;
    }

    // Extract sensor ID from topic or use default
    // Topic format: /j1/txt/1/i/bme680
    const sensorId = 'bme680'; // Could be extracted from topic if needed
    const timestamp = data.timestamp || data.ts ? new Date(data.timestamp || data.ts!) : new Date();

    const point = new Point('environment')
      .tag('sensor_id', sensorId)
      .tag('sensor_type', 'BME680')
      .timestamp(timestamp);

    // Add fields if they exist
    if (typeof data.temperature === 'number') {
      point.floatField('temperature', data.temperature);
    }
    if (typeof data.humidity === 'number') {
      point.floatField('humidity', data.humidity);
    }
    if (typeof data.iaq === 'number') {
      point.floatField('iaq', data.iaq);
    }
    if (typeof data.pressure === 'number') {
      point.floatField('pressure', data.pressure);
    }
    if (typeof data.gasResistance === 'number') {
      point.floatField('gas_resistance', data.gasResistance);
    }

    points.push(point);
    logger.debug(`Created environment point from ${sensorId}`);
  } catch (error) {
    logger.error('Failed to parse environment message', error);
  }

  return points;
}
