/**
 * UC-03 AI Lifecycle: Structure Configuration
 *
 * Layout: 3 horizontal lanes (top to bottom): Process → DSP → Shopfloor
 * 5 Process steps: Data Capture → Context → Train → Validate → Monitor
 * DSP Edge boxes aligned above Shopfloor boxes for vertical-only connections
 */

export interface Uc03ProcessStep {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey: string;
}

export interface Uc03DspBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  bulletsKey: string;
  /** Icon key for Edge/MC (edgeBox, mcBox) */
  iconKey?: 'edgeBox' | 'mcBox';
}

/** DSP-style: 2 Systems + 4 Devices (reduced icon set per spec) */
export const UC03_SHOPFLOOR_ICONS = {
  systems: ['agv', 'scada'] as const,
  devices: ['mill', 'drill', 'aiqs', 'hbw'] as const,
} as const;

export interface Uc03ShopfloorBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
}

export interface Uc03Structure {
  viewBox: { width: number; height: number };
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };
  laneProcess: { x: number; y: number; width: number; height: number };
  processSteps: Uc03ProcessStep[];
  laneDsp: { x: number; y: number; width: number; height: number };
  dspBoxes: Uc03DspBox[];
  laneShopfloor: { x: number; y: number; width: number; height: number };
  shopfloorBoxes: Uc03ShopfloorBox[];
}

/** Connection element IDs for dim-conn styling (lighter opacity than dim) */
export const UC03_CONNECTION_IDS: readonly string[] = [
  'uc03_conn_train_cockpit',
  'uc03_conn_cockpit_edge1',
  'uc03_conn_cockpit_edge2',
  'uc03_conn_edge1_sf1',
  'uc03_conn_edge2_sf2',
  'uc03_feedback',
];

/** Vertical offset for step description – lanes start below, shifted up so Shopfloor fully visible */
const UC03_DESCRIPTION_HEIGHT = 50;

/**
 * Creates UC-03 AI Lifecycle structure
 * ViewBox 1920x1080, lanes shifted up for full visibility including Shopfloor
 */
export function createUc03Structure(): Uc03Structure {
  const vbW = 1920;
  const vbH = 1080;
  const laneX = 40;
  const laneW = vbW - 80;

  // Lane heights; layout fits in 1080 with description space
  const laneProcessH = 280;
  const laneDspH = 290;
  const laneShopfloorH = 280;

  const laneProcessY = 88 + UC03_DESCRIPTION_HEIGHT;
  const laneDspY = laneProcessY + laneProcessH + 12;
  const laneShopfloorY = laneDspY + laneDspH + 12;

  // Process: 5 step boxes – Data Capture, Context, Train, Validate, Monitor; reduced gap for compact layout
  const stepW = 340;
  const stepH = 140;
  const stepGap = 0;
  const totalProcessWidth = stepW * 5 + stepGap * 4;
  const processStartX = laneX + (laneW - totalProcessWidth) / 2;
  const processStepY = laneProcessY + (laneProcessH - stepH) / 2;

  const processSteps: Uc03ProcessStep[] = [
    { id: 'proc_capture', x: processStartX, y: processStepY, width: stepW, height: stepH, titleKey: 'uc03.proc.capture', bulletsKey: 'uc03.proc.capture.bullets' },
    { id: 'proc_context', x: processStartX + (stepW + stepGap), y: processStepY, width: stepW, height: stepH, titleKey: 'uc03.proc.context', bulletsKey: 'uc03.proc.context.bullets' },
    { id: 'proc_train', x: processStartX + (stepW + stepGap) * 2, y: processStepY, width: stepW, height: stepH, titleKey: 'uc03.proc.train', bulletsKey: 'uc03.proc.train.bullets' },
    { id: 'proc_validate', x: processStartX + (stepW + stepGap) * 3, y: processStepY, width: stepW, height: stepH, titleKey: 'uc03.proc.validate', bulletsKey: 'uc03.proc.validate.bullets' },
    { id: 'proc_monitor', x: processStartX + (stepW + stepGap) * 4, y: processStepY, width: stepW, height: stepH, titleKey: 'uc03.proc.monitor', bulletsKey: 'uc03.proc.monitor.bullets' },
  ];

  // Shopfloor: 2 boxes – Edge 1 left-aligned, Edge 2 right-aligned; width 700 (620+80)
  const sfBoxW = 700;
  const sfBoxH = 220;
  const sfPad = 24;
  const sfBoxY = laneShopfloorY + (laneShopfloorH - sfBoxH) / 2;

  const sf1Cx = laneX + sfPad + sfBoxW / 2;
  const sf2Cx = laneX + laneW - sfPad - sfBoxW / 2;

  const shopfloorBoxes: Uc03ShopfloorBox[] = [
    { id: 'sf_systems_devices_edge1', x: laneX + sfPad, y: sfBoxY, width: sfBoxW, height: sfBoxH, titleKey: 'uc03.sf.shopfloor1' },
    { id: 'sf_systems_devices_edge2', x: laneX + laneW - sfPad - sfBoxW, y: sfBoxY, width: sfBoxW, height: sfBoxH, titleKey: 'uc03.sf.shopfloor2' },
  ];

  // DSP: Edge1 and Edge2 centered above SF1/SF2 for vertical-only connections; Cockpit in middle
  const dspEdgeW = 380;
  const dspMcW = 360;
  const dspBoxH = 200;
  const dspBoxY = laneDspY + (laneDspH - dspBoxH) / 2;

  const edge1X = sf1Cx - dspEdgeW / 2;
  const edge2X = sf2Cx - dspEdgeW / 2;
  const cockpitX = laneX + laneW / 2 - dspMcW / 2;

  const dspBoxes: Uc03DspBox[] = [
    { id: 'dsp_edge_1', x: edge1X, y: dspBoxY, width: dspEdgeW, height: dspBoxH, titleKey: 'uc03.dsp.edge1', bulletsKey: 'uc03.dsp.edge.bullets', iconKey: 'edgeBox' },
    { id: 'dsp_cockpit', x: cockpitX, y: dspBoxY, width: dspMcW, height: dspBoxH, titleKey: 'uc03.dsp.cockpit', bulletsKey: 'uc03.dsp.cockpit.bullets', iconKey: 'mcBox' },
    { id: 'dsp_edge_2', x: edge2X, y: dspBoxY, width: dspEdgeW, height: dspBoxH, titleKey: 'uc03.dsp.edge2', bulletsKey: 'uc03.dsp.edge.bullets', iconKey: 'edgeBox' },
  ];

  return {
    viewBox: { width: vbW, height: vbH },
    title: { x: vbW / 2, y: 42, key: 'uc03.title' },
    subtitle: { x: vbW / 2, y: 74, key: 'uc03.subtitle' },
    stepDescription: { x: vbW / 2, y: 20, width: 1400, height: 100 },

    laneProcess: { x: laneX, y: laneProcessY, width: laneW, height: laneProcessH },
    processSteps,

    laneDsp: { x: laneX, y: laneDspY, width: laneW, height: laneDspH },
    dspBoxes,

    laneShopfloor: { x: laneX, y: laneShopfloorY, width: laneW, height: laneShopfloorH },
    shopfloorBoxes,
  };
}
