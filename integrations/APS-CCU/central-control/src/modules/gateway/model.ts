import { Workpiece } from '../../../../common/protocol';

export { Workpiece } from '../../../../common/protocol';

export const GW_LOCAL_CONTROLLER_ID = '1';

export const GW_LOCAL_CONTROLLER_TOPIC_BASE = `/j1/txt/${GW_LOCAL_CONTROLLER_ID}`;
export const GatewayPublishTopics = {
  ORDER_STATE: `${GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/i/order`,
  STOCK_TOPIC: `${GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/i/stock`,
  HBW_CONFIG_TOPIC: `${GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/i/config/hbw`,
};
export const GatewaySubscriptionTopics = {
  ALL_TOPICS: `${GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/o/#`,
  ORDER_TOPIC: `${GW_LOCAL_CONTROLLER_TOPIC_BASE}/f/o/order`,
};

export enum GatewayOrderStateEnum {
  WAITINGFORORDER = 'WAITING_FOR_ORDER',
  ORDERED = 'ORDERED',
  INPROCESS = 'IN_PROCESS',
  SHIPPED = 'SHIPPED',
}

export interface GatewayOrder {
  state?: GatewayOrderStateEnum;
  type?: Workpiece;
  /**
   * Timestamp to ISO8601
   */
  ts?: Date;
}

export interface GatewayHBWInfo {
  ts: Date; // iso date string
  warehouses: string[]; // ids of hbws
}
