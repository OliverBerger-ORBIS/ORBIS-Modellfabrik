import { matchTopics } from './helpers';

describe('Topic matching', () => {
  it('should match the single level wildcard topics', () => {
    const subscribeSingleLevelWildCard = 'module/v1/ff/+/state';
    const topicSingleLevelWildCard = 'module/v1/ff/mockedSerial/state';
    expect(matchTopics(subscribeSingleLevelWildCard, topicSingleLevelWildCard)).toBe(true);
  });

  it('should match the single level wildcard topics with multiple subscribed topics', () => {
    const subscribeSingleLevelWildCard = 'level1/level2/+/level4';
    const subscribeSingleLevelWildCard2 = 'noMatch/level2/noMatch/level4';
    const topicSingleLevelWildCard = 'level1/level2/level3/level4';
    expect(matchTopics([subscribeSingleLevelWildCard, subscribeSingleLevelWildCard2], topicSingleLevelWildCard)).toBe(true);
  });

  it('should match the multi level wildcard topics', () => {
    const subscribeSingleLevelWildCard = 'level1/#';
    const topicSingleLevelWildCard = 'level1/level2/level3/level4';
    expect(matchTopics(subscribeSingleLevelWildCard, topicSingleLevelWildCard)).toBe(true);
  });

  it('should match the multi level wildcard topics with multiple subscribed topics', () => {
    const subscribeSingleLevelWildCard = 'level1/#';
    const subscribeSingleLevelWildCard2 = 'noMatch/level2/noMatch/level4';
    const topicSingleLevelWildCard = 'level1/level2/level3/level4';
    expect(matchTopics([subscribeSingleLevelWildCard, subscribeSingleLevelWildCard2], topicSingleLevelWildCard)).toBe(true);
  });

  it('should not match single level wildcard with single subscription', () => {
    const subscribeSingleLevelWildCard = 'module/v1/ff/+/state';
    const topicSingleLevelWildCard = 'module/v1/ff/mockedSerial/order';
    expect(matchTopics(subscribeSingleLevelWildCard, topicSingleLevelWildCard)).toBe(false);
  });

  it('should not match the single level wildcard topics with multiple subscribed topics', () => {
    const subscribeSingleLevelWildCard = 'level1/level2/+/level4';
    const subscribeSingleLevelWildCard2 = 'noMatch/level2/noMatch/level4';
    const topicSingleLevelWildCard = 'second/level2/level3/level4';
    expect(matchTopics([subscribeSingleLevelWildCard, subscribeSingleLevelWildCard2], topicSingleLevelWildCard)).toBe(false);
  });

  it('should not match the multi level wildcard topics', () => {
    const subscribeSingleLevelWildCard = 'level1/#';
    const topicSingleLevelWildCard = 'noMatch/level2/level3/level4';
    expect(matchTopics(subscribeSingleLevelWildCard, topicSingleLevelWildCard)).toBe(false);
  });

  it('should not match the multi level wildcard topics with multiple subscribed topics', () => {
    const subscribeSingleLevelWildCard = 'level1/#';
    const subscribeSingleLevelWildCard2 = 'noMatch/level2/noMatch/level4';
    const topicSingleLevelWildCard = 'second/level2/level3/level4';
    expect(matchTopics([subscribeSingleLevelWildCard, subscribeSingleLevelWildCard2], topicSingleLevelWildCard)).toBe(false);
  });
});
