import { getIconPath, ICONS } from '../../../assets/icon-registry';
import type { IconKey } from '../../../assets/icon-registry';
import { ECME_CONFIG } from './ecme/ecme-config';
import { FMF_CONFIG } from './fmf/fmf-config';
import { LOGIMAT_CONFIG } from './logimat/logimat-config';
import { OSF_CUSTOMER_CONNECT_2026_CONFIG } from './osf/osf-customer-connect-2026-config';
import { OSF_HANNOVER_2026_CONFIG } from './osf/osf-hannover-2026-config';
import { OSF_OCC_2026_CONFIG } from './osf/osf-occ-2026-config';
import { OSF_CONFIG } from './osf/osf-config';
import type { CustomerDspConfig } from './types';

const CUSTOMER_CONFIGS: CustomerDspConfig[] = [
  FMF_CONFIG,
  LOGIMAT_CONFIG,
  OSF_CUSTOMER_CONNECT_2026_CONFIG,
  OSF_HANNOVER_2026_CONFIG,
  OSF_OCC_2026_CONFIG,
  OSF_CONFIG,
  ECME_CONFIG,
];

describe('customIconPath mappings', () => {
  it('resolve all configured customIconPath values to non-fallback icons', () => {
    const fallback = ICONS.shopfloor.shared.question;
    const customIconPaths = new Set<string>();

    for (const config of CUSTOMER_CONFIGS) {
      for (const device of config.sfDevices) {
        if (device.customIconPath) customIconPaths.add(device.customIconPath);
      }
      for (const system of config.sfSystems) {
        if (system.customIconPath) customIconPaths.add(system.customIconPath);
      }
      for (const process of config.bpProcesses) {
        if (process.customIconPath) customIconPaths.add(process.customIconPath);
      }
    }

    for (const iconPathKey of customIconPaths) {
      expect(getIconPath(iconPathKey as IconKey)).not.toBe(fallback);
    }
  });
});

