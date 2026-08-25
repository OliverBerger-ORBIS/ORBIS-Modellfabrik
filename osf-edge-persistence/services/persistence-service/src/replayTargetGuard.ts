import { ServiceConfig } from './config';

const DEFAULT_ALLOWED_REPLAY_DB_HOSTS = [
  'localhost',
  '127.0.0.1',
  '::1',
  'host.docker.internal',
  'mssql',
  'osf-edge-mssql',
] as const;

/**
 * PERSISTENCE_MODE=replay must not target the live VE DB (.201).
 * Allowlist of local/dev DB hosts; extend via REPLAY_ALLOW_DB_HOSTS (comma-separated).
 */
export function assertReplayTargetAllowed(config: ServiceConfig): void {
  if (config.runtime.mode !== 'replay') {
    return;
  }

  const host = config.mssql.host.trim().toLowerCase();

  const fromEnv = (process.env.REPLAY_ALLOW_DB_HOSTS ?? '')
    .split(',')
    .map((h) => h.trim().toLowerCase())
    .filter(Boolean);

  const allowed = new Set<string>([...DEFAULT_ALLOWED_REPLAY_DB_HOSTS, ...fromEnv]);

  if (!allowed.has(host)) {
    throw new Error(
      `Refusing PERSISTENCE_MODE=replay against DB host "${host}". ` +
        `Replay ingest is for the local scratch DB only (not .201 / live). ` +
        `Allowed: ${[...allowed].sort().join(', ')}. ` +
        `Override with REPLAY_ALLOW_DB_HOSTS if needed.`
    );
  }
}

export function defaultAllowedReplayDbHosts(): readonly string[] {
  return DEFAULT_ALLOWED_REPLAY_DB_HOSTS;
}
