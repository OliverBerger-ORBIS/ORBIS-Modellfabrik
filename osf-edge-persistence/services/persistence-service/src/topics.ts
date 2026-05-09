export const SUBSCRIBE_TOPICS: string[] = [
  // Process + CCU
  'ccu/order/active',
  'ccu/order/completed',
  'ccu/state/stock',
  'ccu/state/layout',
  'ccu/state/config',
  'ccu/state/flows',
  'ccu/pairing/state',

  // Module + FTS
  'module/v1/ff/+/state',
  'module/v1/ff/+/connection',
  'module/v1/ff/NodeRed/+/state',
  'module/v1/ff/NodeRed/+/connection',
  'fts/v1/ff/+/state',
  'fts/v1/ff/+/connection',

  // TXT sensors
  '/j1/txt/1/i/bme680',
  '/j1/txt/1/i/ldr',
  '/j1/txt/1/i/cam',

  // OSF Arduino sensor topics (existing DR-18 pattern)
  'osf/arduino/+/+/+',

  // Optional compatibility patterns (future sources)
  'osf/+/sensor/+',
  'osf/+/sensor/+/+',
];
