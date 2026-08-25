import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

/** Logical tables for MSSQL OSF edge schema (UC-02: env_* for Umwelt). */
const EXPECTED_TABLES = [
  'shopfloor_event',
  'shopfloor_order',
  'production_step',
  'workpiece',
  'env_sensor_snapshot',
  'mqtt_raw_message',
  'replay_session_ingest',
] as const;

const ROOT = resolve(__dirname, '../../../../');

function tablesFromSqlFiles(paths: string[]): string[] {
  const pattern = /CREATE\s+TABLE\s+dbo\.(\w+)/gi;
  const found = new Set<string>();
  for (const rel of paths) {
    const sql = readFileSync(resolve(ROOT, rel), 'utf8');
    for (const match of sql.matchAll(pattern)) {
      found.add(match[1]!.toLowerCase());
    }
  }
  return [...found].sort();
}

describe('schema contract MSSQL', () => {
  it('lists core + env + replay tables', () => {
    const msTables = tablesFromSqlFiles([
      'db/mssql/002_schema.sql',
      'db/mssql/011_replay_session_ingest.sql',
    ]);

    expect(msTables).toEqual([...EXPECTED_TABLES].sort());
  });

  it('MSSQL schema stores JSON payloads as NVARCHAR(MAX) (no JSONB)', () => {
    const ms = readFileSync(resolve(ROOT, 'db/mssql/002_schema.sql'), 'utf8');
    expect(ms).toMatch(/payload_json\s+NVARCHAR\(MAX\)/i);
    expect(ms).not.toMatch(/JSONB/i);
  });

  it('MSSQL schema keeps sensor reason check values on env_sensor_snapshot', () => {
    const ms = readFileSync(resolve(ROOT, 'db/mssql/002_schema.sql'), 'utf8');
    expect(ms).toMatch(/env_sensor_snapshot/);
    expect(ms).toMatch(/EVENT/);
    expect(ms).toMatch(/INTERVAL/);
    expect(ms).toMatch(/THRESHOLD/);
  });
});
