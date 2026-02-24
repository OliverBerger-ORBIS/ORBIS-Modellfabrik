import { IClientSubscribeOptions } from 'async-mqtt';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { CcuTopic } from '../../../../common/protocol';
import { PairingStates } from '../pairing/pairing-states';
import { ModuleCalibration } from '../../../../common/protocol/ccu';
import { sendCalibrationInstantAction } from './calibration';

export const TOPICS: string[] = [CcuTopic.SET_MODULE_CALIBRATION];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

/**
 * Handle messages to dynamically configure module specific settings
 * @param message
 */
export const handleMessage = async (message: string): Promise<void> => {
  // TODO: FITEFF22-373 errors with the message format should be handled better
  const calibration = JSON.parse(message, jsonIsoDateReviver) as ModuleCalibration;
  const modState = PairingStates.getInstance();
  if (modState.get(calibration.serialNumber)) {
    console.debug(`CALIBRATION: Send calibration action to: ${calibration.serialNumber}`);
    return sendCalibrationInstantAction(calibration);
  }
};
