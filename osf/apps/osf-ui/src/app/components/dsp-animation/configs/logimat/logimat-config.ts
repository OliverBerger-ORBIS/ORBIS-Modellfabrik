/**
 * LogiMAT trade fair customer configuration: same shopfloor as FMF,
 * business layer with ORBIS MES, SAP EWM (no generic “Cloud Applications” box).
 */
import type { CustomerDspConfig } from '../types';
import { FMF_CONFIG } from '../fmf/fmf-config';

export const LOGIMAT_CONFIG: CustomerDspConfig = {
  customerKey: 'logimat',
  customerName: 'LogiMAT (ORBIS Demo)',
  sfDevices: FMF_CONFIG.sfDevices.map((d) => ({ ...d })),
  sfSystems: FMF_CONFIG.sfSystems.map((s) => ({ ...s })),

  bpProcesses: [
    {
      id: 'bp-erp',
      /** Singular: concrete SAP application (LogiMAT), not generic “ERP Applications” */
      label: $localize`:@@dspArchLabelSapErpApp:ERP Application`,
      iconKey: 'erp',
      brandLogoKey: 'sap',
    },
    {
      id: 'bp-mes',
      label: $localize`:@@dspArchLabelSapMesApp:MES Application`,
      iconKey: 'mes',
      brandLogoKey: 'sap',
      customBrandLogoPath: 'logo-orbis',
      secondaryLogoPosition: 'top-left',
    },
    {
      id: 'bp-ewm',
      label: $localize`:@@dspArchLabelEWMApp:EWM Application`,
      iconKey: 'cloud',
      brandLogoKey: 'sap',
      customIconPath: 'ewm-application',
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
      customIconPath: 'bp-data-lake',
      brandLogoKey: 'aws',
    },
  ],

  customerLogoPath: 'assets/customers/fmf/logo.svg',
};
