/**
 * UC-01 Track & Trace Genealogy — Partiture Structure Configuration
 *
 * Based on Draw.io: Track-Trace_Concept_Partiture.drawio
 * ViewBox: 1920 × 1080 (16:9 Landscape)
 *
 * Structure:
 *   3 horizontal lanes (Business Context | Trace & Genealogy | Shopfloor & Enrichment)
 *   NFC Thread connecting 8 station nodes
 *   Business boxes (PO, SO, CO, PROD) → join lines to stations
 *   Enrichment boxes (AGV, OEE, CFG, CAM, TEMP) → join lines to stations
 *   Phase brackets (Procurement, Production Fulfillment)
 *
 * Naming: uc01_ prefix, consistent with ICONS registry and ORBIS_COLORS
 */

import { ORBIS_COLORS } from '../../../assets/color-palette';

// ===== Color Constants (Draw.io → ORBIS_COLORS.diagram mapping) =====
// All colors reference ORBIS_COLORS.diagram for consistent cross-diagram changes.
// UC-01-specific overrides can be added as additional properties below.

const D = ORBIS_COLORS.diagram;

export const UC01_COLORS = {
  // Lane backgrounds — mapped from ORBIS_COLORS.diagram
  laneBusinessFill: D.laneBusinessFill,
  laneBusinessStroke: D.laneBusinessStroke,
  laneTraceFill: D.laneTraceFill,
  laneTraceStroke: D.laneTraceStroke,
  laneShopfloorFill: D.laneShopfloorFill,
  laneShopfloorStroke: D.laneShopfloorStroke,
  // Station nodes
  nodeDefault: D.nodeDefault,
  nodeParallel: D.nodeParallel,
  nodeStroke: D.nodeStroke,
  // NFC Thread
  threadCyan: D.threadCyan,
  // Connections
  joinStroke: D.connectionStroke,
  agvParallelStroke: D.connectionAlert,
  // Text
  textDark: ORBIS_COLORS.orbisNightBlue,
  // Box
  boxFill: D.boxFill,
  boxStroke: D.boxStroke,
} as const;

// ===== Interfaces =====

export interface Uc01Lane {
  id: string;
  x: number; y: number; width: number; height: number;
  fill: string; stroke: string; rx: number;
  titleKey: string;
  titleX: number; titleY: number;
}

export interface Uc01StationNode {
  id: string;
  labelKey: string;
  cx: number; cy: number; r: number;
  fill: string; stroke: string;
  isParallel: boolean;
  /** Icon key from ICONS.shopfloor.stations (for future: replace circle with station icon) */
  iconKey?: string;
}

export interface Uc01Badge {
  id: string;
  cx: number; cy: number; r: number;
  text: string;
  nearNodeId: string;
}

export interface Uc01Box {
  id: string;
  x: number; y: number; width: number; height: number;
  textKey: string;
  fill: string; stroke: string; rx: number;
}

export interface Uc01Thread {
  x1: number; y1: number; x2: number; y2: number;
  color: string; strokeWidth: number;
  labelLine1Key: string;
  labelLine2Key: string;
  labelX: number; labelY: number; labelWidth: number; labelHeight: number;
}

export interface Uc01Connection {
  id: string;
  path: string;           // SVG <path d="..."> attribute
  dashed: boolean;
  color: string;
  strokeWidth: number;
  dashPattern?: string;   // e.g. '5,5' or '8,8'
  /** Correlation ID (e.g. [PO-ID]) on join; drawn near Business Context */
  labelKey?: string;
  labelX?: number;
  labelY?: number;
}

export interface Uc01Phase {
  id: string;
  textKey: string;
  bracketX: number;       // Start X of bracket
  bracketWidth: number;
  bracketY: number;       // Y position (within business lane, below boxes)
}

export interface Uc01Structure {
  viewBox: { width: number; height: number };
  title: { x: number; y: number; key: string };
  subtitle: { x: number; y: number; key: string };
  outcome: { x: number; y: number; key: string };
  stepDescription: { x: number; y: number; width: number; height: number };

