import { PairedModule } from '../../../../common/protocol/ccu';
import { getMqttClient } from '../../mqtt/mqtt';
import { FtsTopic, getFtsTopic, getModuleTopic, ModuleTopic } from '../../../../common/protocol';
import { InstantAction, InstantActions } from '../../../../common/protocol/vda';
import { v4 as uuid } from 'uuid';

export async function requestFactsheet(module: PairedModule): Promise<void> {
  const mqtt = getMqttClient();
  let topic: string;
  switch (module.type) {
    case 'MODULE':
      topic = getModuleTopic(module.serialNumber, ModuleTopic.INSTANT_ACTION);
      break;
    case 'FTS':
      topic = getFtsTopic(module.serialNumber, FtsTopic.INSTANT_ACTION);
      break;
    default:
      throw Error('Unknown module type');
  }
  const action: InstantAction = {
    timestamp: new Date(),
    serialNumber: module.serialNumber,
    actions: [{ actionId: uuid(), actionType: InstantActions.FACTSHEET_REQUEST }],
  };
  return mqtt.publish(topic, JSON.stringify(action), { qos: 2 });
}
