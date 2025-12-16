import { FMF_CONFIG } from './fmf-config';

describe('FMF_CONFIG', () => {
  it('should be defined', () => {
    expect(FMF_CONFIG).toBeDefined();
  });

  it('should have correct customer key', () => {
    expect(FMF_CONFIG.customerKey).toBe('fmf');
  });

  it('should have correct customer name', () => {
    expect(FMF_CONFIG.customerName).toBe('Fischertechnik Modellfabrik');
  });

  describe('sfDevices', () => {
    it('should have device mappings', () => {
      expect(FMF_CONFIG.sfDevices).toBeDefined();
      expect(FMF_CONFIG.sfDevices.length).toBeGreaterThan(0);
    });

    it('should have 6 devices', () => {
      expect(FMF_CONFIG.sfDevices.length).toBe(6);
    });

    it('should have mill device with abstract ID', () => {
      const mill = FMF_CONFIG.sfDevices.find(d => d.iconKey === 'mill');
      expect(mill).toBeDefined();
      expect(mill?.id).toBe('sf-device-1');
      expect(mill?.label).toBeTruthy();
    });

    it('should have drill device with abstract ID', () => {
      const drill = FMF_CONFIG.sfDevices.find(d => d.iconKey === 'drill');
      expect(drill).toBeDefined();
      expect(drill?.id).toBe('sf-device-2');
      expect(drill?.label).toBeTruthy();
    });

    it('should have hbw device with abstract ID', () => {
      const hbw = FMF_CONFIG.sfDevices.find(d => d.iconKey === 'hbw');
      expect(hbw).toBeDefined();
      expect(hbw?.id).toBe('sf-device-4');
      expect(hbw?.label).toBeTruthy();
    });

    it('should have conveyor device with abstract ID', () => {
      const conveyor = FMF_CONFIG.sfDevices.find(d => d.iconKey === 'conveyor');
      expect(conveyor).toBeDefined();
      expect(conveyor?.id).toBe('sf-device-5');
      expect(conveyor?.label).toBeTruthy();
    });

    it('should have robot-arm devices', () => {
      const robotDevices = FMF_CONFIG.sfDevices.filter(d => d.iconKey === 'robot-arm');
      expect(robotDevices.length).toBeGreaterThan(0);
    });

    it('should have all devices with valid IDs', () => {
      FMF_CONFIG.sfDevices.forEach(device => {
        expect(device.id).toBeTruthy();
        expect(device.id).toMatch(/^sf-device-/);
      });
    });

    it('should have all devices with labels', () => {
      FMF_CONFIG.sfDevices.forEach(device => {
        expect(device.label).toBeTruthy();
      });
    });

    it('should have all devices with icon keys', () => {
      FMF_CONFIG.sfDevices.forEach(device => {
        expect(device.iconKey).toBeTruthy();
      });
    });
  });

  describe('sfSystems', () => {
    it('should have system mappings', () => {
      expect(FMF_CONFIG.sfSystems).toBeDefined();
      expect(FMF_CONFIG.sfSystems.length).toBeGreaterThan(0);
    });

    it('should have 2 systems', () => {
      expect(FMF_CONFIG.sfSystems.length).toBe(2);
    });

    it('should have warehouse system with abstract ID', () => {
      const warehouse = FMF_CONFIG.sfSystems.find(s => s.iconKey === 'warehouse-system');
      expect(warehouse).toBeDefined();
      expect(warehouse?.id).toBe('sf-system-1');
      expect(warehouse?.label).toBeTruthy();
    });

    it('should have AGV system with abstract ID', () => {
      const agv = FMF_CONFIG.sfSystems.find(s => s.iconKey === 'agv');
      expect(agv).toBeDefined();
      expect(agv?.id).toBe('sf-system-2');
      expect(agv?.label).toBeTruthy();
    });

    it('should have all systems with valid IDs', () => {
      FMF_CONFIG.sfSystems.forEach(system => {
        expect(system.id).toBeTruthy();
        expect(system.id).toMatch(/^sf-system-/);
      });
    });

    it('should have all systems with labels', () => {
      FMF_CONFIG.sfSystems.forEach(system => {
        expect(system.label).toBeTruthy();
      });
    });

    it('should have all systems with icon keys', () => {
      FMF_CONFIG.sfSystems.forEach(system => {
        expect(system.iconKey).toBeTruthy();
      });
    });
  });

  describe('bpProcesses', () => {
    it('should have business process mappings', () => {
      expect(FMF_CONFIG.bpProcesses).toBeDefined();
      expect(FMF_CONFIG.bpProcesses.length).toBeGreaterThan(0);
    });

    it('should have ERP process with SAP logo', () => {
      const erp = FMF_CONFIG.bpProcesses.find(bp => bp.id === 'bp-erp');
      expect(erp).toBeDefined();
      expect(erp?.iconKey).toBe('erp');
      expect(erp?.brandLogoKey).toBe('sap');
    });

    it('should have MES process with SAP logo', () => {
      const mes = FMF_CONFIG.bpProcesses.find(bp => bp.id === 'bp-mes');
      expect(mes).toBeDefined();
      expect(mes?.iconKey).toBe('mes');
      expect(mes?.brandLogoKey).toBe('sap');
    });

    it('should have Cloud process with AWS logo', () => {
      const cloud = FMF_CONFIG.bpProcesses.find(bp => bp.id === 'bp-cloud');
      expect(cloud).toBeDefined();
      expect(cloud?.iconKey).toBe('cloud');
      expect(cloud?.brandLogoKey).toBe('aws');
    });

    it('should have Analytics process with Grafana logo', () => {
      const analytics = FMF_CONFIG.bpProcesses.find(bp => bp.id === 'bp-analytics');
      expect(analytics).toBeDefined();
      expect(analytics?.iconKey).toBe('analytics');
      expect(analytics?.brandLogoKey).toBe('grafana');
    });

    it('should have Data Lake process', () => {
      const dataLake = FMF_CONFIG.bpProcesses.find(bp => bp.id === 'bp-data-lake');
      expect(dataLake).toBeDefined();
      expect(dataLake?.iconKey).toBe('cloud');
    });

    it('should have all processes with valid IDs', () => {
      FMF_CONFIG.bpProcesses.forEach(process => {
        expect(process.id).toBeTruthy();
        expect(process.id).toMatch(/^bp-/);
      });
    });

    it('should have all processes with labels', () => {
      FMF_CONFIG.bpProcesses.forEach(process => {
        expect(process.label).toBeTruthy();
      });
    });

    it('should have all processes with icon keys', () => {
      FMF_CONFIG.bpProcesses.forEach(process => {
        expect(process.iconKey).toBeTruthy();
      });
    });

    it('should have all processes with brand logo keys', () => {
      FMF_CONFIG.bpProcesses.forEach(process => {
        expect(process.brandLogoKey).toBeTruthy();
      });
    });
  });

  it('should have customer logo path', () => {
    expect(FMF_CONFIG.customerLogoPath).toBeDefined();
    expect(FMF_CONFIG.customerLogoPath).toContain('fmf');
  });
});
