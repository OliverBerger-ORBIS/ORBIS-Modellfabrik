export const SIMPLE_ISO_DATE_REGEX = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d*)?)?Z$/;

/**
 * Checks if a json value should be parsed as a Date.
 *
 * Valid dates are a subset of ISO 8601 dates of the format
 * "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'" (seconds and millseconds are optional)
 *
 * @param {string} _ is unused, but required for JSON reviver function signatures
 * @param {T} value the json value to convert if required
 * @returns the parsed date as a Date object or the unchanged value
 */
export function jsonIsoDateReviver<T>(_: string, value: T): T | Date {
  if (typeof value === "string" && SIMPLE_ISO_DATE_REGEX.test(value)) {
    return new Date(value);
  }
  return value;
}
