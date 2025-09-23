"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleCancelOrders = exports.handleMessage = exports.validateStorageOrderRequestAndReserveBay = exports.TOPIC_OPTIONS_CANCEL_ORDER = exports.TOPICS_CANCEL_ORDER = exports.TOPIC_OPTIONS = exports.TOPICS = exports.sendResponse = exports.sortOrderSteps = exports.generateOrderStepList = void 0;
const protocol_1 = require("../../../../common/protocol");
const mqtt_1 = require("../../mqtt/mqtt");
const state_1 = require("../state");
const ccu_1 = require("../../../../common/protocol/ccu");
const order_management_1 = require("./management/order-management");
const uuid_1 = require("uuid");
const json_revivers_1 = require("../../../../common/util/json.revivers");
const pairing_states_1 = require("../pairing/pairing-states");
const module_1 = require("../../../../common/protocol/module");
const order_flow_service_1 = require("./flow/order-flow-service");
const cloud_stock_1 = require("../production/cloud-stock");
const stock_management_service_1 = require("./stock/stock-management-service");
const production_1 = require("../production/production");
const generateOrderStepList = (productionDefinition) => {
    let orderNavSteps = [];
    if (!!productionDefinition.navigationSteps) {
        orderNavSteps = productionDefinition.navigationSteps;
    }
    const orderProductionSteps = productionDefinition.productionSteps;
    const orderResponseSteps = [...orderNavSteps, ...orderProductionSteps];
    return (0, exports.sortOrderSteps)(orderResponseSteps);
};
exports.generateOrderStepList = generateOrderStepList;
/** Sort a list of Array<OrderNavigationStep | OrderManufactureStep> where the fist element has no dependentActionId and every other element as the id from the previous as dependentActionId */
const sortOrderSteps = (orderSteps) => {
    const resultList = [];
    const indepenentIds = [];
    const dependentSteps = [];
    orderSteps.forEach(step => {
        if (!step.dependentActionId) {
            indepenentIds.push(step.id);
            resultList.push(step);
        }
        else {
            dependentSteps.push(step);
        }
    });
    indepenentIds.forEach(actionId => {
        let nextStep = findNextDependentStep(actionId, dependentSteps);
        while (!!nextStep) {
            resultList.push(nextStep);
            nextStep = findNextDependentStep(nextStep.id, dependentSteps);
        }
    });
    return resultList;
};
exports.sortOrderSteps = sortOrderSteps;
const findNextDependentStep = (actionId, orderSteps) => {
    return orderSteps.find(nextStep => {
        return nextStep.dependentActionId === actionId;
    });
};
/**
 * Confirm the order by publishing a response to the mqtt topic /ccu/order/response
 * @param orderRequest the request that was received
 * @param orderId the generated order id
 * @param productionDefinition the production definition that was generated for the order
 */
const sendResponse = async (orderRequest, orderId, productionDefinition) => {
    const productionSteps = (0, exports.generateOrderStepList)(productionDefinition);
    const response = {
        orderType: orderRequest.orderType,
        type: orderRequest.type,
        timestamp: orderRequest.timestamp,
        orderId,
        productionSteps: productionSteps,
        receivedAt: new Date(),
        state: ccu_1.OrderState.ENQUEUED,
        workpieceId: orderRequest.workpieceId ? orderRequest.workpieceId : undefined,
        simulationId: orderRequest.simulationId,
    };
    await order_management_1.OrderManagement.getInstance().cacheOrder(response);
    console.debug('Confirm order: ', orderId);
    // TODO: What happens if this is null?
    await (0, state_1.addOrderLogEntry)(response);
    const mqtt = (0, mqtt_1.getMqttClient)();
    return mqtt.publish(protocol_1.CcuTopic.ORDER_RESPONSE, JSON.stringify(response));
};
exports.sendResponse = sendResponse;
exports.TOPICS = [protocol_1.CcuTopic.ORDER_REQUEST];
exports.TOPIC_OPTIONS = {
    qos: 2,
};
exports.TOPICS_CANCEL_ORDER = [protocol_1.CcuTopic.CANCEL_ORDERS];
exports.TOPIC_OPTIONS_CANCEL_ORDER = {
    qos: 2,
};
/**
 * Setting the DPS for a specific order to ready.
 * This is done to block it from any new orders, since the workpiece is still on the DPS, and it cannot process a new one
 * @param orderId the order id enable the DPS for
 */
const setDpsReadyForOrder = async (orderId) => {
    const paringStates = pairing_states_1.PairingStates.getInstance();
    const dps = paringStates.getForModuleType(module_1.ModuleType.DPS);
    if (!dps) {
        return;
    }
    await paringStates.updateAvailability(dps.serialNumber, ccu_1.AvailableState.READY, orderId);
};
/**
 * Validate a storage order request and try to reserve an empty storage bay.
 * @param productionDef
 * @param orderId
 * @param orderRequest
 * @return boolean that indicates the success of validation and bay reservation
 */
const validateStorageOrderRequestAndReserveBay = async (productionDef, orderId, orderRequest) => {
    if (!productionDef.navigationSteps?.length) {
        console.error('Storage order has no navigation steps configured, aborting ...');
        return false;
    }
    else if (!stock_management_service_1.StockManagementService.reserveEmptyBay(orderId, orderRequest.type)) {
        console.error('No empty storage bay available to create storage order for ' + orderRequest.type);
        return false;
    }
    return true;
};
exports.validateStorageOrderRequestAndReserveBay = validateStorageOrderRequestAndReserveBay;
/**
 * Handles all incoming order messages and responds on the respective response topic
 * @param message
 */
const handleMessage = async (message) => {
    const orderId = (0, uuid_1.v4)();
    const orderRequest = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    // load the production definition to trigger following actions
    const isProductionOrder = orderRequest.orderType === 'PRODUCTION';
    let productionDef;
    if (isProductionOrder) {
        productionDef = order_flow_service_1.OrderFlowService.getProductionDefinition(orderRequest.type);
        if (!productionDef.navigationSteps) {
            console.error('Production order has no navigation steps configured, aborting ...');
            return;
        }
        else if (!stock_management_service_1.StockManagementService.reserveWorkpiece(orderId, orderRequest.type)) {
            console.error('No workpiece available to create order for ' + orderRequest.type);
            return;
        }
    }
    else {
        // FITEFF22-592 Require empty HBW position. Send an instantAction to the DPS to discard the workpiece if the warehouse is full
        productionDef = order_flow_service_1.OrderFlowService.getStorageProductionDefinition();
        const valid = await (0, exports.validateStorageOrderRequestAndReserveBay)(productionDef, orderId, orderRequest);
        if (!valid) {
            // send the cancel request to have the DPS discard the workpiece when it cannot be stored
            await (0, production_1.sendCancelStorageOrder)(pairing_states_1.PairingStates.getInstance().getAllReady(module_1.ModuleType.DPS)[0]?.serialNumber);
            return;
        }
        // set the dps to blocked for any new order, because a workpiece is still on it
        await setDpsReadyForOrder(orderId);
    }
    await (0, exports.sendResponse)(orderRequest, orderId, productionDef);
    await (0, cloud_stock_1.publishStock)();
};
exports.handleMessage = handleMessage;
const handleCancelOrders = async (message) => {
    const orderIds = JSON.parse(message, json_revivers_1.jsonIsoDateReviver);
    await order_management_1.OrderManagement.getInstance().cancelOrders(orderIds);
};
exports.handleCancelOrders = handleCancelOrders;
exports.default = exports.handleMessage;
