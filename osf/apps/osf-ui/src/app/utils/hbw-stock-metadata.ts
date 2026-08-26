/** Minimal HBW module state shape for stock slot extraction. */
export interface HbwStockPayload {
  actionState?: {
    metadata?: {
      row?: string | number;
      column?: string | number;
      slot?: string;
      workpieceId?: string;
      workpiece?: { workpieceId?: string };
    };
  };
  loads?: Array<{ loadId?: string; loadPosition?: string }>;
}

export function extractHbwStockRow(payload: HbwStockPayload): string | number | undefined {
  if (payload.actionState?.metadata?.row !== undefined) {
    return payload.actionState.metadata.row;
  }

  const workpieceId =
    payload.actionState?.metadata?.workpieceId ?? payload.actionState?.metadata?.workpiece?.workpieceId;
  if (workpieceId && payload.loads && Array.isArray(payload.loads)) {
    const matchingLoad = payload.loads.find((l) => l.loadId === workpieceId && l.loadPosition);
    if (matchingLoad?.loadPosition) {
      return matchingLoad.loadPosition.charAt(0);
    }
  }

  if (payload.actionState?.metadata?.slot) {
    const slot = String(payload.actionState.metadata.slot);
    if (slot.length > 0) {
      return slot.charAt(0);
    }
  }

  return undefined;
}

export function extractHbwStockColumn(payload: HbwStockPayload): string | number | undefined {
  if (payload.actionState?.metadata?.column !== undefined) {
    return payload.actionState.metadata.column;
  }

  const workpieceId =
    payload.actionState?.metadata?.workpieceId ?? payload.actionState?.metadata?.workpiece?.workpieceId;
  if (workpieceId && payload.loads && Array.isArray(payload.loads)) {
    const matchingLoad = payload.loads.find((l) => l.loadId === workpieceId && l.loadPosition);
    if (matchingLoad?.loadPosition) {
      const pos = matchingLoad.loadPosition;
      if (pos.length > 1) {
        return pos.substring(1);
      }
    }
  }

  if (payload.actionState?.metadata?.slot) {
    const slot = String(payload.actionState.metadata.slot);
    if (slot.length > 1) {
      return slot.substring(1);
    }
  }

  return undefined;
}
