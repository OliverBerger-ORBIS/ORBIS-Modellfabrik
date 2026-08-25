import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

/** Logical tables shared by Postgres init and MSSQL T-SQL (Häppchen 2). */
const EXPECTED_TABLES = [
  'shopfloor_event',
  'production_order',
  'production_step',
  'workpiece',
  'sensor_snapshot',
  'mqtt_raw_message',
] as const;

const ROOT = resolve(__dirname, '../../../../');

function tablesFromSql(sql: string, dialect: 'postgres' | 'mssql'): string[] {
  const pattern =
    dialect === 'postgres'
      ? /CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)/gi
      : /CREATE\s+TABLE\s+dbo\.(\w+)/gi;
  const found = new Set<string>();
  for (const match of sql.matchAll(pattern)) {
    found.add(match[1]!.toLowerCase());
  }
  return [...found].sort();
}

describe('schema contract Postgres ↔ MSSQL', () => {
  it('lists the same core tables in both dialects', () => {
    const pg = readFileSync(resolve(ROOT, 'db/init/001_schema.sql'), 'utf8');
    const ms = readFileSync(resolve(ROOT, 'db/mssql/002_schema.sql'), 'utf8');

    const pgTables = tablesFromSql(pg, 'postgres');
    const msTables = tablesFromSql(ms, 'mssql');

    expect(pgTables).toEqual([...EXPECTED_TABLES].sort());
    expect(msTables).toEqual([...EXPECTED_TABLES].sort());
  });

  it('MSSQL schema stores JSON payloads as NVARCHAR(MAX) (no JSONB)', () => {
    const ms = readFileSync(resolve(ROOT, 'db/mssql/002_schema.sql'), 'utf8');
    expect(ms).toMatch(/payload_json\s+NVARCHAR\(MAX\)/i);
    expect(ms).not.toMatch(/JSONB/i);
  });

  it('MSSQL schema keeps sensor reason check values', () => {
    const ms = readFileSync(resolve(ROOT, 'db/mssql/002_schema.sql'), 'utf8');
    expect(ms).toMatch(/EVENT/);
    expect(ms).toMatch(/INTERVAL/);
    expect(ms).toMatch(/THRESHOLD/);
  });
});
