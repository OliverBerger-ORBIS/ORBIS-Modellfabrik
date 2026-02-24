import { OrderResponse } from "../../common/protocol";
import { GeneralConfig, OrderManufactureStep, OrderNavigationStep } from "../../common/protocol/ccu";

export function oee(orders: OrderResponse[], config: GeneralConfig): number {
    const availabilityValue = availability(orders);
    const performanceValue = performance(orders, config);
    const qualityValue = quality(orders);
    return availabilityValue * performanceValue * qualityValue;
}

export function oeeForOrder(order: OrderResponse, config: GeneralConfig): number {
    const availabilityValue = availabilityForOrder(order);
    const performanceValue = performanceForOrder(order, config);
    const qualityValue = qualityForOrder(order);
    return availabilityValue * performanceValue * qualityValue;
}

export function quality(orders: OrderResponse[]): number {
    const numberOfOrders = orders.length;
    const numberOfErroredOrders = orders.filter(order => ['ERROR', 'CANCELLED'].includes(order.state)).length;
    return (numberOfOrders - numberOfErroredOrders) / numberOfOrders;
}

export function qualityForOrder(order: OrderResponse): number {
    if (['ERROR', 'CANCELLED'].includes(order.state)) {
        return 0;
    }
    return 1;
}

export function performance(orders: OrderResponse[], config: GeneralConfig): number {
    const totalOrderDurations = orders.reduce((acc, order) => {
        return acc + durationForOrder(order, config);
    }, 0);
    const plannedOrderDurations = orders.reduce((acc, order) => {
        return acc + config.productionDurations[order.type]!;
    }, 0);
    return plannedOrderDurations / totalOrderDurations;
}

export function performanceForOrder(order: OrderResponse, config: GeneralConfig): number {
    const plannedOrderDuration = config.productionDurations[order.type]!;
    const actualOrderDuration = durationForOrder(order, config);
    return plannedOrderDuration / actualOrderDuration;
}

/**
 * Uses the general config as fallback in case the order is not yet started or finished.
 */
export function durationForOrder(order: OrderResponse, config: GeneralConfig): number {
    if (!order.startedAt && !order.stoppedAt) {
        return config.productionDurations[order.type]!;
    } else if (order.startedAt && !order.stoppedAt) {
        return Math.max(config.productionDurations[order.type]!, (Date.now() - order.startedAt.getTime()) / 1000);
    } else {
        return (order.stoppedAt!.getTime() - order.startedAt!.getTime()) / 1000;
    }
}

export function availability(orders: OrderResponse[]): number {
    let totalProductionTime = 0;
    let totalWaitingTime = 0;
    for (let order of orders) {
        totalProductionTime += productionTimeForOrder(order);
        totalWaitingTime += waitingTimeForOrder(order);
    }
    const totalDuration = totalProductionTime + totalWaitingTime;
    return totalProductionTime / totalDuration;
}

export function availabilityForOrder(order: OrderResponse): number {
    const productionTime = productionTimeForOrder(order);
    const waitingTime = waitingTimeForOrder(order);
    const totalDuration = productionTime + waitingTime;
    return productionTime / totalDuration;
}

/**
 * If the time between the previous step ended and the current step started is longer than the threshold,
 * we assume that the machine was waiting for the operator to start the next step.
 * Otherwise we assume, that this is due to system delays, which we do not take into account.
 */
const WAITING_TIME_THRESHOLD_MS = 500;
export function waitingTimeForOrder(order: OrderResponse): number {
    let waitingTime = 0;
    for (let step of order.productionSteps) {
        if (!step.startedAt) {
            continue;
        }
        // the initial step does not have a dependent action and only depends on the order-received event
        if (!step.dependentActionId) {
            const delta = (step.startedAt?.getTime() || Date.now()) - order.receivedAt!.getTime();
            if (delta > WAITING_TIME_THRESHOLD_MS) {
                waitingTime += delta;
            }
        } else {
            const dependentStep = order.productionSteps.find(s => s.id === step.dependentActionId);
            // if the previous step is not yet finished, we cannot take this step into account yet
            if (dependentStep && dependentStep.stoppedAt) {
                const delta = step.startedAt!.getTime() - dependentStep.stoppedAt.getTime();
                if (delta > WAITING_TIME_THRESHOLD_MS) {
                    waitingTime += delta;
                }
            }
        }
    }
    return waitingTime / 1000;
}

export function productionTimeForOrder(order: OrderResponse): number {
    let productionTime = 0;
    for (let step of order.productionSteps) {
        productionTime += calculateStepDuration(step);
    }
    return productionTime;
}

export function calculateStepDuration(step: OrderNavigationStep | OrderManufactureStep): number {
    let duration = 0;
    if (step.startedAt && step.stoppedAt) {
        duration = step.stoppedAt.getTime() - step.startedAt.getTime();
    } else {
        duration = step.startedAt ? Date.now() - step.startedAt.getTime() : 0;
    }
    return duration / 1000;
}
