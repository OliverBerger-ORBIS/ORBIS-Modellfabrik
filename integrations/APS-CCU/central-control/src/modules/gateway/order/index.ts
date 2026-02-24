import { CcuTopic, OrderRequest } from '../../../../../common/protocol';
import { IClientSubscribeOptions } from 'async-mqtt';
import { jsonIsoDateReviver } from '../../../../../common/util/json.revivers';
import { getMqttClient } from '../../../mqtt/mqtt';
import { GatewayOrder, GatewaySubscriptionTopics } from '../model';

export const TOPICS: string[] = [GatewaySubscriptionTopics.ORDER_TOPIC];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

export const handleMessage = async (message: string): Promise<void> => {
  const gatewayOrder = JSON.parse(message, jsonIsoDateReviver) as GatewayOrder;
  if (!(gatewayOrder && gatewayOrder.type && gatewayOrder.ts)) {
    console.debug('handleMessage for gateway: received invalid order: ', gatewayOrder);
    return;
  }
  const order: OrderRequest = {
    type: gatewayOrder.type,
    timestamp: gatewayOrder.ts,
    orderType: 'PRODUCTION',
  };
  return getMqttClient().publish(CcuTopic.ORDER_REQUEST, JSON.stringify(order), { qos: 2 });
};
