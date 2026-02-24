/**
 * UC-02 Architecture Lanes: Structure Configuration
 *
 * Layout: 3 horizontal lanes (top to bottom): Analytics → DSP → Data
 * Fills viewBox 1920x1080 like UC-01 (lanes use 90–900)
 * Same semantic IDs as Concept for animation compatibility.
 */

export interface Uc02LanesSource {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  subtitleKey: string;
}

export interface Uc02LanesDspStep {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  titleKey: string;
  subtitleKey: string;
}

export interface Uc02LanesTarget {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  textKey: string;
}

export interface Uc02LanesStructure {
  viewBox: { width: number; height: number };
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  outcome: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };
  laneAnalytics: { x: number; y: number; width: number; height: number };
  targets: Uc02LanesTarget[];
  laneDsp: { x: number; y: number; width: number; height: number };
  dspSteps: Uc02LanesDspStep[];
  note: { x: number; y: number; width: number; height: number; textKey: string };
  laneData: { x: number; y: number; width: number; height: number };
  sources: Uc02LanesSource[];
  footer: { x: number; y: number; key: string };
}

/** Vertical offset: shift lanes down so step description (y 20–120) does not overlap Analytics lane */
const UC02_LANES_CONTENT_OFFSET = 35;

/**
 * Creates UC-02 Architecture Lanes structure
 * ViewBox 1920x1080, lanes use full height (no footer); content offset for description clearance
 */
export function createUc02LanesStructure(): Uc02LanesStructure {
  const vbW = 1920;
  const vbH = 1080;
  const o = UC02_LANES_CONTENT_OFFSET;

  const laneX = 40;
  const laneW = vbW - 80;

  // Lane heights; use extra space from removed footer (~35px) for taller lanes
  const laneAnalyticsH = 310;
  const laneDspH = 310;
  const laneDataH = 295;

  const laneAnalyticsY = 90 + o;
  const laneDspY = laneAnalyticsY + laneAnalyticsH + 10;
  const laneDataY = laneDspY + laneDspH + 10;

  return {
    viewBox: { width: vbW, height: vbH },
    title: { x: vbW / 2, y: 42, key: 'uc02.title' },
    subtitle: { x: vbW / 2, y: 74, key: 'uc02.subtitle' },    outcome: { x: vbW / 2, y: 104, key: 'uc02.outcome' },    stepDescription: { x: vbW / 2, y: 20, width: 1400, height: 100 },

    laneAnalytics: { x: laneX, y: laneAnalyticsY, width: laneW, height: laneAnalyticsH },
    targets: [
      { id: 'tgt_analytics', x: 220, y: laneAnalyticsY + 75, width: 380, height: 140, textKey: 'uc02.tgt.analytics' },
      { id: 'tgt_bi', x: 770, y: laneAnalyticsY + 75, width: 380, height: 140, textKey: 'uc02.tgt.bi' },
      { id: 'tgt_closed_loop', x: 1320, y: laneAnalyticsY + 75, width: 380, height: 140, textKey: 'uc02.tgt.closed_loop' },
    ],

    laneDsp: { x: laneX, y: laneDspY, width: laneW, height: laneDspH },
    dspSteps: [
      { id: 'step_normalize', x: 220, y: laneDspY + 85, width: 380, height: 120, titleKey: 'uc02.step.normalize', subtitleKey: 'uc02.step.normalize.sub' },
      { id: 'step_enrich', x: 770, y: laneDspY + 85, width: 380, height: 120, titleKey: 'uc02.step.enrich', subtitleKey: 'uc02.step.enrich.sub' },
      { id: 'step_correlate', x: 1320, y: laneDspY + 85, width: 380, height: 120, titleKey: 'uc02.step.correlate', subtitleKey: 'uc02.step.correlate.sub' },
    ],
    note: { x: laneX + 20, y: laneDspY + laneDspH - 100, width: 180, height: 80, textKey: 'uc02.note.context' },

    laneData: { x: laneX, y: laneDataY, width: laneW, height: laneDataH },
    sources: [
      { id: 'src_shopfloor', x: 220, y: laneDataY + 55, width: 380, height: 156, titleKey: 'uc02.src.shopfloor', subtitleKey: 'uc02.src.shopfloor.sub' },
      { id: 'src_business', x: 770, y: laneDataY + 55, width: 380, height: 156, titleKey: 'uc02.src.business', subtitleKey: 'uc02.src.business.sub' },
      { id: 'src_env', x: 1320, y: laneDataY + 55, width: 380, height: 156, titleKey: 'uc02.src.env', subtitleKey: 'uc02.src.env.sub' },
    ],

    footer: { x: vbW / 2, y: vbH - 35, key: 'uc02.footer' },
  };
}
