/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { LoadingBayCache, LoadingBayMap } from '../fts/load/loadingBayCache';
import { AvailableState, DeviceType, FtsPairedModule } from '../../../../common/protocol/ccu';
import { Factsheet } from '../../../../common/protocol/vda';
import { ModuleData } from './pairing-states';
import { LoadingBay, LoadingBayId, NODE_ID_UNKNOWN } from '../../../../common/protocol/fts';
import { publishPairingState } from './index';
import { BasePairingStates } from './base-pairing-states';
import { FactoryLayoutService } from '../layout/factory-layout-service';

export class FtsPairingStates extends BasePairingStates<FtsPairedModule> {
  private static instance: FtsPairingStates;

  private readonly knownModules: Map<string, ModuleData<FtsPairedModule>>;
  private readonly loadingBayCache: LoadingBayCache;
  private readonly type: DeviceType;

  private constructor() {
    super();
    this.type = 'FTS';
    // TODO FITEFF22-347 do we need to store the previous FTS pairings?
    this.knownModules = new Map<string, ModuleData<FtsPairedModule>>();
    this.loadingBayCache = LoadingBayCache.getInstance();
  }

  protected getKnownModules(): Map<string, ModuleData<FtsPairedModule>> {
    return this.knownModules;
  }

  public static getInstance(): FtsPairingStates {
    if (!FtsPairingStates.instance) {
      FtsPairingStates.instance = new FtsPairingStates();
    }
    return FtsPairingStates.instance;
  }

  public isReady(serialNumber: string): boolean {
    const state = this.knownModules.get(serialNumber)?.state;

    if (!state || !state.connected) {
      return false;
    }

    return state.available === AvailableState.READY;
  }

  public isReadyForOrder(serialNumber: string, orderId: string) {
    const data = this.knownModules.get(serialNumber);
    if (!data?.state?.connected) {
      return false;
    }
    if (data.orderId && data.orderId !== orderId) {
      return false;
    }
    return data.state.available === AvailableState.READY;
  }

  public updateFacts(facts: Factsheet) {
    this.initializePairingStateObject(facts.serialNumber);
    const data = this.knownModules.get(facts.serialNumber)!;
    data.factsheet = facts;
    if (data.state.connected) {
      data.state.lastSeen = new Date();
    }
  }

  /**
   * Update the availability of an FTS
   * @param serialNumber the serial number of the FTS
   * @param avail the available state
   * @param orderId the order id the FTS is reserved for
   * @param nodeId the id of the last node the FTS was at
   * @param lastModuleSerialNumber the id of the module the fts stops at
   * @param lastLoadPosition the load position the fts is docking with
   */
  public async updateAvailability(
    serialNumber: string,
    avail: AvailableState,
    orderId?: string,
    nodeId?: string,
    lastModuleSerialNumber?: string,
    lastLoadPosition?: LoadingBayId,
  ): Promise<void> {
    this.initializePairingStateObject(serialNumber);
    const data = this.knownModules.get(serialNumber)!;
    data.state.available = avail;
    data.orderId = orderId;
    if (nodeId && nodeId !== data.state.lastNodeId) {
      console.debug(`${this.type} ${serialNumber} is now at position ${nodeId}`);
      data.state.lastNodeId = nodeId;
      if (nodeId === NODE_ID_UNKNOWN) {
        data.state.pairedSince = undefined;
        data.state.lastModuleSerialNumber = NODE_ID_UNKNOWN;
      } else if (data.state.lastNodeId === NODE_ID_UNKNOWN) {
        FactoryLayoutService.blockNodeSequence([
          {
            ftsSerialNumber: serialNumber,
            nodeId: nodeId,
          },
        ]);
      }
    }
    if (lastModuleSerialNumber && lastModuleSerialNumber !== data.state.lastModuleSerialNumber) {
      console.debug(`${this.type} ${serialNumber} is now at module ${lastModuleSerialNumber}`);
      data.state.lastModuleSerialNumber = lastModuleSerialNumber;
      // mark an FTS as paired when we know where it is in the factory
      if (lastModuleSerialNumber !== NODE_ID_UNKNOWN && !data.state.pairedSince) {
        data.state.pairedSince = new Date();
      } else if (lastModuleSerialNumber === NODE_ID_UNKNOWN && data.state.pairedSince) {
        data.state.pairedSince = undefined;
      }
    }
    if (lastModuleSerialNumber && lastLoadPosition) {
      data.state.lastLoadPosition = lastLoadPosition;
    } else if ((lastModuleSerialNumber === NODE_ID_UNKNOWN && !lastLoadPosition) || !data.state.lastLoadPosition) {
      data.state.lastLoadPosition = LoadingBay.MIDDLE;
    }
    await publishPairingState();
  }

  /**
   * Update the battery voltage and charging state
   * @param serialNumber
   * @param charging
   * @param voltage
   * @param percentage
   */
  public updateCharge(serialNumber: string, charging: boolean, voltage: number, percentage?: number) {
    console.log('CHARGING:..' + charging + ' ' + serialNumber + ' ' + voltage);
    this.initializePairingStateObject(serialNumber);
    const data = this.knownModules.get(serialNumber)!;
    data.state.charging = charging;
    data.state.batteryVoltage = voltage;
    data.state.batteryPercentage = percentage;
  }

  public isCharging(serialNumber: string): boolean {
    return this.get(serialNumber)?.charging ?? false;
  }

