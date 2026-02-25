import { IClientSubscribeOptions } from 'async-mqtt';
import { ANY_SERIAL, FtsTopic, getFtsTopic, getModuleTopic, ModuleTopic } from '../../../../common/protocol';
import { Factsheet } from '../../../../common/protocol/vda';
import { PairingStates } from '../pairing/pairing-states';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { sendPairingState } from '../pairing';
import { StockManagementService } from '../order/stock/stock-management-service';
import { ModuleType } from '../../../../common/protocol/module';
import { applyPendingStockForHbw } from '../production/cloud-stock';
import { FactoryLayoutService } from '../layout/factory-layout-service';
import { VersionPlausibilityService } from '../version-checker/version-plausibility-service';

export const TOPICS: string[] = [getModuleTopic(ANY_SERIAL, ModuleTopic.FACTSHEET), getFtsTopic(ANY_SERIAL, FtsTopic.FACTSHEET)];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 1,
};

export const handleMessage = async (message: string, topic: string): Promise<void> => {
  if (!message) {
    // Ignoring empty message
    return;
  }
  const facts = JSON.parse(message, jsonIsoDateReviver) as Factsheet;
  const modState = PairingStates.getInstance();
  const ftsState = FtsPairingStates.getInstance();
  await VersionPlausibilityService.registerModuleVersion(facts, false);
  if (topic.startsWith(ModuleTopic.ROOT)) {
    modState.updateFacts(facts);
    const moduleType = modState.getModuleType(facts.serialNumber);
    if (moduleType) {
      console.debug('REPLACING PLACEHOLDER: ' + moduleType);
      await FactoryLayoutService.replacePlaceholder(moduleType, facts.serialNumber);
    }
    StockManagementService.updateBaysFromModule(facts.serialNumber);
    if (modState.getModuleType(facts.serialNumber) === ModuleType.HBW) {
      await applyPendingStockForHbw(facts.serialNumber);
    }
  } else if (topic.startsWith(FtsTopic.ROOT)) {
    ftsState.updateFacts(facts);
  } else {
    console.error('Unknown topic: ' + topic);
    return;
  }
  return sendPairingState(modState, ftsState);
};
