/**
 * Handler for fts/v1/ff/+/instantAction topic
 * Maps FTS instant actions to InfluxDB measurement: fts_instant_actions
 */

import { Point } from '@influxdata/influxdb-client';
import { FtsInstantAction } from '../types';
import { logger } from '../logger';

/**
 * Extract FTS ID from topic path
 * Topic format: fts/v1/ff/{ftsId}/instantAction
 */
function extractFtsId(topic: string): string {
  const parts = topic.split('/');
  return parts[3] || 'unknown';
}

/**
 * Parse and create InfluxDB points from FTS instant action messages
 * 
 * Measurement: fts_instant_actions
 * Tags: fts_id, action_id, action_type
 * Fields: action_count (always 1)
 * Time: timestamp from payload or current time
 */
export function handleFtsInstantAction(topic: string, payloadStr: string): Point[] {
  const points: Point[] = [];

  try {
    let action: FtsInstantAction;
    const parsed = JSON.parse(payloadStr);

    // Handle nested payload structure
    if (parsed.payload) {
      if (typeof parsed.payload === 'string') {
        action = JSON.parse(parsed.payload);
      } else {
        action = parsed.payload;
      }
    } else {
      action = parsed;
    }

    const ftsId = extractFtsId(topic);
    const timestamp = action.timestamp ? new Date(action.timestamp) : new Date();

    const point = new Point('fts_instant_actions')
      .tag('fts_id', ftsId)
      .tag('action_id', action.actionId)
      .tag('action_type', action.actionType)
      .intField('action_count', 1)
      .timestamp(timestamp);

    points.push(point);
    logger.debug(`Created FTS instant action point for ${ftsId}: ${action.actionType}`);
  } catch (error) {
    logger.error('Failed to parse FTS instant action message', error);
  }

  return points;
}