  lanes: Uc01Lane[];
  thread: Uc01Thread;
  timeArrow: { x: number; y: number; key: string };
  stationNodes: Uc01StationNode[];
  badges: Uc01Badge[];
  businessBoxes: Uc01Box[];
  enrichmentBoxes: Uc01Box[];
  joinConnections: Uc01Connection[];
  enrichConnections: Uc01Connection[];
  agvConnections: Uc01Connection[];
  agvParallelConnections: Uc01Connection[];
  phases: Uc01Phase[];
  legend: { x: number; y: number; width: number; height: number; textKey: string };
  footer: { x: number; y: number; key: string };
}

// ===== Structure Factory =====

/** Vertical offset: shift diagram content down so step description (y 20–120) does not overlap Business lane */
const UC01_CONTENT_OFFSET = 35;

export function createUc01Structure(): Uc01Structure {
  const C = UC01_COLORS;
  const o = UC01_CONTENT_OFFSET;

  return {
    viewBox: { width: 1920, height: 1080 },

    title: { x: 960, y: 52, key: 'uc01.title' },
    subtitle: { x: 960, y: 78, key: 'uc01.subtitle' },
    outcome: { x: 960, y: 110, key: 'uc01.outcome' },
    footer: { x: 960, y: 1080 - 24, key: 'uc01.footer' },
    stepDescription: { x: 960, y: 20, width: 1400, height: 160 },

    // ───── 3 Horizontal Lanes ─────
    lanes: [
      {
        id: 'business',
        x: 40, y: 90 + o, width: 1840, height: 220,
        fill: C.laneBusinessFill, stroke: C.laneBusinessStroke, rx: 12,
        titleKey: 'uc01.lane.business',
        titleX: 60, titleY: 120 + o,
      },
      {
        id: 'trace',
        x: 40, y: 320 + o, width: 1840, height: 380,
        fill: C.laneTraceFill, stroke: C.laneTraceStroke, rx: 12,
        titleKey: 'uc01.lane.trace',
        titleX: 60, titleY: 350 + o,
      },
      {
        id: 'shopfloor',
        x: 40, y: 710 + o, width: 1840, height: 250,
        fill: C.laneShopfloorFill, stroke: C.laneShopfloorStroke, rx: 12,
        titleKey: 'uc01.lane.shopfloor',
        titleX: 60, titleY: 755 + o,
      },
    ],

    // ───── NFC Thread (horizontal line through trace lane) ─────
    thread: {
      x1: 144, y1: 504 + o, x2: 1524, y2: 504 + o,
      color: C.threadCyan, strokeWidth: 12,
      labelLine1Key: 'uc01.thread.line1',
      labelLine2Key: 'uc01.thread.line2',
      // Narrow chip, start after thread line ends (1524) so cyan trace stays visible
      labelX: 1540,
      labelY: 486 + o,
      labelWidth: 280,
      labelHeight: 68,
    },

    // ───── Time Arrow ─────
    timeArrow: { x: 60, y: 375 + o, key: 'uc01.time_arrow' },

    // ───── 8 Station Nodes (circles on thread, from Draw.io) ─────
    stationNodes: [
      { id: 'dps_in',   labelKey: 'uc01.node.dps',      cx: 192,  cy: 500 + o, r: 44, fill: C.nodeDefault,  stroke: C.nodeStroke, isParallel: false, iconKey: 'dps' },
      { id: 'mill_par', labelKey: 'uc01.node.mill_par',  cx: 362,  cy: 500 + o, r: 44, fill: C.nodeParallel, stroke: C.nodeStroke, isParallel: true,  iconKey: 'mill' },
      { id: 'hbw',      labelKey: 'uc01.node.hbw',       cx: 542,  cy: 500 + o, r: 44, fill: C.nodeDefault,  stroke: C.nodeStroke, isParallel: false, iconKey: 'hbw' },
      { id: 'aiqs_par', labelKey: 'uc01.node.aiqs_par',  cx: 722,  cy: 500 + o, r: 44, fill: C.nodeParallel, stroke: C.nodeStroke, isParallel: true,  iconKey: 'aiqs' },
      { id: 'drill',    labelKey: 'uc01.node.drill',     cx: 902,  cy: 500 + o, r: 44, fill: C.nodeDefault,  stroke: C.nodeStroke, isParallel: false, iconKey: 'drill' },
      { id: 'dps_par',  labelKey: 'uc01.node.dps_par',   cx: 1082, cy: 500 + o, r: 44, fill: C.nodeParallel, stroke: C.nodeStroke, isParallel: true,  iconKey: 'dps' },
      { id: 'aiqs',     labelKey: 'uc01.node.aiqs',      cx: 1262, cy: 500 + o, r: 44, fill: C.nodeDefault,  stroke: C.nodeStroke, isParallel: false, iconKey: 'aiqs' },
      { id: 'dps_out',  labelKey: 'uc01.node.dps_out',   cx: 1442, cy: 500 + o, r: 44, fill: C.nodeDefault,  stroke: C.nodeStroke, isParallel: false, iconKey: 'dps' },
    ],

    // ───── Badges (parallel job markers ①) ─────
    badges: [
      { id: 'badge_mill', cx: 382, cy: 434 + o, r: 20, text: '1', nearNodeId: 'mill_par' },
      { id: 'badge_aiqs', cx: 742, cy: 434 + o, r: 20, text: '1', nearNodeId: 'aiqs_par' },
      { id: 'badge_dps',  cx: 1102, cy: 434 + o, r: 20, text: '1', nearNodeId: 'dps_par' },
    ],

    // ───── Business Boxes (in Business Context lane) ─────
    businessBoxes: [
      { id: 'po',   x: 125, y: 150 + o, width: 160, height: 68, textKey: 'uc01.biz.po',   fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
      { id: 'so',   x: 320, y: 150 + o, width: 160, height: 68, textKey: 'uc01.biz.so',   fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
      { id: 'co',   x: 550, y: 150 + o, width: 160, height: 68, textKey: 'uc01.biz.co',   fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
      { id: 'prod', x: 754, y: 150 + o, width: 180, height: 68, textKey: 'uc01.biz.prod', fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
    ],

    // ───── Enrichment Boxes (in Shopfloor lane) ─────
    enrichmentBoxes: [
      { id: 'agv',  x: 260,  y: 790 + o, width: 160, height: 88, textKey: 'uc01.enrich.agv',  fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
      { id: 'oee',  x: 650,  y: 790 + o, width: 160, height: 88, textKey: 'uc01.enrich.oee',  fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
      { id: 'cfg',  x: 954,  y: 790 + o, width: 160, height: 88, textKey: 'uc01.enrich.cfg',  fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
      { id: 'cam',  x: 1180, y: 786 + o, width: 160, height: 88, textKey: 'uc01.enrich.cam',  fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
      { id: 'temp', x: 1367, y: 770 + o, width: 160, height: 88, textKey: 'uc01.enrich.temp', fill: C.boxFill, stroke: C.boxStroke, rx: 12 },
    ],

    // ───── Join Connections (Business → Stations, dashed) ─────
    joinConnections: [
      {
        id: 'join_po_dps',
        path: `M 205 ${218 + o} L 205 ${360 + o} L 192 ${360 + o} L 192 ${456 + o}`,
        dashed: true,
        color: C.joinStroke,
        strokeWidth: 1,
        labelKey: 'uc01.join.id.po',
        labelX: 205,
        labelY: 289 + o,
      },
      {
        id: 'join_so_dps',
        path: `M 400 ${218 + o} L 400 ${360 + o} L 214 ${360 + o} L 214 ${456 + o}`,
        dashed: true,
        color: C.joinStroke,
        strokeWidth: 1,
        labelKey: 'uc01.join.id.so',
        labelX: 400,
        labelY: 289 + o,
      },
      {
        id: 'join_co_hbw',
        path: `M 630 ${218 + o} L 630 ${360 + o} L 542 ${360 + o} L 542 ${456 + o}`,
        dashed: true,
        color: C.joinStroke,
        strokeWidth: 1,
        labelKey: 'uc01.join.id.co',
        labelX: 630,
        labelY: 289 + o,
      },
      {
        id: 'join_prod_hbw',
        path: `M 844 ${218 + o} L 844 ${360 + o} L 542 ${360 + o} L 542 ${456 + o}`,
        dashed: true,
        color: C.joinStroke,
        strokeWidth: 1,
        labelKey: 'uc01.join.id.prod',
        labelX: 844,
        labelY: 289 + o,
      },
    ],

    // ───── Enrichment Connections (Enrichment → Stations, dashed) ─────
    enrichConnections: [
      { id: 'enrich_temp_dps',  path: `M 1447 ${770 + o} L 1447 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
      { id: 'enrich_cam_aiqs',  path: `M 1260 ${786 + o} L 1260 ${600 + o} L 1262 ${600 + o} L 1262 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
      { id: 'enrich_oee_drill', path: `M 730 ${790 + o} L 730 ${600 + o} L 902 ${600 + o} L 902 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
      { id: 'enrich_cfg_drill', path: `M 1034 ${790 + o} L 1034 ${600 + o} L 902 ${600 + o} L 902 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
    ],

    // ───── AGV Connections (normal, dashed) ─────
    agvConnections: [
      { id: 'agv_dps_in',  path: `M 340 ${790 + o} L 340 ${600 + o} L 192 ${600 + o} L 192 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
      { id: 'agv_hbw',     path: `M 340 ${790 + o} L 340 ${600 + o} L 542 ${600 + o} L 542 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
      { id: 'agv_drill',   path: `M 340 ${790 + o} L 340 ${600 + o} L 902 ${600 + o} L 902 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
      { id: 'agv_aiqs',    path: `M 340 ${790 + o} L 340 ${600 + o} L 1262 ${600 + o} L 1262 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
      { id: 'agv_dps_out', path: `M 340 ${790 + o} L 340 ${600 + o} L 1442 ${600 + o} L 1442 ${544 + o}`, dashed: true, color: C.joinStroke, strokeWidth: 1 },
    ],

    // ───── AGV Parallel Connections (red, dashed) ─────
    agvParallelConnections: [
      { id: 'agv_par_mill', path: `M 410 ${856 + o} L 450 ${856 + o} L 450 ${650 + o} L 362 ${650 + o} L 362 ${544 + o}`, dashed: true, color: C.agvParallelStroke, strokeWidth: 1, dashPattern: '8,8' },
      { id: 'agv_par_aiqs', path: `M 410 ${856 + o} L 620 ${856 + o} L 620 ${650 + o} L 722 ${650 + o} L 722 ${544 + o}`, dashed: true, color: C.agvParallelStroke, strokeWidth: 1, dashPattern: '8,8' },
      { id: 'agv_par_dps',  path: `M 410 ${856 + o} L 620 ${856 + o} L 620 ${650 + o} L 1082 ${650 + o} L 1082 ${544 + o}`, dashed: true, color: C.agvParallelStroke, strokeWidth: 1, dashPattern: '8,8' },
    ],

    // ───── Phase Brackets (between business boxes and trace lane) ─────
    phases: [
      { id: 'phase_procurement', textKey: 'uc01.phase.procurement', bracketX: 89,  bracketWidth: 362, bracketY: 267 + o },
      { id: 'phase_production',  textKey: 'uc01.phase.production',  bracketX: 528, bracketWidth: 984, bracketY: 267 + o },
    ],

    // ───── Legend ─────
    // Top-right of business lane; y high enough to clear phase brackets (Phase 2 ends ~1512 x)
    legend: {
      x: 1480, y: 100 + o, width: 400, height: 158,
      textKey: 'uc01.legend',
    },
  };
}
