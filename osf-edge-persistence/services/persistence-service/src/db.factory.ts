import { ServiceConfig } from './config';
import { MssqlPersistenceDb } from './db.mssql';
import { Logger } from './logger';
import { PersistenceStore } from './persistenceStore';

export function createPersistenceStore(config: ServiceConfig, logger: Logger): PersistenceStore {
  return new MssqlPersistenceDb(config, logger);
}
