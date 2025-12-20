import { TestBed } from '@angular/core/testing';
import {
  DspArchitectureConfigService,
  STANDARD_LAYER_HEIGHT,
  EXTENDED_DSP_LAYER_HEIGHT,
  STANDARD_LAYER_POSITIONS,
  EXTENDED_LAYER_POSITIONS,
} from '../dsp-architecture-config.service';

describe('DspArchitectureConfigService', () => {
  let service: DspArchitectureConfigService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [DspArchitectureConfigService],
    });
    service = TestBed.inject(DspArchitectureConfigService);
  });

  describe('Service Creation', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });
  });

  describe('Constants', () => {
    it('should have correct standard layer height', () => {
      expect(STANDARD_LAYER_HEIGHT).toBe(260);
    });

    it('should have correct extended DSP layer height', () => {
      expect(EXTENDED_DSP_LAYER_HEIGHT).toBe(300);
    });

    it('should have correct standard layer positions', () => {
      expect(STANDARD_LAYER_POSITIONS.BUSINESS_Y).toBe(80);
      expect(STANDARD_LAYER_POSITIONS.DSP_Y).toBe(340);
      expect(STANDARD_LAYER_POSITIONS.SHOPFLOOR_Y).toBe(600);
    });

    it('should have correct extended layer positions', () => {
      expect(EXTENDED_LAYER_POSITIONS.BUSINESS_Y).toBe(80);
      expect(EXTENDED_LAYER_POSITIONS.DSP_Y).toBe(340);
      expect(EXTENDED_LAYER_POSITIONS.SHOPFLOOR_Y).toBe(640);
    });
  });

  describe('getBusinessLayerBackground', () => {
    it('should return business layer background config', () => {
      const config = service.getBusinessLayerBackground();

      expect(config.id).toBe('layer-business');
      expect(config.type).toBe('layer');
      expect(config.y).toBe(STANDARD_LAYER_POSITIONS.BUSINESS_Y);
      expect(config.height).toBe(STANDARD_LAYER_HEIGHT);
      expect(config.width).toBe(1200);
      expect(config.isGroup).toBe(true);
    });
  });

  describe('getDspLayerBackground', () => {
    it('should return DSP layer background config', () => {
      const config = service.getDspLayerBackground();

      expect(config.id).toBe('layer-dsp');
      expect(config.type).toBe('layer');
      expect(config.y).toBe(STANDARD_LAYER_POSITIONS.DSP_Y);
      expect(config.height).toBe(STANDARD_LAYER_HEIGHT);
      expect(config.width).toBe(1200);
      expect(config.isGroup).toBe(true);
    });
  });

  describe('getExtendedDspLayerBackground', () => {
    it('should return extended DSP layer background config', () => {
      const config = service.getExtendedDspLayerBackground();

      expect(config.id).toBe('layer-dsp');
      expect(config.type).toBe('layer');
      expect(config.y).toBe(EXTENDED_LAYER_POSITIONS.DSP_Y);
      expect(config.height).toBe(EXTENDED_DSP_LAYER_HEIGHT);
      expect(config.width).toBe(1200);
    });
  });

  describe('getShopfloorLayerBackground', () => {
    it('should return shopfloor layer background config', () => {
      const config = service.getShopfloorLayerBackground();

      expect(config.id).toBe('layer-shopfloor');
      expect(config.type).toBe('layer');
      expect(config.y).toBe(STANDARD_LAYER_POSITIONS.SHOPFLOOR_Y);
      expect(config.height).toBe(STANDARD_LAYER_HEIGHT);
      expect(config.width).toBe(1200);
    });
  });

  describe('getExtendedShopfloorLayerBackground', () => {
    it('should return extended shopfloor layer background config', () => {
      const config = service.getExtendedShopfloorLayerBackground();

      expect(config.id).toBe('layer-shopfloor');
      expect(config.type).toBe('layer');
      expect(config.y).toBe(EXTENDED_LAYER_POSITIONS.SHOPFLOOR_Y);
      expect(config.height).toBe(STANDARD_LAYER_HEIGHT);
    });
  });

  describe('getBusinessLayerContainers', () => {
    it('should return all business layer containers', () => {
      const containers = service.getBusinessLayerContainers();

      expect(containers.erp).toBeDefined();
      expect(containers.erp.id).toBe('business-erp');
      expect(containers.erp.type).toBe('business');

      expect(containers.cloud).toBeDefined();
      expect(containers.cloud.id).toBe('business-cloud');

      expect(containers.analytics).toBeDefined();
      expect(containers.analytics.id).toBe('business-analytics');

      expect(containers.dataLake).toBeDefined();
      expect(containers.dataLake.id).toBe('business-data-lake');

      expect(containers.dashboard).toBeDefined();
      expect(containers.dashboard?.id).toBe('business-dashboard');
      expect(containers.dashboard?.type).toBe('ux');
    });

    it('should position containers correctly', () => {
      const containers = service.getBusinessLayerContainers();

      expect(containers.erp.width).toBe(200);
      expect(containers.erp.height).toBe(140);
      expect(containers.cloud.width).toBe(200);
      expect(containers.analytics.width).toBe(200);
      expect(containers.dataLake.width).toBe(200);
    });
  });

  describe('getShopfloorLayerContainers', () => {
    it('should return shopfloor layer containers', () => {
      const containers = service.getShopfloorLayerContainers();

      expect(containers.systems).toBeDefined();
      expect(containers.systems.id).toBe('shopfloor-systems');
      expect(containers.systems.type).toBe('shopfloor');

      expect(containers.devices).toBeDefined();
      expect(containers.devices.id).toBe('shopfloor-devices');
      expect(containers.devices.type).toBe('shopfloor');
    });

    it('should position containers in shopfloor layer', () => {
      const containers = service.getShopfloorLayerContainers();

      expect(containers.systems.y).toBe(STANDARD_LAYER_POSITIONS.SHOPFLOOR_Y + 80);
      expect(containers.devices.y).toBe(STANDARD_LAYER_POSITIONS.SHOPFLOOR_Y + 80);
    });
  });

  describe('getCloudLayerContainers', () => {
    it('should return cloud layer containers', () => {
      const containers = service.getCloudLayerContainers();

      expect(containers.managementCockpit).toBeDefined();
      expect(containers.managementCockpit.id).toBe('cloud-management-cockpit');
      expect(containers.managementCockpit.type).toBe('dsp-cloud');
      expect(containers.managementCockpit.logoIconKey).toBe('logo-azure');
    });
  });

  describe('getAllLayerBackgrounds', () => {
    it('should return all standard layer backgrounds', () => {
      const layers = service.getAllLayerBackgrounds();

      expect(layers.length).toBe(3);
      expect(layers[0].id).toBe('layer-business');
      expect(layers[1].id).toBe('layer-dsp');
      expect(layers[2].id).toBe('layer-shopfloor');
    });

    it('should have consistent heights', () => {
      const layers = service.getAllLayerBackgrounds();

      expect(layers[0].height).toBe(STANDARD_LAYER_HEIGHT);
      expect(layers[1].height).toBe(STANDARD_LAYER_HEIGHT);
      expect(layers[2].height).toBe(STANDARD_LAYER_HEIGHT);
    });
  });

  describe('getAllExtendedLayerBackgrounds', () => {
    it('should return all extended layer backgrounds', () => {
      const layers = service.getAllExtendedLayerBackgrounds();

      expect(layers.length).toBe(3);
      expect(layers[0].id).toBe('layer-business');
      expect(layers[1].id).toBe('layer-dsp');
      expect(layers[2].id).toBe('layer-shopfloor');
    });

    it('should have extended DSP layer height', () => {
      const layers = service.getAllExtendedLayerBackgrounds();

      expect(layers[1].height).toBe(EXTENDED_DSP_LAYER_HEIGHT);
      expect(layers[1].id).toBe('layer-dsp');
    });

    it('should have adjusted shopfloor Y position', () => {
      const layers = service.getAllExtendedLayerBackgrounds();

      expect(layers[2].y).toBe(EXTENDED_LAYER_POSITIONS.SHOPFLOOR_Y);
    });
  });

  describe('getAllBusinessContainers', () => {
    it('should return all business containers as array', () => {
      const containers = service.getAllBusinessContainers();

      expect(containers.length).toBe(5); // ERP, Cloud, Analytics, Data Lake, Dashboard
      expect(containers.map(c => c.id)).toContain('business-erp');
      expect(containers.map(c => c.id)).toContain('business-cloud');
      expect(containers.map(c => c.id)).toContain('business-analytics');
      expect(containers.map(c => c.id)).toContain('business-data-lake');
      expect(containers.map(c => c.id)).toContain('business-dashboard');
    });
  });

  describe('getAllShopfloorContainers', () => {
    it('should return all shopfloor containers as array', () => {
      const containers = service.getAllShopfloorContainers();

      expect(containers.length).toBe(2);
      expect(containers[0].id).toBe('shopfloor-systems');
      expect(containers[1].id).toBe('shopfloor-devices');
    });
  });

  describe('getAllCloudContainers', () => {
    it('should return all cloud containers as array', () => {
      const containers = service.getAllCloudContainers();

      expect(containers.length).toBe(1);
      expect(containers[0].id).toBe('cloud-management-cockpit');
    });
  });

  describe('getAllStandardContainers', () => {
    it('should return all standard containers combined', () => {
      const containers = service.getAllStandardContainers();

      expect(containers.length).toBe(8); // 5 business + 2 shopfloor + 1 cloud
      expect(containers.map(c => c.id)).toContain('business-erp');
      expect(containers.map(c => c.id)).toContain('shopfloor-systems');
      expect(containers.map(c => c.id)).toContain('cloud-management-cockpit');
    });
  });

  describe('createCustomerConfiguration', () => {
    it('should create default configuration', () => {
      const config = service.createCustomerConfiguration();

      expect(config.layers.length).toBe(3);
      expect(config.business).toBeDefined();
      expect(config.shopfloor).toBeDefined();
      expect(config.cloud).toBeDefined();
    });

    it('should merge custom business containers', () => {
      const customBusiness = {
        erp: {
          id: 'custom-erp',
          label: 'Custom ERP',
          x: 100,
          y: 100,
          width: 150,
          height: 150,
          type: 'business' as const,
          state: 'normal' as const,
        },
      };

      const config = service.createCustomerConfiguration({
        businessContainers: customBusiness,
      });

      expect(config.business.erp.id).toBe('custom-erp');
      expect(config.business.erp.label).toBe('Custom ERP');
      // Other containers should still exist
      expect(config.business.cloud).toBeDefined();
      expect(config.business.analytics).toBeDefined();
    });

    it('should merge custom shopfloor containers', () => {
      const customShopfloor = {
        systems: {
          id: 'custom-systems',
          label: 'Custom Systems',
          x: 200,
          y: 200,
          width: 180,
          height: 120,
          type: 'shopfloor' as const,
          state: 'normal' as const,
        },
      };

      const config = service.createCustomerConfiguration({
        shopfloorContainers: customShopfloor,
      });

      expect(config.shopfloor.systems.id).toBe('custom-systems');
      expect(config.shopfloor.devices).toBeDefined(); // Should still exist
    });

    it('should merge custom cloud containers', () => {
      const customCloud = {
        managementCockpit: {
          id: 'custom-cockpit',
          label: 'Custom Cockpit',
          x: 900,
          y: 100,
          width: 250,
          height: 150,
          type: 'dsp-cloud' as const,
          state: 'normal' as const,
        },
      };

      const config = service.createCustomerConfiguration({
        cloudContainers: customCloud,
      });

      expect(config.cloud.managementCockpit.id).toBe('custom-cockpit');
      expect(config.cloud.managementCockpit.label).toBe('Custom Cockpit');
    });
  });

  describe('createExtendedCustomerConfiguration', () => {
    it('should create extended configuration with taller DSP layer', () => {
      const config = service.createExtendedCustomerConfiguration();

      expect(config.layers.length).toBe(3);
      expect(config.layers[1].id).toBe('layer-dsp');
      expect(config.layers[1].height).toBe(EXTENDED_DSP_LAYER_HEIGHT);
    });

    it('should have adjusted shopfloor Y position', () => {
      const config = service.createExtendedCustomerConfiguration();

      expect(config.layers[2].y).toBe(EXTENDED_LAYER_POSITIONS.SHOPFLOOR_Y);
    });

    it('should merge custom containers in extended config', () => {
      const customBusiness = {
        dashboard: {
          id: 'custom-dashboard',
          label: 'Custom Dashboard',
          x: 150,
          y: 400,
          width: 120,
          height: 140,
          type: 'ux' as const,
          state: 'normal' as const,
        },
      };

      const config = service.createExtendedCustomerConfiguration({
        businessContainers: customBusiness,
      });

      expect(config.business.dashboard?.id).toBe('custom-dashboard');
      expect(config.business.erp).toBeDefined(); // Should still exist
    });
  });
});
