/**
 * OSF (ORBIS Smart Factory) default customer: LogiMAT-style business layer (ORBIS MES, EWM, …),
 * shopfloor with Sensor Station (Arduino) + FTS instead of generic “any system”.
 */
import type { CustomerDspConfig } from '../types';
import { FMF_CONFIG } from '../fmf/fmf-config';
import { LOGIMAT_CONFIG } from '../logimat/logimat-config';

export const OSF_CONFIG: CustomerDspConfig = {
  customerKey: 'osf',
  customerName: 'ORBIS Smart Factory (Demo)',
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
  bpProcesses: LOGIMAT_CONFIG.bpProcesses.map((bp) => ({ ...bp })),
  customerLogoPath: 'assets/customers/fmf/logo.svg',
};
