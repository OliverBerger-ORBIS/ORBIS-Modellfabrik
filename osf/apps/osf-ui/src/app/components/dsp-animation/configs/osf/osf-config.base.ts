/**
 * OSF (ORBIS Smart Factory) base customer mapping.
 *
 * Variants (LogiMAT / Hannover / Customer Connect) should import this base config and only
 * override customerKey/customerName and, if needed, bpProcesses ordering/contents.
 */
import type { CustomerDspConfig } from '../types';
import { FMF_CONFIG } from '../fmf/fmf-config';
import { LOGIMAT_CONFIG } from '../logimat/logimat-config';

export const OSF_BASE_CONFIG: CustomerDspConfig = {
  customerKey: 'osf-base',
  customerName: 'ORBIS Smart Factory (Base)',
  sfDevices: FMF_CONFIG.sfDevices.map((d) => ({ ...d })),
  sfSystems: [
    {
      id: 'sf-system-sensor',
      label: $localize`:@@dspArchLabelSensorStation:Sensor Station`,
      iconKey: 'sensor-station-system',
    },
    {
      id: 'sf-system-fts',
      label: $localize`:@@dspArchLabelFTS:AGV\nSystem`,
      iconKey: 'agv-system',
    },
  ],
  // Start from the LogiMAT business layer (ORBIS MES/EWM/etc.), variants may override.
  bpProcesses: LOGIMAT_CONFIG.bpProcesses.map((bp) => ({ ...bp })),
  customerLogoPath: 'assets/customers/fmf/logo.svg',
};

