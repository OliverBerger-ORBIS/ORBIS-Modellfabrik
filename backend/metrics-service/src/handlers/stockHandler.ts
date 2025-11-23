/**
 * Handler for /j1/txt/1/f/i/stock topic
 * Maps stock/inventory data to InfluxDB measurement: stock_levels
 */

import { Point } from '@influxdata/influxdb-client';
import { StockData } from '../types';
import { logger } from '../logger';

/**
 * Parse and create InfluxDB points from stock inventory messages
 * 
 * Measurement: stock_levels
 * Tags: hbw, location, workpiece_type, workpiece_state
 * Fields: stock_count (1 per item), has_workpiece
 * Time: timestamp from payload or current time
 */
export function handleStock(topic: string, payloadStr: string): Point[] {
  const points: Point[] = [];

  try {
    let data: StockData;
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

    const timestamp = data.ts ? new Date(data.ts) : new Date();

    // Create a point for each stock item
    if (data.stockItems && Array.isArray(data.stockItems)) {
      for (const item of data.stockItems) {
        const point = new Point('stock_levels')
          .tag('hbw', item.hbw || 'unknown')
          .tag('location', item.location || 'unknown')
          .timestamp(timestamp);

        // Check if location has a workpiece
        const hasWorkpiece = item.workpiece && item.workpiece.id && item.workpiece.id !== '';
        point.booleanField('has_workpiece', hasWorkpiece);
        point.intField('stock_count', hasWorkpiece ? 1 : 0);

        if (hasWorkpiece) {
          // Add workpiece details as tags
          if (item.workpiece.type) {
            point.tag('workpiece_type', item.workpiece.type);
          }
          if (item.workpiece.state) {
            point.tag('workpiece_state', item.workpiece.state);
          }
          if (item.workpiece.id) {
            point.tag('workpiece_id', item.workpiece.id);
          }
        }

        points.push(point);
      }

      logger.debug(`Created ${points.length} stock level points`);
    }

    // Also create an aggregate point for total stock
    if (data.stockItems && Array.isArray(data.stockItems)) {
      const totalItems = data.stockItems.filter(
        item => item.workpiece && item.workpiece.id && item.workpiece.id !== ''
      ).length;
      
      const rawItems = data.stockItems.filter(
        item => item.workpiece && item.workpiece.state === 'RAW'
      ).length;
      
      const processedItems = data.stockItems.filter(
        item => item.workpiece && item.workpiece.state === 'PROCESSED'
      ).length;

      // Get HBW from first item
      const hbw = data.stockItems[0]?.hbw || 'unknown';

      const aggregatePoint = new Point('stock_aggregate')
        .tag('hbw', hbw)
        .intField('total_items', totalItems)
        .intField('raw_items', rawItems)
        .intField('processed_items', processedItems)
        .intField('empty_locations', data.stockItems.length - totalItems)
        .timestamp(timestamp);

      points.push(aggregatePoint);
    }
  } catch (error) {
    logger.error('Failed to parse stock message', error);
  }

  return points;
}
