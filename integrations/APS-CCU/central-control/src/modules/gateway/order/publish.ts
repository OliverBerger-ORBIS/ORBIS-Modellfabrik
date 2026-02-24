import { OrderResponse } from '../../../../../common/protocol';
import { OrderState, Workpiece } from '../../../../../common/protocol/ccu';
import { GatewayOrder, GatewayOrderStateEnum, GatewayPublishTopics } from '../model';
import { getMqttClient } from '../../../mqtt/mqtt';

/**
 * Get the first order that has the given order state
 * @param orders
 * @param state
 */
const getFirstOrderWithState = (orders: OrderResponse[], state: OrderState): OrderResponse | undefined => {
  return orders.find(order => order.state === state);
};

/**
 * Publishes an overall order state for the given list of orders
 * The states are sent in this manner as an {@link GatewayOrderStateEnum}
 *  - `INPROCESS` - if any order is in progress
 *  - `ORDERED` - if no order is in progress but there is an enqueued order
 *  - `WAITINGFORORDER` - if no order is in process and none are enqueued
 *
 * @param orders
 */
export const publishGatewayOrderUpdate = async (orders: OrderResponse[]): Promise<void> => {
  let orderState = GatewayOrderStateEnum.WAITINGFORORDER;
  let type: Workpiece | undefined = undefined;

  // naive translation of the states of all orders to a singular state for the order component
  const order = getFirstOrderWithState(orders, OrderState.IN_PROGRESS) ?? getFirstOrderWithState(orders, OrderState.ENQUEUED);
  if (order) {
    type = order.type;
    switch (order.state) {
      case OrderState.IN_PROGRESS:
        orderState = GatewayOrderStateEnum.INPROCESS;
        break;
      case OrderState.ENQUEUED:
        orderState = GatewayOrderStateEnum.ORDERED;
        break;
    }
  }
  const gatewayOrder: GatewayOrder = {
    ts: new Date(),
    type,
    state: orderState,
  };
  return getMqttClient().publish(GatewayPublishTopics.ORDER_STATE, JSON.stringify(gatewayOrder), {
    retain: true, // all values displayed in the UI have to be retained in order to survive a reload
    qos: 1,
  });
};
