/** Canonical FTS serials when shopfloor layout is not loaded yet (keep in sync with shopfloor_layout.json). */
export const FTS_SERIALS_FALLBACK = ['5iO4', 'xkI4'] as const;

const FTS_TOPIC_SERIAL_RE = /^fts\/v1\/ff\/([^/]+)\/(?:state|order)$/;

export interface FtsSerialResolverInputs {
  getAgvOptions: () => ReadonlyArray<{ serial: string }>;
  getTopics?: () => readonly string[];
}

/**
 * FTS serials for subscriptions, replay, and UI fallbacks: layout fts[], canonical fallback,
 * and any fts/v1/ff/<serial>/state|order topics already in MessageMonitor.
 */
export function getEffectiveFtsSerials(inputs: FtsSerialResolverInputs): string[] {
  const serials = new Set<string>(FTS_SERIALS_FALLBACK);
  for (const opt of inputs.getAgvOptions()) {
    if (opt.serial) {
      serials.add(opt.serial);
    }
  }
  if (inputs.getTopics) {
    for (const topic of inputs.getTopics()) {
      const match = topic.match(FTS_TOPIC_SERIAL_RE);
      if (match?.[1]) {
        serials.add(match[1]);
      }
    }
  }
  return [...serials];
}

/** AGV dropdown options when layout is not loaded (AGV-1, AGV-2). */
export function getFtsFallbackAgvOptions(): Array<{ serial: string; label: string }> {
  return FTS_SERIALS_FALLBACK.map((serial, index) => ({
    serial,
    label: `AGV-${index + 1}`,
  }));
}
