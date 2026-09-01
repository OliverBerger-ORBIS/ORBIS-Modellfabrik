import {
  FTS_SERIALS_FALLBACK,
  getEffectiveFtsSerials,
  getFtsFallbackAgvOptions,
} from './fts-serial-resolver';

describe('fts-serial-resolver', () => {
  it('should expose canonical dual-AGV fallback serials', () => {
    expect(FTS_SERIALS_FALLBACK).toEqual(['5iO4', 'xkI4']);
  });

  it('should return fallback serials when layout is empty and no topics', () => {
    expect(getEffectiveFtsSerials({ getAgvOptions: () => [] })).toEqual(['5iO4', 'xkI4']);
  });

  it('should merge layout serials with fallback', () => {
    const serials = getEffectiveFtsSerials({
      getAgvOptions: () => [{ serial: '5iO4' }, { serial: 'xkI4' }],
    });
    expect(serials).toEqual(expect.arrayContaining(['5iO4', 'xkI4']));
    expect(serials).toHaveLength(2);
  });

  it('should discover serials from FTS state and order topics', () => {
    const serials = getEffectiveFtsSerials({
      getAgvOptions: () => [],
      getTopics: () => [
        'fts/v1/ff/xkI4/state',
        'fts/v1/ff/5iO4/order',
        'module/v1/ff/SVR3QA0022/state',
      ],
    });
    expect(serials).toEqual(expect.arrayContaining(['5iO4', 'xkI4']));
  });

  it('should include extra serial from topics not in layout', () => {
    const serials = getEffectiveFtsSerials({
      getAgvOptions: () => [{ serial: '5iO4' }, { serial: 'xkI4' }],
      getTopics: () => ['fts/v1/ff/newFt/state'],
    });
    expect(serials).toContain('newFt');
  });

  it('should provide labeled fallback AGV options', () => {
    expect(getFtsFallbackAgvOptions()).toEqual([
      { serial: '5iO4', label: 'AGV-1' },
      { serial: 'xkI4', label: 'AGV-2' },
    ]);
  });
});
