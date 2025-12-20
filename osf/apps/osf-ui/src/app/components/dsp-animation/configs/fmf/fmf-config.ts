/**
 * FMF (Fischertechnik Modellfabrik) Customer Configuration
 * Maps FMF's Fischertechnik equipment to generic icons using abstract IDs
 */
import type { CustomerDspConfig } from '../types';

export const FMF_CONFIG: CustomerDspConfig = {
  customerKey: 'fmf',
  customerName: 'Fischertechnik Modellfabrik',
  
  // Shopfloor devices - 6 Fischertechnik stations with concrete IDs matching existing container IDs
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
      iconKey: 'robot-arm', // Not used, customIconPath takes precedence
      customIconPath: 'device-aiqs', // Use correct AIQS icon
    },
    {
      id: 'sf-device-hbw',
      label: $localize`:@@deviceHBW:Hochregal / lager`,
      iconKey: 'hbw',
    },
    {
      id: 'sf-device-dps',
      label: $localize`:@@deviceDPS:Waren Ein- / und Ausgang`,
      iconKey: 'conveyor', // Not used, customIconPath takes precedence
      customIconPath: 'device-dps', // Use correct DPS icon
    },
    {
      id: 'sf-device-chrg',
      label: $localize`:@@deviceCHRG:Lade- / station`,
      iconKey: 'robot-arm', // CHRG is a loading/robot station
    },
  ],
  
  // Shopfloor systems - 2 systems with abstract IDs
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
  ],
  
  // Business processes - 5 applications
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
      iconKey: 'cloud', // Not used for Business Processes (logoIconKey is used instead)
      customIconPath: 'bp-data-lake', // Use correct data-lake icon instead of generic-system-cloud
      brandLogoKey: 'aws',
    },
  ],
  
  customerLogoPath: 'assets/customers/fmf/logo.svg',
};
