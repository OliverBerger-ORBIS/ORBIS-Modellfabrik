import { IClientSubscribeOptions } from 'async-mqtt';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { publishPairingState } from '../pairing';
import { CcuTopic } from '../../../../common/protocol';
import { PairingStates } from '../pairing/pairing-states';
import { ModuleSettings } from '../../../../common/protocol/ccu';

export const TOPICS: string[] = [CcuTopic.SET_MODULE_DURATION];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

/**
 * Handle messages to dynamically configure module specific settings
 * @param message
 */
export const handleMessage = async (message: string): Promise<void> => {
  // TODO: FITEFF22-373 errors with the message format should be handled better
  const duration = JSON.parse(message, jsonIsoDateReviver) as ModuleSettings;
  const modState = PairingStates.getInstance();
  if (modState.get(duration.serialNumber)) {
    console.debug(`Handle setting duration for: ${duration.serialNumber}`);
    modState.updateDuration(duration.serialNumber, duration.duration);
  }
  return publishPairingState();
};
