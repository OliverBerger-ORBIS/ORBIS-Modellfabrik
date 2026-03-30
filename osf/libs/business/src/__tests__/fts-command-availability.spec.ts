import assert from 'node:assert/strict';
import test from 'node:test';

import {
  ftsCanOfferInitialDockCommand,
  ftsCanOfferStartChargeCommand,
  ftsCanOfferStopChargeCommand,
  ftsNeedsInitialDockPosition,
} from '@osf/entities';

test('needs initial dock when node or module unknown', () => {
  assert.equal(ftsNeedsInitialDockPosition({ lastNodeId: undefined, lastModuleSerialNumber: undefined }), true);
  assert.equal(
    ftsNeedsInitialDockPosition({ lastNodeId: 'UNKNOWN', lastModuleSerialNumber: 'SVR3QA0022' }),
    true,
  );
  assert.equal(
    ftsNeedsInitialDockPosition({ lastNodeId: 'SVR4H73275', lastModuleSerialNumber: 'UNKNOWN' }),
    true,
  );
  assert.equal(
    ftsNeedsInitialDockPosition({ lastNodeId: 'SVR4H73275', lastModuleSerialNumber: 'SVR3QA0022' }),
    false,
  );
});

test('offers dock when connected and position unknown and not driving or waiting', () => {
  assert.equal(
    ftsCanOfferInitialDockCommand({
      connected: true,
      lastNodeId: 'UNKNOWN',
      charging: false,
    }),
    true,
  );
  assert.equal(
    ftsCanOfferInitialDockCommand({
      connected: true,
      lastNodeId: 'UNKNOWN',
      driving: true,
    }),
    false,
  );
  assert.equal(
    ftsCanOfferInitialDockCommand({
      connected: true,
      lastNodeId: 'UNKNOWN',
      waitingForLoadHandling: true,
    }),
    false,
  );
});

test('offers start charge when connected, not charging, not driving, not waiting', () => {
  assert.equal(
    ftsCanOfferStartChargeCommand({
      connected: true,
      charging: false,
    }),
    true,
  );
  assert.equal(
    ftsCanOfferStartChargeCommand({
      connected: true,
      charging: false,
      driving: true,
    }),
    false,
  );
  assert.equal(
    ftsCanOfferStartChargeCommand({
      connected: true,
      charging: true,
    }),
    false,
  );
});

test('offers stop charge only when charging', () => {
  assert.equal(
    ftsCanOfferStopChargeCommand({
      connected: true,
      charging: true,
    }),
    true,
  );
  assert.equal(
    ftsCanOfferStopChargeCommand({
      connected: true,
      charging: false,
    }),
    false,
  );
});
