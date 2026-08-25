import { Logger } from './logger';
import { PersistenceStore } from './persistenceStore';

export const REPLAY_SESSION_TOPIC = 'osf/persistence/replay/session';

export type ReplaySessionAction = 'begin' | 'commit';

export interface ReplaySessionControl {
  action: ReplaySessionAction;
  sessionId: string;
}

/**
 * Local replay idempotency: after a successful commit, the same sessionId
 * is recorded in replay_session_ingest and further MQTT for that run is skipped.
 * Live mode ignores control messages and always persists.
 */
export class ReplaySessionGate {
  private activeSessionId: string | null = null;
  private skipWrites = false;
  private onBeginPersist: (() => void) | undefined;

  constructor(
    private readonly mode: 'live' | 'replay',
    private readonly store: PersistenceStore,
    private readonly logger: Logger,
    options?: { onBeginPersist?: () => void }
  ) {
    this.onBeginPersist = options?.onBeginPersist;
  }

  isControlTopic(topic: string): boolean {
    return topic === REPLAY_SESSION_TOPIC;
  }

  /** In replay mode, persist only after begin and when session is not already ingested. */
  shouldPersistShopfloor(): boolean {
    if (this.mode !== 'replay') {
      return true;
    }
    if (!this.activeSessionId) {
      return false;
    }
    return !this.skipWrites;
  }

  async handleControlMessage(payloadText: string): Promise<void> {
    if (this.mode !== 'replay') {
      this.logger.debug('Ignoring replay session control in live mode');
      return;
    }

    const control = parseReplaySessionControl(payloadText);
    if (!control) {
      this.logger.warn('Invalid replay session control payload', { payloadText: payloadText.slice(0, 200) });
      return;
    }

    if (control.action === 'begin') {
      await this.onBegin(control.sessionId);
      return;
    }
    await this.onCommit(control.sessionId);
  }

  private async onBegin(sessionId: string): Promise<void> {
    this.activeSessionId = sessionId;
    const already = await this.store.hasReplaySession(sessionId);
    this.skipWrites = already;
    if (already) {
      this.logger.info('Replay session already ingested — skipping persists', { sessionId });
    } else {
      this.logger.info('Replay session begin — persisting', { sessionId });
      this.onBeginPersist?.();
    }
  }

  private async onCommit(sessionId: string): Promise<void> {
    if (this.skipWrites) {
      this.logger.info('Replay session commit ignored (was skip)', { sessionId });
      this.activeSessionId = null;
      return;
    }
    if (this.activeSessionId && this.activeSessionId !== sessionId) {
      this.logger.warn('Replay session commit id mismatch', {
        active: this.activeSessionId,
        commit: sessionId,
      });
    }
    await this.store.recordReplaySession(sessionId);
    this.logger.info('Replay session committed to ingest list', { sessionId });
    this.activeSessionId = null;
    this.skipWrites = false;
  }
}

export function parseReplaySessionControl(payloadText: string): ReplaySessionControl | undefined {
  try {
    const parsed = JSON.parse(payloadText) as Record<string, unknown>;
    const actionRaw = String(parsed.action ?? '').trim().toLowerCase();
    const sessionId = String(parsed.sessionId ?? parsed.session_id ?? '').trim();
    if (!sessionId) {
      return undefined;
    }
    if (actionRaw !== 'begin' && actionRaw !== 'commit') {
      return undefined;
    }
    return { action: actionRaw, sessionId };
  } catch {
    return undefined;
  }
}
