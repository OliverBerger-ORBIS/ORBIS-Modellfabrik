export type CalibrationData = {
  [moduleType: string]: {
    [positionName: string]: Array<string>;
  };
};

export const calibrationData: CalibrationData = {
  HBW: {
    REF: [],
    RACK_REIHE_1_SPALTE_A: [
      'cal__rackOffset',
      'cal__row1',
      'cal__colA',
    ],
    RACK_REIHE_2_SPALTE_B: [
      'cal__rackOffset',
      'cal__row2',
      'cal__colB',
    ],
    RACK_REIHE_3_SPALTE_C: [
      'cal__rackOffset',
      'cal__row3',
      'cal__colC',
    ],
    RAMPE: [
      'cal__rampOffset',
      'cal__rampPositionX',
      'cal__rampPositionY',
      'cal__rampPositionRot',
      'cal__rampPositionRotCheck',
    ],
    DROP: ['cal__AGVPositionRot'],
    PICK: ['cal__AGVPositionRot'],
    FACTORY_BASE_SETTINGS: [
      'cal__timeProcessEnd',
      'cal__timeGripperValveClose',
      'cal__timeGripperValveOpen',
      'cal__timeCompressor',
    ],
  },
  DPS: {
    REF: [],
    HOME_BASE: ['RA.HOME.BASE.X', 'RA.HOME.BASE.Y', 'RA.HOME.BASE.Z'],
    HOME_INPUT: ['RA.HOME.INPUT.X', 'RA.HOME.INPUT.Y', 'RA.HOME.INPUT.Z'],
    HOME_OUTPUT: ['RA.HOME.OUTPUT.X', 'RA.HOME.OUTPUT.Y', 'RA.HOME.OUTPUT.Z'],
    NIO_APPROACH: [
      'RA.NIO.APPROACH.X',
      'RA.NIO.APPROACH.Y',
      'RA.NIO.APPROACH.Z',
    ],
    NIO_TARGET: ['RA.NIO.TARGET.X', 'RA.NIO.TARGET.Y', 'RA.NIO.TARGET.Z'],
    CS_APPROACH: [
      'RA.CS.APPROACH.X',
      'RA.CS.APPROACH.Y',
      'RA.CS.APPROACH.Z',
      'cal__colorRedSetpoint',
      'cal__colorBlueSetpoint',
      'cal__colorWhiteSetpoint',
      'cal__colorValue',
    ],
    CS_TARGET: [
      'RA.CS.TARGET.X',
      'RA.CS.TARGET.Y',
      'RA.CS.TARGET.Z',
      'cal__colorRedSetpoint',
      'cal__colorBlueSetpoint',
      'cal__colorWhiteSetpoint',
      'cal__colorValue',
    ],
    NFC_APPROACH: [
      'RA.NFC.APPROACH.X',
      'RA.NFC.APPROACH.Y',
      'RA.NFC.APPROACH.Z',
    ],
    NFC_TARGET: ['RA.NFC.TARGET.X', 'RA.NFC.TARGET.Y', 'RA.NFC.TARGET.Z'],
    INPUT_PICK_APPROACH_A: [
      'RA.INPUT.PICK.APPROACH_A.X',
      'RA.INPUT.PICK.APPROACH_A.Y',
      'RA.INPUT.PICK.APPROACH_A.Z',
    ],
    INPUT_PICK_APPROACH_B: [
      'RA.INPUT.PICK.APPROACH_B.X',
      'RA.INPUT.PICK.APPROACH_B.Y',
      'RA.INPUT.PICK.APPROACH_B.Z',
    ],
    INPUT_PICK_TARGET: [
      'RA.INPUT.PICK.TARGET.X',
      'RA.INPUT.PICK.TARGET.Y',
      'RA.INPUT.PICK.TARGET.Z',
    ],
    OUTPUT_DROP_APPROACH_A: [
      'RA.OUTPUT.DROP.APPROACH_A.X',
      'RA.OUTPUT.DROP.APPROACH_A.Y',
      'RA.OUTPUT.DROP.APPROACH_A.Z',
    ],
    OUTPUT_DROP_APPROACH_B: [
      'RA.OUTPUT.DROP.APPROACH_B.X',
      'RA.OUTPUT.DROP.APPROACH_B.Y',
      'RA.OUTPUT.DROP.APPROACH_B.Z',
    ],
    OUTPUT_DROP_TARGET: [
      'RA.OUTPUT.DROP.TARGET.X',
      'RA.OUTPUT.DROP.TARGET.Y',
      'RA.OUTPUT.DROP.TARGET.Z',
    ],
    FTS_PICK_APPROACH_A: [
      'RA.FTS.PICK.APPROACH_A.X',
      'RA.FTS.PICK.APPROACH_A.Y',
      'RA.FTS.PICK.APPROACH_A.Z',
    ],
    FTS_PICK_APPROACH_B: [
      'RA.FTS.PICK.APPROACH_B.X',
      'RA.FTS.PICK.APPROACH_B.Y',
      'RA.FTS.PICK.APPROACH_B.Z',
    ],
    FTS_PICK_TARGET: [
      'RA.FTS.PICK.TARGET.X',
      'RA.FTS.PICK.TARGET.Y',
      'RA.FTS.PICK.TARGET.Z',
    ],
    FTS_DROP_APPROACH_A: [
      'RA.FTS.DROP.APPROACH_A.X',
      'RA.FTS.DROP.APPROACH_A.Y',
      'RA.FTS.DROP.APPROACH_A.Z',
    ],
    FTS_DROP_APPROACH_B: [
      'RA.FTS.DROP.APPROACH_B.X',
      'RA.FTS.DROP.APPROACH_B.Y',
      'RA.FTS.DROP.APPROACH_B.Z',
    ],
    FTS_DROP_TARGET: [
      'RA.FTS.DROP.TARGET.X',
      'RA.FTS.DROP.TARGET.Y',
      'RA.FTS.DROP.TARGET.Z',
    ],
    GRIP_ON: [],
    GRIP_OFF: [],
    CAMERA_HOME: ['cal__homePosX', 'cal__homePosY'],
    CAMERA_HBW: ['cal__customPosX', 'cal__customPosY'],
    FACTORY_BASE_SETTINGS: [
      'cal__shortProcessWaitTime',
      'cal__colorRange',
    ],
  },
  AIQS: {
    TO_NIO_BIN: ['cal__badTime'],
    TO_CAMERA: ['cal__cameraTime'],
    TO_PICKUP: [],
    PICK: ['STEPS_BELT_CAMERA', 'STEPS_BELT_BIN', 'STEPS_BELT_GRIPPER'],
    DROP: ['STEPS_BELT_CAMERA', 'STEPS_BELT_BIN', 'STEPS_BELT_GRIPPER'],
    CHECK: ['STEPS_BELT_CAMERA', 'STEPS_BELT_BIN', 'STEPS_BELT_GRIPPER'],
    FACTORY_BASE_SETTINGS: [
      'cal__processEndTime',
      'cal__midLightGateTime',
      'cal__gripperDownTime',
      'cal__vacuumReleaseTime',
      'cal__prePhotoTime',
    ],
  },
};

export default calibrationData;

