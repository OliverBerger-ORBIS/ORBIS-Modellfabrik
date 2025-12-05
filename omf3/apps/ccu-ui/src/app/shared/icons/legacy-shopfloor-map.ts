/**
 * Mapping alter Shopfloor-Asset-Pfade (public/shopfloor/*.svg) auf neue Struktur unter assets/svg/.
 * Wenn kein Eintrag gefunden wird, wird der Pfad unverändert zurückgegeben.
 */
const LEGACY_MAP: Record<string, string> = {
  'shopfloor/bohrer.svg': 'assets/svg/shopfloor/stations/drill-station.svg',
  'shopfloor/milling-machine.svg': 'assets/svg/shopfloor/stations/mill-station.svg',
  'shopfloor/stock.svg': 'assets/svg/shopfloor/stations/hbw-station.svg',
  'shopfloor/ai-assistant.svg': 'assets/svg/shopfloor/stations/aiqs-station.svg',
  'shopfloor/robot-arm.svg': 'assets/svg/shopfloor/stations/dps-station.svg',
  'shopfloor/fuel.svg': 'assets/svg/shopfloor/stations/chrg-station.svg',
  'shopfloor/conveyor.svg': 'assets/svg/shopfloor/stations/conveyor.svg',
  'shopfloor/mixer.svg': 'assets/svg/shopfloor/stations/mixer.svg',
  'shopfloor/stone-oven.svg': 'assets/svg/shopfloor/stations/stone-oven.svg',
  'shopfloor/hbw.svg': 'assets/svg/shopfloor/stations/hbw-station.svg',
  'shopfloor/aiqs.svg': 'assets/svg/shopfloor/stations/aiqs-station.svg',
  'shopfloor/intersection.svg': 'assets/svg/shopfloor/shared/question.svg',

  'shopfloor/robotic.svg': 'assets/svg/shopfloor/shared/agv-vehicle.svg',
  'shopfloor/battery.svg': 'assets/svg/shopfloor/shared/battery.svg',
  'shopfloor/driving-status.svg': 'assets/svg/shopfloor/shared/driving-status.svg',
  'shopfloor/stopped-status.svg': 'assets/svg/shopfloor/shared/stopped-status.svg',
  'shopfloor/paused-status.svg': 'assets/svg/shopfloor/shared/paused-status.svg',
  'shopfloor/charging-active.svg': 'assets/svg/shopfloor/shared/charging-active.svg',
  'shopfloor/location-marker.svg': 'assets/svg/shopfloor/shared/location-marker.svg',
  'shopfloor/order-tracking.svg': 'assets/svg/shopfloor/shared/order-tracking.svg',
  'shopfloor/question.svg': 'assets/svg/shopfloor/shared/question.svg',
  'shopfloor/pass-event.svg': 'assets/svg/shopfloor/shared/pass-event.svg',
  'shopfloor/pick-event.svg': 'assets/svg/shopfloor/shared/pick-event.svg',
  'shopfloor/drop-event.svg': 'assets/svg/shopfloor/shared/drop-event.svg',
  'shopfloor/dock-event.svg': 'assets/svg/shopfloor/shared/dock-event.svg',
  'shopfloor/turn-event.svg': 'assets/svg/shopfloor/shared/turn-event.svg',
  'shopfloor/process-event.svg': 'assets/svg/shopfloor/shared/process-event.svg',
  'shopfloor/information-technology.svg': 'assets/svg/brand/dsp-logo.svg',
  'shopfloor/factory.svg': 'assets/svg/shopfloor/systems/factory.svg',
  'shopfloor/warehouse.svg': 'assets/svg/shopfloor/systems/warehouse.svg',
  'shopfloor/ORBIS_logo_RGB.svg': 'assets/svg/brand/orbis-logo.svg',
};

export function resolveLegacyShopfloorPath(path: string | undefined): string {
  if (!path) return 'assets/svg/shopfloor/shared/question.svg';
  const clean = path.startsWith('/') ? path.slice(1) : path;
  return LEGACY_MAP[clean] ?? clean;
}

