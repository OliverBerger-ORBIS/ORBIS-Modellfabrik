import { randomUUID } from 'node:crypto';
import { CcuTopic } from '../../../../common/protocol';
import { CloudStock, CloudStockItem } from '../../../../common/protocol/ccu';
import { ModuleState, ModuleType } from '../../../../common/protocol/module';
import { LoadType } from '../../../../common/protocol/vda';
import { getMqttClient } from '../../mqtt/mqtt';
import { publishGatewayStock, publishWarehouses } from '../gateway/stock';
import { OrderManagement } from '../order/management/order-management';
import { StockManagementService, StockStoredLoad } from '../order/stock/stock-management-service';
import { PairingStates } from '../pairing/pairing-states';

const AVAILABLE_CLOUD_BAYS = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];

/**
 * Clear the internal stock cache and publish the updated stock.
 */
export const clearStock = async () => {
  const mqtt = getMqttClient();
  const toPublish: CloudStock = {
    ts: new Date(),
    stockItems: [],
  };
  StockManagementService.clearStock();
  await publishGatewayStock(toPublish);
  await mqtt.publish(CcuTopic.STOCK, JSON.stringify(toPublish), { retain: true });
};

/**
 * Send the stock state to ccu/state/stock topic when an update from an HBW module is received.
 */
/** Cache last HBW state when it arrives before factsheet (MQTT ordering) */
const pendingHbwState = new Map<string, ModuleState>();

export const handleStock = async (state: ModuleState): Promise<void> => {
  const pairingInstance = PairingStates.getInstance();
  const factsheet = pairingInstance.getFactsheet(state.serialNumber);
  if (factsheet?.typeSpecification.moduleClass !== ModuleType.HBW) {
    if (state.serialNumber?.includes('HBW') && state.loads?.length) {
      pendingHbwState.set(state.serialNumber, state);
      console.log(`CLOUD_STOCK: Cached pending state for ${state.serialNumber} (factsheet not yet HBW)`);
    }
    return;
  }
  pendingHbwState.delete(state.serialNumber);
  const loads = state.loads || [];
  console.log(`CLOUD_STOCK: Update stock for HBW ${state.serialNumber}, loads=${loads.length}`);
  StockManagementService.setStock(state.serialNumber, loads);
  await OrderManagement.getInstance().startNextOrder();
  try {
    await publishStock();
  } catch (error) {
    console.error(error);
  }
};

/** Apply pending HBW state when factsheet arrives (handles MQTT message ordering) */
export const applyPendingStockForHbw = async (serialNumber: string): Promise<void> => {
  const state = pendingHbwState.get(serialNumber);
  if (state) {
    pendingHbwState.delete(serialNumber);
    console.log(`CLOUD_STOCK: Applying pending state for ${serialNumber}`);
    await handleStock(state);
  }
};

/**
 * Map the stock state from the HBW module to the cloud stock state.
 * @param stock THe list of stored items
 * @param availableHbw THe available hbws. For all available HBWs unused bays are added as empty.
 */
export const mapHbwToCloudStock = (stock: StockStoredLoad[], availableHbw: string[]): CloudStock => {
  const toPublish: CloudStock = {
    ts: new Date(),
    stockItems: [],
  };

  if (!stock) {
    return toPublish;
  }
  // change the load type to the workpiece type
  for (const stored of stock) {
    const load = stored.workpiece;
    if (!load.loadPosition) {
      console.log('CLOUD_STOCK: Incomplete load: ', load);
      continue;
    }
    const stockItem: CloudStockItem = {
      workpiece: {
        // the cloud expects a UUID as workpiece id or a string 'none'
        id: load.loadId ?? 'NONE' + randomUUID(),
        type: load.loadType as LoadType,
        state: stored.reserved ? 'RESERVED' : 'RAW',
      },
      location: load.loadPosition,
      hbw: stored.hbwSerial,
    };
    toPublish.stockItems.push(stockItem);
  }
  for (const serialNumber of availableHbw) {
    for (const location of AVAILABLE_CLOUD_BAYS) {
      if (!toPublish.stockItems.some(item => item.hbw === serialNumber && item.location === location)) {
        toPublish.stockItems.push({
          hbw: serialNumber,
          location: location,
          workpiece: undefined,
        });
      }
    }
  }
  return toPublish;
};

export const publishStock = async () => {
  const stock = StockManagementService.getStock();
  const hbw = StockManagementService.getWarehouses();
  const cloudStock = mapHbwToCloudStock(stock, hbw);
  await publishGatewayStock(cloudStock);
  await getMqttClient().publish(CcuTopic.STOCK, JSON.stringify(cloudStock), { qos: 1, retain: true });
};

export const updateActiveWarehouses = async () => {
  const hbw = PairingStates.getInstance()
    .getAllPaired(ModuleType.HBW)
    .map(data => data.serialNumber);
  StockManagementService.setWarehouses(hbw);
  await publishWarehouses();
  await publishStock();
};
