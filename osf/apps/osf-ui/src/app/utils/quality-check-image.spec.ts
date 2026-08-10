import {
  normalizeQualityResult,
  parseQualityCheckPayload,
  qualityResultsMatch,
  qualityTimestampsWithinWindow,
  QUALITY_IMAGE_MATCH_WINDOW_MS,
} from './quality-check-image';

describe('quality-check-image utils', () => {
  it('parses valid quality_check payload', () => {
    const parsed = parseQualityCheckPayload({
      result: 'FAILED',
      ts: '2026-08-07T09:08:36.886Z',
      data: 'data:image/png;base64,abc',
      classification: 'CRACK',
      classificationDesc: 'Crack',
    });
    expect(parsed).toEqual({
      dataUrl: 'data:image/png;base64,abc',
      ts: '2026-08-07T09:08:36.886Z',
      result: 'FAILED',
      classification: 'CRACK',
      classificationDesc: 'Crack',
    });
  });

  it('rejects payload without image data URL', () => {
    expect(parseQualityCheckPayload({ result: 'PASSED', data: 'not-an-image' })).toBeNull();
    expect(parseQualityCheckPayload(null)).toBeNull();
  });

  it('normalizes OK/PASS to PASSED and FAIL to FAILED', () => {
    expect(normalizeQualityResult('OK')).toBe('PASSED');
    expect(normalizeQualityResult('passed')).toBe('PASSED');
    expect(normalizeQualityResult('NOK')).toBe('FAILED');
    expect(qualityResultsMatch('OK', 'PASSED')).toBe(true);
    expect(qualityResultsMatch('FAILED', 'PASSED')).toBe(false);
  });

  it('matches timestamps within window', () => {
    const a = '2026-08-07T09:08:37.000Z';
    const b = '2026-08-07T09:08:50.000Z';
    expect(qualityTimestampsWithinWindow(a, b, QUALITY_IMAGE_MATCH_WINDOW_MS)).toBe(true);
    expect(qualityTimestampsWithinWindow(a, '2026-08-07T09:10:00.000Z', 30_000)).toBe(false);
  });
});
