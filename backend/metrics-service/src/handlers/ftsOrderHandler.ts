/**
 * Handler for fts/v1/ff/+/order topic
 * Maps FTS order data to InfluxDB measurement: fts_orders
 */

import { Point } from '@influxdata/influxdb-client';
import { FtsOrder } from '../types';
import { logger } from '../logger';

/**
 * Extract FTS ID from topic path
 * Topic format: fts/v1/ff/{ftsId}/order
 */
function extractFtsId(topic: string): string {
  const parts = topic.split('/');
  return parts[3] || 'unknown';
}

/**
 * Parse and create InfluxDB points from FTS order messages
 * 
 * Measurement: fts_orders
 * Tags: fts_id, order_id, order_type, load_type
 * Fields: order_count (always 1), order_update_id, node_count, edge_count
 * Time: timestamp from payload or current time
 */
export function handleFtsOrder(topic: string, payloadStr: string): Point[] {
  const points: Point[] = [];

  try {
    let order: FtsOrder;
    const parsed = JSON.parse(payloadStr);

    // Handle nested payload structure
    if (parsed.payload) {
      if (typeof parsed.payload === 'string') {
        order = JSON.parse(parsed.payload);
      } else {
        order = parsed.payload;
      }
    } else {
      order = parsed;
    }

    const ftsId = extractFtsId(topic);
    const timestamp = order.timestamp ? new Date(order.timestamp) : new Date();

    const point = new Point('fts_orders')
      .tag('fts_id', ftsId)
      .tag('order_id', order.orderId)
      .intField('order_count', 1)
      .timestamp(timestamp);

    // Add optional tags
    if (order.orderType) {
      point.tag('order_type', order.orderType);
    }
    if (order.loadType) {
      point.tag('load_type', order.loadType);
    }

    // Add optional fields
    if (typeof order.orderUpdateId === 'number') {
      point.intField('order_update_id', order.orderUpdateId);
    }
    if (order.nodes && Array.isArray(order.nodes)) {
      point.intField('node_count', order.nodes.length);
    }
    if (order.edges && Array.isArray(order.edges)) {
      point.intField('edge_count', order.edges.length);
    }

    points.push(point);
    logger.debug(`Created FTS order point for ${ftsId}, order ${order.orderId}`);
  } catch (error) {
    logger.error('Failed to parse FTS order message', error);
  }

  return points;
}
