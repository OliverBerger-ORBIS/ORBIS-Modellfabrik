/**
 * OSF default customer config.
 *
 * OCC stays the canonical default profile, while older event variants remain
 * available as separate customer configs (e.g. Hannover Messe, Customer Connect).
 */
import type { CustomerDspConfig } from '../types';
import { OSF_OCC_2026_CONFIG } from './osf-occ-2026-config';

export const OSF_CONFIG: CustomerDspConfig = {
  ...OSF_OCC_2026_CONFIG,
  customerKey: 'osf',
  customerName: 'ORBIS Smart Factory (OCC Default)',
};
