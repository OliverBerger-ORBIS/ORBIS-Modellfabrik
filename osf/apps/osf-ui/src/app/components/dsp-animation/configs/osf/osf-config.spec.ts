import { OSF_CONFIG } from './osf-config';

describe('OSF_CONFIG', () => {
  it('should use sf-system-sensor only for OSF (not sf-system-any)', () => {
    const ids = OSF_CONFIG.sfSystems.map((s) => s.id);
    expect(ids).toContain('sf-system-sensor');
    expect(ids).not.toContain('sf-system-any');
  });

  it('should include sensor-station-system icon key', () => {
    const sensor = OSF_CONFIG.sfSystems.find((s) => s.id === 'sf-system-sensor');
    expect(sensor?.iconKey).toBe('sensor-station-system');
  });
});
