/**
 * UC-06 Process Optimization: Structure Configuration
 *
 * Layout: 3 horizontal lanes (wie UC-04/05) – optimaler vertikaler Platz
 * 1. Process Lane: Observe → Analyze → Recommend → Simulate → Execute → Feedback
 * 2. Mixed: DSP | Recommendation/Simulation | Target (MES/ERP/Planning) – gleiche Box-Größen wie UC-04
 * 3. Shopfloor Lane: Sources links (700×220, Systems & Devices) | Optimization Target rechts (dieselben Icons, Ziel der Ausführung)
 */

export interface Uc06ProcessStep {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey: string;
}

export interface Uc06MixedBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey?: string;
  type: 'dsp-edge' | 'recommendation' | 'target';
}

export interface Uc06ShopfloorBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
}

export interface Uc06ShopfloorTargetsBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
}

export interface Uc06Structure {
  viewBox: { width: number; height: number };
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  outcome: { x: number; y: number; key: string };
  footer: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };
  laneProcess: { x: number; y: number; width: number; height: number };
  processSteps: Uc06ProcessStep[];
  mixedArea: { x: number; y: number; width: number; height: number };
  mixedBoxes: Uc06MixedBox[];
  laneShopfloor: { x: number; y: number; width: number; height: number };
  shopfloorSourcesBox: Uc06ShopfloorBox;
  shopfloorTargetsBox: Uc06ShopfloorTargetsBox;
}

/** Connection element IDs for dim-conn styling */
export const UC06_CONNECTION_IDS: readonly string[] = [
  'uc06_conn_sources_dsp',
  'uc06_conn_dsp_recommend',
  'uc06_conn_recommend_target',
  'uc06_conn_recommend_execute',
  'uc06_conn_target_targets',
  'uc06_feedback',
];

const UC06_DESCRIPTION_HEIGHT = 50;

export function createUc06Structure(): Uc06Structure {
  const vbW = 1920;
  const vbH = 1080;
  const laneX = 40;
  const laneW = vbW - 80;

  // Lane-Höhen wie UC-04 für optimalen vertikalen Platz
  const laneProcessH = 280;
  const laneMixedH = 290;
  const laneShopfloorH = 280;

  const laneProcessY = 88 + UC06_DESCRIPTION_HEIGHT;
  const laneMixedY = laneProcessY + laneProcessH + 12;
  const laneShopfloorY = laneMixedY + laneMixedH + 12;

  // 6 Prozessschritte: stepW 300, stepH 140 (wie UC-04) – passt in 1840
  const stepW = 300;
  const stepH = 140;
  const stepGap = 4;
  const totalProcessWidth = stepW * 6 + stepGap * 5;
  const processStartX = laneX + (laneW - totalProcessWidth) / 2;
  const processStepY = laneProcessY + (laneProcessH - stepH) / 2;

  const processSteps: Uc06ProcessStep[] = [
    { id: 'proc_observe', x: processStartX, y: processStepY, width: stepW, height: stepH, titleKey: 'uc06.proc.observe', bulletsKey: 'uc06.proc.observe.bullets' },
    { id: 'proc_analyze', x: processStartX + (stepW + stepGap), y: processStepY, width: stepW, height: stepH, titleKey: 'uc06.proc.analyze', bulletsKey: 'uc06.proc.analyze.bullets' },
    { id: 'proc_recommend', x: processStartX + (stepW + stepGap) * 2, y: processStepY, width: stepW, height: stepH, titleKey: 'uc06.proc.recommend', bulletsKey: 'uc06.proc.recommend.bullets' },
    { id: 'proc_simulate', x: processStartX + (stepW + stepGap) * 3, y: processStepY, width: stepW, height: stepH, titleKey: 'uc06.proc.simulate', bulletsKey: 'uc06.proc.simulate.bullets' },
    { id: 'proc_execute', x: processStartX + (stepW + stepGap) * 4, y: processStepY, width: stepW, height: stepH, titleKey: 'uc06.proc.execute', bulletsKey: 'uc06.proc.execute.bullets' },
    { id: 'proc_feedback', x: processStartX + (stepW + stepGap) * 5, y: processStepY, width: stepW, height: stepH, titleKey: 'uc06.proc.feedback', bulletsKey: 'uc06.proc.feedback.bullets' },
  ];

  // Mixed boxes: gleiche Größen wie UC-04 (dspW 700, zentrales Element quadratisch, target 700)
  const boxGap = 12;
  const mixedBoxY = laneMixedY + 10;
  const gapToProcess = mixedBoxY - (laneProcessY + laneProcessH);
  const mixedBoxH = laneShopfloorY - mixedBoxY - gapToProcess;

  const dspX = laneX;
  const dspW = 700;

  const recommendW = mixedBoxH;
  const recommendCenterX = processStartX + 2.5 * (stepW + stepGap) + stepW / 2;
  const recommendX = recommendCenterX - recommendW / 2;

  const targetRightX = laneX + laneW;
  const targetW = dspW;
  const targetX = targetRightX - targetW;

  const mixedBoxes: Uc06MixedBox[] = [
    { id: 'mixed_dsp', x: dspX, y: mixedBoxY, width: dspW, height: mixedBoxH, titleKey: 'uc06.mixed.dsp', bulletsKey: 'uc06.mixed.dsp.bullets', type: 'dsp-edge' },
    { id: 'mixed_recommend', x: recommendX, y: mixedBoxY, width: recommendW, height: mixedBoxH, titleKey: 'uc06.mixed.recommend', type: 'recommendation' },
    { id: 'mixed_target', x: targetX, y: mixedBoxY, width: targetW, height: mixedBoxH, titleKey: 'uc06.mixed.target', bulletsKey: 'uc06.mixed.target.bullets', type: 'target' },
  ];

  // Shopfloor: links Sources (Systems & Devices) | rechts Optimization Target (dieselben Icons, Ziel)
  const sfPad = 24;
  const sfBoxW = 700;
  const sfBoxH = 220;
  const sfGap = 60;
  const sfBoxY = laneShopfloorY + (laneShopfloorH - sfBoxH) / 2;

  const shopfloorSourcesBox: Uc06ShopfloorBox = {
    id: 'sf_sources',
    x: laneX + sfPad,
    y: sfBoxY,
    width: sfBoxW,
    height: sfBoxH,
    titleKey: 'uc06.sf.sourcesTitle',
  };

  const shopfloorTargetsBox: Uc06ShopfloorTargetsBox = {
    id: 'sf_targets',
    x: laneX + laneW - sfPad - sfBoxW,
    y: sfBoxY,
    width: sfBoxW,
    height: sfBoxH,
    titleKey: 'uc06.sf.targetsTitle',
  };

  return {
    viewBox: { width: vbW, height: vbH },
    title: { x: vbW / 2, y: 42, key: 'uc06.title' },
    subtitle: { x: vbW / 2, y: 74, key: 'uc06.subtitle' },
    outcome: { x: vbW / 2, y: 110, key: 'uc06.outcome' },
    footer: { x: vbW / 2, y: vbH - 20, key: 'uc06.footer' },
    stepDescription: { x: vbW / 2, y: 20, width: 1400, height: 100 },

    laneProcess: { x: laneX, y: laneProcessY, width: laneW, height: laneProcessH },
    processSteps,

    mixedArea: { x: laneX, y: laneMixedY, width: laneW, height: laneMixedH },
    mixedBoxes,

    laneShopfloor: { x: laneX, y: laneShopfloorY, width: laneW, height: laneShopfloorH },
    shopfloorSourcesBox,
    shopfloorTargetsBox,
  };
}
