import type { FtsState } from '@osf/entities';

/** Minimal shape for `app-shopfloor-preview` [ftsPositions] input */
export interface FtsPreviewPositionInput {
  serial: string;
  x: number;
  y: number;
  color: string;
}

function resolveFtsState(
  ftsStates: Record<string, FtsState | undefined>,
  serial: string
): FtsState | undefined {
  const direct = ftsStates[serial];
  if (direct) {
    return direct;
  }
  for (const s of Object.values(ftsStates)) {
    if (s?.serialNumber === serial) {
      return s;
    }
  }
  return undefined;
}

/**
 * Build multi-AGV overlay items from `ftsStates$` snapshot and layout node positions.
 * Mirrors AGV-Tab stationary resolution (no animation path).
 */
export function buildFtsPreviewPositionsFromStates(
  ftsStates: Record<string, FtsState | undefined>,
  agvSerialsOrdered: string[],
  getPositionFromNodeId: (nodeId: string) => { x: number; y: number } | null,
  getAgvColor: (serial: string) => string
): FtsPreviewPositionInput[] {
  const result: FtsPreviewPositionInput[] = [];
  for (const serial of agvSerialsOrdered) {
    const state = resolveFtsState(ftsStates, serial);
    const nodeId = state?.lastNodeId;
    if (!nodeId) {
      continue;
    }
    const fromNode = getPositionFromNodeId(nodeId);
    const pos =
      fromNode ?? (state?.position ? { x: state.position.x, y: state.position.y } : null);
    if (!pos) {
      continue;
    }
    result.push({
      serial,
      x: pos.x,
      y: pos.y,
      color: getAgvColor(serial),
    });
  }
  return result;
}
