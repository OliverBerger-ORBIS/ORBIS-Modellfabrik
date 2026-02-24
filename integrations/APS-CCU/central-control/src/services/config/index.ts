import { IClientSubscribeOptions } from 'async-mqtt';
import { CcuTopic } from '../../../../common/protocol';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { GeneralConfigService } from './general-config-service';
import { GeneralConfig } from '../../../../common/protocol/ccu';

export const TOPICS: string[] = [CcuTopic.SET_CONFIG];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 1,
};

export const handleMessage = async (message: string): Promise<void> => {
  const config = JSON.parse(message, jsonIsoDateReviver) as GeneralConfig;
  if ('productionDurations' in config) {
    await GeneralConfigService.saveConfig(config);
  }
};

export default handleMessage;
