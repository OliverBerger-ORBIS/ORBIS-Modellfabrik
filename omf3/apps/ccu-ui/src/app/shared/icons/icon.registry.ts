export const ICONS = {
  brand: {
    orbis: 'assets/svg/brand/orbis-logo.svg',
    sap: 'assets/svg/brand/sap-logo.svg',
    azure: 'assets/svg/brand/azure-logo.svg',
    dsp: 'assets/svg/brand/dsp-logo.svg',
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
    },
    systems: {
      agv: 'assets/svg/shopfloor/shared/agv-vehicle.svg',
      fts: 'assets/svg/shopfloor/shared/agv-vehicle.svg', // alias for MQTT terminology
      any: 'assets/svg/shopfloor/systems/any-system.svg',
      factory: 'assets/svg/shopfloor/systems/factory-system.svg',
      warehouse: 'assets/svg/shopfloor/systems/warehouse-system.svg',
    },
    intersections: {
      1: 'assets/svg/shopfloor/intersections/intersection-1.svg',
      2: 'assets/svg/shopfloor/intersections/intersection-2.svg',
      3: 'assets/svg/shopfloor/intersections/intersection-3.svg',
      4: 'assets/svg/shopfloor/intersections/intersection-4.svg',
    },
    shared: {
      agvVehicle: 'assets/svg/shopfloor/shared/agv-vehicle.svg',
      question: 'assets/svg/shopfloor/shared/question.svg',
      turnEvent: 'assets/svg/shopfloor/shared/turn-event.svg',
      dockEvent: 'assets/svg/shopfloor/shared/dock-event.svg',
      passEvent: 'assets/svg/shopfloor/shared/pass-event.svg',
      pickEvent: 'assets/svg/shopfloor/shared/pick-event.svg',
      dropEvent: 'assets/svg/shopfloor/shared/drop-event.svg',
      processEvent: 'assets/svg/shopfloor/shared/process-event.svg',
      battery: 'assets/svg/shopfloor/shared/battery.svg',
      drivingStatus: 'assets/svg/shopfloor/shared/driving-status.svg',
      stoppedStatus: 'assets/svg/shopfloor/shared/stopped-status.svg',
      pausedStatus: 'assets/svg/shopfloor/shared/paused-status.svg',
      chargingActive: 'assets/svg/shopfloor/shared/charging-active.svg',
      locationMarker: 'assets/svg/shopfloor/shared/location-marker.svg',
      orderTracking: 'assets/svg/shopfloor/shared/order-tracking.svg',
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
    dataLake: 'assets/svg/business/data-lake.svg',
    mes: 'assets/svg/business/mes-application.svg',
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

