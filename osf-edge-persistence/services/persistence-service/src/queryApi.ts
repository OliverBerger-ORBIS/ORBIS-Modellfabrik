import http from 'node:http';
import type { IncomingMessage, ServerResponse } from 'node:http';
import { Logger } from './logger';
import { isValidNfcId, parseTimeRangeFilter } from './queryMap';
import type { HistoryQueryStore } from './queryTypes';

export type QueryRoute =
  | { kind: 'health' }
  | { kind: 'workpieces' }
  | { kind: 'timeline'; nfc: string }
  | { kind: 'bad_nfc' }
  | { kind: 'not_found' };

export function matchQueryRoute(method: string, pathname: string): QueryRoute {
  const normalizedMethod = method.toUpperCase();
  const path = pathname.replace(/\/+$/, '') || '/';

  if (normalizedMethod === 'GET' && (path === '/health' || path === '/v1/health')) {
    return { kind: 'health' };
  }
  if (normalizedMethod === 'GET' && path === '/v1/workpieces') {
    return { kind: 'workpieces' };
  }
  const timeline = path.match(/^\/v1\/workpieces\/([^/]+)\/timeline$/);
  if (normalizedMethod === 'GET' && timeline) {
    const nfc = decodeURIComponent(timeline[1] ?? '');
    if (!isValidNfcId(nfc)) {
      return { kind: 'bad_nfc' };
    }
    return { kind: 'timeline', nfc };
  }
  return { kind: 'not_found' };
}

function applyCors(res: ServerResponse, origin: string): void {
  res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function sendJson(res: ServerResponse, status: number, body: unknown, corsOrigin: string): void {
  applyCors(res, corsOrigin);
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.end(JSON.stringify(body));
}

export async function handleQueryRequest(
  req: IncomingMessage,
  res: ServerResponse,
  store: HistoryQueryStore,
  corsOrigin: string
): Promise<void> {
  const method = req.method ?? 'GET';
  if (method.toUpperCase() === 'OPTIONS') {
    applyCors(res, corsOrigin);
    res.statusCode = 204;
    res.end();
    return;
  }

  const url = new URL(req.url ?? '/', 'http://127.0.0.1');
  const route = matchQueryRoute(method, url.pathname);

  try {
    if (route.kind === 'health') {
      sendJson(res, 200, { ok: true, service: 'osf-edge-query' }, corsOrigin);
      return;
    }
    if (route.kind === 'not_found') {
      sendJson(res, 404, { error: 'Not found' }, corsOrigin);
      return;
    }
    if (route.kind === 'bad_nfc') {
      sendJson(res, 400, { error: 'Invalid NFC id' }, corsOrigin);
      return;
    }

    const filter = parseTimeRangeFilter(url.searchParams);
    if (route.kind === 'workpieces') {
      const items = await store.listWorkpieces(filter);
      sendJson(res, 200, { items }, corsOrigin);
      return;
    }
    const events = await store.listTimeline(route.nfc, filter);
    sendJson(res, 200, { nfc: route.nfc, events }, corsOrigin);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (message.startsWith('Invalid timestamp:')) {
      sendJson(res, 400, { error: message }, corsOrigin);
      return;
    }
    sendJson(res, 500, { error: 'Query failed' }, corsOrigin);
  }
}

export function startQueryApi(opts: {
  port: number;
  corsOrigin: string;
  logger: Logger;
  store: HistoryQueryStore;
}): http.Server {
  const server = http.createServer((req, res) => {
    void handleQueryRequest(req, res, opts.store, opts.corsOrigin).catch((error) => {
      opts.logger.error('Query API request failed', String(error));
      if (!res.headersSent) {
        sendJson(res, 500, { error: 'Query failed' }, opts.corsOrigin);
      }
    });
  });
  server.listen(opts.port, '0.0.0.0', () => {
    opts.logger.info('Query API listening', { port: opts.port, corsOrigin: opts.corsOrigin });
  });
  return server;
}
