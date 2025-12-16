import { ECME_CONFIG } from './ecme-config';

describe('ECME_CONFIG', () => {
  it('should be defined', () => {
    expect(ECME_CONFIG).toBeDefined();
  });

  it('should have correct customer key', () => {
    expect(ECME_CONFIG.customerKey).toBe('ecme');
  });

  it('should have correct customer name', () => {
    expect(ECME_CONFIG.customerName).toBe('European Company Manufacturing Everything');
  });

  describe('sfDevices', () => {
    it('should have exactly 5 device mappings', () => {
      expect(ECME_CONFIG.sfDevices).toBeDefined();
      expect(ECME_CONFIG.sfDevices.length).toBe(5);
    });

    it('should have cnc device', () => {
      const cnc = ECME_CONFIG.sfDevices.find(d => d.iconKey === 'cnc');
      expect(cnc).toBeDefined();
      expect(cnc?.customIconPath).toBe('device-cnc');
    });

    it('should have hydraulic device', () => {
      const hydraulic = ECME_CONFIG.sfDevices.find(d => d.iconKey === 'hydraulic');
      expect(hydraulic).toBeDefined();
      expect(hydraulic?.customIconPath).toBe('device-hydraulic');
    });

    it('should have printer-3d device', () => {
      const printer = ECME_CONFIG.sfDevices.find(d => d.iconKey === 'printer-3d');
      expect(printer).toBeDefined();
      expect(printer?.customIconPath).toBe('device-printer-3d');
    });

    it('should have weight device', () => {
      const weight = ECME_CONFIG.sfDevices.find(d => d.iconKey === 'weight');
      expect(weight).toBeDefined();
      expect(weight?.customIconPath).toBe('device-weight');
    });

    it('should have laser device', () => {
      const laser = ECME_CONFIG.sfDevices.find(d => d.iconKey === 'laser');
      expect(laser).toBeDefined();
      expect(laser?.customIconPath).toBe('device-laser');
    });

    it('should have all devices with valid IDs', () => {
      ECME_CONFIG.sfDevices.forEach(device => {
        expect(device.id).toBeTruthy();
        expect(device.id).toMatch(/^sf-device-/);
      });
    });

    it('should have all devices with labels', () => {
      ECME_CONFIG.sfDevices.forEach(device => {
        expect(device.label).toBeTruthy();
      });
    });

    it('should have all devices with icon keys', () => {
      ECME_CONFIG.sfDevices.forEach(device => {
        expect(device.iconKey).toBeTruthy();
      });
    });

    it('should have all devices with custom icon paths', () => {
      ECME_CONFIG.sfDevices.forEach(device => {
        expect(device.customIconPath).toBeTruthy();
      });
    });
  });

  describe('sfSystems', () => {
    it('should have exactly 4 system mappings', () => {
      expect(ECME_CONFIG.sfSystems).toBeDefined();
      expect(ECME_CONFIG.sfSystems.length).toBe(4);
    });

    it('should have scada system', () => {
      const scada = ECME_CONFIG.sfSystems.find(s => s.iconKey === 'scada');
      expect(scada).toBeDefined();
      expect(scada?.customIconPath).toBe('shopfloor-scada');
    });

    it('should have industrial-process system', () => {
      const industrial = ECME_CONFIG.sfSystems.find(s => s.iconKey === 'industrial-process');
      expect(industrial).toBeDefined();
      expect(industrial?.customIconPath).toBe('shopfloor-industrial-process');
    });

    it('should have cargo system', () => {
      const cargo = ECME_CONFIG.sfSystems.find(s => s.iconKey === 'cargo');
      expect(cargo).toBeDefined();
      expect(cargo?.customIconPath).toBe('shopfloor-cargo');
    });

    it('should have pump system', () => {
      const pump = ECME_CONFIG.sfSystems.find(s => s.iconKey === 'pump');
      expect(pump).toBeDefined();
      expect(pump?.customIconPath).toBe('shopfloor-pump');
    });

    it('should have all systems with valid IDs', () => {
      ECME_CONFIG.sfSystems.forEach(system => {
        expect(system.id).toBeTruthy();
        expect(system.id).toMatch(/^sf-system-/);
      });
    });

    it('should have all systems with labels', () => {
      ECME_CONFIG.sfSystems.forEach(system => {
        expect(system.label).toBeTruthy();
      });
    });

    it('should have all systems with icon keys', () => {
      ECME_CONFIG.sfSystems.forEach(system => {
        expect(system.iconKey).toBeTruthy();
      });
    });

    it('should have all systems with custom icon paths', () => {
      ECME_CONFIG.sfSystems.forEach(system => {
        expect(system.customIconPath).toBeTruthy();
      });
    });
  });

  describe('bpProcesses', () => {
    it('should have business process mappings', () => {
      expect(ECME_CONFIG.bpProcesses).toBeDefined();
      expect(ECME_CONFIG.bpProcesses.length).toBeGreaterThan(0);
    });

    it('should have 4 business processes (no bp-cloud)', () => {
      expect(ECME_CONFIG.bpProcesses.length).toBe(4);
      const cloudProcess = ECME_CONFIG.bpProcesses.find(bp => bp.id === 'bp-cloud');
      expect(cloudProcess).toBeUndefined();
    });

    it('should have ERP process with Alpha-X logo', () => {
      const erp = ECME_CONFIG.bpProcesses.find(bp => bp.id === 'bp-erp');
      expect(erp).toBeDefined();
      expect(erp?.iconKey).toBe('erp');
      expect(erp?.brandLogoKey).toBe('alpha-x');
    });

    it('should have Data Platform with Azure logo', () => {
      const dataLake = ECME_CONFIG.bpProcesses.find(bp => bp.id === 'bp-data-lake');
      expect(dataLake).toBeDefined();
      expect(dataLake?.iconKey).toBe('cloud');
      expect(dataLake?.brandLogoKey).toBe('azure');
    });

    it('should have Analytics process with PowerBI logo', () => {
      const analytics = ECME_CONFIG.bpProcesses.find(bp => bp.id === 'bp-analytics');
      expect(analytics).toBeDefined();
      expect(analytics?.iconKey).toBe('analytics');
      expect(analytics?.brandLogoKey).toBe('powerbi');
    });

    it('should have all processes with valid IDs', () => {
      ECME_CONFIG.bpProcesses.forEach(process => {
        expect(process.id).toBeTruthy();
        expect(process.id).toMatch(/^bp-/);
      });
    });

    it('should have all processes with labels', () => {
      ECME_CONFIG.bpProcesses.forEach(process => {
        expect(process.label).toBeTruthy();
      });
    });

    it('should have all processes with icon keys', () => {
      ECME_CONFIG.bpProcesses.forEach(process => {
        expect(process.iconKey).toBeTruthy();
      });
    });

    it('should have all processes with brand logo keys', () => {
      ECME_CONFIG.bpProcesses.forEach(process => {
        expect(process.brandLogoKey).toBeTruthy();
      });
    });
  });

  it('should have customer logo path', () => {
    expect(ECME_CONFIG.customerLogoPath).toBeDefined();
    expect(ECME_CONFIG.customerLogoPath).toContain('ecme');
  });

  it('should demonstrate different equipment than FMF', () => {
    const deviceIconKeys = ECME_CONFIG.sfDevices.map(d => d.iconKey);
    // ECME should have cnc, hydraulic, printer-3d, weight, laser which are different from FMF
    const uniqueDevices = deviceIconKeys.filter(key => 
      ['cnc', 'hydraulic', 'printer-3d', 'weight', 'laser'].includes(key)
    );
    expect(uniqueDevices.length).toBeGreaterThan(0);
  });
});
