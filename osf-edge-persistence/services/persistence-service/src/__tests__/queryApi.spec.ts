import { once } from 'node:events';
import type { AddressInfo } from 'node:net';
import { afterEach, describe, expect, it } from 'vitest';
import { Logger } from '../logger';
import { matchQueryRoute, startQueryApi } from '../queryApi';
import type { HistoryQueryStore, TimelineEventDto, WorkpieceSummaryDto } from '../queryTypes';

describe('matchQueryRoute', () => {
  it('matches health and collection paths', () => {
    expect(matchQueryRoute('GET', '/health')).toEqual({ kind: 'health' });
    expect(matchQueryRoute('GET', '/v1/health')).toEqual({ kind: 'health' });
    expect(matchQueryRoute('GET', '/v1/workpieces')).toEqual({ kind: 'workpieces' });
    expect(matchQueryRoute('GET', '/v1/workpieces/92e0ad91595f63/timeline')).toEqual({
      kind: 'timeline',
      nfc: '92e0ad91595f63',
    });
  });

  it('rejects unsafe NFC path segments', () => {
    expect(matchQueryRoute('GET', '/v1/workpieces/../x/timeline')).toEqual({ kind: 'not_found' });
    expect(matchQueryRoute('GET', '/v1/workpieces/ab/timeline')).toEqual({ kind: 'bad_nfc' });
  });
});

describe('startQueryApi HTTP', () => {
  let close: (() => Promise<void>) | undefined;

  afterEach(async () => {
    if (close) {
      await close();
      close = undefined;
    }
  });

  async function listen(store: HistoryQueryStore): Promise<number> {
    const server = startQueryApi({
      port: 0,
      corsOrigin: '*',
      logger: new Logger('error'),
      store,
    });
    await once(server, 'listening');
    const addr = server.address() as AddressInfo;
    close = () =>
      new Promise((resolve, reject) => {
        server.close((err) => (err ? reject(err) : resolve()));
      });
    return addr.port;
  }

  it('serves health, workpieces, and timeline', async () => {
    const items: WorkpieceSummaryDto[] = [
      {
        nfc: '92e0ad91595f63',
        color: 'WHITE',
        currentState: 'FINISHED',
        lastLocation: 'DPS',
        firstSeenAt: '2026-09-03T09:00:00.000Z',
        lastSeenAt: '2026-09-03T10:00:00.000Z',
      },
    ];
    const events: TimelineEventDto[] = [
      {
        ts: '2026-09-03T09:15:00.000Z',
        nfc: '92e0ad91595f63',
        color: 'WHITE',
        station: 'HBW',
        action: 'PICK',
        actionState: 'FINISHED',
        orderId: 'ord-1',
        orderType: 'STORAGE',
        moduleSerial: 'SVR3QA0022',
        eventSource: 'module',
        eventType: 'PICK',
      },
    ];
    const store: HistoryQueryStore = {
      listWorkpieces: async () => items,
      listTimeline: async (nfc) => (nfc === '92e0ad91595f63' ? events : []),
    };
    const port = await listen(store);

    const health = await fetch(`http://127.0.0.1:${port}/v1/health`);
    expect(health.status).toBe(200);
    await expect(health.json()).resolves.toMatchObject({ ok: true });

    const list = await fetch(`http://127.0.0.1:${port}/v1/workpieces`);
    expect(list.status).toBe(200);
    await expect(list.json()).resolves.toEqual({ items });

    const timeline = await fetch(
      `http://127.0.0.1:${port}/v1/workpieces/92e0ad91595f63/timeline`
    );
    expect(timeline.status).toBe(200);
    await expect(timeline.json()).resolves.toEqual({ nfc: '92e0ad91595f63', events });
  });

  it('returns 400 for invalid NFC', async () => {
    const store: HistoryQueryStore = {
      listWorkpieces: async () => [],
      listTimeline: async () => [],
    };
    const port = await listen(store);
    const res = await fetch(`http://127.0.0.1:${port}/v1/workpieces/ab/timeline`);
    expect(res.status).toBe(400);
  });
});
