import { IClientSubscribeOptions } from 'async-mqtt';
import { ANY_SERIAL, getModuleTopic, ModuleTopic } from '../../../../common/protocol';
import { Factsheet } from '../../../../common/protocol/vda';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { VersionPlausibilityService } from './version-plausibility-service';

export const TOPICS: string[] = [getModuleTopic('NodeRed/' + ANY_SERIAL, ModuleTopic.FACTSHEET)];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 1,
};

export const handleMessage = async (message: string): Promise<void> => {
  if (!message) {
    // Ignoring empty message
    return;
  }
  console.debug('TXT-24V: received factsheet');
  const facts = JSON.parse(message, jsonIsoDateReviver) as Factsheet;
  if (facts.serialNumber && facts.typeSpecification?.seriesName) {
    await VersionPlausibilityService.registerModuleVersion(facts, true);
  }
};
