/**
 * UC-05 Predictive Maintenance: Structure Configuration
 *
 * Layout: 3 horizontal lanes (top to bottom)
 * 1. Process Lane: Detektieren → Bewerten → Alarm → Aktion → Feedback
 * 2. Mixed (no lane bg): DSP Edge Box | ALARM Box | Target Box — aligned to Process steps
 *    - DSP: from left to X of Evaluate step peak
 *    - Alarm: width = Alarm step width
 *    - Target: from Act step start to end
 * 3. Shopfloor Lane: Trigger + Detector (individual boxes left) | Systems+Devices (right, 700x220 like UC-03)
 *
 * Lane heights aligned with UC-03 for good vertical fill.
 */

export interface Uc05ProcessStep {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey: string;
}

export interface Uc05MixedBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey?: string;
  type: 'dsp-edge' | 'alarm' | 'target';
}

/** UC-05 Shopfloor left: Stimmgabel (trigger) + Vibrationssensor (detector) as separate boxes; right: Systems/Devices like UC-03 */
export const UC05_SHOPFLOOR_ICONS = {
  trigger: 'tuningFork' as const,
  detector: 'vibrationSensor' as const,
  systems: ['agv', 'scada'] as const,
  devices: ['mill', 'drill', 'aiqs', 'hbw'] as const,
} as const;

export interface Uc05ShopfloorBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
}

/** Single icon box for Trigger or Detector */
export interface Uc05ShopfloorIconBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  iconKey: 'trigger' | 'detector';
}

export interface Uc05Structure {
  viewBox: { width: number; height: number };
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };
  laneProcess: { x: number; y: number; width: number; height: number };
  processSteps: Uc05ProcessStep[];
  /** Mixed area (no rect drawn) – vertical space for 3 boxes, same as UC-03 DSP lane */
  mixedArea: { x: number; y: number; width: number; height: number };
  mixedBoxes: Uc05MixedBox[];
  laneShopfloor: { x: number; y: number; width: number; height: number };
  /** Left: Trigger box */
  shopfloorTriggerBox: Uc05ShopfloorIconBox;
  /** Signal triangle (Trigger→Detector): vertical lines in triangular arrangement */
  shopfloorSignalTriangle: { x: number; y: number; width: number; height: number };
  /** Detector box (shifted right of signal triangle) */
  shopfloorDetectorBox: Uc05ShopfloorIconBox;
  /** Right: Systems+Devices box, same size as UC-03 Shopfloor 2 (700x220) */
  shopfloorSystemsDevicesBox: Uc05ShopfloorBox;
}

const UC05_DESCRIPTION_HEIGHT = 50;

