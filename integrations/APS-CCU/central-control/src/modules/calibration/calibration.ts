// a function to receive a Module state, extract calibration data and forward it to the UI.

import { ModuleInfoTypes, ModuleState } from '../../../../common/protocol/module';
import { InstantAction, InstantActions, ReferenceValue, State, VdaInformation } from '../../../../common/protocol/vda';
import { PairingStates } from '../pairing/pairing-states';
import { publishPairingState } from '../pairing';
import { ModuleCalibration, ModuleCalibrationCommand, ModuleCalibrationState } from '../../../../common/protocol/ccu';
import { getCcuCalibrationTopic, getModuleTopic, ModuleTopic } from '../../../../common/protocol';
import { randomUUID } from 'node:crypto';
import { getMqttClient } from '../../mqtt/mqtt';
import { checkAndSendParkRequests, clearParkRequest } from '../park';

/**
 * Send a calibration action to a module using the commands received from the frontend
 * @param calibration
 */
export const sendCalibrationInstantAction = async (calibration: ModuleCalibration) => {
  const topic = getModuleTopic(calibration.serialNumber, ModuleTopic.INSTANT_ACTION);
  const calibrationCommandToAction: { [s in ModuleCalibrationCommand]: InstantActions } = {
    [ModuleCalibrationCommand.SET_VALUES]: InstantActions.CALIBRATION_SET_VALUES,
    [ModuleCalibrationCommand.RESET]: InstantActions.CALIBRATION_RESET,
    [ModuleCalibrationCommand.STORE]: InstantActions.CALIBRATION_STORE,
    [ModuleCalibrationCommand.SELECT]: InstantActions.CALIBRATION_SELECT,
    [ModuleCalibrationCommand.TEST]: InstantActions.CALIBRATION_TEST,
    [ModuleCalibrationCommand.START]: InstantActions.CALIBRATION_START,
    [ModuleCalibrationCommand.STOP]: InstantActions.CALIBRATION_STOP,
  };
  const action: InstantAction = {
    timestamp: new Date(),
    serialNumber: calibration.serialNumber,
    actions: [
      {
        actionType: calibrationCommandToAction[calibration.command],
        actionId: randomUUID(),
        metadata: {
          references: calibration.references,
          factory: calibration.factory,
          position: calibration.position,
        },
      },
    ],
  };
  return getMqttClient().publish(topic, JSON.stringify(action), { qos: 2 });
};

/**
 * Publish the calibration data for a module
 * @param serialNumber
 * @param calibrating
 * @param references
 * @param status_references
 */
export const publishModuleCalibrationData = async (
  serialNumber: string,
  calibrating: boolean,
  references?: Array<ReferenceValue>,
  status_references?: Array<ReferenceValue>,
) => {
  const calib_data: ModuleCalibrationState = {
    timestamp: new Date(),
    serialNumber,
    calibrating,
    references,
    status_references,
  };
  return getMqttClient().publish(getCcuCalibrationTopic(serialNumber), JSON.stringify(calib_data), { qos: 2 });
};

/**
 * Handle detecting a module in calibration mode and sending the data to the frontend
 * @param state
 */
export const updateModuleCalibrationState = async (state: ModuleState) => {
  const calibration_data: VdaInformation | undefined = state.information?.find(info => info.infoType === ModuleInfoTypes.CALIBRATION_DATA);
  const calibration_status: VdaInformation | undefined = state.information?.find(
    info => info.infoType === ModuleInfoTypes.CALIBRATION_STATUS,
  );
  const pairingStates = PairingStates.getInstance();
  const module = pairingStates.get(state.serialNumber);
  if (!module) {
    return;
  }
  const isCalibrating = !!(state.paused && calibration_data);
  const wasCalibrating = !!module.calibrating;
  if (isCalibrating && (!state.actionState || state.actionState.state == State.FINISHED)) {
    await checkAndSendParkRequests(state.serialNumber);
  }
  if (wasCalibrating !== isCalibrating) {
    pairingStates.setCalibrating(state.serialNumber, isCalibrating);
    await publishPairingState();
    if (!isCalibrating) {
      clearParkRequest(state.serialNumber);
      await publishModuleCalibrationData(state.serialNumber, false);
    }
  }
  if (calibration_data) {
    await publishModuleCalibrationData(
      state.serialNumber,
      isCalibrating,
      calibration_data.infoReferences,
      calibration_status?.infoReferences,
    );
  }
};
