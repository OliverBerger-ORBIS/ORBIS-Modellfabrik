import { IClientSubscribeOptions } from 'async-mqtt';
import { CcuTopic } from '../../../../../common/protocol';
import { jsonIsoDateReviver } from '../../../../../common/util/json.revivers';
import { FactoryLayoutService } from '../factory-layout-service';
import { DefaultLayoutRequest } from '../../../../../common/protocol/ccu';

export const TOPICS: string[] = [CcuTopic.SET_DEFAULT_LAYOUT];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

export const handleMessage = async (message: string): Promise<void> => {
  const layout = JSON.parse(message, jsonIsoDateReviver) as DefaultLayoutRequest;
  // Some basic check to verify that the received object is most likely a valid FactoryJsonLayout
  if (layout.timestamp) {
    await FactoryLayoutService.resetToDefaultLayout();
  }
};

export default handleMessage;
