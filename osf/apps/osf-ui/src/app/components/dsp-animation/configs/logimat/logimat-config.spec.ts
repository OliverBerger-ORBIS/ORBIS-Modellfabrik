import { LOGIMAT_CONFIG } from './logimat-config';

describe('LOGIMAT_CONFIG', () => {
  it('should be defined', () => {
    expect(LOGIMAT_CONFIG).toBeDefined();
  });

  it('should have correct customer key', () => {
    expect(LOGIMAT_CONFIG.customerKey).toBe('logimat');
  });

  it('should include bp-ewm and not bp-cloud', () => {
    const ids = LOGIMAT_CONFIG.bpProcesses.map((bp) => bp.id);
    expect(ids).toContain('bp-ewm');
    expect(ids).not.toContain('bp-cloud');
  });

  it('should have EWM with ewm-application icon path', () => {
    const ewm = LOGIMAT_CONFIG.bpProcesses.find((bp) => bp.id === 'bp-ewm');
    expect(ewm?.customIconPath).toBe('ewm-application');
    expect(ewm?.brandLogoKey).toBe('sap');
  });
});
