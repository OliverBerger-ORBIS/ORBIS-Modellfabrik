import { IClientSubscribeOptions } from 'async-mqtt';
import { CcuTopic } from '../../../../../common/protocol';
import { jsonIsoDateReviver } from '../../../../../common/util/json.revivers';
import { ProductionFlows } from '../../../../../common/protocol/ccu';
import { OrderFlowService } from './order-flow-service';

export const TOPICS: string[] = [CcuTopic.SET_FLOWS];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

export const handleMessage = async (message: string): Promise<void> => {
  const flows = JSON.parse(message, jsonIsoDateReviver) as ProductionFlows;
  // Some basic check to verify that the received object is most likely a valid ProductionsFlows object
  if (flows) {
    console.debug('handleMessage: set flows to ', flows);
    OrderFlowService.setFlows(flows);
    const status = await Promise.allSettled([OrderFlowService.publishFlows(), OrderFlowService.saveFlows()]);
    if (status[0].status === 'rejected') {
      console.error('handleMessage: failed to publish flows: ', status[0].reason);
    }
    if (status[1].status === 'rejected') {
      console.error('handleMessage: failed to save flows: ', status[1].reason);
    }
  } else {
    console.error('handleMessage: set flows failed: Received object is not a valid ProductionFlows object: ', message);
  }
};

export default handleMessage;
