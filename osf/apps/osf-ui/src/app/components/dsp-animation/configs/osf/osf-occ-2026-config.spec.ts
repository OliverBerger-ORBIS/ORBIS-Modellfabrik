import { OSF_OCC_2026_CONFIG } from './osf-occ-2026-config';

describe('OSF_OCC_2026_CONFIG', () => {
  it('should be defined', () => {
    expect(OSF_OCC_2026_CONFIG).toBeDefined();
  });

  it('should define OCC business process order', () => {
    expect(OSF_OCC_2026_CONFIG.bpProcesses.map((bp) => bp.id)).toEqual([
      'bp-erp',
      'bp-mes',
      'bp-ewm',
      'bp-crm',
      'bp-analytics',
      'bp-data-lake',
    ]);
  });

  it('should use microsoft branding for CRM', () => {
    const crm = OSF_OCC_2026_CONFIG.bpProcesses.find((bp) => bp.id === 'bp-crm');
    expect(crm?.brandLogoKey).toBe('microsoft');
    expect(crm?.customIconPath).toBe('crm-application');
  });
});

