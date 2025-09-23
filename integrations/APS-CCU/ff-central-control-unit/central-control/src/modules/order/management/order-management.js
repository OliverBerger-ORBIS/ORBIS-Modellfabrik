"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderManagement = void 0;
const protocol_1 = require("../../../../../common/protocol");
const mqtt_1 = require("../../../mqtt/mqtt");
const ccu_1 = require("../../../../../common/protocol/ccu");
const navigation_1 = require("../../fts/navigation/navigation");
const production_1 = require("../../production/production");
const vda_1 = require("../../../../../common/protocol/vda");
const module_1 = require("../../../../../common/protocol/module");
const index_1 = require("../index");
const pairing_states_1 = require("../../pairing/pairing-states");
const publish_1 = require("../../gateway/order/publish");
const models_1 = require("../../../models/models");
const fts_pairing_states_1 = require("../../pairing/fts-pairing-states");
const order_flow_service_1 = require("../flow/order-flow-service");
const node_crypto_1 = require("node:crypto");
const helper_1 = require("../../production/helper");
const stock_management_service_1 = require("../stock/stock-management-service");
const cloud_stock_1 = require("../../production/cloud-stock");
const uuid_1 = require("uuid");
const general_config_service_1 = require("../../../services/config/general-config-service");
class OrderManagement {
    static getInstance() {
        if (!OrderManagement.instance) {
            OrderManagement.instance = new OrderManagement();
        }
        return OrderManagement.instance;
    }
    constructor() {
        this.navStepsToExecute = [];
        this.manufactureStepsToExecute = [];
        this.orderQueue = new Array();
        this.activeOrders = new Array();
        this.completedOrders = new Array();
        this.pairingStates = pairing_states_1.PairingStates.getInstance();
        this.ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
    }
    /**
     * Reinitialize the order management and clear all orders
     */
    async reinitialize() {
        this.orderQueue = [];
        this.activeOrders = [];
        this.completedOrders = [];
        this.navStepsToExecute = [];
        this.manufactureStepsToExecute = [];
        this.pairingStates = pairing_states_1.PairingStates.getInstance();
        this.ftsPairingStates = fts_pairing_states_1.FtsPairingStates.getInstance();
        await this.sendOrderListUpdate();
        await this.sendCompletedOrderListUpdate();
        stock_management_service_1.StockManagementService.removeAllReservations();
    }
    /**
     * Publishes the current order list to the broker
     */
    async sendOrderListUpdate() {
        const mqtt = (0, mqtt_1.getMqttClient)();
        if (!mqtt) {
            return Promise.resolve();
        }
        await (0, publish_1.publishGatewayOrderUpdate)(this.orderQueue);
        return await mqtt.publish(protocol_1.CcuTopic.ACTIVE_ORDERS, JSON.stringify(this.orderQueue), { qos: 2, retain: true });
    }
    async sendCompletedOrderListUpdate() {
        const mqtt = (0, mqtt_1.getMqttClient)();
        if (!mqtt) {
            return await Promise.resolve();
        }
        return await mqtt.publish(protocol_1.CcuTopic.COMPLETED_ORDERS, JSON.stringify(this.completedOrders), { qos: 2, retain: true });
    }
    async cacheOrder(order) {
        this.orderQueue.push(order);
        await this.startOrder(order);
        return this.sendOrderListUpdate();
    }
    /** Start an order */
    startOrder(order) {
        const maxParallelOrders = general_config_service_1.GeneralConfigService.config.productionSettings.maxParallelOrders;
        if (this.activeOrders.length >= maxParallelOrders && order.orderType === 'PRODUCTION') {
            // StorageOrders should always be possbile
            console.debug('ORDER_MANAGEMENT: Maximum number of parallel orders reached, not starting Order with id: ' + order.orderId);
            return Promise.resolve();
        }
        // only start the order if a workpiece / empty bay can be reserved.
        if (order.orderType === 'PRODUCTION' && !stock_management_service_1.StockManagementService.reserveWorkpiece(order.orderId, order.type)) {
            return Promise.resolve();
        }
        else if (order.orderType === 'STORAGE' && !stock_management_service_1.StockManagementService.reserveEmptyBay(order.orderId, order.type)) {
            return Promise.resolve();
        }
        console.debug(`ORDER_MANAGEMENT: Starting order  ${order.orderId}`);
        this.activeOrders.push(order);
        order.state = ccu_1.OrderState.IN_PROGRESS;
        order.startedAt = new Date();
        const independentActionList = order.productionSteps
            .filter(step => !step.dependentActionId)
            .filter(step => step.state === ccu_1.OrderState.ENQUEUED)
            .map((value, index) => ({
            index,
            value,
            orderId: order.orderId,
            workpiece: order.type,
            workpieceId: order.workpieceId,
        }));
        return this.triggerIndependentActions(order, independentActionList);
    }
    /**
     * Determine the target module for a navigation action
     * @param actionId
     * @returns the target
     */
    getTargetModuleTypeForNavActionId(actionId) {
        const combinedOrders = [...this.completedOrders, ...this.orderQueue];
        for (const order of combinedOrders) {
            const dockStep = order.productionSteps.find(step => step.id === actionId);
            if (dockStep && dockStep.type === 'NAVIGATION') {
                // TODO: FITEFF22-262 Change to serial number to allow multiple modules
                console.debug(`Found Id: ${dockStep.id} with target: ${dockStep.target}`);
                return dockStep.target;
            }
        }
        return undefined;
    }
    addIfNotPresent(list, newEntry) {
        const present = list.find(entry => entry.value.id === newEntry.value.id);
        if (present) {
            return;
        }
        console.log('ORDER_MANAGEMENT: Adding new entry to list: ', newEntry);
        list.push(newEntry);
    }
    // TODO: Verify this actually does what it is supposed to
    async triggerIndependentActions(order, independentActionList) {
        independentActionList.filter(step => step.value.type === 'NAVIGATION').map(step => this.addIfNotPresent(this.navStepsToExecute, step));
        for (const step of independentActionList.filter(step => step.value.type === 'MANUFACTURE')) {
            const action = step.value;
            if (action.command === module_1.ModuleCommandType.DROP) {
                await this.handleNextActionDrop(order, step);
            }
            else {
                this.addIfNotPresent(this.manufactureStepsToExecute, step);
            }
        }
        await this.triggerNavigationSteps();
        await this.triggerManufactureSteps();
    }
    /**
     * Generates the actual next action if the action to be executed equals a drop action.
     * The result can either be a navigation if there is not fts docked at the module or a manufacture action if the fts is docked at the correct module.
     * @param order the order of the action is associated with
     * @param step the step to be executed
     * @private
     */
    async handleNextActionDrop(order, step) {
        const action = await this.generateNextActionForDrop(order, step.value);
        if (action.value.type === 'NAVIGATION') {
            this.addIfNotPresent(this.navStepsToExecute, action);
        }
        else {
            this.addIfNotPresent(this.manufactureStepsToExecute, action);
        }
    }
    /**
     * Check that a workpiece is available when driving to the storage.
     * An FTS either already has a workpiece and deliver it workpiece or
     * or it receives it from the storage and it has to be available and reserved.
     * @param step
     * @private
     * @returns true if the target is the storage and the order has no assigned workpiece
     */
    isStorageTargetWithoutAvailableWorkpiece(step) {
        if (step.value.type !== 'NAVIGATION' || step.value.target !== module_1.ModuleType.HBW) {
            return false;
        }
        if (step.workpieceId) {
            return false;
        }
        return !stock_management_service_1.StockManagementService.reserveWorkpiece(step.orderId, step.workpiece);
    }
    /**
     * Check that an empty storage bay is available when driving to the storage with a workpiece
     * Try to reserve an empty bay if necessary.
     * @param step
     * @private
     * @returns true if the target is the storage and the order has no assigned bay for its workpiece
     */
    isStorageTargetWithoutAvailableBay(step) {
        if (step.value.type !== 'NAVIGATION' || step.value.target !== module_1.ModuleType.HBW) {
            return false;
        }
        if (!step.workpieceId) {
            return false;
        }
        return !stock_management_service_1.StockManagementService.reserveEmptyBay(step.orderId, step.workpiece);
    }
    /**
     * Choose the correct FTS for an order step
     * @param orderId
     * @param targetId
     * @param nav
     * @private
     */
    chooseReadyFtsForStep(orderId, targetId, nav) {
        const order = this.getActiveOrder(orderId);
        console.log('order found that needs navigation: ', order);
        if (!order) {
            return undefined;
        }
        return (0, navigation_1.selectFtsPathForStep)(order, targetId, nav);
    }
    getActiveOrder(orderId) {
        return this.activeOrders.find(o => o.orderId === orderId);
    }
    /**
     * Choose the module target for a navigation step.
     * If an order has a reserved workpiece when navigating to an HBW, then select that HBW.
     * If an order is currently assigned to a module, then use that module and fail if the module type does not match
     * If nothing applies, choose module that is ready to accept this order.
     * @param orderId
     * @param targetType
     * @private
     */
    chooseModuleForNavigationTarget(orderId, targetType) {
        if (targetType === module_1.ModuleType.HBW) {
            const serialNumber = stock_management_service_1.StockManagementService.getReservedWarehouse(orderId);
            if (serialNumber && this.pairingStates.get(serialNumber)) {
                console.log(`ORDER_MANAGEMENT: Navigation to the warehouse with the reserved workpiece for ${orderId}: ${serialNumber}`);
                return this.pairingStates.get(serialNumber);
            }
        }
        console.log(`ORDER_MANAGEMENT: Finding Navigation target module currently assigned to the order ${orderId} and target type: ${targetType}`);
        const orderTarget = this.pairingStates.getModuleForOrder(orderId);
        console.log(`ORDER_MANAGEMENT: Found order target ${JSON.stringify(orderTarget)}`);
        // An assigned target was found, return that
        if (orderTarget && orderTarget.subType === targetType) {
            console.log(`ORDER_MANAGEMENT: Navigation to the module currently assigned to the order ${orderId}: ${orderTarget.serialNumber}`);
            return orderTarget;
        }
        // An assigned target was found, but the subtype is invalid. Try to look again (maybe there are duplicate assignments
        if (orderTarget && orderTarget.subType !== targetType) {
            console.log(`ORDER_MANAGEMENT: Assigned module is of the wrong type for ${orderId}. Expected ${targetType} but got ${orderTarget.subType}`);
            const orderTargetModule = this.pairingStates.getModuleForOrder(orderId, targetType);
            if (orderTargetModule) {
                console.warn(`ORDER_MANAGEMENT: Found module of the correct type for ${orderId}: ${orderTargetModule.serialNumber}
          This indicates that some module was still assigned to an order which should not happen.`);
                return orderTargetModule;
            }
        }
        // choose a ready unassigned module if the order has no module assigned.
        const target = this.pairingStates.getReadyForModuleType(targetType, orderId);
        if (target) {
            return target;
        }
    }
    async triggerNavigationSteps() {
        // only trigger steps which are not in progress
        let triggeredSteps = 0;
        const unTriggeredNav = this.navStepsToExecute.filter(step => step.value.state === ccu_1.OrderState.ENQUEUED);
        const availableFtsIds = new Set(this.ftsPairingStates.getAllReadyUnassigned().map(fts => fts.state.serialNumber));
        const blockedModules = [];
        for (const step of unTriggeredNav) {
            try {
                if (step.value.type !== 'NAVIGATION') {
                    console.log('ORDER_MANAGEMENT: Wrong step type assigned to navigation step array');
                    continue;
                }
                const nav = step.value;
                // only try to navigate to the HBW for an order when we have a workpiece or can reserve one.
                if (this.isStorageTargetWithoutAvailableWorkpiece(step)) {
                    console.log('ORDER_MANAGEMENT: No workpiece available for order : ' + step.orderId);
                    continue;
                }
                // only try to navigate to the HBW for a STORAGE order if we can store the workpiece in an empty bay.
                if (this.isStorageTargetWithoutAvailableBay(step)) {
                    console.log('ORDER_MANAGEMENT: No empty storage bay available for order : ' + step.orderId);
                    continue;
                }
                // find module that exists for order
                const target = this.chooseModuleForNavigationTarget(step.orderId, nav.target);
                if (!target) {
                    console.log('ORDER_MANAGEMENT: No module ready for order : ' + step.orderId);
                    continue;
                }
                else if (!this.pairingStates.isReadyForOrder(target.serialNumber, step.orderId)) {
                    console.log(`ORDER_MANAGEMENT: Chosen module ${target.serialNumber} for order ${step.orderId} is not ready`);
                    continue;
                }
                const ftsPath = this.chooseReadyFtsForStep(step.orderId, target.serialNumber, nav);
                console.log('ftspath: ', ftsPath);
                if (!ftsPath || !ftsPath.path) {
                    console.log('ORDER_MANAGEMENT: No FTS with free path ready for order: ' + step.orderId);
                    const fts = this.ftsPairingStates.getFtsAtPosition(target.serialNumber);
                    if (fts) {
                        console.log(`ORDER_MANAGEMENT: FTS ${fts.serialNumber} is blocking module ${target.serialNumber}`);
                        blockedModules.push({
                            ftsSerial: fts.serialNumber,
                            moduleSerial: target.serialNumber,
                        });
                    }
                    continue;
                }
                const fts = ftsPath.fts;
                // Setting the state to in progress will prevent the step from being triggered again
                step.value.state = ccu_1.OrderState.IN_PROGRESS;
                await (0, navigation_1.sendNavigationRequest)(nav, step.orderId, step.index, step.workpiece, step.workpieceId, fts, target.serialNumber);
                // send the active output to the DPS
                if (nav.target === module_1.ModuleType.DPS && this.getNextStepCommand(step) === module_1.ModuleCommandType.PICK) {
                    await (0, production_1.sendAnnounceDpsOutput)(target.serialNumber, step.orderId, step.workpiece);
                }
                availableFtsIds.delete(fts.serialNumber);
                console.debug(`sending nav command for order: ${step.orderId} source: ${nav.source} target: ${nav.target}`);
                this.navStepsToExecute.splice(this.navStepsToExecute.indexOf(step), 1);
                // log the time the command was sent as the start time of this step
                nav.startedAt = new Date();
                triggeredSteps++;
                // remove the return command allowing only a single order.
                // the FTS is now assigned to the order and cannot be reused.
                // that makes it possible to start the next order with the next FTS.
            }
            catch (e) {
                if (e instanceof models_1.FTSNotReadyError) {
                    console.warn(`FTS not ready order: ${step.orderId} action: ${step.value.id} message: ${e.message}`);
                }
                else {
                    console.warn('Error while sending navigation request', e);
                }
                // if an error occurs, we set the state back to enqueued to try again later
                step.value.state = ccu_1.OrderState.ENQUEUED;
            }
        }
        // After all possible normal navigation orders are sent look for modules that are blocked by an FTS and move those.
        for (const blocked of blockedModules) {
            if (availableFtsIds.has(blocked.ftsSerial)) {
                try {
                    await (0, navigation_1.sendClearModuleNodeNavigationRequest)(blocked.moduleSerial);
                    availableFtsIds.delete(blocked.ftsSerial);
                }
                catch (e) {
                    // If an error occurs, continue and wait
                    console.warn(`Error while sending navigation request to ${blocked.ftsSerial} to clear module ${blocked.moduleSerial}`, e);
                }
            }
        }
        return triggeredSteps;
    }
    /**
     * Skips the current navigation step and directly start the manufacture
     * @param step
     * @param order
     * @param nextStep manufacture step
     * @param fts
     * @throws FTSNotReadyError
     * @private
     */
    async skipNavStepAndStartDrop(step, order, nextStep, fts) {
        if (!fts.lastLoadPosition || !fts.lastModuleSerialNumber || step.value.type !== 'NAVIGATION') {
            return;
        }
        if (!this.ftsPairingStates.isLoadingBayFree(fts.serialNumber, fts.lastLoadPosition) &&
            // allow the loading bay to be filled/reserved by the same orderId
            this.ftsPairingStates.getLoadingBayForOrder(fts.serialNumber, order.orderId) !== fts.lastLoadPosition) {
            throw new models_1.FTSNotReadyError(`FTS ${fts.serialNumber} is docked, but loading bay ${fts.lastLoadPosition} is occupied`);
        }
        if (!this.pairingStates.isReadyForOrder(fts.lastModuleSerialNumber, order.orderId)) {
            throw new models_1.ControllerNotReadyError('MODULE', nextStep.moduleType, `Module with workpiece is not ready to drop`);
        }
        step.value.startedAt = new Date();
        step.value.stoppedAt = new Date();
        step.value.state = ccu_1.OrderState.FINISHED;
        this.navStepsToExecute.splice(this.navStepsToExecute.indexOf(step), 1);
        const nextStepIndex = order.productionSteps.indexOf(nextStep);
        this.ftsPairingStates.setLoadingBay(fts.serialNumber, fts.lastLoadPosition, order.orderId);
        await this.ftsPairingStates.updateAvailability(fts.serialNumber, ccu_1.AvailableState.READY, order.orderId);
        const nextStepAction = this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
        // block the target for the current order so that the command can be sent to the correct one and no other order can use it
        await this.pairingStates.updateAvailability(fts.lastModuleSerialNumber, ccu_1.AvailableState.READY, order.orderId);
        this.manufactureStepsToExecute.push(nextStepAction);
        await this.triggerOneManufactureStep(nextStepAction);
    }
    async triggerManufactureSteps() {
        let triggeredSteps = 0;
        const unTriggeredManufacture = this.manufactureStepsToExecute.filter(step => step.value.state === ccu_1.OrderState.ENQUEUED);
        for (const step of unTriggeredManufacture) {
            if (await this.triggerOneManufactureStep(step)) {
                triggeredSteps++;
            }
        }
        return triggeredSteps;
    }
    async triggerOneManufactureStep(step) {
        let result = false;
        try {
            const prod = step.value;
            const pairedModule = pairing_states_1.PairingStates.getInstance().getReadyForModuleType(prod.moduleType, step.orderId);
            if (!pairedModule) {
                console.warn(`Module for action of type ${step.value.moduleType} is not ready. Retrying later`);
                return false;
            }
            const serialNumber = pairedModule.serialNumber;
            step.value.state = ccu_1.OrderState.IN_PROGRESS;
            // generate metadata for the command and add it as parameter to sendProductionCommand
            const metadata = this.generateMetadataForProductionCommand(prod, pairedModule, step.workpiece, step.workpieceId);
            await (0, production_1.sendProductionCommand)(prod, step.orderId, step.index, pairedModule, metadata);
            console.debug(`COMMAND_SENDING: manufacturing nav command for order: ${step.orderId} module: ${prod.moduleType} command: ${prod.command} workpieceId: ${step.workpieceId}`);
            const stepIndex = this.manufactureStepsToExecute.indexOf(step);
            if (stepIndex >= 0) {
                this.manufactureStepsToExecute.splice(stepIndex, 1);
            }
            // log the time the command was sent as the start time of this step
            prod.startedAt = new Date();
            // remember the module that was chosen for this step
            prod.serialNumber = serialNumber;
            result = true;
        }
        catch (e) {
            console.warn(`Module for action of type ${step.value.moduleType} is not ready. Retrying`, e);
            step.value.state = ccu_1.OrderState.ENQUEUED;
        }
        return result;
    }
    generateMetadataForProductionCommand(productionStep, pairedModule, workpiece, workpieceId) {
        if (productionStep.moduleType === module_1.ModuleType.DPS && workpieceId) {
            // in case of DPS generate the workpiece production history
            return this.generateDpsMetadata(workpiece, workpieceId);
        }
        return (0, helper_1.metadataForCommand)(productionStep.moduleType, productionStep.command, pairedModule, workpiece, workpieceId);
    }
    generateDpsMetadata(workpiece, workpieceId) {
        const history = [];
        // history ts ist der timestamp von end of the process
        [...this.orderQueue, ...this.completedOrders]
            .filter(order => order.workpieceId === workpieceId)
            .map(order => {
            order.productionSteps
                .filter(step => step.type === 'MANUFACTURE')
                .map(step => step)
                .filter(step => step.state === ccu_1.OrderState.FINISHED)
                .forEach(step => {
                const nfcPosition = (0, module_1.getNfcPosition)(step.moduleType, step.command);
                if (!nfcPosition) {
                    return;
                }
                history.push({
                    // we filter for finished steps a few lines above, so we can be sure that stoppedAt is set
                    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                    ts: step.stoppedAt.getTime(),
                    code: nfcPosition,
                });
            });
        });
        console.debug(`ORDER_MANAGEMENT: Building history for workpieceId: ${workpieceId} history:`, history);
        return {
            workpiece: {
                workpieceId,
                type: workpiece,
                history: history,
                state: 'PROCESSED',
            },
        };
    }
    async handleActionUpdate(orderId, actionId, state, result) {
        // if the action is not finished or failed don't do anything. Errors have to be rest manually on the
        // FTS/Module which will delete the order completely
        console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} and action id: ${actionId} and state: ${state}`);
        if (state !== vda_1.State.FINISHED && state !== vda_1.State.FAILED) {
            return Promise.resolve();
        }
        const activeOrder = this.activeOrders.find(order => order.orderId === orderId);
        if (!activeOrder) {
            console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} no active order found`);
            return Promise.resolve();
        }
        const step = activeOrder.productionSteps.find(step => step.id === actionId);
        if (!step) {
            console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} no step found for id: ${actionId}`);
            return Promise.resolve();
        }
        if (step.state !== ccu_1.OrderState.IN_PROGRESS && step.state !== ccu_1.OrderState.ENQUEUED) {
            console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} steps has already been handled for id: ${actionId}`);
            return Promise.resolve();
        }
        // log the first time the finished or error status has been received for an action
        if (!step.stoppedAt) {
            step.stoppedAt = new Date();
        }
        if (state === vda_1.State.FAILED) {
            // a failed action will only set the error state. The error has to be cleared on the fts/module
            console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} set error for id: ${actionId}`);
            step.state = ccu_1.OrderState.ERROR;
            return this.sendOrderListUpdate();
        }
        else {
            step.state = ccu_1.OrderState.FINISHED;
        }
        if (this.isQualityCheckFailure(step, result)) {
            return this.handleActionUpdateQualityCheckFailure(activeOrder, step);
        }
        if (this.isStoragePickDrop(step)) {
            stock_management_service_1.StockManagementService.removeReservation(orderId);
            await (0, cloud_stock_1.publishStock)();
            // start next order if possible
            await this.startNextOrder();
        }
        const stepIndex = activeOrder.productionSteps.indexOf(step);
        // if step is last step in order, remove order from queue and start next order
        if (stepIndex === activeOrder.productionSteps.length - 1) {
            console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} action: ${actionId} is the last step in order. Starting next one if present`);
            activeOrder.state = ccu_1.OrderState.FINISHED;
            await this.deleteFinishedOrders(activeOrder);
            // try to resume existing orders
            await this.retriggerFTSSteps();
            await this.startNextOrder();
        }
        else {
            console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} starting next step in order`);
            await this.startNextStep(activeOrder, step);
        }
        return this.sendOrderListUpdate();
    }
    /**
     * Handle the case of an unsatisfactory quality check.
     *
     * If the quality check fails the workpiece, then it is discarded
     * and a new workpiece is commissioned and attached to the order
     *
     * @param order The order that contains the step
     * @param step The quality control step that failed
     * @returns `true` if the step was handled, `false` if the step is still unhandled
     * @private
     */
    async handleActionUpdateQualityCheckFailure(order, step) {
        // set the AIQS availability to available for any order, since the workpiece will be discarded and is no longer on the module itself
        this.pairingStates.clearModuleForOrder(order.orderId);
        step.state = ccu_1.OrderState.ERROR;
        // cancel the remaining order steps
        this.cancelRemainingSteps(order, step);
        // as of FITEFF22-657 create a new order instead of updating the old one.
        order.state = ccu_1.OrderState.ERROR;
        await this.deleteFinishedOrders(order);
        const orderRequest = {
            orderType: order.orderType,
            type: order.type,
            timestamp: order.timestamp,
            simulationId: order.simulationId,
        };
        const response = await this.createOrder(orderRequest);
        console.debug(`QUALITY_FAILURE: Replacing order ${order.orderId} with new order ${response?.orderId ?? 'FAILED'}`);
    }
    async createOrder(orderRequest) {
        const orderId = (0, uuid_1.v4)();
        const productionDefinition = order_flow_service_1.OrderFlowService.getProductionDefinition(orderRequest.type);
        if (!productionDefinition.navigationSteps) {
            console.error('Production order has no navigation steps configured, aborting ...');
            return null;
        }
        else if (!stock_management_service_1.StockManagementService.reserveWorkpiece(orderId, orderRequest.type)) {
            console.error('No workpiece available to create order for ' + orderRequest.type);
            return null;
        }
        const productionSteps = (0, index_1.generateOrderStepList)(productionDefinition);
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
        await this.cacheOrder(response);
        return response;
    }
    /**
     * Checks if the given step is a quality control action that failed the quality check
     * @param step The step to check
     * @param result The result of the action triggered by the step
     */
    isQualityCheckFailure(step, result) {
        return (step &&
            step.type === 'MANUFACTURE' &&
            step.moduleType === module_1.ModuleType.AIQS &&
            step.command === module_1.ModuleCommandType.CHECK_QUALITY &&
            result === module_1.QualityResult.FAILED);
    }
    /**
     * Checks if the given step is a storage pick or drop action
     * @param step The step to check
     */
    isStoragePickDrop(step) {
        if (!step || step.type !== 'MANUFACTURE' || step.moduleType !== module_1.ModuleType.HBW) {
            return false;
        }
        return step.command === module_1.ModuleCommandType.DROP || step.command === module_1.ModuleCommandType.PICK;
    }
    /**
     * Generate the production steps necessary to produce a new workpiece when the FTS is docked at AIQS
     * @param type the workpiece type to produce again
     * @returns all steps to send the FTS to the start and produce the workpiece
     * @private
     */
    generateReproductionOrderSteps(type) {
        const productionDefinition = order_flow_service_1.OrderFlowService.getProductionDefinition(type);
        return (0, index_1.generateOrderStepList)(productionDefinition);
    }
    /**
     * Cancel all remaining actions of an order.
     *
     * This should be done when the result of a step indicates that the order cannot be continued further.
     *
     * @param order The order that contains the step
     * @param step The last step that is not cancelled, usually a failed step
     * @private
     */
    cancelRemainingSteps(order, step) {
        const stepIndex = order.productionSteps.indexOf(step);
        if (stepIndex < 0) {
            return;
        }
        // cancel all following steps
        const nextStepIndex = stepIndex + 1;
        for (const nextStep of order.productionSteps.slice(nextStepIndex)) {
            nextStep.state = ccu_1.OrderState.CANCELLED;
        }
        console.debug(`Cancelled remaining steps for order ${order.orderId}`);
    }
    async startNextStep(order, step) {
        step.state = ccu_1.OrderState.FINISHED;
        const nextStep = order.productionSteps.find(nextStep => nextStep.dependentActionId === step.id);
        if (!nextStep) {
            console.debug(`ORDER_MANAGEMENT: start next step for orderId: ${order.orderId} no next step found`);
            return Promise.resolve();
        }
        if (nextStep.state !== ccu_1.OrderState.ENQUEUED) {
            console.debug(`ORDER_MANAGEMENT: next step for orderId: ${order.orderId} is not in state ENQUEUED but ${nextStep.state} no need to start it`);
            // try to resume navigation for other existing orders
            await this.retriggerFTSSteps();
            return Promise.resolve();
        }
        console.debug(`ORDER_MANAGEMENT: start next step for orderId: ${order.orderId} next step found with id ${nextStep.id}`);
        const nextStepIndex = order.productionSteps.indexOf(nextStep);
        const nextStepAction = this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
        return this.triggerIndependentActions(order, [nextStepAction]);
    }
    /**
     * Returns the command for the next step.
     * @param step
     */
    getNextStepCommand(step) {
        const order = this.orderQueue.find(order => order.orderId === step.orderId);
        const nextStep = order?.productionSteps.find(nextStep => nextStep.dependentActionId === step.value.id);
        if (nextStep?.type === 'MANUFACTURE') {
            return nextStep.command;
        }
        else if (nextStep?.type === 'NAVIGATION') {
            return 'NAVIGATION';
        }
    }
    /**
     * Generates the next action for a drop command.
     * If there is no FTS docked ot the target module, generate a navigation command to navigate one to it. And add the new action to the production definitions of the order
     * If there is one generate the drop command as is
     * @param order the order of the step
     * @param nextStep the next step to get the target
     * @private
     */
    async generateNextActionForDrop(order, nextStep) {
        const idPrevStep = nextStep?.dependentActionId;
        const nextStepIndex = order.productionSteps.indexOf(nextStep);
        if (!idPrevStep) {
            return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
        }
        const prevStep = order.productionSteps.find(step => step.id === idPrevStep);
        if (!prevStep) {
            return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
        }
        if (prevStep.type !== 'MANUFACTURE') {
            return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
        }
        const serialNumberPrevStep = prevStep.serialNumber;
        if (!serialNumberPrevStep) {
            return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
        }
        if (this.ftsPairingStates.isFtsWaitingAtPosition(order.orderId, serialNumberPrevStep)) {
            return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
        }
        const fts = this.ftsPairingStates.getFtsAtPosition(serialNumberPrevStep, order.orderId);
        if (fts && fts.lastLoadPosition) {
            // This sets the load for the current position to the order that will run
            this.ftsPairingStates.setLoadingBay(fts.serialNumber, fts.lastLoadPosition, order.orderId);
            await this.ftsPairingStates.updateAvailability(fts.serialNumber, ccu_1.AvailableState.BUSY, order.orderId);
            return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
        }
        const moduleType = prevStep.moduleType;
        // generate navigation steps to move the FTS to the next module and update the dependent actionIds and action list
        const navId = (0, node_crypto_1.randomUUID)();
        const navStep = order_flow_service_1.OrderFlowService.getNavigationStep(navId, moduleType, nextStep.moduleType);
        nextStep.dependentActionId = navId;
        navStep.dependentActionId = idPrevStep;
        // update the action list
        const navIndexNew = order.productionSteps.indexOf(nextStep);
        order.productionSteps.splice(navIndexNew, 0, navStep);
        return this.generateOrderManagementAction(navStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    }
    isOrderStartable(order) {
        if (order.state !== ccu_1.OrderState.ENQUEUED) {
            return false;
        }
        if (order.orderType === 'STORAGE') {
            return stock_management_service_1.StockManagementService.hasReservedEmptyBay(order.orderId) || stock_management_service_1.StockManagementService.emptyBayAvailable(order.type);
        }
        return stock_management_service_1.StockManagementService.hasReservedWorkpiece(order.orderId) || stock_management_service_1.StockManagementService.stockAvailable(order.type);
    }
    /** Start the next order in the queue that has available stock */
    async startNextOrder() {
        const nextOrder = this.orderQueue.find(order => {
            return this.isOrderStartable(order);
        });
        if (!nextOrder) {
            return Promise.resolve();
        }
        await this.startOrder(nextOrder);
        await this.sendOrderListUpdate();
    }
    /**
     * Retry FTS steps that had unavailable modules or FTS
     * @returns the number of sent navigation requests
     */
    async retriggerFTSSteps() {
        console.log(`ORDER_MANAGEMENT: re-triggering FTS steps`);
        return await this.triggerNavigationSteps();
    }
    /**
     * Retry module steps that had unavailable modules
     * @returns the number of sent manufacture requests
     */
    async retriggerModuleSteps() {
        return await this.triggerManufactureSteps();
    }
    /**
     * Retry queued order steps that were blocked by unavailable modules or fts.
     * If no steps are queued, try to start a new waiting order.
     */
    async resumeOrders() {
        if (!this.hasActiveOrders()) {
            return this.startNextOrder();
        }
        const triggeredFtsSteps = await this.retriggerFTSSteps();
        const triggeredModuleSteps = await this.retriggerModuleSteps();
        if (triggeredFtsSteps > 0 || triggeredModuleSteps > 0) {
            return this.sendOrderListUpdate();
        }
    }
    /**
     *  Reset an order this will delete an order based on the provided orderId. This will delete any order regardless of its state.
     *  @param orderId the id of the order to reset
     */
    async resetOrder(orderId) {
        const activeOrder = this.activeOrders.find(order => order.orderId === orderId);
        if (activeOrder) {
            activeOrder.state = ccu_1.OrderState.CANCELLED;
            await this.deleteFinishedOrders(activeOrder);
            stock_management_service_1.StockManagementService.removeReservation(orderId);
            await (0, cloud_stock_1.publishStock)();
            this.navStepsToExecute = this.navStepsToExecute.filter(step => step.orderId !== orderId);
            this.manufactureStepsToExecute = this.manufactureStepsToExecute.filter(step => step.orderId !== orderId);
        }
        await this.retriggerFTSSteps();
        await this.startNextOrder();
        return activeOrder ? this.sendOrderListUpdate() : Promise.resolve();
    }
    async deleteFinishedOrders(order) {
        if (!order.stoppedAt) {
            order.stoppedAt = new Date();
        }
        this.completedOrders.push(order);
        await this.sendCompletedOrderListUpdate();
        const queuePos = this.orderQueue.indexOf(order);
        if (queuePos !== -1) {
            this.orderQueue.splice(queuePos, 1);
        }
        const activePos = this.activeOrders.indexOf(order);
        if (activePos !== -1) {
            this.activeOrders.splice(activePos, 1);
        }
        await this.sendOrderListUpdate();
        // make sure no reservation is left over.
        if (stock_management_service_1.StockManagementService.hasReservedWorkpiece(order.orderId)) {
            console.warn(`ORDER_MANAGEMENT: Stock reservation still exists while handling a completed order: ${order.orderId}`);
            stock_management_service_1.StockManagementService.removeReservation(order.orderId);
            await (0, cloud_stock_1.publishStock)();
        }
    }
    async deleteOrder(orderId) {
        const order = this.orderQueue.find(order => order.orderId === orderId);
        if (!order) {
            return;
        }
        if (order.state === ccu_1.OrderState.IN_PROGRESS) {
            return;
        }
        order.state = ccu_1.OrderState.CANCELLED;
        this.completedOrders.push(order);
        this.orderQueue.splice(this.orderQueue.indexOf(order), 1);
        await this.sendCompletedOrderListUpdate();
        if (stock_management_service_1.StockManagementService.hasReservedWorkpiece(order.orderId)) {
            console.warn(`ORDER_MANAGEMENT: Stock reservation still exists while deleting an order: ${order.orderId}`);
            stock_management_service_1.StockManagementService.removeReservation(order.orderId);
            await (0, cloud_stock_1.publishStock)();
        }
    }
    async cancelOrders(orderIds) {
        for (const orderId of orderIds) {
            await this.deleteOrder(orderId);
        }
        return this.sendOrderListUpdate();
    }
    getWorkpieceType(orderId) {
        let workpieceType = this.orderQueue.find(order => order.orderId === orderId)?.type;
        if (!workpieceType) {
            workpieceType = this.completedOrders.find(order => order.orderId === orderId)?.type;
        }
        return workpieceType;
    }
    getWorkpieceId(orderId) {
        let workpieceId = this.orderQueue.find(order => order.orderId === orderId)?.workpieceId;
        if (!workpieceId) {
            workpieceId = this.completedOrders.find(order => order.orderId === orderId)?.workpieceId;
        }
        return workpieceId;
    }
    getOrderForWorkpieceId(workpieceId) {
        let orderId = this.orderQueue.find(order => order.workpieceId === workpieceId)?.orderId;
        if (!orderId) {
            orderId = this.completedOrders.find(order => order.workpieceId === workpieceId)?.orderId;
        }
        return orderId;
    }
    hasActiveOrders() {
        return this.activeOrders.length > 0;
    }
    /**
     * Generate an action from an order step to be executed by the order management service
     * @param nextStep the next step to be executed
     * @param stepIndex the index of the step in the order
     * @param orderId the id of the order
     * @param workpiece the workpiece type
     * @param workpieceId the id of the workpiece
     * @private
     */
    generateOrderManagementAction(nextStep, stepIndex, orderId, workpiece, workpieceId) {
        return {
            index: stepIndex,
            value: nextStep,
            orderId,
            workpiece,
            workpieceId,
        };
    }
    /**
     * Update an order and set a new workpiece id.
     * This happens when a new workpiece is fetched from the HBW for the order.
     *
     * @param orderId
     * @param newWorkpieceId
     */
    updateOrderWorkpieceId(orderId, newWorkpieceId) {
        const order = this.orderQueue.find(order => order.orderId === orderId);
        if (!order) {
            return;
        }
        console.debug(`ORDER_MANAGEMENT: update workpieceId for order: ${orderId} from ${order.workpieceId} to ${newWorkpieceId}`);
        order.workpieceId = newWorkpieceId;
        const navStepsToUpdate = this.navStepsToExecute.filter(step => step.orderId === orderId);
        for (const step of navStepsToUpdate) {
            step.workpieceId = newWorkpieceId;
        }
        const manufactureStepsToUpdate = this.manufactureStepsToExecute.filter(step => step.orderId === orderId);
        for (const step of manufactureStepsToUpdate) {
            step.workpieceId = newWorkpieceId;
        }
    }
    isOrderActionRunning(orderId, actionId) {
        const activeOrder = this.activeOrders.find(order => order.orderId === orderId);
        if (!activeOrder) {
            console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} no active order found`);
            return false;
        }
        const step = activeOrder.productionSteps.find(step => step.id === actionId);
        if (!step) {
            console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} no step found for id: ${actionId}`);
            return false;
        }
        return step.state == ccu_1.OrderState.IN_PROGRESS;
    }
}
exports.OrderManagement = OrderManagement;
