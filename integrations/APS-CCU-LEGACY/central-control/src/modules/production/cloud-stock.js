"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.updateActiveWarehouses = exports.publishStock = exports.mapHbwToCloudStock = exports.handleStock = exports.clearStock = void 0;
const node_crypto_1 = require("node:crypto");
const protocol_1 = require("../../../../common/protocol");
const module_1 = require("../../../../common/protocol/module");
const mqtt_1 = require("../../mqtt/mqtt");
const stock_1 = require("../gateway/stock");
const order_management_1 = require("../order/management/order-management");
const stock_management_service_1 = require("../order/stock/stock-management-service");
const pairing_states_1 = require("../pairing/pairing-states");
const AVAILABLE_CLOUD_BAYS = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'];
/**
 * Clear the internal stock cache and publish the updated stock.
 */
const clearStock = async () => {
    const mqtt = (0, mqtt_1.getMqttClient)();
    const toPublish = {
        ts: new Date(),
        stockItems: [],
    };
    stock_management_service_1.StockManagementService.clearStock();
    await (0, stock_1.publishGatewayStock)(toPublish);
    await mqtt.publish(protocol_1.CcuTopic.STOCK, JSON.stringify(toPublish), { retain: true });
};
exports.clearStock = clearStock;
/**
 * Send the stock state to ccu/state/stock topic when an update from an HBW module is received.
 */
const handleStock = async (state) => {
    const pairingInstance = pairing_states_1.PairingStates.getInstance();
    const factsheet = pairingInstance.getFactsheet(state.serialNumber);
    if (factsheet?.typeSpecification.moduleClass !== module_1.ModuleType.HBW) {
        return;
    }
    console.debug(`CLOUD_STOCK: Update stock for HBW`);
    // cache the stock and send it to the cloud
    stock_management_service_1.StockManagementService.setStock(state.serialNumber, state.loads || []);
    await order_management_1.OrderManagement.getInstance().startNextOrder();
    try {
        await (0, exports.publishStock)();
    }
    catch (error) {
        console.error(error);
    }
};
exports.handleStock = handleStock;
/**
 * Map the stock state from the HBW module to the cloud stock state.
 * @param stock THe list of stored items
 * @param availableHbw THe available hbws. For all available HBWs unused bays are added as empty.
 */
const mapHbwToCloudStock = (stock, availableHbw) => {
    const toPublish = {
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
        const stockItem = {
            workpiece: {
                // the cloud expects a UUID as workpiece id or a string 'none'
                id: load.loadId ?? 'NONE' + (0, node_crypto_1.randomUUID)(),
                type: load.loadType,
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
exports.mapHbwToCloudStock = mapHbwToCloudStock;
const publishStock = async () => {
    const stock = stock_management_service_1.StockManagementService.getStock();
    const hbw = stock_management_service_1.StockManagementService.getWarehouses();
    const cloudStock = (0, exports.mapHbwToCloudStock)(stock, hbw);
    await (0, stock_1.publishGatewayStock)(cloudStock);
    await (0, mqtt_1.getMqttClient)().publish(protocol_1.CcuTopic.STOCK, JSON.stringify(cloudStock), { qos: 1, retain: true });
};
exports.publishStock = publishStock;
const updateActiveWarehouses = async () => {
    const hbw = pairing_states_1.PairingStates.getInstance()
        .getAllPaired(module_1.ModuleType.HBW)
        .map(data => data.serialNumber);
    stock_management_service_1.StockManagementService.setWarehouses(hbw);
    await (0, stock_1.publishWarehouses)();
    await (0, exports.publishStock)();
};
exports.updateActiveWarehouses = updateActiveWarehouses;
