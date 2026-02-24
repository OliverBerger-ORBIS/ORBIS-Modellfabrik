import { readJsonFile, writeJsonFile } from '../helpers';

export abstract class PersistenceService {
  protected static storageLocation: string;

  public static async init<T = unknown>(storageLocation: string): Promise<T | undefined> {
    this.storageLocation = storageLocation;
    if (this.storageLocation) {
      return this.load();
    }

    return undefined;
  }

  /**
   * Loads the data from the storage location on the disc.
   */
  protected static async load<T = unknown>(): Promise<T | undefined> {
    if (!this.storageLocation) {
      return undefined;
    }

    try {
      const value = await readJsonFile<T>(this.storageLocation);
      return value;
    } catch (error) {
      console.error('Error while loading file: ' + this.storageLocation, error);
    }
  }

  /**
   * Persists the provided data to the storage location on the disc.
   */
  public static async persist(data: unknown) {
    if (!this.storageLocation) {
      return;
    }

    try {
      await writeJsonFile(this.storageLocation, data);
    } catch (error) {
      console.error('Error while saving file: ' + this.storageLocation, error);
    }
  }
}
