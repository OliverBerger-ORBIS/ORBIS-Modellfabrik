import { describe, expect, it } from 'vitest';
import { SUBSCRIBE_TOPICS } from '../topics';

describe('SUBSCRIBE_TOPICS', () => {
  it('includes CCU request/response and module/FTS order command topics', () => {
    expect(SUBSCRIBE_TOPICS).toContain('ccu/order/request');
    expect(SUBSCRIBE_TOPICS).toContain('ccu/order/response');
    expect(SUBSCRIBE_TOPICS).toContain('module/v1/ff/+/order');
    expect(SUBSCRIBE_TOPICS).toContain('module/v1/ff/NodeRed/+/order');
    expect(SUBSCRIBE_TOPICS).toContain('fts/v1/ff/+/order');
  });
});
