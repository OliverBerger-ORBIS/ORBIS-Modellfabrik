/**
 * Canonical ISO-8601 UTC timestamps with millisecond precision and `Z` suffix.
 * Same string shape as `Date.prototype.toISOString()` and Arduino `OSF_MultiSensor_R4WiFi` v1.1.6+ payload `timestamp`.
 */
export function utcIsoTimestampMs(date: Date = new Date()): string {
  return date.toISOString();
}
