/**
 * AIQS quality_check MQTT payload helpers (Shopfloor + Track&Trace).
 * Topic: `/j1/txt/1/i/quality_check`
 */

export const QUALITY_CHECK_TOPIC = '/j1/txt/1/i/quality_check';

/** Chrome may reject very long data: URLs for img src; blob URLs are safe. */
export const MAX_DATA_URL_LENGTH_FOR_IMG = 1_800_000;

/** Match window between module CHECK_QUALITY and quality_check MQTT (ms). */
export const QUALITY_IMAGE_MATCH_WINDOW_MS = 30_000;

export interface QualityCheckPayload {
  num?: number;
  result?: 'PASSED' | 'FAILED' | string;
  ts?: string;
  data?: string;
  classification?: string;
  classificationDesc?: string;
}

export interface QualityCheckAttachment {
  dataUrl: string;
  ts?: string;
  result?: string;
  classification?: string;
  classificationDesc?: string;
}

export function toDisplayImageUrl(dataUrl: string): { url: string; revoke: boolean } {
  if (dataUrl.length <= MAX_DATA_URL_LENGTH_FOR_IMG) {
    return { url: dataUrl, revoke: false };
  }
  const m = /^data:([^;]+);base64,([\s\S]+)$/.exec(dataUrl);
  if (!m) {
    return { url: dataUrl, revoke: false };
  }
  try {
    const binary = atob(m[2]);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: m[1] });
    return { url: URL.createObjectURL(blob), revoke: true };
  } catch {
    return { url: dataUrl, revoke: false };
  }
}

/** Normalize module/MQTT quality results for matching (OK ≈ PASSED). */
export function normalizeQualityResult(result: unknown): string | null {
  if (typeof result !== 'string' || !result.trim()) {
    return null;
  }
  const upper = result.trim().toUpperCase();
  if (upper === 'OK' || upper === 'PASS' || upper === 'PASSED') {
    return 'PASSED';
  }
  if (upper === 'FAIL' || upper === 'FAILED' || upper === 'NOK' || upper === 'ERROR') {
    return 'FAILED';
  }
  return upper;
}

export function parseQualityCheckPayload(raw: unknown): QualityCheckAttachment | null {
  let payload: QualityCheckPayload;
  if (typeof raw === 'string') {
    try {
      payload = JSON.parse(raw) as QualityCheckPayload;
    } catch {
      return null;
    }
  } else if (raw && typeof raw === 'object') {
    payload = raw as QualityCheckPayload;
  } else {
    return null;
  }

  const imageData = payload.data;
  if (!imageData || typeof imageData !== 'string' || !imageData.startsWith('data:image/')) {
    return null;
  }

  return {
    dataUrl: imageData,
    ts: typeof payload.ts === 'string' ? payload.ts : undefined,
    result: typeof payload.result === 'string' ? payload.result : undefined,
    classification: typeof payload.classification === 'string' ? payload.classification : undefined,
    classificationDesc:
      typeof payload.classificationDesc === 'string' ? payload.classificationDesc : undefined,
  };
}

export function qualityResultsMatch(eventResult: unknown, qualityResult: unknown): boolean {
  const a = normalizeQualityResult(eventResult);
  const b = normalizeQualityResult(qualityResult);
  if (!a || !b) {
    // If either side lacks result, still allow time-based match
    return true;
  }
  return a === b;
}

export function qualityTimestampsWithinWindow(
  eventTimestamp: string | undefined,
  qualityTs: string | undefined,
  windowMs: number = QUALITY_IMAGE_MATCH_WINDOW_MS
): boolean {
  if (!eventTimestamp || !qualityTs) {
    return true;
  }
  const eventMs = Date.parse(eventTimestamp);
  const qualityMs = Date.parse(qualityTs);
  if (!Number.isFinite(eventMs) || !Number.isFinite(qualityMs)) {
    return true;
  }
  return Math.abs(eventMs - qualityMs) <= windowMs;
}
