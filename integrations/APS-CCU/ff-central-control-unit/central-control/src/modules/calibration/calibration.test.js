"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const module_1 = require("../../../../common/protocol/module");
const calibrationMock = __importStar(require("./calibration"));
const calibration_1 = require("./calibration");
const mqttMock = __importStar(require("../../mqtt/mqtt"));
const pairing_states_1 = require("../pairing/pairing-states");
describe('Test Calibration functions', () => {
    let mqttPublishSpy;
    const MOCK_DATE = new Date('2022-02-03T11:12:13.1234Z');
    beforeEach(() => {
        mqttPublishSpy = jest.fn().mockImplementation(() => Promise.resolve());
        jest.spyOn(mqttMock, 'getMqttClient').mockReturnValue({ publish: mqttPublishSpy });
        jest.useFakeTimers();
        jest.setSystemTime(MOCK_DATE);
    });
    afterEach(() => {
        jest.clearAllTimers();
        jest.restoreAllMocks();
        pairing_states_1.PairingStates.getInstance().reset();
    });
    it('should convert a state to the correct calibration values', async () => {
        const serialNumber = 'testSerial';
        const pairingModule = {
            subType: module_1.ModuleType.AIQS,
            serialNumber: serialNumber,
            type: 'MODULE',
        };
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'get').mockReturnValue(pairingModule);
        const setCalibratingSpy = jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'setCalibrating').mockReturnValue();
        const publishMock = jest.spyOn(calibrationMock, 'publishModuleCalibrationData').mockResolvedValue();
        const state = {
            timestamp: new Date(),
            type: module_1.ModuleType.AIQS,
            serialNumber: serialNumber,
            orderId: '',
            orderUpdateId: 0,
            errors: [],
            paused: true,
            information: [
                {
                    infoType: module_1.ModuleInfoTypes.CALIBRATION_DATA,
                    infoLevel: 'DEBUG',
                    infoReferences: [
                        {
                            referenceValue: 123,
                            referenceKey: 'TEST',
                        },
                        {
                            referenceValue: 42,
                            referenceKey: 'PARAM',
                        },
                    ],
                },
                {
                    infoType: module_1.ModuleInfoTypes.CALIBRATION_STATUS,
                    infoLevel: 'DEBUG',
                    infoReferences: [
                        {
                            referenceValue: 'test',
                            referenceKey: 'TESTSTATE',
                        },
                        {
                            referenceValue: 'test,value',
                            referenceKey: 'STATEPARAM',
                        },
                    ],
                },
            ],
        };
        const calibrating = true;
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const expectedValues = JSON.parse(JSON.stringify(state.information[0].infoReferences));
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const expectedStatusValues = JSON.parse(JSON.stringify(state.information[1].infoReferences));
        await (0, calibration_1.updateModuleCalibrationState)(state);
        expect(setCalibratingSpy).toHaveBeenCalledWith(serialNumber, calibrating);
        expect(publishMock).toHaveBeenCalledWith(serialNumber, calibrating, expectedValues, expectedStatusValues);
    });
    it('should not set calibrating to true when the module was already calibrating', async () => {
        const serialNumber = 'testSerial';
        const pairingModule = {
            subType: module_1.ModuleType.AIQS,
            serialNumber: serialNumber,
            calibrating: true,
            type: 'MODULE',
        };
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'get').mockReturnValue(pairingModule);
        const setCalibratingSpy = jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'setCalibrating').mockReturnValue();
        const publishMock = jest.spyOn(calibrationMock, 'publishModuleCalibrationData').mockResolvedValue();
        const state = {
            timestamp: new Date(),
            type: module_1.ModuleType.AIQS,
            serialNumber: serialNumber,
            orderId: '',
            orderUpdateId: 0,
            errors: [],
            paused: true,
            information: [
                {
                    infoType: module_1.ModuleInfoTypes.CALIBRATION_DATA,
                    infoLevel: 'DEBUG',
                    infoReferences: [
                        {
                            referenceValue: 123,
                            referenceKey: 'TEST',
                        },
                        {
                            referenceValue: 42,
                            referenceKey: 'PARAM',
                        },
                    ],
                },
                {
                    infoType: module_1.ModuleInfoTypes.CALIBRATION_STATUS,
                    infoLevel: 'DEBUG',
                    infoReferences: [
                        {
                            referenceValue: 'test',
                            referenceKey: 'TESTSTATE',
                        },
                        {
                            referenceValue: 'test,value',
                            referenceKey: 'STATEPARAM',
                        },
                    ],
                },
            ],
        };
        const calibrating = true;
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const expectedValues = JSON.parse(JSON.stringify(state.information[0].infoReferences));
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        const expectedStatusValues = JSON.parse(JSON.stringify(state.information[1].infoReferences));
        await (0, calibration_1.updateModuleCalibrationState)(state);
        expect(setCalibratingSpy).not.toHaveBeenCalled();
        expect(publishMock).toHaveBeenCalledWith(serialNumber, calibrating, expectedValues, expectedStatusValues);
    });
    it('should set calibrating to false when the module was calibrating and calibration has stopped', async () => {
        const serialNumber = 'testSerial';
        const pairingModule = {
            subType: module_1.ModuleType.AIQS,
            serialNumber: serialNumber,
            calibrating: true,
            type: 'MODULE',
        };
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'get').mockReturnValue(pairingModule);
        const setCalibratingSpy = jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'setCalibrating').mockReturnValue();
        const publishMock = jest.spyOn(calibrationMock, 'publishModuleCalibrationData').mockResolvedValue();
        const state = {
            timestamp: new Date(),
            type: module_1.ModuleType.AIQS,
            serialNumber: serialNumber,
            orderId: '',
            orderUpdateId: 0,
            errors: [],
            paused: true,
            information: [],
        };
        const calibrating = false;
        await (0, calibration_1.updateModuleCalibrationState)(state);
        expect(setCalibratingSpy).toHaveBeenCalledWith(serialNumber, calibrating);
        expect(publishMock).toHaveBeenCalledWith(serialNumber, calibrating);
    });
    it('should not change anything when the module was not calibrating and no calibration data is available', async () => {
        const serialNumber = 'testSerial';
        const pairingModule = {
            subType: module_1.ModuleType.AIQS,
            serialNumber: serialNumber,
            calibrating: false,
            type: 'MODULE',
        };
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'get').mockReturnValue(pairingModule);
        const setCalibratingSpy = jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'setCalibrating').mockReturnValue();
        const publishMock = jest.spyOn(calibrationMock, 'publishModuleCalibrationData').mockResolvedValue();
        const state = {
            timestamp: new Date(),
            type: module_1.ModuleType.AIQS,
            serialNumber: serialNumber,
            orderId: '',
            orderUpdateId: 0,
            errors: [],
            paused: true,
            information: [],
        };
        await (0, calibration_1.updateModuleCalibrationState)(state);
        expect(setCalibratingSpy).not.toHaveBeenCalled();
        expect(publishMock).not.toHaveBeenCalledWith();
    });
});
