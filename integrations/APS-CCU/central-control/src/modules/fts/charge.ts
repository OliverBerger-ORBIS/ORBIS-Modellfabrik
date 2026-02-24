import { FtsCommandType, FtsState, LoadingBay } from '../../../../common/protocol/fts';
import { NavigatorService } from './navigation/navigator-service';
import { PairingStates } from '../pairing/pairing-states';
import { ModuleType } from '../../../../common/protocol/module';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { AvailableState } from '../../../../common/protocol/ccu';
import { randomUUID } from 'node:crypto';
import { getBlockedNodesForOrder, getSortedModulePaths, sendClearModuleNodeNavigationRequest } from './navigation/navigation';
import { DockingMetadata, FtsOrder } from './model';
import { getMqttClient } from '../../mqtt/mqtt';
import { FtsTopic, getFtsTopic } from '../../../../common/protocol';
import { FactoryLayoutService } from '../layout/factory-layout-service';
import config from '../../config';
import { InstantAction, InstantActions } from '../../../../common/protocol/vda';
import { GeneralConfigService } from '../../services/config/general-config-service';

export const FTS_WAITING_FOR_RECHARGE: Set<string> = new Set<string>();

/**
 * Check if the FTS battery is low and should be recharged
 * @param state
 */
export const isBatteryLow = (state: FtsState): boolean => {
  // battery is nominal 8.4V. The FTS fails at less than 8.4V
  // maybe there should be a boost converter from 8.4 to 9V, so we can use the nominal battery voltage?
  // isNaN check returns true if the value is null so we need to check for null first
  if (state.batteryState?.percentage != null && !isNaN(state.batteryState?.percentage as number)) {
    return state.batteryState.percentage <= GeneralConfigService.config.ftsSettings.chargeThresholdPercent;
  }
  return false;
};

/**
 * Handle updating the FTS charge status and the charger availability
 * @param state
 */
export const handleChargingUpdate = (state: FtsState) => {
  const ftsPairingState = FtsPairingStates.getInstance();
  const pairingState = PairingStates.getInstance();
  if (!state.batteryState?.charging && ftsPairingState.isCharging(state.serialNumber)) {
    if (state.orderId) {
      pairingState.clearModuleForOrder(state.orderId);
    }
  }
  ftsPairingState.updateCharge(
    state.serialNumber,
    state.batteryState?.charging ?? false,
    state.batteryState?.currentVoltage ?? 0,
    state.batteryState?.percentage,
  );
};

/**
 * Retrigger charging orders that could not be issued due to path problems, or missing chargers
 */
export const retriggerChargeOrders = async () => {
  for (const serial of FTS_WAITING_FOR_RECHARGE) {
    await triggerChargeOrderForFts(serial);
  }
};

/**
 * Mark busy chargers, that have no FTS on them, as ready again
 */
export const resetBusyChargersThatAreEmpty = async (): Promise<void> => {
  const pairingStates = PairingStates.getInstance();
  const ftsPairingStates = FtsPairingStates.getInstance();
  const modules = pairingStates.getAllPaired(ModuleType.CHRG);
  for (const charger of modules) {
    if (charger.serialNumber && charger.available === AvailableState.BUSY) {
      const fts = ftsPairingStates.getFtsAtPosition(charger.serialNumber);
      if (!fts) {
        await pairingStates.updateAvailability(charger.serialNumber, AvailableState.READY);
      }
    }
  }
};

/**
 * If there are FTS waiting to charge, try to free up a charger blocked by a ready fts if that is possible.
 *
 * @param force free chargers even if it is not necessary, do not let an FTS idle on a charger
 */
export const freeBlockedChargers = async (force = false) => {
  if (!force && !FTS_WAITING_FOR_RECHARGE.size) {
    return;
  }
  const ftsPairingStates = FtsPairingStates.getInstance();
  const modules = PairingStates.getInstance().getAllReady(ModuleType.CHRG);
  for (const blocked of modules) {
    try {
      if (ftsPairingStates.getFtsAtPosition(blocked.serialNumber)) {
        await sendClearModuleNodeNavigationRequest(blocked.serialNumber);
        return;
      }
    } catch {
      console.log(`FTS CHARGE: Freeing of module ${blocked.serialNumber} failed, trying next module.`);
    }
  }
};

/**
 * Verifies if charging command is enabled by config {@link config.ftsCharge.enabled}.
 * If it is not enabled, prints an info and aborts any further actions
 *
 * If it is enabled, it checks if a charging order can be issued:
 * - FTS must be ready
 * - A READY charger module must be in the layout
 * - The position of the FTS must be known
 * - A valid path to the charger must exist (this also takes blocked nodes into consideration)
 *
 * If any of the checks fail, the serialnumber is queued and a retry will be issued on FTS state change
 * @param serialNumber The FTS serial number to trigger the charge order for
 * @param forceCharge If true, the charge order will be issued even if the automatic charging is disabled.
 * All other checks (charger available, FTS ready, ...) still apply. This is used for manual triggered loading
 * via the UI.
 */
