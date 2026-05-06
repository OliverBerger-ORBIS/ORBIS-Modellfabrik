/**
 * UC-07 Anomaly Detection: Structure Configuration
 *
 * Layout mirrors UC-05 so both stories stay comparable.
 */
export interface Uc07ProcessStep {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey: string;
}

export interface Uc07MixedBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey?: string;
  type: 'dsp-edge' | 'alarm' | 'target';
}

export interface Uc07ShopfloorBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
}

export interface Uc07ShopfloorIconBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  iconKey: 'trigger' | 'detector';
}

export interface Uc07Structure {
  viewBox: { width: number; height: number };
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  outcome: { x: number; y: number; key: string };
  footer: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };
  laneProcess: { x: number; y: number; width: number; height: number };
  processSteps: Uc07ProcessStep[];
  mixedArea: { x: number; y: number; width: number; height: number };
  mixedBoxes: Uc07MixedBox[];
  laneShopfloor: { x: number; y: number; width: number; height: number };
  shopfloorTriggerBox: Uc07ShopfloorIconBox;
  shopfloorSignalTriangle: { x: number; y: number; width: number; height: number };
  shopfloorDetectorBox: Uc07ShopfloorIconBox;
  shopfloorSystemsDevicesBox: Uc07ShopfloorBox;
}

export const UC07_CONNECTION_IDS: readonly string[] = [
  'uc07_conn_sensor_dsp',
  'uc07_conn_dsp_alarm',
  'uc07_conn_alarm_target',
  'uc07_conn_alarm_process',
  'uc07_conn_alarm_systems',
  'uc07_feedback',
];

const UC07_DESCRIPTION_HEIGHT = 50;

