import { LoadingBayId } from '../../../../../common/protocol/fts';

export type LoadingBayMap = {
  '1': string | undefined;
  '2': string | undefined;
  '3': string | undefined;
};

export class LoadingBayOccupiedError extends Error {
  constructor(serialNumber: string, position: LoadingBayId) {
    super(`The loading bay for FTS ${serialNumber} and position ${position} is already occupied`);
    this.name = 'LoadingBayOccupiedError';
  }
}

export class LoadingBayCache {
  private static instance: LoadingBayCache;

  public static getInstance(): LoadingBayCache {
    if (!LoadingBayCache.instance) {
      LoadingBayCache.instance = new LoadingBayCache();
    }
    return LoadingBayCache.instance;
  }

  private loadingBayCache: Map<string, LoadingBayMap>;

  private constructor() {
    this.loadingBayCache = new Map<string, LoadingBayMap>();
  }

  private initLoadingBayForFTS(serialNumber: string): void {
    this.loadingBayCache.set(serialNumber, {
      '1': undefined,
      '2': undefined,
      '3': undefined,
    });
  }

  /**
   * Returns the loading bay for the given serial number.
   * @param serialNumber the serial number of the FTS
   */
  public getLoadingBayForFTS(serialNumber: string): LoadingBayMap {
    if (!this.loadingBayCache.has(serialNumber)) {
      this.initLoadingBayForFTS(serialNumber);
    }

    return this.loadingBayCache.get(serialNumber) as LoadingBayMap;
  }

  public getLoadingBayForOrder(serialNumber: string, orderId: string): LoadingBayId | undefined {
    if (!this.loadingBayCache.has(serialNumber)) {
      return undefined;
    }

    const loadingBays = this.loadingBayCache.get(serialNumber) as LoadingBayMap;
    if (!loadingBays) {
      return undefined;
    }

    const positions: Array<keyof LoadingBayMap> = Object.keys(loadingBays) as Array<keyof LoadingBayMap>;
    for (const position of positions) {
      if (loadingBays[position] === orderId) {
        return position;
      }
    }

    return undefined;
  }

  /**
   * Sets the loading bay for the given serial number.
   * @param serialNumber the serial number of the FTS
   * @param loadPosition the loading bay
   * @param orderId the order associated with the loading bay
   * @throws LoadingBayOccupiedError if the loading bay is already occupied
   */
  public setLoadingBay(serialNumber: string, loadPosition: LoadingBayId, orderId: string): void {
    if (!this.loadingBayCache.has(serialNumber)) {
      this.initLoadingBayForFTS(serialNumber);
    }

    const loadingBays = this.loadingBayCache.get(serialNumber) as LoadingBayMap;
    if (loadingBays.hasOwnProperty(loadPosition) && loadingBays[loadPosition]) {
      if (loadingBays[loadPosition] !== orderId) {
        throw new LoadingBayOccupiedError(serialNumber, loadPosition);
      }
    }

    loadingBays[loadPosition] = orderId;
  }

  /**
   * Clears the loading bay for the given serial number and order.
   * @param serialNumber the serial number of the FTS
   * @param orderId the id of the order
   */
  public clearLoadingBayForOrder(serialNumber: string, orderId: string): void {
    if (!this.loadingBayCache.has(serialNumber)) {
      this.initLoadingBayForFTS(serialNumber);
    }

    const loadingBays = this.loadingBayCache.get(serialNumber) as LoadingBayMap;
    if (!loadingBays) {
      return;
    }

    const positions: Array<keyof LoadingBayMap> = Object.keys(loadingBays) as Array<keyof LoadingBayMap>;
    for (const position of positions) {
      if (loadingBays[position] === orderId) {
        loadingBays[position] = undefined;
      }
    }
    console.log(loadingBays);
  }

  public resetLoadingBayForFts(serialNumber: string): void {
    if (!this.loadingBayCache.has(serialNumber)) {
      return;
    }

    this.loadingBayCache.set(serialNumber, {
      '1': undefined,
      '2': undefined,
      '3': undefined,
    });
  }

  public reset(): void {
    this.loadingBayCache.clear();
  }
}
