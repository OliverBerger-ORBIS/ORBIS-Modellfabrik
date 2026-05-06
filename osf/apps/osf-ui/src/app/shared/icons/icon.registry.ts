import { VERSION } from '../../../environments/version';

/**
 * Cache-bust for `shopfloor/shared/*.svg` URLs. Uses `VERSION` from `environments/version.ts`
 * (written by `npm run update-version` from root `package.json` + current build date).
 *
 * Do not use a hand-maintained `?v=…` — it is easy to forget; run `npm run update-version`
 * after changing SVGs so `buildDate` (and/or `full` after a version bump) changes.
 */
function shopfloorSharedCacheQuery(): string {
  return `?v=${encodeURIComponent(`${VERSION.full}|${VERSION.buildDate}`)}`;
}

function sfShared(file: string): string {
  return `assets/svg/shopfloor/shared/${file}${shopfloorSharedCacheQuery()}`;
}

export const ICONS = {
  brand: {
    orbis: 'assets/svg/brand/orbis-logo.svg',
    sap: 'assets/svg/brand/sap-logo.svg',
    azure: 'assets/svg/brand/azure-logo.svg',
    microsoft: 'assets/svg/brand/microsoft-logo.svg',
    dsp: 'assets/svg/brand/orbis-dsp-logo.svg',
    grafana: 'assets/svg/brand/grafana-logo.svg',
  },
  shopfloor: {
    stations: {
      drill: 'assets/svg/shopfloor/stations/drill-station.svg',
      mill: 'assets/svg/shopfloor/stations/mill-station.svg',
      hbw: 'assets/svg/shopfloor/stations/hbw-station.svg',
      aiqs: 'assets/svg/shopfloor/stations/aiqs-station.svg',
      dps: 'assets/svg/shopfloor/stations/dps-station.svg',
      chrg: 'assets/svg/shopfloor/stations/chrg-station.svg',
      cnc: 'assets/svg/shopfloor/stations/cnc-station.svg',
      hydraulic: 'assets/svg/shopfloor/stations/hydraulic-station.svg',
      printer3d: 'assets/svg/shopfloor/stations/printer-3d-station.svg',
      weight: 'assets/svg/shopfloor/stations/weight-station.svg',
      laser: 'assets/svg/shopfloor/stations/laser-station.svg',
    },
    systems: {
      agv: sfShared('agv-vehicle.svg'),
      fts: sfShared('agv-vehicle.svg'), // alias for MQTT terminology
      any: 'assets/svg/shopfloor/systems/any-system.svg',
      sensorStation: 'assets/svg/shopfloor/systems/sensor-station-system.svg',
      factory: 'assets/svg/shopfloor/systems/factory-system.svg',
      warehouse: 'assets/svg/shopfloor/systems/warehouse-system.svg',
      scada: 'assets/svg/shopfloor/systems/scada-system.svg',
      industrialProcess: 'assets/svg/shopfloor/systems/industrial-process-system.svg',
      cargo: 'assets/svg/shopfloor/systems/cargo-system.svg',
      pump: 'assets/svg/shopfloor/systems/pump-system.svg',
    },
    intersections: {
      1: 'assets/svg/shopfloor/intersections/intersection-1.svg',
      2: 'assets/svg/shopfloor/intersections/intersection-2.svg',
      3: 'assets/svg/shopfloor/intersections/intersection-3.svg',
      4: 'assets/svg/shopfloor/intersections/intersection-4.svg',
    },
    shared: {
      agvVehicle: sfShared('agv-vehicle.svg'),
      question: sfShared('question.svg'),
      turnEvent: sfShared('turn-event.svg'),
      turnLeftEvent: sfShared('turn-left-event.svg'),
      turnRightEvent: sfShared('turn-right-event.svg'),
      dockEvent: sfShared('dock-event.svg'),
      passEvent: sfShared('pass-event.svg'),
      pickEvent: sfShared('pick-event.svg'),
      dropEvent: sfShared('drop-event.svg'),
      processEvent: sfShared('process-event.svg'),
      battery: sfShared('battery.svg'),
      drivingStatus: sfShared('driving-status.svg'),
      stoppedStatus: sfShared('stopped-status.svg'),
      pausedStatus: sfShared('paused-status.svg'),
      chargingActive: sfShared('charging-active.svg'),
      locationMarker: sfShared('location-marker.svg'),
      orderTracking: sfShared('order-tracking.svg'),
      temperatureSensor: sfShared('temperature-sensor.svg'),
      humiditySensor: sfShared('humidity-sensor.svg'),
      flameSensor: sfShared('flame-sensor.svg'),
      gasSensor: sfShared('gas-sensor.svg'),
      vibrationSensor: sfShared('vibration-sensor.svg'),
      tiltSensor: sfShared('tilt-sensor.svg'),
      tuningFork: sfShared('tuning-fork.svg'),
      pressureSensor: sfShared('pressure-sensor.svg'),
      alarm: sfShared('alarm.svg'),
      bellAlarm: sfShared('bell-alarm.svg'),
    },
    workpieces: {
      blue: {
        product: 'assets/svg/shopfloor/workpieces/wp-blue-product.svg',
        dim3: 'assets/svg/shopfloor/workpieces/wp-blue-3dim.svg',
        instockUnprocessed: 'assets/svg/shopfloor/workpieces/wp-blue-instock-unprocessed.svg',
        instockReserved: 'assets/svg/shopfloor/workpieces/wp-blue-instock-reserved.svg',
        instockProcessed: 'assets/svg/shopfloor/workpieces/wp-blue-instock-processed.svg',
      },
      white: {
        product: 'assets/svg/shopfloor/workpieces/wp-white-product.svg',
        dim3: 'assets/svg/shopfloor/workpieces/wp-white-3dim.svg',
        instockUnprocessed: 'assets/svg/shopfloor/workpieces/wp-white-instock-unprocessed.svg',
        instockReserved: 'assets/svg/shopfloor/workpieces/wp-white-instock-reserved.svg',
        instockProcessed: 'assets/svg/shopfloor/workpieces/wp-white-instock-processed.svg',
      },
      red: {
        product: 'assets/svg/shopfloor/workpieces/wp-red-product.svg',
        dim3: 'assets/svg/shopfloor/workpieces/wp-red-3dim.svg',
        instockUnprocessed: 'assets/svg/shopfloor/workpieces/wp-red-instock-unprocessed.svg',
        instockReserved: 'assets/svg/shopfloor/workpieces/wp-red-instock-reserved.svg',
        instockProcessed: 'assets/svg/shopfloor/workpieces/wp-red-instock-processed.svg',
      },
      slotEmpty: 'assets/svg/shopfloor/workpieces/wp-slot-empty.svg',
    },
  },
  dsp: {
    architecture: {
      uxBox: 'assets/svg/dsp/architecture/dsp-ux-box.svg',
      edgeBox: 'assets/svg/dsp/architecture/dsp-edge-box.svg',
      mcBox: 'assets/svg/dsp/architecture/dsp-mc-box.svg',
    },
    functions: {
      connectivity: 'assets/svg/dsp/functions/edge-connectivity.svg',
      digitalTwin: 'assets/svg/dsp/functions/edge-digital-twin.svg',
      processLogic: 'assets/svg/dsp/functions/edge-process-logic.svg',
      analytics: 'assets/svg/dsp/functions/edge-analytics.svg',
      buffering: 'assets/svg/dsp/functions/edge-buffering.svg',
      dataStorage: 'assets/svg/dsp/functions/edge-data-storage.svg',
      workflow: 'assets/svg/dsp/functions/edge-choreography.svg',
    },
    edgeComponents: {
      disc: 'assets/svg/dsp/edge-components/edge-disc.svg',
      eventBus: 'assets/svg/dsp/edge-components/edge-event-bus.svg',
      appServer: 'assets/svg/dsp/edge-components/edge-app-server.svg',
      router: 'assets/svg/dsp/edge-components/edge-router.svg',
      agent: 'assets/svg/dsp/edge-components/edge-agent.svg',
      logServer: 'assets/svg/dsp/edge-components/edge-log-server.svg',
      disi: 'assets/svg/dsp/edge-components/edge-disi.svg',
      database: 'assets/svg/dsp/edge-components/edge-database.svg',
    },
  },
  business: {
    erp: 'assets/svg/business/erp-application.svg',
    crm: 'assets/svg/business/crm-application.svg',
    scm: 'assets/svg/business/scm-application.svg',
    cloud: 'assets/svg/business/cloud-application.svg',
    analytics: 'assets/svg/business/analytics-application.svg',
    dataLake: 'assets/svg/business/data-lake-application.svg',
    mes: 'assets/svg/business/mes-application.svg',
    /** SAP EWM / warehouse management – business-layer icon (see ewm-application.svg) */
    ewm: 'assets/svg/business/ewm-application.svg',
  },
  methodology: {
    // Incremental development phases
    phase1: 'assets/svg/dsp/methodology/phase1-data-foundation.svg',
    phase2: 'assets/svg/dsp/methodology/phase2-data-integration.svg',
    phase3: 'assets/svg/dsp/methodology/phase3-advanced-analytics.svg',
    phase4: 'assets/svg/dsp/methodology/phase4-automation-orchestration.svg',
    phase5: 'assets/svg/dsp/methodology/phase5-autonomous-enterprise.svg',
  },
  ui: {
    orderProduction: 'assets/svg/ui/order-production.svg',
    orderStorage: 'assets/svg/ui/order-storage.svg',
    processFlow: 'assets/svg/ui/process-flow.svg',
  },
} as const;

export type IconRegistry = typeof ICONS;

