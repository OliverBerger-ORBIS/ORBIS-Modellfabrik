import { IClientSubscribeOptions } from 'async-mqtt';
import { CcuTopic } from '../../../../common/protocol';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { FactoryLayoutService } from './factory-layout-service';
import { FactoryLayout } from '../../../../common/protocol/ccu';
import { OrderManagement } from '../order/management/order-management';
import { updateActiveWarehouses } from '../production/cloud-stock';

export const TOPICS: string[] = [CcuTopic.SET_LAYOUT];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

export const handleMessage = async (message: string): Promise<void> => {
  const layout = JSON.parse(message, jsonIsoDateReviver) as FactoryLayout;
  // Some basic check to verify that the received object is most likely a valid FactoryJsonLayout
  if ('roads' in layout && 'modules' in layout && 'intersections' in layout) {
    FactoryLayoutService.setLayout(layout);
    await FactoryLayoutService.saveLayout();
    await FactoryLayoutService.publishLayout();
    await updateActiveWarehouses();
    // try to resume orders and steps that were not possible with the old layout
    await OrderManagement.getInstance().resumeOrders();
  }
};

export default handleMessage;
