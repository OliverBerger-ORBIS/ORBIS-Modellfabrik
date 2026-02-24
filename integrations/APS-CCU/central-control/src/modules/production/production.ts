import { getMqttClient } from '../../mqtt/mqtt';
import { getModuleTopic, ModuleTopic, Workpiece } from '../../../../common/protocol';
import {
  DeliveryMetadata,
  DurationMetadata,
  ModuleType,
  ProductionCommand,
  StorageModuleBayPosition,
  StoreMetadata,
} from '../../../../common/protocol/module';
import { AvailableState, OrderManufactureStep, PairedModule } from '../../../../common/protocol/ccu';
import { PairingStates } from '../pairing/pairing-states';
import { ControllerNotReadyError } from '../../models/models';
import { InstantAction, InstantActions } from '../../../../common/protocol/vda';
import { randomUUID } from 'node:crypto';

const convertProductionType = (
  prodStep: OrderManufactureStep,
  orderId: string,
  orderUpdateId: number,
  pairedModule: PairedModule,
  metadata: DurationMetadata | StoreMetadata | DeliveryMetadata,
): ProductionCommand => {
  return {
    timestamp: new Date(),
    serialNumber: pairedModule.serialNumber,
    orderId,
    orderUpdateId,
    action: {
      id: prodStep.id,
      command: prodStep.command,
      metadata,
    },
  };
};

/**
 * sends the production command to a module and return the chosen module serialNumber
 * @param productionStep
 * @param orderId
 * @param orderUpdateId
 * @param pairedModule
 * @param metadata
 */
export const sendProductionCommand = async (
  productionStep: OrderManufactureStep,
  orderId: string,
  orderUpdateId: number,
  pairedModule: PairedModule,
  metadata: DurationMetadata | StoreMetadata | DeliveryMetadata,
): Promise<void> => {
  // sanity check
  const serialNumber = pairedModule.serialNumber;
  if (!PairingStates.getInstance().isReadyForOrder(serialNumber, orderId)) {
    throw new ControllerNotReadyError('MODULE', productionStep.moduleType);
  }

  const command: ProductionCommand = convertProductionType(productionStep, orderId, orderUpdateId, pairedModule, metadata);
  const mqtt = getMqttClient();
  return mqtt
    .publish(getModuleTopic(serialNumber, ModuleTopic.ORDER), JSON.stringify(command))
    .then(() => console.debug(`command published: ${productionStep.command}`))
    .catch(err => console.error(`command not published: ${productionStep.command}`, err));
};

/**
 * Sends a SET_STORAGE instant action to the given module that clears all stored workpieces
 * @param serialNumber
 */
const sendEmptySetStorageAction = async (serialNumber: string) => {
  const instantAction: InstantAction = {
    timestamp: new Date(),
    serialNumber: serialNumber,
    actions: [
      {
        actionType: InstantActions.SET_STORAGE,
        actionId: randomUUID(),
        metadata: {
          contents: {},
        },
      },
    ],
  };
  if (instantAction.actions[0]?.metadata && 'contents' in instantAction.actions[0].metadata) {
    for (const position of Object.values(StorageModuleBayPosition)) {
      instantAction.actions[0].metadata.contents[position] = {};
    }
  }

  const mqtt = getMqttClient();
  return mqtt.publish(getModuleTopic(serialNumber, ModuleTopic.INSTANT_ACTION), JSON.stringify(instantAction));
};

/**
 * Clear the contents of all storage modules to a new empty state.
 */
export const clearHBWContents = async () => {
  const modules = PairingStates.getInstance()
    .getAll()
    .filter(mod => mod.subType === ModuleType.HBW);
  for (const mod of modules) {
    await sendEmptySetStorageAction(mod.serialNumber);
  }
};

/**
 * Send an instant action to the FTS to reset it and force a re-pairing.
 */
export const sendResetModuleInstantAction = async (serialNumber: string): Promise<void> => {
  const topic = getModuleTopic(serialNumber, ModuleTopic.INSTANT_ACTION);

  console.debug(`Sending reset instant action for Module ${serialNumber} to topic ${topic}`);
  const instantAction: InstantAction = {
    serialNumber,
    timestamp: new Date(),
    actions: [
      {
        actionId: randomUUID(),
        actionType: InstantActions.RESET,
      },
    ],
  };
  const pairingStates = PairingStates.getInstance();
  await pairingStates.updateAvailability(serialNumber, AvailableState.BLOCKED);

  const mqttClient = getMqttClient();

  return mqttClient.publish(topic, JSON.stringify(instantAction), { qos: 2 });
};

/**
 * Send an instant action to the DPS to announce a PICK command to output a workpice.
 * The DPS will then abort running input processes that have not been published and wait for the PICK command.
 * @param serialNumber
 * @param orderId
 * @param workpiece
 */
export const sendAnnounceDpsOutput = async (serialNumber: string, orderId: string, workpiece?: Workpiece): Promise<void> => {
  const topic = getModuleTopic(serialNumber, ModuleTopic.INSTANT_ACTION);

  console.debug(`Sending announceOutput instant action for Module ${serialNumber} to topic ${topic}`);
  const instantAction: InstantAction = {
    serialNumber,
    timestamp: new Date(),
    actions: [
      {
        actionId: randomUUID(),
        actionType: InstantActions.ANNOUNCE_OUTPUT,
        metadata: {
          orderId: orderId,
          type: workpiece,
        },
      },
    ],
  };
  const mqttClient = getMqttClient();

  return mqttClient.publish(topic, JSON.stringify(instantAction), { qos: 2 });
};

/**
 * Send an instant action to the DPS to cancel the storage order for a loaded workpiece.
 * The DPS will then cancel the order and discard the workpiece to NIO.
 * @param serialNumber
 */
export const sendCancelStorageOrder = async (serialNumber: string): Promise<void> => {
  const topic = getModuleTopic(serialNumber, ModuleTopic.INSTANT_ACTION);

  console.debug(`Sending cancelStorageOrder instant action for Module ${serialNumber} to topic ${topic}`);
  const instantAction: InstantAction = {
    serialNumber,
    timestamp: new Date(),
    actions: [
      {
        actionId: randomUUID(),
        actionType: InstantActions.CANCEL_STORAGE_ORDER,
      },
    ],
  };
  const mqttClient = getMqttClient();

  return mqttClient.publish(topic, JSON.stringify(instantAction), { qos: 2 });
};
