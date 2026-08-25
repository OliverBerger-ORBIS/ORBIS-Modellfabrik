export const SUBSCRIBE_TOPICS: string[] = [
  // Process + CCU
  'ccu/order/active',
  'ccu/order/completed',
  'ccu/order/request',
  'ccu/order/response',
  'ccu/state/stock',
  'ccu/state/layout',
  'ccu/state/config',
  'ccu/state/flows',
  'ccu/pairing/state',

  // Module + FTS
  'module/v1/ff/+/state',
  'module/v1/ff/+/connection',
  'module/v1/ff/+/order',
  'module/v1/ff/NodeRed/+/state',
  'module/v1/ff/NodeRed/+/connection',
  'module/v1/ff/NodeRed/+/order',
  'fts/v1/ff/+/state',
  'fts/v1/ff/+/connection',
  'fts/v1/ff/+/order',

  // TXT sensors
  '/j1/txt/1/i/bme680',
  '/j1/txt/1/i/ldr',
  '/j1/txt/1/i/cam',

  // OSF Arduino sensor topics (existing DR-18 pattern)
  'osf/arduino/+/+/+',

  // Live-only facade (DR-30). Session logs do not contain this topic; Replay NFC
  // comes from module RGB_NFC / FTS loadId / CCU workpieceId.
  'osf/workpiece/intake',

  // Local replay session gate (begin/commit). Ignored in PERSISTENCE_MODE=live.
  'osf/persistence/replay/session',

  // Optional compatibility patterns (future sources)
  'osf/+/sensor/+',
  'osf/+/sensor/+/+',
];
