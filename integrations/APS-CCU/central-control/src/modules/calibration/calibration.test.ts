import { ModuleInfoTypes, ModuleState, ModuleType } from '../../../../common/protocol/module';
import * as calibrationMock from './calibration';
import { updateModuleCalibrationState } from './calibration';
import * as mqttMock from '../../mqtt/mqtt';
import { AsyncMqttClient } from 'async-mqtt';
import { PairingStates } from '../pairing/pairing-states';
import { PairedModule } from '../../../../common/protocol/ccu';

describe('Test Calibration functions', () => {
  let mqttPublishSpy: jest.Mock;
  const MOCK_DATE = new Date('2022-02-03T11:12:13.1234Z');

  beforeEach(() => {
    mqttPublishSpy = jest.fn().mockImplementation(() => Promise.resolve());
    jest.spyOn(mqttMock, 'getMqttClient').mockReturnValue({ publish: mqttPublishSpy } as unknown as AsyncMqttClient);
    jest.useFakeTimers();
    jest.setSystemTime(MOCK_DATE);
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.restoreAllMocks();
    PairingStates.getInstance().reset();
  });

  it('should convert a state to the correct calibration values', async () => {
    const serialNumber = 'testSerial';
    const pairingModule: PairedModule = {
      subType: ModuleType.AIQS,
      serialNumber: serialNumber,
      type: 'MODULE',
    };
    jest.spyOn(PairingStates.getInstance(), 'get').mockReturnValue(pairingModule);
    const setCalibratingSpy = jest.spyOn(PairingStates.getInstance(), 'setCalibrating').mockReturnValue();
    const publishMock = jest.spyOn(calibrationMock, 'publishModuleCalibrationData').mockResolvedValue();
    const state: ModuleState = {
      timestamp: new Date(),
      type: ModuleType.AIQS,
      serialNumber: serialNumber,
      orderId: '',
      orderUpdateId: 0,
      errors: [],
      paused: true,
      information: [
        {
          infoType: ModuleInfoTypes.CALIBRATION_DATA,
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
          infoType: ModuleInfoTypes.CALIBRATION_STATUS,
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
    const expectedValues = JSON.parse(JSON.stringify(state.information![0].infoReferences));
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const expectedStatusValues = JSON.parse(JSON.stringify(state.information![1].infoReferences));

    await updateModuleCalibrationState(state);
    expect(setCalibratingSpy).toHaveBeenCalledWith(serialNumber, calibrating);
    expect(publishMock).toHaveBeenCalledWith(serialNumber, calibrating, expectedValues, expectedStatusValues);
  });

  it('should not set calibrating to true when the module was already calibrating', async () => {
    const serialNumber = 'testSerial';
    const pairingModule: PairedModule = {
      subType: ModuleType.AIQS,
      serialNumber: serialNumber,
      calibrating: true,
      type: 'MODULE',
    };
    jest.spyOn(PairingStates.getInstance(), 'get').mockReturnValue(pairingModule);
    const setCalibratingSpy = jest.spyOn(PairingStates.getInstance(), 'setCalibrating').mockReturnValue();
    const publishMock = jest.spyOn(calibrationMock, 'publishModuleCalibrationData').mockResolvedValue();
    const state: ModuleState = {
      timestamp: new Date(),
      type: ModuleType.AIQS,
      serialNumber: serialNumber,
      orderId: '',
      orderUpdateId: 0,
      errors: [],
      paused: true,
      information: [
        {
          infoType: ModuleInfoTypes.CALIBRATION_DATA,
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
          infoType: ModuleInfoTypes.CALIBRATION_STATUS,
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
    const expectedValues = JSON.parse(JSON.stringify(state.information![0].infoReferences));
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const expectedStatusValues = JSON.parse(JSON.stringify(state.information![1].infoReferences));

    await updateModuleCalibrationState(state);
    expect(setCalibratingSpy).not.toHaveBeenCalled();
    expect(publishMock).toHaveBeenCalledWith(serialNumber, calibrating, expectedValues, expectedStatusValues);
  });

  it('should set calibrating to false when the module was calibrating and calibration has stopped', async () => {
    const serialNumber = 'testSerial';
    const pairingModule: PairedModule = {
      subType: ModuleType.AIQS,
      serialNumber: serialNumber,
      calibrating: true,
      type: 'MODULE',
    };
    jest.spyOn(PairingStates.getInstance(), 'get').mockReturnValue(pairingModule);
    const setCalibratingSpy = jest.spyOn(PairingStates.getInstance(), 'setCalibrating').mockReturnValue();
    const publishMock = jest.spyOn(calibrationMock, 'publishModuleCalibrationData').mockResolvedValue();
    const state: ModuleState = {
      timestamp: new Date(),
      type: ModuleType.AIQS,
      serialNumber: serialNumber,
      orderId: '',
      orderUpdateId: 0,
      errors: [],
      paused: true,
      information: [],
    };

    const calibrating = false;

    await updateModuleCalibrationState(state);
    expect(setCalibratingSpy).toHaveBeenCalledWith(serialNumber, calibrating);
    expect(publishMock).toHaveBeenCalledWith(serialNumber, calibrating);
  });

  it('should not change anything when the module was not calibrating and no calibration data is available', async () => {
    const serialNumber = 'testSerial';
    const pairingModule: PairedModule = {
      subType: ModuleType.AIQS,
      serialNumber: serialNumber,
      calibrating: false,
      type: 'MODULE',
    };
    jest.spyOn(PairingStates.getInstance(), 'get').mockReturnValue(pairingModule);
    const setCalibratingSpy = jest.spyOn(PairingStates.getInstance(), 'setCalibrating').mockReturnValue();
    const publishMock = jest.spyOn(calibrationMock, 'publishModuleCalibrationData').mockResolvedValue();
    const state: ModuleState = {
      timestamp: new Date(),
      type: ModuleType.AIQS,
      serialNumber: serialNumber,
      orderId: '',
      orderUpdateId: 0,
      errors: [],
      paused: true,
      information: [],
    };

    await updateModuleCalibrationState(state);
    expect(setCalibratingSpy).not.toHaveBeenCalled();
    expect(publishMock).not.toHaveBeenCalledWith();
  });
});
