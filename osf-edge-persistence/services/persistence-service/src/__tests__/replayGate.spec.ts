import { describe, expect, it } from 'vitest';
import { loadConfig } from '../config';
import { parseReplaySessionControl, ReplaySessionGate } from '../replaySessionGate';
import { assertReplayTargetAllowed, defaultAllowedReplayDbHosts } from '../replayTargetGuard';

function withEnv(updates: Record<string, string | undefined>, run: () => void): void {
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

describe('assertReplayTargetAllowed', () => {
  it('allows live mode against any host including .201', () => {
    withEnv(
      {
        PERSISTENCE_MODE: 'live',
        MSSQL_HOST: '192.168.0.201',
      },
      () => {
        expect(() => assertReplayTargetAllowed(loadConfig())).not.toThrow();
      }
    );
  });

  it('allows replay against local allowlisted hosts', () => {
    for (const host of defaultAllowedReplayDbHosts()) {
      withEnv(
        {
          PERSISTENCE_MODE: 'replay',
          MSSQL_HOST: host,
        },
        () => {
          expect(() => assertReplayTargetAllowed(loadConfig())).not.toThrow();
        }
      );
    }
  });

  it('refuses replay against .201', () => {
    withEnv(
      {
        PERSISTENCE_MODE: 'replay',
        MSSQL_HOST: '192.168.0.201',
      },
      () => {
        expect(() => assertReplayTargetAllowed(loadConfig())).toThrow(/192\.168\.0\.201/);
      }
    );
  });

  it('allows extra hosts via REPLAY_ALLOW_DB_HOSTS', () => {
    withEnv(
      {
        PERSISTENCE_MODE: 'replay',
        MSSQL_HOST: 'custom-scratch',
        REPLAY_ALLOW_DB_HOSTS: 'custom-scratch',
      },
      () => {
        expect(() => assertReplayTargetAllowed(loadConfig())).not.toThrow();
      }
    );
  });
});

describe('parseReplaySessionControl', () => {
  it('parses begin and commit', () => {
    expect(parseReplaySessionControl('{"action":"begin","sessionId":"a.log"}')).toEqual({
      action: 'begin',
      sessionId: 'a.log',
    });
    expect(parseReplaySessionControl('{"action":"commit","session_id":"b.log"}')).toEqual({
      action: 'commit',
      sessionId: 'b.log',
    });
  });

  it('rejects invalid payloads', () => {
    expect(parseReplaySessionControl('{}')).toBeUndefined();
    expect(parseReplaySessionControl('{"action":"begin"}')).toBeUndefined();
    expect(parseReplaySessionControl('not-json')).toBeUndefined();
  });
});

describe('ReplaySessionGate', () => {
  it('skips shopfloor until begin in replay mode', async () => {
    const store = {
      hasReplaySession: async () => false,
      recordReplaySession: async () => undefined,
    };
    const logger = { info: () => undefined, warn: () => undefined, debug: () => undefined };
    const gate = new ReplaySessionGate('replay', store as never, logger as never);
    expect(gate.shouldPersistShopfloor()).toBe(false);
    await gate.handleControlMessage('{"action":"begin","sessionId":"s1.log"}');
    expect(gate.shouldPersistShopfloor()).toBe(true);
  });

  it('skips writes when session already ingested', async () => {
    const recorded: string[] = [];
    const store = {
      hasReplaySession: async () => true,
      recordReplaySession: async (id: string) => {
        recorded.push(id);
      },
    };
    const logger = { info: () => undefined, warn: () => undefined, debug: () => undefined };
    const gate = new ReplaySessionGate('replay', store as never, logger as never);
    await gate.handleControlMessage('{"action":"begin","sessionId":"s1.log"}');
    expect(gate.shouldPersistShopfloor()).toBe(false);
    await gate.handleControlMessage('{"action":"commit","sessionId":"s1.log"}');
    expect(recorded).toEqual([]);
  });

  it('records session on commit when newly ingested', async () => {
    const recorded: string[] = [];
    const store = {
      hasReplaySession: async () => false,
      recordReplaySession: async (id: string) => {
        recorded.push(id);
      },
    };
    const logger = { info: () => undefined, warn: () => undefined, debug: () => undefined };
    const gate = new ReplaySessionGate('replay', store as never, logger as never);
    await gate.handleControlMessage('{"action":"begin","sessionId":"s1.log"}');
    await gate.handleControlMessage('{"action":"commit","sessionId":"s1.log"}');
    expect(recorded).toEqual(['s1.log']);
  });

  it('always persists in live mode and ignores control', async () => {
    let hasCalls = 0;
    const store = {
      hasReplaySession: async () => {
        hasCalls += 1;
        return false;
      },
      recordReplaySession: async () => undefined,
    };
    const logger = { info: () => undefined, warn: () => undefined, debug: () => undefined };
    const gate = new ReplaySessionGate('live', store as never, logger as never);
    expect(gate.shouldPersistShopfloor()).toBe(true);
    await gate.handleControlMessage('{"action":"begin","sessionId":"s1.log"}');
    expect(hasCalls).toBe(0);
    expect(gate.shouldPersistShopfloor()).toBe(true);
  });
});
