import { describe, expect, it } from 'vitest';
import { loadConfig } from '../config';
import { createPersistenceStore } from '../db.factory';
import { MssqlPersistenceDb } from '../db.mssql';
import { Logger } from '../logger';

describe('createPersistenceStore', () => {
  it('returns MSSQL store', () => {
    const store = createPersistenceStore(loadConfig(), new Logger('error'));
    expect(store).toBeInstanceOf(MssqlPersistenceDb);
  });
});
