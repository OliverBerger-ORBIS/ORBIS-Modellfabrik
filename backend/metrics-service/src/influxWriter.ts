/**
 * InfluxDB writer with batching and error handling
 */

import { InfluxDB, Point, WriteApi } from '@influxdata/influxdb-client';
import { Config } from './config';
import { logger } from './logger';

export class InfluxWriter {
  private influxDB: InfluxDB;
  private writeApi: WriteApi;

  constructor(config: Config) {
    this.influxDB = new InfluxDB({
      url: config.influx.url,
      token: config.influx.token,
    });

    // Configure batching for performance
    this.writeApi = this.influxDB.getWriteApi(
      config.influx.org,
      config.influx.bucket,
      'ms', // millisecond precision
      {
        batchSize: 10,
        flushInterval: 5000, // 5 seconds
      }
    );

    // Set default tags (empty for now)
    this.writeApi.useDefaultTags({});
  }

  /**
   * Write a point to InfluxDB
   */
  writePoint(point: Point): void {
    try {
      this.writeApi.writePoint(point);
      logger.debug(`Wrote point to InfluxDB: ${point.toLineProtocol()}`);
    } catch (error) {
      logger.error('Failed to write point to InfluxDB', error);
    }
  }

  /**
   * Write multiple points to InfluxDB
   */
  writePoints(points: Point[]): void {
    try {
      this.writeApi.writePoints(points);
      logger.debug(`Wrote ${points.length} points to InfluxDB`);
    } catch (error) {
      logger.error('Failed to write points to InfluxDB', error);
    }
  }

  /**
   * Flush any pending writes
   */
  async flush(): Promise<void> {
    try {
      await this.writeApi.flush();
      logger.debug('Flushed InfluxDB write buffer');
    } catch (error) {
      logger.error('Failed to flush InfluxDB write buffer', error);
    }
  }

  /**
   * Close the writer and flush all pending writes
   */
  async close(): Promise<void> {
    try {
      await this.writeApi.close();
      logger.info('Closed InfluxDB writer');
    } catch (error) {
      logger.error('Failed to close InfluxDB writer', error);
    }
  }

  /**
   * Get a new Point instance for building measurements
   */
  createPoint(measurement: string): Point {
    return new Point(measurement);
  }
}
