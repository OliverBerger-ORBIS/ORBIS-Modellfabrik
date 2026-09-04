import { ServiceConfig } from './config';
import { Logger } from './logger';
import { HistoryQueryStore } from './queryTypes';
import { NormalizedMessage } from './types';

export interface PersistenceStore extends HistoryQueryStore {
  connect(): Promise<void>;
  close(): Promise<void>;
  persist(normalized: NormalizedMessage): Promise<void>;
  cleanupRawRetention(): Promise<void>;
  hasReplaySession(sessionId: string): Promise<boolean>;
  recordReplaySession(sessionId: string): Promise<void>;
}

export type PersistenceStoreFactory = (config: ServiceConfig, logger: Logger) => PersistenceStore;
