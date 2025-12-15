/**
 * FMF (Fischertechnik Modellfabrik) Customer Configuration
 * Maps FMF's Fischertechnik equipment to generic icons
 */
import type { CustomerDspConfig } from '../types';

export const FMF_CONFIG: CustomerDspConfig = {
  customerKey: 'fmf',
  customerName: 'Fischertechnik Modellfabrik',
  
  // Shopfloor devices - Fischertechnik stations
  sfDevices: [
    {
      id: 'sf-device-1',
      label: $localize`:@@deviceMILL:Fräs / station`,
      iconKey: 'mill',
    },
    {
      id: 'sf-device-2',
      label: $localize`:@@deviceDRILL:Bohr / station`,
      iconKey: 'drill',
    },
    {
      id: 'sf-device-3',
      label: $localize`:@@deviceAIQS:KI- / Qualitäts / station`,
      iconKey: 'robot-arm', // Using robot-arm as closest match for AIQS
    },
    {
      id: 'sf-device-4',
      label: $localize`:@@deviceHBW:Hochregal / lager`,
      iconKey: 'hbw',
    },
    {
      id: 'sf-device-5',
      label: $localize`:@@deviceDPS:Waren Ein- / und Ausgang`,
      iconKey: 'conveyor', // DPS is a material handling station
    },
    {
      id: 'sf-device-6',
      label: $localize`:@@deviceCHRG:Lade- / station`,
      iconKey: 'robot-arm', // CHRG is a loading/robot station
    },
    {
      id: 'sf-device-7',
      label: $localize`:@@deviceConveyor:Förder- / station`,
      iconKey: 'conveyor',
    },
    {
      id: 'sf-device-8',
      label: $localize`:@@deviceStoneOven:Ofen / station`,
      iconKey: 'oven',
    },
  ],
  
  // Shopfloor systems
  sfSystems: [
    {
      id: 'sf-system-1',
      label: $localize`:@@dspArchLabelAnySystem:any System`,
      iconKey: 'warehouse-system',
    },
    {
      id: 'sf-system-2',
      label: $localize`:@@dspArchLabelFTS:AGV\nSystem`,
      iconKey: 'agv',
    },
    {
      id: 'sf-system-3',
      label: $localize`:@@dspArchLabelWarehouse:Warehouse`,
      iconKey: 'warehouse-system',
    },
    {
      id: 'sf-system-4',
      label: $localize`:@@dspArchLabelFactory:Factory`,
      iconKey: 'warehouse-system', // Using warehouse as generic factory icon
    },
  ],
  
  // Business processes
  bpProcesses: [
    {
      id: 'bp-1',
      label: $localize`:@@dspArchLabelERP:ERP Applications`,
      iconKey: 'erp',
      brandLogoKey: 'sap',
    },
    {
      id: 'bp-2',
      label: $localize`:@@dspArchLabelMESApp:MES Applications`,
      iconKey: 'mes',
      brandLogoKey: 'sap',
    },
    {
      id: 'bp-3',
      label: $localize`:@@dspArchLabelCloudApps:Cloud\nApplications`,
      iconKey: 'cloud',
      brandLogoKey: 'aws',
    },
    {
      id: 'bp-4',
      label: $localize`:@@dspArchLabelAnalytics:Analytical\nApplications`,
      iconKey: 'analytics',
      brandLogoKey: 'grafana',
    },
    {
      id: 'bp-5',
      label: $localize`:@@dspArchLabelDataLake:Data Lake`,
      iconKey: 'cloud',
      brandLogoKey: 'aws',
    },
  ],
  
  customerLogoPath: 'assets/customers/fmf/logo.svg',
};
