import { DEF_CONFIG } from './def-config';

describe('DEF_CONFIG', () => {
  it('should be defined', () => {
    expect(DEF_CONFIG).toBeDefined();
  });

  it('should have correct customer key', () => {
    expect(DEF_CONFIG.customerKey).toBe('def');
  });

  it('should have correct customer name', () => {
    expect(DEF_CONFIG.customerName).toBe('Digital Engineering Facility');
  });

  describe('sfDevices', () => {
    it('should have device mappings', () => {
      expect(DEF_CONFIG.sfDevices).toBeDefined();
      expect(DEF_CONFIG.sfDevices.length).toBeGreaterThan(0);
    });

    it('should have laser device (different from FMF)', () => {
      const laser = DEF_CONFIG.sfDevices.find(d => d.iconKey === 'laser');
      expect(laser).toBeDefined();
    });

    it('should have cnc device (different from FMF)', () => {
      const cnc = DEF_CONFIG.sfDevices.find(d => d.iconKey === 'cnc');
      expect(cnc).toBeDefined();
    });

    it('should have 3D printer device (different from FMF)', () => {
      const printer = DEF_CONFIG.sfDevices.find(d => d.iconKey === 'printer-3d');
      expect(printer).toBeDefined();
    });

    it('should have all devices with valid IDs', () => {
      DEF_CONFIG.sfDevices.forEach(device => {
        expect(device.id).toBeTruthy();
        expect(device.id).toMatch(/^sf-device-/);
      });
    });

    it('should have all devices with labels', () => {
      DEF_CONFIG.sfDevices.forEach(device => {
        expect(device.label).toBeTruthy();
      });
    });

    it('should have all devices with icon keys', () => {
      DEF_CONFIG.sfDevices.forEach(device => {
        expect(device.iconKey).toBeTruthy();
      });
    });
  });

  describe('sfSystems', () => {
    it('should have system mappings', () => {
      expect(DEF_CONFIG.sfSystems).toBeDefined();
      expect(DEF_CONFIG.sfSystems.length).toBeGreaterThan(0);
    });

    it('should have all systems with valid IDs', () => {
      DEF_CONFIG.sfSystems.forEach(system => {
        expect(system.id).toBeTruthy();
        expect(system.id).toMatch(/^sf-system-/);
      });
    });

    it('should have all systems with labels', () => {
      DEF_CONFIG.sfSystems.forEach(system => {
        expect(system.label).toBeTruthy();
      });
    });

    it('should have all systems with icon keys', () => {
      DEF_CONFIG.sfSystems.forEach(system => {
        expect(system.iconKey).toBeTruthy();
      });
    });
  });

  describe('bpProcesses', () => {
    it('should have business process mappings', () => {
      expect(DEF_CONFIG.bpProcesses).toBeDefined();
      expect(DEF_CONFIG.bpProcesses.length).toBeGreaterThan(0);
    });

    it('should have ERP process with Alpha-X logo (different from FMF)', () => {
      const erp = DEF_CONFIG.bpProcesses.find(bp => bp.id === 'bp-erp');
      expect(erp).toBeDefined();
      expect(erp?.iconKey).toBe('erp');
      expect(erp?.brandLogoKey).toBe('alpha-x');
    });

    it('should have Cloud process with Azure logo (different from FMF)', () => {
      const cloud = DEF_CONFIG.bpProcesses.find(bp => bp.id === 'bp-cloud');
      expect(cloud).toBeDefined();
      expect(cloud?.iconKey).toBe('cloud');
      expect(cloud?.brandLogoKey).toBe('azure');
    });

    it('should have Analytics process with PowerBI logo (different from FMF)', () => {
      const analytics = DEF_CONFIG.bpProcesses.find(bp => bp.id === 'bp-analytics');
      expect(analytics).toBeDefined();
      expect(analytics?.iconKey).toBe('analytics');
      expect(analytics?.brandLogoKey).toBe('powerbi');
    });

    it('should use different brand logos than FMF', () => {
      const defBrands = DEF_CONFIG.bpProcesses.map(bp => bp.brandLogoKey);
      expect(defBrands).toContain('azure');
      expect(defBrands).toContain('powerbi');
      expect(defBrands).toContain('alpha-x');
    });

    it('should have all processes with valid IDs', () => {
      DEF_CONFIG.bpProcesses.forEach(process => {
        expect(process.id).toBeTruthy();
        expect(process.id).toMatch(/^bp-/);
      });
    });

    it('should have all processes with labels', () => {
      DEF_CONFIG.bpProcesses.forEach(process => {
        expect(process.label).toBeTruthy();
      });
    });

    it('should have all processes with icon keys', () => {
      DEF_CONFIG.bpProcesses.forEach(process => {
        expect(process.iconKey).toBeTruthy();
      });
    });

    it('should have all processes with brand logo keys', () => {
      DEF_CONFIG.bpProcesses.forEach(process => {
        expect(process.brandLogoKey).toBeTruthy();
      });
    });
  });

  it('should have customer logo path', () => {
    expect(DEF_CONFIG.customerLogoPath).toBeDefined();
    expect(DEF_CONFIG.customerLogoPath).toContain('def');
  });

  it('should demonstrate different equipment than FMF', () => {
    const deviceIconKeys = DEF_CONFIG.sfDevices.map(d => d.iconKey);
    // DEF should have laser, cnc, printer-3d which are different from FMF
    const uniqueDevices = deviceIconKeys.filter(key => 
      ['laser', 'cnc', 'printer-3d'].includes(key)
    );
    expect(uniqueDevices.length).toBeGreaterThan(0);
  });
});
