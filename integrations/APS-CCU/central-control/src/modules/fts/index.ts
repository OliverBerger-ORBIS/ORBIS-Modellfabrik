import { IClientSubscribeOptions } from 'async-mqtt';
import { FtsState } from '../../../../common/protocol/fts';
import { ANY_SERIAL, FtsTopic, getFtsTopic } from '../../../../common/protocol';
import { handleFtsState } from './helper';
import { addFtsLogEntry } from '../state';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { OrderManagement } from '../order/management/order-management';

export const TOPICS: string[] = [getFtsTopic(ANY_SERIAL, FtsTopic.STATE)];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

export const handleMessage = async (message: string): Promise<void> => {
  const state = JSON.parse(message, jsonIsoDateReviver) as FtsState;
  await addFtsLogEntry(state);
  await handleFtsState(state);
  if (state.actionState?.id) {
    console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${state.orderId} and action id: ${state.actionState.id}`);
    return OrderManagement.getInstance().handleActionUpdate(state.orderId, state.actionState.id, state.actionState.state);
  }
};

export default handleMessage;
