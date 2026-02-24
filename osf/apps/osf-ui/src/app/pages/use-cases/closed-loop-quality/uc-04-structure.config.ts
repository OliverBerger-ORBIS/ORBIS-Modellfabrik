/**
 * UC-04 Closed Loop Quality: Structure Configuration
 *
 * Eigenständiges Template – unabhängig von UC-05.
 * Layout: 3 horizontale Lanes
 * 1. Process Lane: Detect (Nonconformance) → Decide → Act → Feedback
 * 2. Mixed: DSP Edge | Quality-Event | Target (MES/ERP/Analytics)
 * 3. Shopfloor Lane: Production Order + AIQS Station (links) | Systems & Devices (rechts)
 */

export interface Uc04ProcessStep {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey: string;
}

export interface Uc04MixedBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey?: string;
  type: 'dsp-edge' | 'quality-event' | 'target';
}

export interface Uc04ShopfloorBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
}

export interface Uc04ShopfloorIconBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  iconKey: 'production-order' | 'aiqs';
}

export interface Uc04Structure {
  viewBox: { width: number; height: number };
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  outcome: { x: number; y: number; key: string };
  footer: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };
  laneProcess: { x: number; y: number; width: number; height: number };
  processSteps: Uc04ProcessStep[];
  mixedArea: { x: number; y: number; width: number; height: number };
  mixedBoxes: Uc04MixedBox[];
  laneShopfloor: { x: number; y: number; width: number; height: number };
  shopfloorProductionOrderBox: Uc04ShopfloorIconBox;
  shopfloorAiqsBox: Uc04ShopfloorIconBox;
  shopfloorSystemsDevicesBox: Uc04ShopfloorBox;
}

/** Connection element IDs for dim-conn styling (lighter opacity than dim) */
export const UC04_CONNECTION_IDS: readonly string[] = [
  'uc04_conn_aiqs_dsp',
  'uc04_conn_dsp_quality',
  'uc04_conn_quality_target',
  'uc04_conn_quality_act',
  'uc04_conn_quality_systems',
  'uc04_feedback',
];

const UC04_DESCRIPTION_HEIGHT = 50;

