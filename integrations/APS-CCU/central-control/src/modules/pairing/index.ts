import { IClientSubscribeOptions } from 'async-mqtt';
import { randomUUID } from 'node:crypto';
import { ANY_SERIAL, CcuTopic, FtsTopic, getFtsTopic, getModuleTopic, ModuleTopic } from '../../../../common/protocol';
import { AvailableState, FtsPairedModule, PairedModule, PairingState } from '../../../../common/protocol/ccu';
import { ModuleType } from '../../../../common/protocol/module';
import { Connection, InstantAction, InstantActions, StatusLEDMetadata } from '../../../../common/protocol/vda';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { getMqttClient } from '../../mqtt/mqtt';
import CurrentErrorsService from '../current-errors/current-errors.service';
import { StockManagementService } from '../order/stock/stock-management-service';
import { FtsPairingStates } from './fts-pairing-states';
import { ModuleData, PairingStates } from './pairing-states';

export const TOPICS: string[] = [getModuleTopic(ANY_SERIAL, ModuleTopic.CONNECTION), getFtsTopic(ANY_SERIAL, FtsTopic.CONNECTION)];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

/**
 * Send the provided knownModules map to the ccu/pairing/known_modules topic for additional debug information.
 * @param knownModules the map of known modules, including their current state
 */
export async function sendKnownModules(knownModules: { [key: string]: ModuleData<PairedModule> }): Promise<void> {
  const mqtt = getMqttClient();
  if (!mqtt) {
    return;
  }
  return mqtt.publish(CcuTopic.KNOWN_MODULES_STATE, JSON.stringify(knownModules), {
    qos: 2,
    retain: true,
  });
}

export async function publishPairingState(): Promise<void> {
  return sendPairingState(PairingStates.getInstance(), FtsPairingStates.getInstance());
}

export async function sendPairingState(modState: PairingStates, ftsState: FtsPairingStates): Promise<void> {
  const mqtt = getMqttClient();
  const pairingState: PairingState = {
    modules: modState.getAll(),
    transports: ftsState.getAll(),
  };

  try {
    console.log('Calculating LED State');
    const module = PairingStates.getInstance().getForModuleType(ModuleType.DPS);
    if (module) {
      const ledInstantAction = calcStatusLEDFromPairingState(pairingState, module.serialNumber);
      console.log('LED UPDATE', JSON.stringify(ledInstantAction));
      const topic = getModuleTopic(module.serialNumber, ModuleTopic.INSTANT_ACTION);
      await mqtt.publish(topic, JSON.stringify(ledInstantAction), { qos: 2 });
      console.log('Calculated LED State published');
    }
  } catch (e) {
    console.error('Error while updating LED State', e);
  }

  try {
    await mqtt.publish(CcuTopic.PAIRING_STATE, JSON.stringify(pairingState), {
      qos: 2,
      retain: true,
    });
  } catch (e) {
    console.error('Error while sending pairing state', e);
  }
}

/**
 * Based on the pairing state, this function determines the global state of the APS and wraps
 * it into an instant action which is used to turn the LEDs on/off on the connected DPS module.
 *
 * Gelb-Grün bedeutet, dass mindestens eine Station auf die Weitergabe eines Werkstücks wartet.
 * Grün bedeutet, alle Stationen befinden sich im Wartezustand.
 * Gelb bedeutet, dass mindestens eine Station aktiv ist.
 * Rot bedeutet einen Fehler, der im Dashboard via Reset gelöst werden muss. Bspw. ein Werkstück wurde nicht
 * an die Station übergeben oder ein FTS hat die Spur verloren
 *
 * @param pairingState
 * @param serialNumber
 */
export const calcStatusLEDFromPairingState = (pairingState: PairingState, serialNumber: string): InstantAction => {
  // initiate instant action with green LED on indicating idle state
  const statusLeds: StatusLEDMetadata = {
    green: false,
    red: false,
    yellow: false,
  };
  const ledInstantAction: InstantAction = {
    serialNumber,
    timestamp: new Date(),
    actions: [
      {
        actionId: randomUUID(),
        actionType: InstantActions.SET_STATUS_LED,
        metadata: statusLeds,
      },
    ],
  };
  const allPairedModules = [...pairingState.modules, ...pairingState.transports].filter(mod => mod.pairedSince !== undefined);
  const currentErrors = CurrentErrorsService.getInstance().getAllCurrentErrors();

  let overallBlocked = false;
  let overallBusy = false;
  let overallAssigned = false;

  for (const module of allPairedModules) {
    const hasError = currentErrors.some(
      error => error.serialNumber === module.serialNumber && (error.errors ?? []).some(err => err.errorLevel === 'FATAL'),
    );
    const isChargingFts = module.type === 'FTS' && (module as FtsPairedModule).charging;
    if (module.available === AvailableState.BLOCKED && hasError && !isChargingFts) {
      overallBlocked = true;
      break; // Red is the highest prio, if there is one module with errors, then the LED is red in any case
    }
    if (!hasError && (module.available === AvailableState.BUSY || module.available === AvailableState.BLOCKED)) {
      overallBusy = true;
    }
    if (module.available === AvailableState.READY && module.assigned) {
      overallAssigned = true;
      // The DPS should be busy if it has a load.
      // Currently there is no good way to differentiate between busy input and waiting for FTS
      if (module.subType === ModuleType.DPS) {
        overallBusy = true;
      }
    }
  }
  if (overallBlocked) {
    statusLeds.red = true;
  } else if (overallBusy) {
    statusLeds.yellow = true;
  } else if (overallAssigned) {
    statusLeds.green = true;
  } else {
    statusLeds.green = true;
  }

  return ledInstantAction;
};

export const handleMessage = async (message: string, topic: string): Promise<void> => {
  if (!message) {
    // ignoring empty message
    return;
  }
  console.log('handleMessage connection', message);
  const conn = JSON.parse(message, jsonIsoDateReviver) as Connection;
  const modState = PairingStates.getInstance();
  const ftsState = FtsPairingStates.getInstance();
  if (topic.startsWith(ModuleTopic.ROOT)) {
    await modState.update(conn);
    StockManagementService.updateBaysFromModule(conn.serialNumber);
  } else if (topic.startsWith(FtsTopic.ROOT)) {
    await ftsState.update(conn);
  } else {
    console.error('Unknown topic: ' + topic);
    return;
  }
  return sendPairingState(modState, ftsState);
};
