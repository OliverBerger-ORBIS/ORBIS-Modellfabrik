/**
 * Shared rules for when FTS supervisor commands (dock to initial, charge on/off) should be offered.
 * Shopfloor: only push actions when {@link ftsCanOffer*} is true (buttons omitted).
 * AGV tab: keep buttons visible, use the same predicates for disabled + tooltip.
 */

export interface FtsCommandAvailabilityInput {
  /** MQTT/pairing connected and telemetry usable (Shopfloor: transport.connected; AGV: FTS state present). */
  connected: boolean;
  lastNodeId?: string | null;
  lastModuleSerialNumber?: string | null;
  charging?: boolean;
  driving?: boolean;
  /** When true, do not offer dock or start-charge (module load handshake). */
  waitingForLoadHandling?: boolean;
}

/** True when reported node or module is still unknown — initial dock may be required. */
export function ftsNeedsInitialDockPosition(
  input: Pick<FtsCommandAvailabilityInput, 'lastNodeId' | 'lastModuleSerialNumber'>,
): boolean {
  const nodeUnknown = !input.lastNodeId || input.lastNodeId === 'UNKNOWN';
  const moduleUnknown = !input.lastModuleSerialNumber || input.lastModuleSerialNumber === 'UNKNOWN';
  return nodeUnknown || moduleUnknown;
}

export function ftsCanOfferInitialDockCommand(input: FtsCommandAvailabilityInput): boolean {
  if (!input.connected) {
    return false;
  }
  if (!ftsNeedsInitialDockPosition(input)) {
    return false;
  }
  if (input.driving === true) {
    return false;
  }
  if (input.waitingForLoadHandling === true) {
    return false;
  }
  return true;
}

export function ftsCanOfferStartChargeCommand(input: FtsCommandAvailabilityInput): boolean {
  if (!input.connected) {
    return false;
  }
  if (input.charging === true) {
    return false;
  }
  if (input.driving === true) {
    return false;
  }
  if (input.waitingForLoadHandling === true) {
    return false;
  }
  return true;
}

export function ftsCanOfferStopChargeCommand(input: FtsCommandAvailabilityInput): boolean {
  if (!input.connected) {
    return false;
  }
  return input.charging === true;
}
