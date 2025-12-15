/**
 * FMF (Fischertechnik Modellfabrik) Customer Configuration
 * Maps FMF's Fischertechnik equipment to generic icons
 */
import type { CustomerDspConfig } from '../types';

export const FMF_CONFIG: CustomerDspConfig = {
  customerKey: 'fmf',
  customerName: 'Fischertechnik Modellfabrik',
  
  // Shopfloor devices - Fischertechnik stations
  // Using EXISTING container IDs from layout.shared.config.ts
  sfDevices: [
    {
      id: 'sf-device-mill',
      label: $localize`:@@deviceMILL:Fräs / station`,
      iconKey: 'mill',
    },
    {
      id: 'sf-device-drill',
      label: $localize`:@@deviceDRILL:Bohr / station`,
      iconKey: 'drill',
    },
    {
      id: 'sf-device-aiqs',
      label: $localize`:@@deviceAIQS:KI- / Qualitäts / station`,
      iconKey: 'robot-arm', // Using robot-arm as closest match for AIQS
    },
    {
      id: 'sf-device-hbw',
      label: $localize`:@@deviceHBW:Hochregal / lager`,
      iconKey: 'hbw',
    },
    {
      id: 'sf-device-dps',
      label: $localize`:@@deviceDPS:Waren Ein- / und Ausgang`,
      iconKey: 'conveyor', // DPS is a material handling station
    },
    {
      id: 'sf-device-chrg',
      label: $localize`:@@deviceCHRG:Lade- / station`,
      iconKey: 'robot-arm', // CHRG is a loading/robot station
    },
    {
      id: 'sf-device-conveyor',
      label: $localize`:@@deviceConveyor:Förder- / station`,
      iconKey: 'conveyor',
    },
    {
      id: 'sf-device-stone-oven',
      label: $localize`:@@deviceStoneOven:Ofen / station`,
      iconKey: 'oven',
    },
  ],
  
  // Shopfloor systems
  // Using EXISTING container IDs from layout.shared.config.ts
  sfSystems: [
    {
      id: 'sf-system-any',
      label: $localize`:@@dspArchLabelAnySystem:any System`,
      iconKey: 'warehouse-system',
    },
    {
      id: 'sf-system-fts',
      label: $localize`:@@dspArchLabelFTS:AGV\nSystem`,
      iconKey: 'agv',
    },
    {
      id: 'sf-system-warehouse',
      label: $localize`:@@dspArchLabelWarehouse:Warehouse`,
      iconKey: 'warehouse-system',
    },
    {
      id: 'sf-system-factory',
      label: $localize`:@@dspArchLabelFactory:Factory`,
      iconKey: 'warehouse-system', // Using warehouse as generic factory icon
    },
  ],
  
  // Business processes
  // Using EXISTING container IDs from layout.shared.config.ts
  bpProcesses: [
    {
      id: 'bp-erp',
      label: $localize`:@@dspArchLabelERP:ERP Applications`,
      iconKey: 'erp',
      brandLogoKey: 'sap',
    },
    {
      id: 'bp-mes',
      label: $localize`:@@dspArchLabelMESApp:MES Applications`,
      iconKey: 'mes',
      brandLogoKey: 'sap',
    },
    {
      id: 'bp-cloud',
      label: $localize`:@@dspArchLabelCloudApps:Cloud\nApplications`,
      iconKey: 'cloud',
      brandLogoKey: 'aws',
    },
    {
      id: 'bp-analytics',
      label: $localize`:@@dspArchLabelAnalytics:Analytical\nApplications`,
      iconKey: 'analytics',
      brandLogoKey: 'grafana',
    },
    {
      id: 'bp-data-lake',
      label: $localize`:@@dspArchLabelDataLake:Data Lake`,
      iconKey: 'cloud',
      brandLogoKey: 'aws',
    },
  ],
  
  customerLogoPath: 'assets/customers/fmf/logo.svg',
};
