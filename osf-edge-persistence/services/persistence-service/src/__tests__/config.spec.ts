import { afterEach, describe, expect, it } from 'vitest';
import { loadConfig } from '../config';

function withEnv(
  updates: Record<string, string | undefined>,
  run: () => void
): void {
  const previous = new Map<string, string | undefined>();
  for (const [key, value] of Object.entries(updates)) {
    previous.set(key, process.env[key]);
    if (value === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }
  try {
    run();
  } finally {
    for (const [key, value] of previous.entries()) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
  }
}

describe('loadConfig runtime mode', () => {
  afterEach(() => {
    delete process.env.PERSISTENCE_MODE;
  });

  it('defaults to live mode when env is not set', () => {
    withEnv({ PERSISTENCE_MODE: undefined }, () => {
      const cfg = loadConfig();
      expect(cfg.runtime.mode).toBe('live');
    });
  });

  it('parses replay mode explicitly', () => {
    withEnv({ PERSISTENCE_MODE: 'replay' }, () => {
      const cfg = loadConfig();
      expect(cfg.runtime.mode).toBe('replay');
    });
  });

  it('falls back to live mode for unknown values', () => {
    withEnv({ PERSISTENCE_MODE: 'experimental' }, () => {
      const cfg = loadConfig();
      expect(cfg.runtime.mode).toBe('live');
    });
  });
});
