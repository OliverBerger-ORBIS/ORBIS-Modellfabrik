import { IClientSubscribeOptions } from 'async-mqtt';
import { jsonIsoDateReviver } from '../../../../../common/util/json.revivers';
import { CcuTopic } from '../../../../../common/protocol';
import { FtsChargeRequest, FtsPairedModule } from '../../../../../common/protocol/ccu';
import { FtsPairingStates } from '../../pairing/fts-pairing-states';
import { sendStopChargingInstantAction, triggerChargeOrderForFts } from '../charge';

export const TOPICS: string[] = [CcuTopic.SET_CHARGE];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

/**
 * Handle messages to charge an FTS
 * @param message
 */
export const handleMessage = async (message: string): Promise<void> => {
  const chargeRequest = JSON.parse(message, jsonIsoDateReviver) as FtsChargeRequest;
  if (!chargeRequest?.serialNumber) {
    console.error('Charge request is not valid');
    return;
  }

  const startCharge = chargeRequest.charge;
  const ftsSerialNumber = chargeRequest.serialNumber;
  const ftsPairingStates = FtsPairingStates.getInstance();
  const fts: FtsPairedModule | undefined = ftsPairingStates.get(ftsSerialNumber);
  if (fts == undefined) {
    console.error(`FTS with serial number ${ftsSerialNumber} is not paired`);
    return;
  }

  const isCharging = ftsPairingStates.isCharging(ftsSerialNumber);
  console.log(`Start charging: ${startCharge}, is charging: ${isCharging}, serialNumber: ${ftsSerialNumber}`);
  if (startCharge && !isCharging) {
    return triggerChargeOrderForFts(ftsSerialNumber, true);
  } else if (!startCharge && isCharging) {
    return sendStopChargingInstantAction(ftsSerialNumber);
  }

  // fallthrough when state of fts does not match the request, e.g. fts should go to charge but is already charging
  // Do not crash the CCU, just log the error because this should not happen, unless the interface is used manually
  console.error(`FTS with serial number ${ftsSerialNumber} is already charging: ${isCharging} and should not be charged: ${startCharge}`);
};