export function createUc05Structure(): Uc05Structure {
  const vbW = 1920;
  const vbH = 1080;
  const laneX = 40;
  const laneW = vbW - 80;

  // Lane heights aligned with UC-03
  const laneProcessH = 280;
  const laneMixedH = 290; // same as UC-03 DSP lane
  const laneShopfloorH = 280;

  const laneProcessY = 88 + UC05_DESCRIPTION_HEIGHT;
  const laneMixedY = laneProcessY + laneProcessH + 12;
  const laneShopfloorY = laneMixedY + laneMixedH + 12;

  // Process: 5 steps (like UC-03: stepW 340, stepH 140)
  const stepW = 340;
  const stepH = 140;
  const stepGap = 0;
  const totalProcessWidth = stepW * 5 + stepGap * 4;
  const processStartX = laneX + (laneW - totalProcessWidth) / 2;
  const processStepY = laneProcessY + (laneProcessH - stepH) / 2;

  const processSteps: Uc05ProcessStep[] = [
    { id: 'proc_detect', x: processStartX, y: processStepY, width: stepW, height: stepH, titleKey: 'uc05.proc.detect', bulletsKey: 'uc05.proc.detect.bullets' },
    { id: 'proc_evaluate', x: processStartX + (stepW + stepGap), y: processStepY, width: stepW, height: stepH, titleKey: 'uc05.proc.evaluate', bulletsKey: 'uc05.proc.evaluate.bullets' },
    { id: 'proc_alarm', x: processStartX + (stepW + stepGap) * 2, y: processStepY, width: stepW, height: stepH, titleKey: 'uc05.proc.alarm', bulletsKey: 'uc05.proc.alarm.bullets' },
    { id: 'proc_action', x: processStartX + (stepW + stepGap) * 3, y: processStepY, width: stepW, height: stepH, titleKey: 'uc05.proc.action', bulletsKey: 'uc05.proc.action.bullets' },
    { id: 'proc_feedback', x: processStartX + (stepW + stepGap) * 4, y: processStepY, width: stepW, height: stepH, titleKey: 'uc05.proc.feedback', bulletsKey: 'uc05.proc.feedback.bullets' },
  ];

  // Mixed boxes – nach unten vergrößert: Abstand zu Shopfloor = Abstand zu Process
  const boxGap = 12;
  const mixedBoxY = laneMixedY + 10; // 10px von oben
  const gapToProcess = mixedBoxY - (laneProcessY + laneProcessH);
  const mixedBoxH = laneShopfloorY - mixedBoxY - gapToProcess; // Abstand unten = Abstand oben

  // DSP: X = laneX (optische Linie), rechte Kante bis Evaluate-Spitze minus 50px
  const dspX = laneX;
  const evaluatePeakX = processStartX + 2 * stepW;
  const dspW = evaluatePeakX - dspX - 50; // Breite -50px (ohne boxGap)

  // Alarm: mittig unter Alarm-Step, Breite = Höhe (quadratisch)
  const alarmW = mixedBoxH;
  const alarmStepCenterX = processStartX + 2 * stepW + stepW / 2;
  const alarmX = alarmStepCenterX - alarmW / 2;

  // Target: rechter Rand = rechter Rand Process/Shopfloor Lane, Breite = DSP-Breite
  const targetRightX = laneX + laneW;
  const targetW = dspW;
  const targetX = targetRightX - targetW;

  const mixedBoxes: Uc05MixedBox[] = [
    { id: 'mixed_dsp_edge', x: dspX, y: mixedBoxY, width: dspW, height: mixedBoxH, titleKey: 'uc05.mixed.dspEdge', bulletsKey: 'uc05.mixed.dspEdge.bullets', type: 'dsp-edge' },
    { id: 'mixed_alarm', x: alarmX, y: mixedBoxY, width: alarmW, height: mixedBoxH, titleKey: 'uc05.mixed.alarm', type: 'alarm' },
    { id: 'mixed_target', x: targetX, y: mixedBoxY, width: targetW, height: mixedBoxH, titleKey: 'uc05.mixed.target', bulletsKey: 'uc05.mixed.target.bullets', type: 'target' },
  ];

  // Shopfloor: Überschrift links; Trigger, Signal, Detector +60px nach rechts
  const sfPad = 24;
  const sfShiftRight = 60;
  const sfSystemsDevicesW = 700;
  const sfSystemsDevicesH = 220;
  const sfSystemsDevicesY = laneShopfloorY + (laneShopfloorH - sfSystemsDevicesH) / 2;
  const sfSystemsDevicesX = laneX + laneW - sfPad - sfSystemsDevicesW;

  const iconBoxW = 160;
  const iconBoxH = 160;
  const detectorBoxW = 200; // vergrößert für zwei Icons nebeneinander
  const detectorBoxH = 180;
  const iconBoxY = laneShopfloorY + (laneShopfloorH - iconBoxH) / 2;
  const detectorBoxY = laneShopfloorY + (laneShopfloorH - detectorBoxH) / 2;
  const iconBoxGap = 12;

  // Dreiecksanordnung nimmt Platz des bisherigen Detectors ein
  const signalTriangleW = iconBoxW;
  const signalTriangleH = iconBoxH;

  const shopfloorTriggerBox: Uc05ShopfloorIconBox = {
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

  const shopfloorDetectorBox: Uc05ShopfloorIconBox = {
    id: 'sf_detector',
    x: laneX + sfPad + sfShiftRight + iconBoxW + iconBoxGap + signalTriangleW + iconBoxGap,
    y: detectorBoxY,
    width: detectorBoxW,
    height: detectorBoxH,
    iconKey: 'detector',
  };

  const shopfloorSystemsDevicesBox: Uc05ShopfloorBox = {
    id: 'sf_systems_devices',
    x: sfSystemsDevicesX,
    y: sfSystemsDevicesY,
    width: sfSystemsDevicesW,
    height: sfSystemsDevicesH,
    titleKey: 'uc05.sf.systemsDevicesTitle',
  };

  return {
    viewBox: { width: vbW, height: vbH },
    title: { x: vbW / 2, y: 42, key: 'uc05.title' },
    subtitle: { x: vbW / 2, y: 74, key: 'uc05.subtitle' },
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
