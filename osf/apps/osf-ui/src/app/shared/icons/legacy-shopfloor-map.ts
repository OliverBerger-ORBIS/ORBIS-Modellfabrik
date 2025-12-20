// Legacy mapping entfernt – alle Aufrufer nutzen die neuen Pfade.
const LEGACY_MAP: Record<string, string> = {};
const DEFAULT_ICON = 'assets/svg/shopfloor/shared/question.svg';

export function resolveLegacyShopfloorPath(path: string | undefined): string {
  if (!path) return DEFAULT_ICON;
  const clean = path.startsWith('/') ? path.slice(1) : path;
  return LEGACY_MAP[clean] ?? clean;
}

