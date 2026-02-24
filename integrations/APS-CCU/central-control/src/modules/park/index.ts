import { IClientSubscribeOptions } from 'async-mqtt';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { CcuTopic } from '../../../../common/protocol';
import { ModuleCalibrationCommand, ParkRequest } from '../../../../common/protocol/ccu';
import { PairingStates } from '../pairing/pairing-states';
import { ModuleType } from '../../../../common/protocol/module';
import { sendCalibrationInstantAction } from '../calibration/calibration';

export const TOPICS: string[] = [CcuTopic.SET_PARK];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

export const parkRequests = new Set<string>();

/**
 * Handle messages to park the factory
 *
 * - Set all HBW, DPS in calibration mode
 * - Set all DPS, HBW in park position
 * @param message
 */
export const handleMessage = async (message: string): Promise<void> => {
  const park = JSON.parse(message, jsonIsoDateReviver) as ParkRequest;
  if (park?.timestamp) {
    // send a calibration/park to all modules
    const pairingStates = PairingStates.getInstance();
    const modulesDpsHbw = [...pairingStates.getAllPaired(ModuleType.DPS), ...pairingStates.getAllPaired(ModuleType.HBW)];
    for (const mod of modulesDpsHbw) {
      parkRequests.add(mod.serialNumber);
      await sendCalibrationInstantAction({
        timestamp: new Date(),
        serialNumber: mod.serialNumber,
        command: ModuleCalibrationCommand.START,
        position: 'PARK',
      });
    }
  }
};

export const checkAndSendParkRequests = async (serialNumber: string) => {
  if (!parkRequests.has(serialNumber)) {
    return;
  }
  parkRequests.delete(serialNumber);
  await sendCalibrationInstantAction({
    timestamp: new Date(),
    serialNumber: serialNumber,
    command: ModuleCalibrationCommand.SELECT,
    position: 'PARK',
  });
};

export const clearParkRequest = (serialNumber: string) => {
  parkRequests.delete(serialNumber);
};
export const clearAllParkRequests = () => {
  parkRequests.clear();
};
