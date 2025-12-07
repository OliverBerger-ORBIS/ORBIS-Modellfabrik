/**
 * Shared service for DSP Architecture configuration.
 * Provides reusable layer and container definitions for both:
 * - Main DSP Reference Architecture (DspArchitectureComponent)
 * - Edge Architecture Animation (EdgeArchitectureAnimatedComponent)
 * 
 * This enables consistent styling and positioning across different views
 * and supports customer-specific configurations.
 */
import { Injectable } from '@angular/core';
import type { ContainerConfig } from '../components/dsp-architecture/dsp-architecture.types';
import type { IconKey } from '../assets/icon-registry';

/** Standard layer heights used across DSP diagrams */
export const STANDARD_LAYER_HEIGHT = 260;
/** Extended DSP layer height to accommodate edge component details (3 rows without overlap) */
export const EXTENDED_DSP_LAYER_HEIGHT = 300;

/** Y-positions for standard 3-layer architecture */
export const STANDARD_LAYER_POSITIONS = {
  BUSINESS_Y: 80,
  DSP_Y: 340,     // 80 + 260
  SHOPFLOOR_Y: 600 // 80 + 260 + 260
};

/** Y-positions for extended DSP layer architecture (with taller DSP layer for edge components) */
export const EXTENDED_LAYER_POSITIONS = {
  BUSINESS_Y: 80,
  DSP_Y: 340,     // 80 + 260
  SHOPFLOOR_Y: 640 // 80 + 260 + 300 (extended DSP layer)
};

/** Business layer container configuration */
export interface BusinessLayerConfig {
  /** ERP Applications container */
  erp: ContainerConfig;
  /** Cloud Applications container */
  cloud: ContainerConfig;
  /** Analytics Applications container */
  analytics: ContainerConfig;
  /** Data Lake container */
  dataLake: ContainerConfig;
  /** SmartFactory Dashboard container (visualization/apps) */
  dashboard?: ContainerConfig;
}

/** Shopfloor layer container configuration */
export interface ShopfloorLayerConfig {
  /** Shopfloor Systems container */
  systems: ContainerConfig;
  /** Shopfloor Devices container */
  devices: ContainerConfig;
}

/** Cloud layer container configuration (for Management Cockpit) */
export interface CloudLayerConfig {
  /** Management Cockpit container */
  managementCockpit: ContainerConfig;
}

/**
 * Service providing shared DSP architecture configuration.
 * Centralizes layer and container definitions for reuse across components.
 */
@Injectable({
  providedIn: 'root'
})
export class DspArchitectureConfigService {

  /**
   * Get Business layer background container configuration.
   */
  getBusinessLayerBackground(): ContainerConfig {
    return {
      id: 'layer-business',
      label: '',  // Set via i18n
      x: 0,
      y: STANDARD_LAYER_POSITIONS.BUSINESS_Y,
      width: 1200,
      height: STANDARD_LAYER_HEIGHT,
      type: 'layer',
      state: 'normal',
      backgroundColor: '#ffffff',
      borderColor: 'rgba(22, 65, 148, 0.1)',
      isGroup: true,
      labelPosition: 'left',
    };
  }

  /**
   * Get DSP layer background container configuration.
   */
  getDspLayerBackground(): ContainerConfig {
    return {
      id: 'layer-dsp',
      label: '',  // Set via i18n
      x: 0,
      y: STANDARD_LAYER_POSITIONS.DSP_Y,
      width: 1200,
      height: STANDARD_LAYER_HEIGHT,
      type: 'layer',
      state: 'normal',
      backgroundColor: 'rgba(207, 230, 255, 0.5)',
      borderColor: 'rgba(22, 65, 148, 0.15)',
      isGroup: true,
      labelPosition: 'left',
    };
  }

  /**
   * Get extended DSP layer background container configuration.
   * Used in Edge Architecture animation to provide enough space for 3 rows of components.
   */
  getExtendedDspLayerBackground(): ContainerConfig {
    return {
      id: 'layer-dsp',
      label: '',  // Set via i18n
      x: 0,
      y: EXTENDED_LAYER_POSITIONS.DSP_Y,
      width: 1200,
      height: EXTENDED_DSP_LAYER_HEIGHT,
      type: 'layer',
      state: 'normal',
      backgroundColor: 'rgba(207, 230, 255, 0.5)',
      borderColor: 'rgba(22, 65, 148, 0.15)',
      isGroup: true,
      labelPosition: 'left',
    };
  }

