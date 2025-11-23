/**
 * Handler for fts/v1/ff/+/connection topic
 * Maps FTS connection status to InfluxDB measurement: fts_connection
 */

import { Point } from '@influxdata/influxdb-client';
import { FtsConnection } from '../types';
import { logger } from '../logger';

/**
 * Extract FTS ID from topic path
 * Topic format: fts/v1/ff/{ftsId}/connection
 */
function extractFtsId(topic: string): string {
  const parts = topic.split('/');
  return parts[3] || 'unknown';
}

/**
 * Parse and create InfluxDB points from FTS connection messages
 * 
 * Measurement: fts_connection
 * Tags: fts_id, connection_state
 * Fields: connected (0 or 1)
 * Time: timestamp from payload or current time
 */
export function handleFtsConnection(topic: string, payloadStr: string): Point[] {
  const points: Point[] = [];

  try {
    let connection: FtsConnection;
    const parsed = JSON.parse(payloadStr);

    // Handle nested payload structure
    if (parsed.payload) {
      if (typeof parsed.payload === 'string') {
        connection = JSON.parse(parsed.payload);
      } else {
        connection = parsed.payload;
      }
    } else {
      connection = parsed;
    }

    const ftsId = extractFtsId(topic);
    const timestamp = connection.timestamp ? new Date(connection.timestamp) : new Date();

    const point = new Point('fts_connection')
      .tag('fts_id', ftsId)
      .intField('connected', connection.connected ? 1 : 0)
      .timestamp(timestamp);

    // Add connection state if available
    if (connection.connectionState) {
      point.tag('connection_state', connection.connectionState);
    }

    points.push(point);
    logger.debug(`Created FTS connection point for ${ftsId}: ${connection.connected ? 'connected' : 'disconnected'}`);
  } catch (error) {
    logger.error('Failed to parse FTS connection message', error);
  }

  return points;
}
