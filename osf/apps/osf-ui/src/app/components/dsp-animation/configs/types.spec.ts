import type {
  GenericIconKey,
  DeviceMapping,
  SystemMapping,
  BusinessProcessMapping,
  CustomerDspConfig,
} from './types';

describe('Customer Configuration Types', () => {
  describe('GenericIconKey', () => {
    it('should accept valid device icon keys', () => {
      const validDeviceKeys: GenericIconKey[] = [
        'drill',
        'mill',
        'oven',
        'laser',
        'cnc',
        'printer-3d',
        'robot-arm',
        'conveyor',
        'warehouse',
        'agv',
        'hbw',
      ];
      expect(validDeviceKeys).toHaveLength(11);
    });

    it('should accept valid system icon keys', () => {
      const validSystemKeys: GenericIconKey[] = [
        'warehouse-system',
        'erp',
        'mes',
        'cloud',
        'analytics',
      ];
      expect(validSystemKeys).toHaveLength(5);
    });

    it('should accept valid brand icon keys', () => {
      const validBrandKeys: GenericIconKey[] = [
        'sap',
        'alpha-x',
        'aws',
        'azure',
        'powerbi',
        'grafana',
      ];
      expect(validBrandKeys).toHaveLength(6);
    });
  });

  describe('DeviceMapping', () => {
    it('should create valid device mapping', () => {
      const mapping: DeviceMapping = {
        id: 'sf-device-mill',
        label: 'Mill Station',
        iconKey: 'mill',
      };
      expect(mapping.id).toBe('sf-device-mill');
      expect(mapping.label).toBe('Mill Station');
      expect(mapping.iconKey).toBe('mill');
    });

    it('should support optional custom icon path', () => {
      const mapping: DeviceMapping = {
        id: 'sf-device-custom',
        label: 'Custom Device',
        iconKey: 'drill',
        customIconPath: 'assets/custom/device.svg',
      };
      expect(mapping.customIconPath).toBe('assets/custom/device.svg');
    });
  });

  describe('SystemMapping', () => {
    it('should create valid system mapping', () => {
      const mapping: SystemMapping = {
        id: 'sf-system-warehouse',
        label: 'Warehouse System',
        iconKey: 'warehouse-system',
      };
      expect(mapping.id).toBe('sf-system-warehouse');
      expect(mapping.label).toBe('Warehouse System');
      expect(mapping.iconKey).toBe('warehouse-system');
    });

    it('should support optional custom icon path', () => {
      const mapping: SystemMapping = {
        id: 'sf-system-custom',
        label: 'Custom System',
        iconKey: 'mes',
        customIconPath: 'assets/custom/system.svg',
      };
      expect(mapping.customIconPath).toBe('assets/custom/system.svg');
    });
  });

  describe('BusinessProcessMapping', () => {
    it('should create valid business process mapping', () => {
      const mapping: BusinessProcessMapping = {
        id: 'bp-erp',
        label: 'ERP Applications',
        iconKey: 'erp',
        brandLogoKey: 'sap',
      };
      expect(mapping.id).toBe('bp-erp');
      expect(mapping.label).toBe('ERP Applications');
      expect(mapping.iconKey).toBe('erp');
      expect(mapping.brandLogoKey).toBe('sap');
    });

    it('should support optional custom icon path', () => {
      const mapping: BusinessProcessMapping = {
        id: 'bp-custom',
        label: 'Custom Process',
        iconKey: 'cloud',
        brandLogoKey: 'aws',
        customIconPath: 'assets/custom/process.svg',
      };
      expect(mapping.customIconPath).toBe('assets/custom/process.svg');
    });

    it('should support optional custom brand logo path', () => {
      const mapping: BusinessProcessMapping = {
        id: 'bp-custom',
        label: 'Custom Process',
        iconKey: 'cloud',
        brandLogoKey: 'aws',
        customBrandLogoPath: 'assets/custom/brand.svg',
      };
      expect(mapping.customBrandLogoPath).toBe('assets/custom/brand.svg');
    });
  });

  describe('CustomerDspConfig', () => {
    it('should create valid customer config', () => {
      const config: CustomerDspConfig = {
        customerKey: 'test',
        customerName: 'Test Customer',
        sfDevices: [
          { id: 'sf-device-1', label: 'Device 1', iconKey: 'mill' },
        ],
        sfSystems: [
          { id: 'sf-system-1', label: 'System 1', iconKey: 'mes' },
        ],
        bpProcesses: [
          { id: 'bp-1', label: 'Process 1', iconKey: 'erp', brandLogoKey: 'sap' },
        ],
      };
      expect(config.customerKey).toBe('test');
      expect(config.customerName).toBe('Test Customer');
      expect(config.sfDevices).toHaveLength(1);
      expect(config.sfSystems).toHaveLength(1);
      expect(config.bpProcesses).toHaveLength(1);
    });

    it('should support optional customer logo path', () => {
      const config: CustomerDspConfig = {
        customerKey: 'test',
        customerName: 'Test Customer',
        sfDevices: [],
        sfSystems: [],
        bpProcesses: [],
        customerLogoPath: 'assets/customers/test/logo.svg',
      };
      expect(config.customerLogoPath).toBe('assets/customers/test/logo.svg');
    });

    it('should handle empty arrays', () => {
      const config: CustomerDspConfig = {
        customerKey: 'minimal',
        customerName: 'Minimal Config',
        sfDevices: [],
        sfSystems: [],
        bpProcesses: [],
      };
      expect(config.sfDevices).toHaveLength(0);
      expect(config.sfSystems).toHaveLength(0);
      expect(config.bpProcesses).toHaveLength(0);
    });

    it('should handle multiple mappings', () => {
      const config: CustomerDspConfig = {
        customerKey: 'multi',
        customerName: 'Multi Config',
        sfDevices: [
          { id: 'sf-device-1', label: 'Device 1', iconKey: 'mill' },
          { id: 'sf-device-2', label: 'Device 2', iconKey: 'drill' },
          { id: 'sf-device-3', label: 'Device 3', iconKey: 'oven' },
        ],
        sfSystems: [
          { id: 'sf-system-1', label: 'System 1', iconKey: 'warehouse-system' },
          { id: 'sf-system-2', label: 'System 2', iconKey: 'mes' },
        ],
        bpProcesses: [
          { id: 'bp-1', label: 'Process 1', iconKey: 'erp', brandLogoKey: 'sap' },
          { id: 'bp-2', label: 'Process 2', iconKey: 'cloud', brandLogoKey: 'aws' },
        ],
      };
      expect(config.sfDevices).toHaveLength(3);
      expect(config.sfSystems).toHaveLength(2);
      expect(config.bpProcesses).toHaveLength(2);
    });
  });
});
