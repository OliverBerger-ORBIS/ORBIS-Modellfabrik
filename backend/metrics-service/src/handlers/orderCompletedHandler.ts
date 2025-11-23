/**
 * Handler for ccu/order/completed topic
 * Maps order completion data to InfluxDB measurement: order_durations
 */

import { Point } from '@influxdata/influxdb-client';
import { OrderCompleted } from '../types';
import { logger } from '../logger';

/**
 * Parse and create InfluxDB points from order completion messages
 * 
 * Measurement: order_durations
 * Tags: order_id, type (color), order_type
 * Fields: duration_s (seconds), steps_count
 * Time: stoppedAt timestamp
 */
export function handleOrderCompleted(topic: string, payloadStr: string): Point[] {
  const points: Point[] = [];

  try {
    // Parse the outer wrapper
    const wrapper = JSON.parse(payloadStr);
    let orders: OrderCompleted[];

    // Check if payload is a JSON string that needs to be parsed again
    if (typeof wrapper.payload === 'string') {
      orders = JSON.parse(wrapper.payload);
    } else if (Array.isArray(wrapper.payload)) {
      orders = wrapper.payload;
    } else if (Array.isArray(wrapper)) {
      orders = wrapper;
    } else {
      orders = [wrapper];
    }

    // Handle both single order and array of orders
    if (!Array.isArray(orders)) {
      orders = [orders];
    }

    for (const order of orders) {
      // Skip if missing critical fields
      if (!order.orderId || !order.startedAt || !order.stoppedAt) {
        logger.warn('Order missing required fields', { orderId: order.orderId });
        continue;
      }

      // Calculate total order duration
      const startTime = new Date(order.startedAt).getTime();
      const stopTime = new Date(order.stoppedAt).getTime();
      const durationMs = stopTime - startTime;
      const durationS = durationMs / 1000;

      const point = new Point('order_durations')
        .tag('order_id', order.orderId)
        .tag('type', order.type || 'UNKNOWN')
        .tag('order_type', order.orderType || 'UNKNOWN')
        .floatField('duration_s', durationS)
        .intField('steps_count', order.productionSteps?.length || 0)
        .timestamp(new Date(order.stoppedAt));

      // Add workpiece ID if available
      if (order.workpieceId) {
        point.tag('workpiece_id', order.workpieceId);
      }

      points.push(point);

      // Also create individual points for each production step
      if (order.productionSteps && order.productionSteps.length > 0) {
        for (const step of order.productionSteps) {
          if (step.startedAt && step.stoppedAt) {
            const stepStartTime = new Date(step.startedAt).getTime();
            const stepStopTime = new Date(step.stoppedAt).getTime();
            const stepDurationS = (stepStopTime - stepStartTime) / 1000;

            const stepPoint = new Point('production_step_durations')
              .tag('order_id', order.orderId)
              .tag('step_id', step.id)
              .tag('step_type', step.type)
              .tag('step_state', step.state)
              .floatField('duration_s', stepDurationS)
              .timestamp(new Date(step.stoppedAt));

            // Add optional tags
            if (step.moduleType) {
              stepPoint.tag('module_type', step.moduleType);
            }
            if (step.serialNumber) {
              stepPoint.tag('serial_number', step.serialNumber);
            }
            if (step.command) {
              stepPoint.tag('command', step.command);
            }

            points.push(stepPoint);
          }
        }
      }

      logger.debug(`Created ${points.length} points for order ${order.orderId}`);
    }
  } catch (error) {
    logger.error('Failed to parse order completed message', error);
  }

  return points;
}
