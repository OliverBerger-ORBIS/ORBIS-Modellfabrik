import { countModuleMessagesForSerial } from './count-module-messages';

describe('countModuleMessagesForSerial', () => {
  const topics = [
    'module/v1/ff/SVR_HBW/state',
    'module/v1/ff/NodeRed/SVR_HBW/connection',
    'module/v1/ff/OTHER/state',
    'fts/v1/ff/5iO4/state',
    'fts/5iO4/legacy',
  ];

  it('counts module and NodeRed topic histories for a serial', () => {
    const lengths: Record<string, number> = {
      'module/v1/ff/SVR_HBW/state': 2,
      'module/v1/ff/NodeRed/SVR_HBW/connection': 1,
    };
    expect(
      countModuleMessagesForSerial('SVR_HBW', topics, (topic) => lengths[topic] ?? 0)
    ).toBe(3);
  });

  it('counts FTS v1 and legacy topic patterns', () => {
    const lengths: Record<string, number> = {
      'fts/v1/ff/5iO4/state': 4,
      'fts/5iO4/legacy': 1,
    };
    expect(countModuleMessagesForSerial('5iO4', topics, (topic) => lengths[topic] ?? 0)).toBe(5);
  });

  it('returns 0 when no topics match', () => {
    expect(countModuleMessagesForSerial('UNKNOWN', topics, () => 99)).toBe(0);
  });
});
