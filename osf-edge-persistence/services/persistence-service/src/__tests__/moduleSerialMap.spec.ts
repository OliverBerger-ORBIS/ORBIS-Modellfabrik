import { describe, expect, it } from 'vitest';
import { resolveModuleType } from '../moduleSerialMap';

describe('resolveModuleType', () => {
  it('maps known APS serials', () => {
    expect(resolveModuleType({ moduleSerial: 'SVR4H73275' })).toBe('DPS');
    expect(resolveModuleType({ moduleSerial: 'SVR3QA0022' })).toBe('HBW');
    expect(resolveModuleType({ moduleSerial: 'SVR4H76449' })).toBe('DRILL');
    expect(resolveModuleType({ moduleSerial: 'SVR3QA2098' })).toBe('MILL');
    expect(resolveModuleType({ moduleSerial: 'SVR4H76530' })).toBe('AIQS');
  });

  it('prefers known payload moduleType over serial', () => {
    expect(
      resolveModuleType({
        payloadModuleType: 'MILL',
        moduleSerial: 'SVR4H73275',
      })
    ).toBe('MILL');
  });

  it('ignores workpiece color as payload type and falls back to serial', () => {
    expect(
      resolveModuleType({
        payloadModuleType: 'WHITE',
        moduleSerial: 'SVR4H73275',
      })
    ).toBe('DPS');
  });

  it('uses topic moduleType (FTS)', () => {
    expect(resolveModuleType({ topicModuleType: 'FTS', moduleSerial: '5iO4' })).toBe('FTS');
  });
});