export const triggerChargeOrderForFts = async (serialNumber: string, forceCharge = false) => {
  if (config.ftsCharge.disabled && !forceCharge) {
    console.info('FTS CHARGE: Disabled by config');
    return;
  }

  const ftsPairingStates = FtsPairingStates.getInstance();
  FTS_WAITING_FOR_RECHARGE.add(serialNumber);
  if (!ftsPairingStates.isReady(serialNumber) || ftsPairingStates.isCharging(serialNumber)) {
    console.warn(`FTS CHARGE: FTS ${serialNumber} not ready to navigate to charger`);
    return;
  }
  const modules = PairingStates.getInstance().getAllReady(ModuleType.CHRG);
  if (!modules.length) {
    console.warn(`FTS CHARGE: cannot navigate to charger for ${serialNumber}, no charger available`);
    return;
  }
  const fts = ftsPairingStates.get(serialNumber);
  if (!fts?.lastModuleSerialNumber) {
    console.warn('FTS CHARGE: cannot navigate from unknown last module for fts ' + serialNumber);
    return;
  }
  const paths = getSortedModulePaths(fts, modules);
  if (!paths?.length) {
    console.warn(`FTS CHARGE: cannot navigate to charger for ${serialNumber}, no charger or no path`);
    return;
  }

  try {
    await sendChargingNavigationRequest(fts.serialNumber, paths[0].module.serialNumber);
    FTS_WAITING_FOR_RECHARGE.delete(serialNumber);
  } catch (e) {
    console.warn(`FTS CHARGE: cannot send charging navigation to ${serialNumber}: `, e);
  }
};

/**
 * send the charging order
 * @param serialNumber
 * @param target
 */
export const sendChargingNavigationRequest = async (serialNumber: string, target: string): Promise<void> => {
  // Is there an FTS ready to take the navigation Request?
  const ftsPairingStates = FtsPairingStates.getInstance();
  const pairingStates = PairingStates.getInstance();
  const orderId = randomUUID();

  const fts = ftsPairingStates.get(serialNumber);
  if (!fts || !ftsPairingStates.isReady(serialNumber)) {
    return;
  }
  const chargeModule = pairingStates.get(target);
  if (!chargeModule || !pairingStates.isReady(target)) {
    throw new Error(`FTS CHARGE: The module ${target} is blocked`);
  }

  const startPosition = fts.lastModuleSerialNumber;
  if (!startPosition) {
    throw new Error(`FTS CHARGE: The start position for FTS ${serialNumber} is unknown`);
  }
  const targetPosition = chargeModule.serialNumber;

  const dockingMetadata: DockingMetadata = {
    loadPosition: LoadingBay.MIDDLE,
    charge: true,
  };

  console.debug(`FTS CHARGE: Fts ${serialNumber} starts at position ${startPosition} to position ${targetPosition} to charge`);

  const newOrder: FtsOrder = NavigatorService.getFTSOrder(startPosition, targetPosition, orderId, 0, serialNumber, randomUUID());
  console.debug(JSON.stringify(newOrder, null, 2));

  newOrder.nodes
    .filter(node => node.action?.type === FtsCommandType.DOCK)
    .forEach(node => {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      node.action!.metadata = dockingMetadata;
    });

  const mqtt = getMqttClient();
  console.debug(`ORDER_MANAGEMENT: Publishing untracked charge order ${orderId} to ${getFtsTopic(serialNumber, FtsTopic.ORDER)}`);
  const blockedNodes = getBlockedNodesForOrder(newOrder);
  FactoryLayoutService.blockNodeSequence(blockedNodes);
  await mqtt.publish(getFtsTopic(serialNumber, FtsTopic.ORDER), JSON.stringify(newOrder));
  await ftsPairingStates.updateAvailability(
    serialNumber,
    AvailableState.BUSY,
    orderId,
    fts.lastNodeId,
    fts.lastModuleSerialNumber,
    dockingMetadata.loadPosition,
  );
  await pairingStates.updateAvailability(target, AvailableState.BUSY, orderId);
};

/**
 * Request the FTS to stop charging
 * @param serialNumber The serial number of the FTS to stop charging
 */
export const sendStopChargingInstantAction = async (serialNumber: string) => {
  const isCharging = FtsPairingStates.getInstance().isCharging(serialNumber);
  if (!isCharging) {
    console.warn(`FTS CHARGE: FTS ${serialNumber} can not stop charging: FTS is not charging`);
    return;
  }
  const stopCharging: InstantAction = {
    serialNumber,
    timestamp: new Date(),
    actions: [
      {
        actionId: randomUUID(),
        actionType: InstantActions.STOP_CHARGING,
      },
    ],
  };
  await getMqttClient().publish(getFtsTopic(serialNumber, FtsTopic.INSTANT_ACTION), JSON.stringify(stopCharging));
};

export const clearChargerQueue = () => {
  FTS_WAITING_FOR_RECHARGE.clear();
};
