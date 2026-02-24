import { GatewayHBWInfo, GatewayPublishTopics } from './model';
import { getMqttClient } from '../../mqtt/mqtt';
import { StockManagementService } from '../order/stock/stock-management-service';
import { CloudStock } from '../../../../common/protocol/ccu';

/**
 * Publish the given cloud stock to the local cloud gateway topics
 * @param stock
 */
export const publishGatewayStock = (stock: CloudStock): Promise<void> => {
  return getMqttClient().publish(GatewayPublishTopics.STOCK_TOPIC, JSON.stringify(stock), { qos: 1, retain: true });
};
export const publishWarehouses = async () => {
  const info: GatewayHBWInfo = {
    ts: new Date(),
    warehouses: StockManagementService.getWarehouses(),
  };
  await getMqttClient().publish(GatewayPublishTopics.HBW_CONFIG_TOPIC, JSON.stringify(info), { qos: 1, retain: true });
};
