"use strict";
// a function to receive a Module state, extract calibration data and forward it to the UI.
Object.defineProperty(exports, "__esModule", { value: true });
exports.updateModuleCalibrationState = exports.publishModuleCalibrationData = exports.sendCalibrationInstantAction = void 0;
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const pairing_states_1 = require("../pairing/pairing-states");
const pairing_1 = require("../pairing");
const ccu_1 = require("../../../../common/protocol/ccu");
const protocol_1 = require("../../../../common/protocol");
const node_crypto_1 = require("node:crypto");
const mqtt_1 = require("../../mqtt/mqtt");
const park_1 = require("../park");
/**
 * Send a calibration action to a module using the commands received from the frontend
 * @param calibration
 */
const sendCalibrationInstantAction = async (calibration) => {
    const topic = (0, protocol_1.getModuleTopic)(calibration.serialNumber, protocol_1.ModuleTopic.INSTANT_ACTION);
    const calibrationCommandToAction = {
        [ccu_1.ModuleCalibrationCommand.SET_VALUES]: vda_1.InstantActions.CALIBRATION_SET_VALUES,
        [ccu_1.ModuleCalibrationCommand.RESET]: vda_1.InstantActions.CALIBRATION_RESET,
        [ccu_1.ModuleCalibrationCommand.STORE]: vda_1.InstantActions.CALIBRATION_STORE,
        [ccu_1.ModuleCalibrationCommand.SELECT]: vda_1.InstantActions.CALIBRATION_SELECT,
        [ccu_1.ModuleCalibrationCommand.TEST]: vda_1.InstantActions.CALIBRATION_TEST,
        [ccu_1.ModuleCalibrationCommand.START]: vda_1.InstantActions.CALIBRATION_START,
        [ccu_1.ModuleCalibrationCommand.STOP]: vda_1.InstantActions.CALIBRATION_STOP,
    };
    const action = {
        timestamp: new Date(),
        serialNumber: calibration.serialNumber,
        actions: [
            {
                actionType: calibrationCommandToAction[calibration.command],
                actionId: (0, node_crypto_1.randomUUID)(),
                metadata: {
                    references: calibration.references,
                    factory: calibration.factory,
                    position: calibration.position,
                },
            },
        ],
    };
    return (0, mqtt_1.getMqttClient)().publish(topic, JSON.stringify(action), { qos: 2 });
};
exports.sendCalibrationInstantAction = sendCalibrationInstantAction;
/**
 * Publish the calibration data for a module
 * @param serialNumber
 * @param calibrating
 * @param references
 * @param status_references
 */
const publishModuleCalibrationData = async (serialNumber, calibrating, references, status_references) => {
    const calib_data = {
        timestamp: new Date(),
        serialNumber,
        calibrating,
        references,
        status_references,
    };
    return (0, mqtt_1.getMqttClient)().publish((0, protocol_1.getCcuCalibrationTopic)(serialNumber), JSON.stringify(calib_data), { qos: 2 });
};
exports.publishModuleCalibrationData = publishModuleCalibrationData;
/**
 * Handle detecting a module in calibration mode and sending the data to the frontend
 * @param state
 */
const updateModuleCalibrationState = async (state) => {
    const calibration_data = state.information?.find(info => info.infoType === module_1.ModuleInfoTypes.CALIBRATION_DATA);
    const calibration_status = state.information?.find(info => info.infoType === module_1.ModuleInfoTypes.CALIBRATION_STATUS);
    const pairingStates = pairing_states_1.PairingStates.getInstance();
    const module = pairingStates.get(state.serialNumber);
    if (!module) {
        return;
    }
    const isCalibrating = !!(state.paused && calibration_data);
    const wasCalibrating = !!module.calibrating;
    if (isCalibrating && (!state.actionState || state.actionState.state == vda_1.State.FINISHED)) {
        await (0, park_1.checkAndSendParkRequests)(state.serialNumber);
    }
    if (wasCalibrating !== isCalibrating) {
        pairingStates.setCalibrating(state.serialNumber, isCalibrating);
        await (0, pairing_1.publishPairingState)();
        if (!isCalibrating) {
            (0, park_1.clearParkRequest)(state.serialNumber);
            await (0, exports.publishModuleCalibrationData)(state.serialNumber, false);
        }
    }
    if (calibration_data) {
        await (0, exports.publishModuleCalibrationData)(state.serialNumber, isCalibrating, calibration_data.infoReferences, calibration_status?.infoReferences);
    }
};
exports.updateModuleCalibrationState = updateModuleCalibrationState;