  /**
   * Get Shopfloor layer background container configuration.
   */
  getShopfloorLayerBackground(): ContainerConfig {
    return {
      id: 'layer-shopfloor',
      label: '',  // Set via i18n
      x: 0,
      y: STANDARD_LAYER_POSITIONS.SHOPFLOOR_Y,
      width: 1200,
      height: STANDARD_LAYER_HEIGHT,
      type: 'layer',
      state: 'normal',
      backgroundColor: 'rgba(241, 243, 247, 0.8)',
      borderColor: 'rgba(31, 54, 91, 0.12)',
      isGroup: true,
      labelPosition: 'left',
    };
  }

  /**
   * Get extended Shopfloor layer background container configuration.
   * Used in Edge Architecture animation with extended DSP layer.
   */
  getExtendedShopfloorLayerBackground(): ContainerConfig {
    return {
      id: 'layer-shopfloor',
      label: '',  // Set via i18n
      x: 0,
      y: EXTENDED_LAYER_POSITIONS.SHOPFLOOR_Y,
      width: 1200,
      height: STANDARD_LAYER_HEIGHT,
      type: 'layer',
      state: 'normal',
      backgroundColor: 'rgba(241, 243, 247, 0.8)',
      borderColor: 'rgba(31, 54, 91, 0.12)',
      isGroup: true,
      labelPosition: 'left',
    };
  }

  /**
   * Get Business layer container configuration.
   * Returns the main business process containers (ERP, Cloud, Analytics, Data Lake).
   */
  getBusinessLayerContainers(): BusinessLayerConfig {
    const startX = 240;
    const boxWidth = 200;
    const boxHeight = 140;
    const gap = 25;

    return {
      erp: {
        id: 'business-erp',
        label: '',  // "ERP Applications" via i18n
        x: startX,
        y: STANDARD_LAYER_POSITIONS.BUSINESS_Y + 60,
        width: boxWidth,
        height: boxHeight,
        type: 'business',
        state: 'normal',
        logoIconKey: 'logo-sap' as IconKey,
        logoPosition: 'top-right',
        labelPosition: 'top-center',
      },
      cloud: {
        id: 'business-cloud',
        label: '',  // "Cloud Applications" via i18n
        x: startX + boxWidth + gap,
        y: STANDARD_LAYER_POSITIONS.BUSINESS_Y + 60,
        width: boxWidth,
        height: boxHeight,
        type: 'business',
        state: 'normal',
        labelPosition: 'top-center',
      },
      analytics: {
        id: 'business-analytics',
        label: '',  // "Analytics Applications" via i18n
        x: startX + 2 * (boxWidth + gap),
        y: STANDARD_LAYER_POSITIONS.BUSINESS_Y + 60,
        width: boxWidth,
        height: boxHeight,
        type: 'business',
        state: 'normal',
        labelPosition: 'top-center',
      },
      dataLake: {
        id: 'business-data-lake',
        label: '',  // "Data Lake" via i18n
        x: startX + 3 * (boxWidth + gap),
        y: STANDARD_LAYER_POSITIONS.BUSINESS_Y + 60,
        width: boxWidth,
        height: boxHeight,
        type: 'business',
        state: 'normal',
        labelPosition: 'top-center',
      },
      dashboard: {
        id: 'business-dashboard',
        label: '',  // "SmartFactory Dashboard" via i18n
        x: 120,
        y: STANDARD_LAYER_POSITIONS.DSP_Y + 70,
        width: 100,
        height: 120,
        type: 'ux',
        state: 'normal',
        labelPosition: 'bottom-center',
      }
    };
  }

  /**
   * Get Shopfloor layer container configuration.
   * Returns shopfloor systems and devices containers.
   */
  getShopfloorLayerContainers(): ShopfloorLayerConfig {
    return {
      systems: {
        id: 'shopfloor-systems',
        label: '',  // "Shopfloor\nSystems" via i18n
        x: 420,
        y: STANDARD_LAYER_POSITIONS.SHOPFLOOR_Y + 80,
        width: 180,
        height: 120,
        type: 'shopfloor',
        state: 'normal',
        labelPosition: 'top-center',
      },
      devices: {
        id: 'shopfloor-devices',
        label: '',  // "Devices" via i18n
        x: 650,
        y: STANDARD_LAYER_POSITIONS.SHOPFLOOR_Y + 80,
        width: 180,
        height: 120,
        type: 'shopfloor',
        state: 'normal',
        labelPosition: 'top-center',
      }
    };
  }

