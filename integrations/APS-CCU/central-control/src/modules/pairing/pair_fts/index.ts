import { IClientSubscribeOptions } from 'async-mqtt';
import { CcuTopic, FtsTopic, getFtsTopic } from '../../../../../common/protocol';
import { PairingStates } from '.././pairing-states';
import { getMqttClient } from '../../../mqtt/mqtt';
import { FtsPairingRequest, PairedModule } from '../../../../../common/protocol/ccu';
import { jsonIsoDateReviver } from '../../../../../common/util/json.revivers';
import { FtsPairingStates } from '.././fts-pairing-states';
import { FindInitialDockPositionMetadata, InstantAction, InstantActions } from '../../../../../common/protocol/vda';
import { randomUUID } from 'node:crypto';
import { ModuleType } from '../../../../../common/protocol/module';

export const TOPICS: string[] = [CcuTopic.PAIRING_PAIR_FTS];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

/**
 * Send the initial docking action to pair the FTS.
 *
 * This tells the FTS it is standing in front of the DPS and it should dock there to get into a known position.
 * If no DPS is connected and available in the layout, do nothing.
 * @param fts
 */
const sendFtsInitialDockingInstantAction = async (fts: PairedModule): Promise<void> => {
  const dps = PairingStates.getInstance().getForModuleType(ModuleType.DPS);
  if (!dps) {
    console.error(`Could not find a DPS to initiate the FTS docking sequence for ${fts.serialNumber}`);
    return;
  }

  const action: InstantAction = {
    timestamp: new Date(),
    serialNumber: fts.serialNumber,
    actions: [
      {
        actionType: InstantActions.FIND_INITIAL_DOCK_POSITION,
        actionId: randomUUID(),
        metadata: <FindInitialDockPositionMetadata>{
          nodeId: dps.serialNumber,
        },
      },
    ],
  };

  return getMqttClient().publish(getFtsTopic(fts.serialNumber, FtsTopic.INSTANT_ACTION), JSON.stringify(action), { qos: 2 });
};
/**
 * Receives the request to pair an fts and position it docked to the DPS.
 * @param message
 */
export const handleMessage = async (message: string): Promise<void> => {
  const request = JSON.parse(message, jsonIsoDateReviver) as FtsPairingRequest;
  const ftsState = FtsPairingStates.getInstance();
  const fts = ftsState.get(request.serialNumber);
  if (fts?.connected && !fts?.pairedSince) {
    await sendFtsInitialDockingInstantAction(fts);
  }
};
