import { IClientSubscribeOptions } from 'async-mqtt';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { CcuTopic } from '../../../../common/protocol';
import { AvailableState, ResetRequest } from '../../../../common/protocol/ccu';
import { clearHBWContents, sendResetModuleInstantAction } from '../production/production';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { clearStock } from '../production/cloud-stock';
import { OrderManagement } from '../order/management/order-management';
import { sendResetFtsInstantAction } from '../fts/helper';
import { PairingStates } from '../pairing/pairing-states';
import { ModuleType } from '../../../../common/protocol/module';
import { clearChargerQueue } from '../fts/charge';
import { getMqttClient } from '../../mqtt/mqtt';
import { FactoryLayoutService } from '../layout/factory-layout-service';
import { clearAllParkRequests } from '../park';
import CurrentErrorsService from '../current-errors/current-errors.service';

export const TOPICS: string[] = [CcuTopic.SET_RESET];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

/**
 * Handle messages to reset the factory to an empty state
 *
 * - No orders pending
 * - No Workpieces in HBW or FTS
 * - No FTS within the layout
 * @param message
 */
export const handleMessage = async (message: string): Promise<void> => {
  const reset = JSON.parse(message, jsonIsoDateReviver) as ResetRequest;
  if (reset?.timestamp) {
    // clear all orders, including history
    await OrderManagement.getInstance().reinitialize();

    // clear storage, if requested by user
    if (reset?.withStorage) {
      // clear local stock cache
      await clearStock();
      // clear stock from all connected HBWs
      await clearHBWContents();
    }

    // clear queue of FTS waiting for charger
    clearChargerQueue();
    // clear blocked node list since all FTS must be re-docked to the DPS anyway
    FactoryLayoutService.releaseAllNodes();

    // send a reset to all fts
    const ftsPairingStates = FtsPairingStates.getInstance();
    for (const fts of ftsPairingStates.getAll()) {
      CurrentErrorsService.getInstance().removeError(fts.serialNumber);
      await sendResetFtsInstantAction(fts.serialNumber);
    }
    clearAllParkRequests();
    // send a reset to all modules
    const pairingStates = PairingStates.getInstance();
    for (const mod of pairingStates.getAll()) {
      if (mod.subType === ModuleType.CHRG) {
        await PairingStates.getInstance().updateAvailability(mod.serialNumber, AvailableState.READY);
      } else {
        CurrentErrorsService.getInstance().removeError(mod.serialNumber);
        await sendResetModuleInstantAction(mod.serialNumber);
      }
    }
    // reset node-red-flows
    await getMqttClient().publish(CcuTopic.GLOBAL, JSON.stringify({ type: 'reset' }), { qos: 2 });
  }
};