export function createUc07Structure(): Uc07Structure {
  const vbW = 1920;
  const vbH = 1080;
  const laneX = 40;
  const laneW = vbW - 80;

  const laneProcessH = 280;
  const laneMixedH = 290;
  const laneShopfloorH = 280;

  const laneProcessY = 88 + UC07_DESCRIPTION_HEIGHT;
  const laneMixedY = laneProcessY + laneProcessH + 12;
  const laneShopfloorY = laneMixedY + laneMixedH + 12;

  const stepW = 340;
  const stepH = 140;
  const totalProcessWidth = stepW * 5;
  const processStartX = laneX + (laneW - totalProcessWidth) / 2;
  const processStepY = laneProcessY + (laneProcessH - stepH) / 2;

  const processSteps: Uc07ProcessStep[] = [
    { id: 'proc_detect', x: processStartX, y: processStepY, width: stepW, height: stepH, titleKey: 'uc07.proc.detect', bulletsKey: 'uc07.proc.detect.bullets' },
    { id: 'proc_validate', x: processStartX + stepW, y: processStepY, width: stepW, height: stepH, titleKey: 'uc07.proc.validate', bulletsKey: 'uc07.proc.validate.bullets' },
    { id: 'proc_alarm', x: processStartX + stepW * 2, y: processStepY, width: stepW, height: stepH, titleKey: 'uc07.proc.alarm', bulletsKey: 'uc07.proc.alarm.bullets' },
    { id: 'proc_route', x: processStartX + stepW * 3, y: processStepY, width: stepW, height: stepH, titleKey: 'uc07.proc.route', bulletsKey: 'uc07.proc.route.bullets' },
    { id: 'proc_feedback', x: processStartX + stepW * 4, y: processStepY, width: stepW, height: stepH, titleKey: 'uc07.proc.feedback', bulletsKey: 'uc07.proc.feedback.bullets' },
  ];

  const boxGap = 12;
  const mixedBoxY = laneMixedY + 10;
  const gapToProcess = mixedBoxY - (laneProcessY + laneProcessH);
  const mixedBoxH = laneShopfloorY - mixedBoxY - gapToProcess;

  const dspX = laneX;
  const validatePeakX = processStartX + stepW * 2;
  const dspW = validatePeakX - dspX - 50;

  const alarmW = mixedBoxH;
  const alarmStepCenterX = processStartX + stepW * 2 + stepW / 2;
  const alarmX = alarmStepCenterX - alarmW / 2;

  const targetRightX = laneX + laneW;
  const targetW = dspW;
  const targetX = targetRightX - targetW;

  const mixedBoxes: Uc07MixedBox[] = [
    { id: 'mixed_dsp_edge', x: dspX, y: mixedBoxY, width: dspW, height: mixedBoxH, titleKey: 'uc07.mixed.dspEdge', bulletsKey: 'uc07.mixed.dspEdge.bullets', type: 'dsp-edge' },
    { id: 'mixed_alarm', x: alarmX, y: mixedBoxY, width: alarmW, height: mixedBoxH, titleKey: 'uc07.mixed.alarm', type: 'alarm' },
    { id: 'mixed_target', x: targetX, y: mixedBoxY, width: targetW, height: mixedBoxH, titleKey: 'uc07.mixed.target', bulletsKey: 'uc07.mixed.target.bullets', type: 'target' },
  ];

  const sfPad = 24;
  const sfShiftRight = 60;
  const sfSystemsDevicesW = 700;
  const sfSystemsDevicesH = 220;
  const sfSystemsDevicesY = laneShopfloorY + (laneShopfloorH - sfSystemsDevicesH) / 2;
  const sfSystemsDevicesX = laneX + laneW - sfPad - sfSystemsDevicesW;

  const iconBoxW = 160;
  const iconBoxH = 160;
  const detectorBoxW = 200;
  const detectorBoxH = 180;
  const iconBoxY = laneShopfloorY + (laneShopfloorH - iconBoxH) / 2;
  const detectorBoxY = laneShopfloorY + (laneShopfloorH - detectorBoxH) / 2;
  const iconBoxGap = boxGap;

  const signalTriangleW = iconBoxW;
  const signalTriangleH = iconBoxH;

  const shopfloorTriggerBox: Uc07ShopfloorIconBox = {
    id: 'sf_trigger',
    x: laneX + sfPad + sfShiftRight,
    y: iconBoxY,
    width: iconBoxW,
    height: iconBoxH,
    iconKey: 'trigger',
  };

  const shopfloorSignalTriangle = {
    x: laneX + sfPad + sfShiftRight + iconBoxW + iconBoxGap,
    y: iconBoxY,
    width: signalTriangleW,
    height: signalTriangleH,
  };

  const shopfloorDetectorBox: Uc07ShopfloorIconBox = {
    id: 'sf_detector',
    x: laneX + sfPad + sfShiftRight + iconBoxW + iconBoxGap + signalTriangleW + iconBoxGap,
    y: detectorBoxY,
    width: detectorBoxW,
    height: detectorBoxH,
    iconKey: 'detector',
  };

  const shopfloorSystemsDevicesBox: Uc07ShopfloorBox = {
    id: 'sf_systems_devices',
    x: sfSystemsDevicesX,
    y: sfSystemsDevicesY,
    width: sfSystemsDevicesW,
    height: sfSystemsDevicesH,
    titleKey: 'uc07.sf.systemsDevicesTitle',
  };

  return {
    viewBox: { width: vbW, height: vbH },
    title: { x: vbW / 2, y: 42, key: 'uc07.title' },
    subtitle: { x: vbW / 2, y: 74, key: 'uc07.subtitle' },
    outcome: { x: vbW / 2, y: 110, key: 'uc07.outcome' },
    footer: { x: vbW / 2, y: vbH - 24, key: 'uc07.footer' },
    stepDescription: { x: vbW / 2, y: 20, width: 1400, height: 100 },
    laneProcess: { x: laneX, y: laneProcessY, width: laneW, height: laneProcessH },
    processSteps,
    mixedArea: { x: laneX, y: laneMixedY, width: laneW, height: laneMixedH },
    mixedBoxes,
    laneShopfloor: { x: laneX, y: laneShopfloorY, width: laneW, height: laneShopfloorH },
    shopfloorTriggerBox,
    shopfloorSignalTriangle,
    shopfloorDetectorBox,
    shopfloorSystemsDevicesBox,
  };
}
