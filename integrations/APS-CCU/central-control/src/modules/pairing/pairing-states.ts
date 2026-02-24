/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { AvailableState, DeviceType, PairedModule } from '../../../../common/protocol/ccu';
import { Module, MODULE_DEFAULT_PRODUCTION_DURATION, ModuleType, SUPPORT_MODULES } from '../../../../common/protocol/module';
import { Connection, Factsheet, InstantActions } from '../../../../common/protocol/vda';
import { BasePairingStates } from './base-pairing-states';
import { publishPairingState, sendKnownModules } from './index';
import config from '../../config';

export interface ModuleData<T extends PairedModule> {
  state: T;
  connection?: Connection;
  factsheet?: Factsheet;
  orderId?: string;
  /** The last finished action id that has been received. */
  lastFinishedActionId?: string;
}

export class PairingStates extends BasePairingStates<PairedModule> {
  private static instance: PairingStates;

  private readonly knownModules: Map<string, ModuleData<PairedModule>>;
  private readonly type: DeviceType;

  private constructor() {
    super();
    // TODO FITEFF22-347 do we need to store the last pairing date and last communication date?
    this.type = 'MODULE';
    this.knownModules = new Map<string, ModuleData<PairedModule>>();
  }

  protected getKnownModules(): Map<string, ModuleData<PairedModule>> {
    if (config.mqtt.debug) {
      sendKnownModules(Object.fromEntries(this.knownModules)).catch(e => {
        // do not crash if we cannot publish the known modules, this is only for debugging
        console.error(e);
      });
    }
    return this.knownModules;
  }

  public static getInstance(): PairingStates {
    if (!PairingStates.instance) {
      PairingStates.instance = new PairingStates();
    }
    return PairingStates.instance;
  }

  /**
   * returns a PairedModule if a module of ModuleType is ready for the given orderId.
   * The readiness is determined by:
   * <ul>
   *   <li>a module is connected and no order is currently execution on it --> a PairedModule is returned</li>
   *   <li>a module is connected, but an order is present on it.
   *    <br>
   *    <ul>
   *      <li>the order has not the same id as orderId --> undefined since the module is not ready</li>
   *      <li>
   *        <ul>
   *          <li>the state of the order != State.FINISHED --> undefined since the module is not ready</li>
   *          <li>the state of the order == State.FINISHED --> a PairedModule is returned as it is in a ready state to receive an order update for the given orderId</li>
   *        </ul>
   *      </li>
   *      <li>the order has the same id as orderId and has a status != State.FINISHED --> undefined since the module is not ready</li>
   *      <li>the order has the same id as orderId and has a status != State.FINISHED --> undefined since the module is not ready</li>
   *    </ul>
   *   </li>
   *   <li>the module is of the given type</li>
   *   </ul>
   * @param moduleType the module type to look for
   * @param orderId the order id to determine if the module is ready for an order.
   */
  public getReadyForModuleType(moduleType: ModuleType, orderId: string): PairedModule | undefined {
    const allReady = this.getAllReadyModuleData('MODULE').filter(data => data.factsheet?.typeSpecification.moduleClass === moduleType);
    console.log(`Found ready modules for ${moduleType}: ${allReady?.length || 0}`);
    return this.findModuleForOrder(allReady, orderId);
  }

  private findModuleForOrder(modules: ModuleData<PairedModule>[], orderId?: string): PairedModule | undefined {
    let pairedMod = undefined;
    for (const mod of modules) {
      if (mod.orderId != undefined && mod.orderId !== orderId) {
        console.log(`Module ${mod.state.serialNumber} is not ready for orderID: ${orderId} 
        because it is already assigned to order ${mod.orderId}`);
        continue;
      }

      pairedMod = mod.state;
      if (mod.orderId === orderId) {
        // Early exit if we have a direct math on the order ID
        return mod.state;
      }
    }

    return pairedMod;
  }

  /**
   * Get the module currently assigned to the order
   * @param orderId
   * @param moduleType
   */
  public getModuleForOrder(orderId: string, moduleType?: ModuleType): PairedModule | undefined {
    return this.getAllReadyModuleData('MODULE').find(data => {
      const orderIDMatches = data.orderId === orderId;
      const typeMatches = moduleType === undefined || data.state.subType === moduleType;
      console.log(`Finding module for order: ${orderId} ${moduleType} -> Results: ${orderIDMatches} ${typeMatches}`);
      return orderIDMatches && typeMatches;
    })?.state;
  }

  /**
   * Return if the module is ready to receive an order with the given orderid.
   * @param serialNumber
   * @param orderId
   */
  public isReadyForOrder(serialNumber: string, orderId: string): boolean {
    const data = this.getKnownModules().get(serialNumber);
    return data != undefined && this.isReady(serialNumber) && (!data.orderId || data.orderId === orderId);
  }

  /**
   * Get a paired module for a given type. This does not check if the module is ready to accept a new order. if this is needed use getReadyForModuleType.
   * Returns undefined if no module of the given type is paired and connected
   * @param moduleType the type the paired module should have
   * @param [orderId] reuse the module for the given orderId if possible
   */
  public getForModuleType(moduleType: ModuleType, orderId?: string): PairedModule | undefined {
    const moduls = this.getAllPairedModuleData()
      .filter(module => module.state.connected)
      .filter(module => module.factsheet?.typeSpecification.moduleClass === moduleType);
    if (!orderId) {
      return moduls[0]?.state;
    }
    return this.findModuleForOrder(moduls, orderId);
  }