  /**
   * Get Cloud layer container configuration.
   * Returns Management Cockpit container.
   */
  getCloudLayerContainers(): CloudLayerConfig {
    return {
      managementCockpit: {
        id: 'cloud-management-cockpit',
        label: '',  // "Management Cockpit" via i18n
        x: 880,
        y: STANDARD_LAYER_POSITIONS.DSP_Y + 30,
        width: 280,
        height: 180,
        type: 'dsp-cloud',
        state: 'normal',
        logoIconKey: 'logo-azure' as IconKey,
        logoPosition: 'top-right',
        labelPosition: 'top-center',
        backgroundColor: 'rgba(207, 230, 255, 0.3)',
        borderColor: 'rgba(22, 65, 148, 0.3)',
      }
    };
  }

  /**
   * Get all standard layer backgrounds as a flat array.
   */
  getAllLayerBackgrounds(): ContainerConfig[] {
    return [
      this.getBusinessLayerBackground(),
      this.getDspLayerBackground(),
      this.getShopfloorLayerBackground(),
    ];
  }

  /**
   * Get all layer backgrounds with extended DSP layer height.
   * Used in Edge Architecture animation to provide enough space for edge components.
   */
  getAllExtendedLayerBackgrounds(): ContainerConfig[] {
    return [
      this.getBusinessLayerBackground(),
      this.getExtendedDspLayerBackground(),
      this.getExtendedShopfloorLayerBackground(),
    ];
  }

  /**
   * Get all business layer containers as a flat array.
   */
  getAllBusinessContainers(): ContainerConfig[] {
    const config = this.getBusinessLayerContainers();
    const containers = [
      config.erp,
      config.cloud,
      config.analytics,
      config.dataLake,
    ];
    if (config.dashboard) {
      containers.push(config.dashboard);
    }
    return containers;
  }

  /**
   * Get all shopfloor layer containers as a flat array.
   */
  getAllShopfloorContainers(): ContainerConfig[] {
    const config = this.getShopfloorLayerContainers();
    return [config.systems, config.devices];
  }

  /**
   * Get all cloud layer containers as a flat array.
   */
  getAllCloudContainers(): ContainerConfig[] {
    const config = this.getCloudLayerContainers();
    return [config.managementCockpit];
  }

  /**
   * Get all standard containers (excluding layer backgrounds).
   * Useful for building complete architecture views.
   */
  getAllStandardContainers(): ContainerConfig[] {
    return [
      ...this.getAllBusinessContainers(),
      ...this.getAllShopfloorContainers(),
      ...this.getAllCloudContainers(),
    ];
  }

  /**
   * Create a customer-specific configuration.
   * This method can be extended to support different customer scenarios.
   * 
   * @param customerConfig Optional custom container configurations
   * @returns Complete configuration with layers and containers
   */
  createCustomerConfiguration(customerConfig?: {
    businessContainers?: Partial<BusinessLayerConfig>;
    shopfloorContainers?: Partial<ShopfloorLayerConfig>;
    cloudContainers?: Partial<CloudLayerConfig>;
  }): {
    layers: ContainerConfig[];
    business: BusinessLayerConfig;
    shopfloor: ShopfloorLayerConfig;
    cloud: CloudLayerConfig;
  } {
    const defaultBusiness = this.getBusinessLayerContainers();
    const defaultShopfloor = this.getShopfloorLayerContainers();
    const defaultCloud = this.getCloudLayerContainers();

    return {
      layers: this.getAllLayerBackgrounds(),
      business: {
        ...defaultBusiness,
        ...customerConfig?.businessContainers,
      },
      shopfloor: {
        ...defaultShopfloor,
        ...customerConfig?.shopfloorContainers,
      },
      cloud: {
        ...defaultCloud,
        ...customerConfig?.cloudContainers,
      },
    };
  }

  /**
   * Create customer configuration with extended DSP layer.
   * Used for Edge Architecture animation that needs more vertical space.
   */
  createExtendedCustomerConfiguration(customerConfig?: {
    businessContainers?: Partial<BusinessLayerConfig>;
    shopfloorContainers?: Partial<ShopfloorLayerConfig>;
    cloudContainers?: Partial<CloudLayerConfig>;
  }): {
    layers: ContainerConfig[];
    business: BusinessLayerConfig;
    shopfloor: ShopfloorLayerConfig;
    cloud: CloudLayerConfig;
  } {
    const defaultBusiness = this.getBusinessLayerContainers();
    const defaultShopfloor = this.getShopfloorLayerContainers();
    const defaultCloud = this.getCloudLayerContainers();

    return {
      layers: this.getAllExtendedLayerBackgrounds(),
      business: {
        ...defaultBusiness,
        ...customerConfig?.businessContainers,
      },
      shopfloor: {
        ...defaultShopfloor,
        ...customerConfig?.shopfloorContainers,
      },
      cloud: {
        ...defaultCloud,
        ...customerConfig?.cloudContainers,
      },
    };
  }
}
