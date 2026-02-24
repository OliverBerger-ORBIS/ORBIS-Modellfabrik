import { AvailableState, DeviceType, PairedModule } from '../../../../common/protocol/ccu';
import { Connection, ConnectionState, Factsheet } from '../../../../common/protocol/vda';
import { requestFactsheet } from '../factsheets/factsheets';
import { ModuleData } from './pairing-states';

export abstract class BasePairingStates<A extends PairedModule> {
  /**
   * Get a PairedModule for a given serial number. undefined if no module is paired.
   * @param serialNumber the serial number of the module
   */
  public get(serialNumber: string): A | undefined {
    return this.getKnownModules().get(serialNumber)?.state;
  }

  /**
   * Returns all paired DeviceTypes
   */
  public getAll(): Array<A> {
    return Array.from(this.getKnownModules().values()).map(data => data.state) as Array<A>;
  }

  /**
   * Returns the factsheet for the module with the given serial number. undefined if no factsheet is available.
   * @param serialNumber
   */
  public getFactsheet(serialNumber: string): Factsheet | undefined {
    return this.getKnownModules().get(serialNumber)?.factsheet;
  }

  /**
   * checks if a module is ready for an order.
   * @param serialNumber the serial number of the module
   */
  public abstract isReady(serialNumber: string): boolean;

  /**
   * Clears all known modules.
   */
  public reset(): void {
    this.getKnownModules().clear();
  }

  /**
   * update the connection state of a device type
   * @param conn the connection state
   */
  public async update(conn: Connection): Promise<void> {
    this.initializePairingStateObject(conn.serialNumber);
    // this will not be null, because we will initialze it in the line above
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const data = this.getKnownModules().get(conn.serialNumber)!;
    const lastConnState = data.connection?.connectionState;
    data.connection = conn;
    data.state.connected = conn.connectionState === ConnectionState.ONLINE;
    data.state.ip = conn.connectionState === ConnectionState.ONLINE ? conn.ip : undefined;
    data.state.version = conn.version;
    console.log('updated state', JSON.stringify(data.state));
    if (data.state.connected) {
      data.state.lastSeen = new Date();
      if (!data.factsheet || (lastConnState && lastConnState !== ConnectionState.ONLINE)) {
        await requestFactsheet(data.state);
      }
    } else {
      data.state.available = AvailableState.BLOCKED;
    }
  }

  /**
   * Mark a module as being in the calibration mode
   * @param serialNumber
   * @param calibrating is the caliration mode active?
   */
  public setCalibrating(serialNumber: string, calibrating: boolean) {
    this.initializePairingStateObject(serialNumber);
    // this will not be null, because we will initialze it in the line above
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    this.getKnownModules().get(serialNumber)!.state.calibrating = calibrating;
  }

  /**
   * update the factsheet of a device type
   * @param factsheet the factsheet
   */
  public abstract updateFacts(factsheet: Factsheet): void;

  /**
   * update the availability of a device type
   * @param type the type to update
   * @param serialNumber the serial number of the module
   * @param avail the availability
   * @param orderId the order id
   */
  public abstract updateAvailability(type: DeviceType, serialNumber: string, avail: AvailableState, orderId?: string): Promise<void>;

  protected abstract getKnownModules(): Map<string, ModuleData<A>>;

  protected abstract getType(): DeviceType;

  /**
   * Initialize a pairing state if necessary
   */
  protected initializePairingStateObject(serialNumber: string): void {
    if (this.getKnownModules().has(serialNumber)) {
      return;
    }

    this.getKnownModules().set(serialNumber, <ModuleData<A>>{
      state: {
        serialNumber: serialNumber,
        type: this.getType(),
        connected: false,
        available: AvailableState.BLOCKED,
      },
    });
  }
}