  private getAllPairedModuleData(): Array<ModuleData<PairedModule>> {
    return Array.from(this.knownModules.values()).filter(m => m.state.type === 'MODULE' && m.state.pairedSince);
  }

  getAllReadyModuleData(type: DeviceType): Array<ModuleData<PairedModule>> {
    return this.getAllPairedModuleData().filter(
      data => data.state?.type === type && data.state?.available === AvailableState.READY && data.state?.connected,
    );
  }

  getAllReady(type: ModuleType): Array<PairedModule> {
    return this.getAllReadyModuleData('MODULE')
      .map(data => data.state)
      .filter(state => state.subType === type);
  }

  getAllPaired(type: ModuleType): Array<PairedModule> {
    return this.getAllPairedModuleData()
      .map(data => data.state)
      .filter(state => state.subType === type);
  }

  /**
   * Checks if a module is ready to receive an order or an order update
   * A module is ready if it is connected and paired and its state is READY.
   *
   * It does not indicate if the module can receive any new order or
   * only order updates for a specific order.
   * @param serialNumber
   */
  public isReady(serialNumber: string): boolean {
    const state = this.knownModules.get(serialNumber)?.state;

    if (!state || !state.connected || !state.pairedSince) {
      return false;
    }

    return state.available === AvailableState.READY;
  }

  public updateFacts(facts: Factsheet) {
    this.initializePairingStateObject(facts.serialNumber);
    const data = this.knownModules.get(facts.serialNumber)!;
    data.factsheet = facts;
    data.state.subType = data.factsheet.typeSpecification.moduleClass as unknown as ModuleType;
    data.state.hasCalibration =
      undefined != data.factsheet.protocolFeatures?.moduleActions?.find(a => a.actionType === InstantActions.CALIBRATION_START);
    // set default productionDuration if it is still missing.
    if (!data.state.productionDuration && !SUPPORT_MODULES.has(data.state.subType) && data.state.subType !== ModuleType.AIQS) {
      data.state.productionDuration = MODULE_DEFAULT_PRODUCTION_DURATION;
    }
    if (data.state.connected) {
      data.state.lastSeen = new Date();
    }
  }

  public async updateAvailability(serialNumber: string, avail: AvailableState, orderId?: string) {
    this.initializePairingStateObject(serialNumber);
    const data = this.knownModules.get(serialNumber)!;
    console.log(`PAIRING: updateAvailability ${serialNumber} ${avail} ${orderId}`);
    data.state.available = avail;
    data.state.assigned = !!orderId;
    data.orderId = orderId;
    await publishPairingState();
  }

  protected getType(): DeviceType {
    return this.type;
  }

  /**
   * Remove the module lock to a specific order, so all orders are accepted again
   * @param orderId
   */
  public clearModuleForOrder(orderId: string): void {
    for (const module of this.knownModules.values()) {
      if (module.orderId !== orderId) {
        continue;
      }
      module.orderId = undefined;
      module.state.assigned = false;
      module.state.available = AvailableState.READY;
    }
  }

  /**
   * Replace the paired modules with a new set of modules
   * This is used to set the paired modules from the modules configured in the layout
   *
   * @param modules all paired modules
   */
  public setPairedModules(modules: Module[]) {
    const pairedIds = new Set(modules.map(module => module.serialNumber));
    // delete pairing for removed modules
    for (const [moduleId, module] of this.knownModules.entries()) {
      if (!pairedIds.has(moduleId)) {
        module.state.pairedSince = undefined;
      }
    }
    // add pairing for added modules
    for (const module of modules) {
      this.initializePairingStateObject(module.serialNumber);
      const state = this.knownModules.get(module.serialNumber)!.state;
      if (!state.subType) {
        state.subType = module.type;
      }
      // set default productionDuration if it is still missing.
      if (!state.productionDuration && !SUPPORT_MODULES.has(module.type) && module.type !== ModuleType.AIQS) {
        state.productionDuration = MODULE_DEFAULT_PRODUCTION_DURATION;
      }
      if (!state.pairedSince) {
        state.pairedSince = new Date();
      }
      if (module.type === ModuleType.CHRG) {
        state.connected = true;
        if (state.available !== AvailableState.BUSY) {
          state.available = AvailableState.READY;
        }
      }
    }
  }

  /**
   * Updates the production duration for a given module.
   *
   * @param {string} serialNumber - The serial number of the module to update.
   * @param {number} duration - The new production duration.
   */
  updateDuration(serialNumber: string, duration: number) {
    const state = this.get(serialNumber);
    console.debug(`Setting duration for ${serialNumber} to ${duration}`);
    if (state && state.subType && !SUPPORT_MODULES.has(state.subType) && state.productionDuration !== undefined) {
      state.productionDuration = duration;
    }
  }

  /**
   * Get the module type for a module by serial number
   * The module type is known only after the module has successfully sent its factsheet.
   *
   * @param serialNumber
   */
  getModuleType(serialNumber: string): ModuleType | undefined {
    return this.getFactsheet(serialNumber)?.typeSpecification.moduleClass;
  }

  /**
   * Removes a module from the known modules by serial number.
   * @param {string} serialNumber - The serial number of the module to remove.
   */
  public async removeKnownModule(serialNumber: string): Promise<void> {
    if (this.getKnownModules().has(serialNumber)) {
      this.getKnownModules().delete(serialNumber);
    }
    await publishPairingState();
  }
}
