import { IClientSubscribeOptions } from 'async-mqtt';
import { ANY_SERIAL, FtsTopic, ModuleTopic, getFtsTopic, getModuleTopic } from '../../../../common/protocol';
import { FtsState } from '../../../../common/protocol/fts';
import { ModuleState } from '../../../../common/protocol/module';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import CurrentErrorsService from './current-errors.service';

export const CURRENT_ERRORS_TOPICS: string[] = [getModuleTopic(ANY_SERIAL, ModuleTopic.STATE), getFtsTopic(ANY_SERIAL, FtsTopic.STATE)];
export const CURRENT_ERRORS_TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

export const handleCurrentErrorsMessage = async (message: string): Promise<void> => {
  if (!message) {
    // ignore empty message
    return;
  }
  const actionState = JSON.parse(message, jsonIsoDateReviver) as ModuleState | FtsState;
  if (!actionState.serialNumber || !actionState.errors) {
    // ignore message with missing serialNumber or errors
    if (actionState.serialNumber) {
      CurrentErrorsService.getInstance().removeError(actionState.serialNumber);
    }
    return;
  }
  CurrentErrorsService.getInstance().addError(actionState.serialNumber, actionState.errors);
};
