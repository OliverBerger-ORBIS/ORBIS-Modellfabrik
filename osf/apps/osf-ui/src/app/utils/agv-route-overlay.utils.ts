export interface AgvMapRouteSegment {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  stroke?: string;
  strokeDasharray?: string;
}

export interface AgvRouteOverlayLayers {
  planned: AgvMapRouteSegment[];
  traveled: AgvMapRouteSegment[];
}

export interface AgvOptionLike {
  serial: string;
  label: string;
}

export function sameStyledAgvRouteSegmentList(a: AgvMapRouteSegment[], b: AgvMapRouteSegment[]): boolean {
  if (a.length !== b.length) {
    return false;
  }
  return a.every((item, i) => {
    const o = b[i];
    return (
      o &&
      item.stroke === o.stroke &&
      item.strokeDasharray === o.strokeDasharray &&
      Math.abs(item.x1 - o.x1) < 0.5 &&
      Math.abs(item.y1 - o.y1) < 0.5 &&
      Math.abs(item.x2 - o.x2) < 0.5 &&
      Math.abs(item.y2 - o.y2) < 0.5
    );
  });
}

export function sameAgvRouteOverlayLayers(a: AgvRouteOverlayLayers, b: AgvRouteOverlayLayers): boolean {
  return sameStyledAgvRouteSegmentList(a.planned, b.planned) && sameStyledAgvRouteSegmentList(a.traveled, b.traveled);
}

export function flattenFtsOrderGraphPath(
  order: unknown,
  findRoutePath: (start: string, target: string) => string[] | null,
  canonicalNodeId: (id: string | undefined) => string
): string[] | null {
  if (!order || typeof order !== 'object') {
    return null;
  }
  const nodes = (order as { nodes?: Array<{ id?: string }> }).nodes;
  if (!Array.isArray(nodes) || nodes.length < 2) {
    return null;
  }
  const ids = nodes.map((n) => n?.id).filter((id): id is string => Boolean(id));
  if (ids.length < 2) {
    return null;
  }
  const flat: string[] = [];
  for (let i = 0; i < ids.length - 1; i += 1) {
    const path = findRoutePath(ids[i], ids[i + 1]);
    if (!path || path.length < 2) {
      continue;
    }
    if (flat.length === 0) {
      flat.push(...path);
    } else {
      const join = canonicalNodeId(path[0]);
      const tail = canonicalNodeId(flat[flat.length - 1]);
      if (join === tail) {
        flat.push(...path.slice(1));
      } else {
        flat.push(...path);
      }
    }
  }
  return flat.length >= 2 ? flat : null;
}

/** AGV serials seen on FTS state topics but not in layout configuration. */
export function detectUnknownAgvSerialsFromTopics(
  topics: readonly string[],
  configuredSerials: ReadonlySet<string>
): AgvOptionLike[] {
  const serials = new Set<string>();
  for (const topic of topics) {
    const m = /^fts\/v1\/ff\/([^/]+)\/state$/.exec(topic);
    if (m?.[1]) {
      serials.add(m[1]);
    }
  }
  return [...serials]
    .filter((s) => !configuredSerials.has(s))
    .sort()
    .map((serial) => ({ serial, label: `AGV-? (${serial})` }));
}
