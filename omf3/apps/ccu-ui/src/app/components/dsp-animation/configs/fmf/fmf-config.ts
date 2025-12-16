/**
 * FMF (Fischertechnik Modellfabrik) Customer Configuration
 * Maps FMF's Fischertechnik equipment to generic icons using abstract IDs
 */
import type { CustomerDspConfig } from '../types';

export const FMF_CONFIG: CustomerDspConfig = {
  customerKey: 'fmf',
  customerName: 'Fischertechnik Modellfabrik',
  
  // Shopfloor devices - 6 Fischertechnik stations with abstract IDs
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
      iconKey: 'cloud',
      brandLogoKey: 'aws',
    },
  ],
  
  customerLogoPath: 'assets/customers/fmf/logo.svg',
};
