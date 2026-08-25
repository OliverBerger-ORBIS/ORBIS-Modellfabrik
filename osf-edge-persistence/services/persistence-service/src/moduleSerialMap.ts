/** Fischertechnik shopfloor serial → station type (APS Modellfabrik). */
export const MODULE_TYPE_BY_SERIAL: Readonly<Record<string, string>> = {
  SVR4H73275: 'DPS',
  SVR3QA0022: 'HBW',
  SVR4H76449: 'DRILL',
  SVR3QA2098: 'MILL',
  SVR4H76530: 'AIQS',
};

const KNOWN_MODULE_TYPES = new Set([
  'DPS',
  'HBW',
  'DRILL',
  'MILL',
  'AIQS',
  'QUALITY',
  'FTS',
]);

/**
 * Prefer an explicit APS moduleType when it is a station label; otherwise map serial.
 * Ignores workpiece colors mistakenly present as payload `type`.
 */
export function resolveModuleType(opts: {
  payloadModuleType?: string;
  topicModuleType?: string;
  moduleSerial?: string;
}): string | undefined {
  const fromPayload = opts.payloadModuleType?.trim().toUpperCase();
  if (fromPayload && KNOWN_MODULE_TYPES.has(fromPayload)) {
    return fromPayload === 'QUALITY' ? 'AIQS' : fromPayload;
  }
  if (opts.topicModuleType) {
    return opts.topicModuleType;
  }
  const serial = opts.moduleSerial?.trim();
  if (serial && MODULE_TYPE_BY_SERIAL[serial]) {
    return MODULE_TYPE_BY_SERIAL[serial];
  }
  return undefined;
}
