/**
 * Handler for fts/v1/ff/+/state topic
 * Maps FTS state data to InfluxDB measurement: fts_state
 */

import { Point } from '@influxdata/influxdb-client';
import { FtsState } from '../types';
import { logger } from '../logger';

/**
 * Extract FTS ID from topic path
 * Topic format: fts/v1/ff/{ftsId}/state
 */
function extractFtsId(topic: string): string {
  const parts = topic.split('/');
  return parts[3] || 'unknown';
}

/**
 * Determine if FTS is driving based on motion state
 */
function isDriving(state: FtsState): boolean {
  const motionState = state.motionState?.toUpperCase();
  return motionState === 'MOVING' || state.driving === true;
}

/**
 * Determine if FTS is idle
 */
function isIdle(state: FtsState): boolean {
  const actionState = state.actionState?.toUpperCase();
  const motionState = state.motionState?.toUpperCase();
  return (
    actionState === 'WAITING' ||
    actionState === 'IDLE' ||
    motionState === 'STOPPED'
  );
}

/**
 * Parse and create InfluxDB points from FTS state messages
 * 
 * Measurement: fts_state
 * Tags: fts_id, action_state, motion_state
 * Fields: battery_level, is_driving, is_idle, has_errors, load_count
 * Time: timestamp from payload or current time
 */
export function handleFtsState(topic: string, payloadStr: string): Point[] {
  const points: Point[] = [];

  try {
    // Parse payload - might be nested in wrapper
    let state: FtsState;
    const parsed = JSON.parse(payloadStr);

    if (parsed.payload) {
      if (typeof parsed.payload === 'string') {
        state = JSON.parse(parsed.payload);
      } else {
        state = parsed.payload;
      }
    } else {
      state = parsed;
    }

    const ftsId = extractFtsId(topic);
    const timestamp = state.timestamp ? new Date(state.timestamp) : new Date();

    const point = new Point('fts_state')
      .tag('fts_id', ftsId);

    // Add state tags
    if (state.actionState) {
      point.tag('action_state', state.actionState);
    }
    if (state.motionState) {
      point.tag('motion_state', state.motionState);
    }

    // Add fields
    if (typeof state.batteryLevel === 'number') {
      point.floatField('battery_level', state.batteryLevel);
    }

    // Derived boolean fields
    point.booleanField('is_driving', isDriving(state));
    point.booleanField('is_idle', isIdle(state));
    point.booleanField('has_errors', (state.errors?.length || 0) > 0);

    // Load information
    if (state.loads && Array.isArray(state.loads)) {
      point.intField('load_count', state.loads.length);
    }

    // Order information
    if (state.orderId) {
      point.tag('order_id', state.orderId);
    }
    if (typeof state.orderUpdateId === 'number') {
      point.intField('order_update_id', state.orderUpdateId);
    }

    point.timestamp(timestamp);
    points.push(point);

    logger.debug(`Created FTS state point for ${ftsId}`);
  } catch (error) {
    logger.error('Failed to parse FTS state message', error);
  }

  return points;
}