  /**
   * Returns an FTS that can accept the order
   * The readiness is determined by:
   * <ul>
   *   <li>If an FTS is assigned to the order or it has the workpiece of the order and it is ready then it is returned</li>
   *   <li>If that assigned FTS is not ready, undefined is returned, for example it is waiting for a load update</li>
   *   <li>Any FTS that is ready and not assigned to an order is returned</li>
   *  </ul>
   * @returns FtsPairedModule or undefined if none is ready for the order
   */
  public getReady(orderId?: string): FtsPairedModule | undefined {
    if (orderId) {
      const fts = this.getForOrder(orderId);
      if (fts) {
        return this.isReady(fts.serialNumber) ? fts : undefined;
      }
    }
    const allReady = this.getAllReadyUnassigned();
    if (allReady.length === 0) {
      return undefined;
    }
    return allReady[0].state;
  }

  /**
   * Find the FTS that is assigned to the order or has a workpiece for the order
   * @param orderId
   */
  public getForOrder(orderId: string): FtsPairedModule | undefined {
    for (const [serialNumber, fts] of this.knownModules) {
      // if an FTS is assigned to the order, use it.
      if (fts.orderId === orderId) {
        return fts.state;
      }
      // if an FTS has a load belonging to the order, use it.
      if (this.loadingBayCache.getLoadingBayForOrder(serialNumber, orderId)) {
        return fts.state;
      }
    }
    return undefined;
  }

  /**
   * gets a connected FTS that is assigned to an order.
   * @param orderId the order id
   */
  public getFtsSerialNumberForOrderId(orderId: string): string | undefined {
    const fts = Array.from(this.knownModules.values()).find(data => data.orderId === orderId && data.state.connected);
    return fts?.state.serialNumber ?? undefined;
  }

  /**
   * Get the data for all ready fts that are not assigned to an order
   */
  public getAllReadyUnassigned(): Array<ModuleData<FtsPairedModule>> {
    return Array.from(this.knownModules.values()).filter(
      data => data.state?.available === AvailableState.READY && data.state?.connected && data.orderId == undefined,
    );
  }

  public setLoadingBay(serialNumber: string, loadPosition: LoadingBayId, orderId: string): void {
    this.loadingBayCache.setLoadingBay(serialNumber, loadPosition, orderId);
  }

  public getOpenloadingBay(serialNumber: string): LoadingBayId | undefined {
    const loadingBays = this.loadingBayCache.getLoadingBayForFTS(serialNumber);
    const loadingBayIds: Array<keyof LoadingBayMap> = Object.keys(loadingBays) as Array<keyof LoadingBayMap>;
    for (const position of loadingBayIds) {
      if (loadingBays.hasOwnProperty(position) && loadingBays[position] === undefined) {
        return position;
      }
    }
    return undefined;
  }

  public getLoadedOrderIds(serialNumber: string): Array<string> {
    const loadingBays = this.loadingBayCache.getLoadingBayForFTS(serialNumber);
    const orderIds: Array<string> = [];
    for (const load of Object.values(loadingBays)) {
      if (load) {
        orderIds.push(load);
      }
    }
    return orderIds;
  }
  public isLoadingBayFree(serialNumber: string, bay: LoadingBayId): boolean {
    const loadingBays = this.loadingBayCache.getLoadingBayForFTS(serialNumber);
    return loadingBays[bay] === undefined;
  }

  public getLoadingBayForOrder(serialNumber: string, orderId: string): LoadingBayId | undefined {
    return this.loadingBayCache.getLoadingBayForOrder(serialNumber, orderId);
  }

  public clearLoadingBay(serialNumber: string, orderId: string): void {
    this.loadingBayCache.clearLoadingBayForOrder(serialNumber, orderId);
  }

  public resetLoadingBay(serialNumber: string): void {
    this.loadingBayCache.resetLoadingBayForFts(serialNumber);
  }

  protected getType(): DeviceType {
    return this.type;
  }

  public reset() {
    super.reset();
    this.loadingBayCache.reset();
  }

  /**
   * Checks if an FTS is waiting for a specific order at a given position.
   * @param orderId
   * @param targetSerialNumber
   */
  public isFtsWaitingAtPosition(orderId: string, targetSerialNumber: string): boolean {
    const fts = Array.from(this.knownModules.values()).find(paired => paired.state.lastModuleSerialNumber === targetSerialNumber);
    if (!fts) {
      return false;
    }

    const loadingBay = this.getLoadingBayForOrder(fts.state.serialNumber, orderId);
    return loadingBay !== undefined;
  }

  /**
   * Checks if an FTS is docked without an order waiting at a given position.
   * @param targetSerialNumber
   * @param [orderId] the orderId that has to be able to be accepted by the FTS
   */
  public getFtsAtPosition(targetSerialNumber: string, orderId?: string): FtsPairedModule | undefined {
    const fts = Array.from(this.knownModules.values()).find(
      paired =>
        paired.state.connected &&
        paired.state.lastModuleSerialNumber === targetSerialNumber &&
        paired.state.available === AvailableState.READY,
    );
    if (!fts) {
      return undefined;
    }

    if (orderId) {
      const loadingBay = this.getLoadingBayForOrder(fts.state.serialNumber, orderId);
      if (loadingBay !== undefined) {
        return undefined;
      }
      if (!fts.state.lastLoadPosition || !this.isLoadingBayFree(fts.state.serialNumber, fts.state.lastLoadPosition)) {
        return undefined;
      }
    }

    return fts.state;
  }

  getLastFinishedDockId(serialNumber: string): string | undefined {
    return this.knownModules.get(serialNumber)?.lastFinishedActionId;
  }

  setLastFinishedDockId(serialNumber: string, actionId: string) {
    this.initializePairingStateObject(serialNumber);
    const data = this.knownModules.get(serialNumber)!;
    data.lastFinishedActionId = actionId;
  }
}
