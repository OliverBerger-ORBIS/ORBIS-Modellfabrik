/**
 * UC-02 Three Data Pools: Structure Configuration
 *
 * Based on UC-02_3-Data-Pools_Concept.drawio
 * Layout: Sources (left) → DSP (center) → Targets (right)
 * Sources: Business, Shopfloor, Environment (3 cylinders)
 * DSP: Container with Normalize → Enrich → Correlate
 * Targets: Analytics & AI, BI / Data Lake, Closed Loop / ERP
 */

export interface Uc02Source {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  subtitleKey: string;
}

export interface Uc02DspStep {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  subtitleKey: string;
}

export interface Uc02Target {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  textKey: string;
}

export interface Uc02Structure {
  viewBox: { width: number; height: number };
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };
  sources: Uc02Source[];
  containerDsp: { x: number; y: number; width: number; height: number };
  dspSteps: Uc02DspStep[];
  note: { x: number; y: number; width: number; height: number; textKey: string };
  targets: Uc02Target[];
  footer: { x: number; y: number; key: string };
}

/**
 * Creates UC-02 structure based on Concept Draw.io
 * ViewBox 1920x1080, DSP centered, steps stacked vertically with arrows pointing down
 */
export function createUc02Structure(): Uc02Structure {
  const vbW = 1920;
  const vbH = 1080;
  const centerX = vbW / 2;

  const containerDspW = 525; // +25% (420 * 1.25)
  const containerDspH = 744; // +20% (620 * 1.2)
  const containerDspX = centerX - containerDspW / 2;
  const containerDspY = 140;

  const stepW = 340;
  const stepH = 120;
  const stepX = containerDspX + (containerDspW - stepW) / 2;
  // Steps evenly distributed in DSP container (Draw.io: ~22%, 53%, 83% of container)
  const step1Y = containerDspY + 80;
  const step2Y = containerDspY + containerDspH / 2 - stepH / 2;
  const step3Y = containerDspY + containerDspH - stepH - 80;

  return {
    viewBox: { width: vbW, height: vbH },
    title: { x: vbW / 2, y: 48, key: 'uc02.title' },
    subtitle: { x: vbW / 2, y: 82, key: 'uc02.subtitle' },
    stepDescription: { x: vbW / 2, y: 20, width: 1400, height: 100 },

    sources: [
      { id: 'src_business', x: 80, y: 200, width: 220, height: 140, titleKey: 'uc02.src.business', subtitleKey: 'uc02.src.business.sub' },
      { id: 'src_shopfloor', x: 80, y: 420, width: 220, height: 140, titleKey: 'uc02.src.shopfloor', subtitleKey: 'uc02.src.shopfloor.sub' },
      { id: 'src_env', x: 80, y: 640, width: 220, height: 140, titleKey: 'uc02.src.env', subtitleKey: 'uc02.src.env.sub' },
    ],

    containerDsp: { x: containerDspX, y: containerDspY, width: containerDspW, height: containerDspH },

    dspSteps: [
      { id: 'step_normalize', x: stepX, y: step1Y, width: stepW, height: stepH, titleKey: 'uc02.step.normalize', subtitleKey: 'uc02.step.normalize.sub' },
      { id: 'step_enrich', x: stepX, y: step2Y, width: stepW, height: stepH, titleKey: 'uc02.step.enrich', subtitleKey: 'uc02.step.enrich.sub' },
      { id: 'step_correlate', x: stepX, y: step3Y, width: stepW, height: stepH, titleKey: 'uc02.step.correlate', subtitleKey: 'uc02.step.correlate.sub' },
    ],

    note: { x: centerX + 320, y: 150, width: 160, height: 90, textKey: 'uc02.note.context' },

    targets: [
      { id: 'tgt_analytics', x: 1480, y: 200, width: 300, height: 140, textKey: 'uc02.tgt.analytics' },
      { id: 'tgt_bi', x: 1480, y: 420, width: 300, height: 140, textKey: 'uc02.tgt.bi' },
      { id: 'tgt_closed_loop', x: 1480, y: 640, width: 300, height: 140, textKey: 'uc02.tgt.closed_loop' },
    ],

    footer: { x: vbW / 2, y: vbH - 35, key: 'uc02.footer' },
  };
}
