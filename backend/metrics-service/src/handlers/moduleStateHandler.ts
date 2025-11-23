/**
 * Handler for module/v1/ff/+/state topic
 * Maps module state data to InfluxDB measurement: module_state
 */

import { Point } from '@influxdata/influxdb-client';
import { ModuleState } from '../types';
import { logger } from '../logger';

/**
 * Extract module ID from topic path
 * Topic format: module/v1/ff/{moduleId}/state
 * or: module/v1/ff/NodeRed/{moduleId}/state
 */
function extractModuleId(topic: string): string {
  const parts = topic.split('/');
  // Check if NodeRed is in the path
  if (parts[3] === 'NodeRed') {
    return parts[4] || 'unknown';
  }
  return parts[3] || 'unknown';
}

/**
 * Check if topic includes NodeRed in path
 */
function isNodeRedTopic(topic: string): boolean {
  return topic.includes('/NodeRed/');
}

/**
 * Parse and create InfluxDB points from module state messages
 * 
 * Measurement: module_state
 * Tags: module_id, state, module_type, is_node_red
 * Fields: active (1 for MANUFACTURE, 0 otherwise), has_order
 * Time: timestamp from payload or current time
 */
export function handleModuleState(topic: string, payloadStr: string): Point[] {
  const points: Point[] = [];

  try {
    let state: ModuleState;
    const parsed = JSON.parse(payloadStr);

    // Handle nested payload structure
    if (parsed.payload) {
      if (typeof parsed.payload === 'string') {
        state = JSON.parse(parsed.payload);
      } else {
        state = parsed.payload;
      }
    } else {
      state = parsed;
    }

    const moduleId = extractModuleId(topic);
    const isNodeRed = isNodeRedTopic(topic);
    const timestamp = state.timestamp ? new Date(state.timestamp) : new Date();

    const point = new Point('module_state')
      .tag('module_id', moduleId)
      .tag('state', state.state || 'UNKNOWN')
      .tag('is_node_red', isNodeRed ? 'true' : 'false');

    // Determine if module is actively manufacturing
    const isManufacturing = state.state?.toUpperCase() === 'MANUFACTURE';
    point.intField('active', isManufacturing ? 1 : 0);

    // Add module type if available
    if (state.moduleType) {
      point.tag('module_type', state.moduleType);
    }
    
    // Add serial number as tag if available and different from module_id
    if (state.serialNumber && state.serialNumber !== moduleId) {
      point.tag('serial_number', state.serialNumber);
    }

    // Add order information
    if (state.orderId) {
      point.tag('order_id', state.orderId);
      point.booleanField('has_order', true);
    } else {
      point.booleanField('has_order', false);
    }

    point.timestamp(timestamp);
    points.push(point);

    logger.debug(`Created module state point for ${moduleId}: ${state.state}`);
  } catch (error) {
    logger.error('Failed to parse module state message', error);
  }

  return points;
}