export function createUc04Structure(): Uc04Structure {
  const vbW = 1920;
  const vbH = 1080;
  const laneX = 40;
  const laneW = vbW - 80;

  const laneProcessH = 280;
  const laneMixedH = 290;
  const laneShopfloorH = 280;

  const laneProcessY = 88 + UC04_DESCRIPTION_HEIGHT;
  const laneMixedY = laneProcessY + laneProcessH + 12;
  const laneShopfloorY = laneMixedY + laneMixedH + 12;

  const stepW = 340;
  const stepH = 140;
  const stepGap = 0;
  const totalProcessWidth = stepW * 4 + stepGap * 3;
  const processStartX = laneX + (laneW - totalProcessWidth) / 2;
  const processStepY = laneProcessY + (laneProcessH - stepH) / 2;

  const processSteps: Uc04ProcessStep[] = [
    { id: 'proc_detect', x: processStartX, y: processStepY, width: stepW, height: stepH, titleKey: 'uc04.proc.detect', bulletsKey: 'uc04.proc.detect.bullets' },
    { id: 'proc_decide', x: processStartX + (stepW + stepGap), y: processStepY, width: stepW, height: stepH, titleKey: 'uc04.proc.decide', bulletsKey: 'uc04.proc.decide.bullets' },
    { id: 'proc_act', x: processStartX + (stepW + stepGap) * 2, y: processStepY, width: stepW, height: stepH, titleKey: 'uc04.proc.act', bulletsKey: 'uc04.proc.act.bullets' },
    { id: 'proc_feedback', x: processStartX + (stepW + stepGap) * 3, y: processStepY, width: stepW, height: stepH, titleKey: 'uc04.proc.feedback', bulletsKey: 'uc04.proc.feedback.bullets' },
  ];

  // Mixed boxes: same position and size as UC-05 (unabhängig von 4 vs 5 Process-Steps)
  const boxGap = 12;
  const mixedBoxY = laneMixedY + 10;
  const gapToProcess = mixedBoxY - (laneProcessY + laneProcessH);
  const mixedBoxH = laneShopfloorY - mixedBoxY - gapToProcess;

  const dspX = laneX;
  const dspW = 700; // wie UC-05: evaluatePeakX - dspX - 50

  const qualityEventW = mixedBoxH; // quadratisch wie UC-05 Alarm
  const qualityEventX = 960 - qualityEventW / 2; // wie UC-05: alarmStepCenterX - alarmW/2

  const targetRightX = laneX + laneW;
  const targetW = dspW;
  const targetX = targetRightX - targetW;

  const mixedBoxes: Uc04MixedBox[] = [
    { id: 'mixed_dsp_edge', x: dspX, y: mixedBoxY, width: dspW, height: mixedBoxH, titleKey: 'uc04.mixed.dspEdge', bulletsKey: 'uc04.mixed.dspEdge.bullets', type: 'dsp-edge' },
    { id: 'mixed_quality_event', x: qualityEventX, y: mixedBoxY, width: qualityEventW, height: mixedBoxH, titleKey: 'uc04.mixed.qualityEvent', type: 'quality-event' },
    { id: 'mixed_target', x: targetX, y: mixedBoxY, width: targetW, height: mixedBoxH, titleKey: 'uc04.mixed.target', bulletsKey: 'uc04.mixed.target.bullets', type: 'target' },
  ];

  const sfPad = 24;
  const sfShiftRight = 60;
  const sfSystemsDevicesW = 700;
  const sfSystemsDevicesH = 220;
  const sfSystemsDevicesY = laneShopfloorY + (laneShopfloorH - sfSystemsDevicesH) / 2;
  const sfSystemsDevicesX = laneX + laneW - sfPad - sfSystemsDevicesW;

  const iconBoxW = 180;
  const iconBoxH = 180;
  const iconBoxY = laneShopfloorY + (laneShopfloorH - iconBoxH) / 2;
  const iconBoxGap = 16;

  const shopfloorProductionOrderBox: Uc04ShopfloorIconBox = {
    id: 'sf_production_order',
    x: laneX + sfPad + sfShiftRight,
    y: iconBoxY,
    width: iconBoxW,
    height: iconBoxH,
    iconKey: 'production-order',
  };

  const shopfloorAiqsBox: Uc04ShopfloorIconBox = {
    id: 'sf_aiqs',
    x: laneX + sfPad + sfShiftRight + iconBoxW + iconBoxGap,
    y: iconBoxY,
    width: iconBoxW,
    height: iconBoxH,
    iconKey: 'aiqs',
  };

  const shopfloorSystemsDevicesBox: Uc04ShopfloorBox = {
    id: 'sf_systems_devices',
    x: sfSystemsDevicesX,
    y: sfSystemsDevicesY,
    width: sfSystemsDevicesW,
    height: sfSystemsDevicesH,
    titleKey: 'uc04.sf.systemsDevicesTitle',
  };

  return {
    viewBox: { width: vbW, height: vbH },
    title: { x: vbW / 2, y: 42, key: 'uc04.title' },
    subtitle: { x: vbW / 2, y: 74, key: 'uc04.subtitle' },
    outcome: { x: vbW / 2, y: 110, key: 'uc04.outcome' },
    footer: { x: vbW / 2, y: vbH - 24, key: 'uc04.footer' },
    stepDescription: { x: vbW / 2, y: 20, width: 1400, height: 100 },

    laneProcess: { x: laneX, y: laneProcessY, width: laneW, height: laneProcessH },
    processSteps,

    mixedArea: { x: laneX, y: laneMixedY, width: laneW, height: laneMixedH },
    mixedBoxes,

    laneShopfloor: { x: laneX, y: laneShopfloorY, width: laneW, height: laneShopfloorH },
    shopfloorProductionOrderBox,
    shopfloorAiqsBox,
    shopfloorSystemsDevicesBox,
  };
}
