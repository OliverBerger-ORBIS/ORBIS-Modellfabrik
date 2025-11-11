import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import test from 'node:test';

import { firstValueFrom } from 'rxjs';
import { take, toArray } from 'rxjs/operators';

import { createOrderFixtureStream, loadOrderFixture } from '../index';

const FIXTURES_ROOT = join(__dirname, '../../../../testing/fixtures/orders');

const fileLoader = (resolvedPath: string) => readFile(resolvedPath, 'utf-8');

test('loadOrderFixture returns trimmed MQTT messages', async () => {
  const messages = await loadOrderFixture('white', {
    baseUrl: FIXTURES_ROOT,
    loader: fileLoader,
  });

  assert.ok(messages.length > 0, 'expected messages to be present');

  const first = messages[0];
  assert.ok(first.topic.length > 0);
  assert.ok(first.timestamp);
  assert.ok(typeof first.payload === 'string');
});

test('createOrderFixtureStream replays fixtures sequentially', async () => {
  const stream = createOrderFixtureStream('blue', {
    baseUrl: FIXTURES_ROOT,
    loader: fileLoader,
  });

  const subset = await firstValueFrom(stream.pipe(take(5), toArray()));
  assert.equal(subset.length, 5);
  assert.ok(subset.every((msg) => msg.topic.length > 0));
});

