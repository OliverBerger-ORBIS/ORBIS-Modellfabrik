/**
 * OSF default customer config.
 *
 * This should always point to the "current demo" variant, while older event variants remain
 * available as separate customer configs (e.g. Hannover Messe, Customer Connect).
 */
import type { CustomerDspConfig } from '../types';
import { OSF_HANNOVER_2026_CONFIG } from './osf-hannover-2026-config';

export const OSF_CONFIG: CustomerDspConfig = {
  ...OSF_HANNOVER_2026_CONFIG,
  customerKey: 'osf',
  customerName: 'ORBIS Smart Factory (Demo)',
};
