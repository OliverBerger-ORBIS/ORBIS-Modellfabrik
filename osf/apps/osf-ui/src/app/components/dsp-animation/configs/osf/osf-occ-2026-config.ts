/**
 * OCC default variant (kept as long-term concept baseline).
 *
 * Evolution context:
 * FMF (historical baseline) -> LogiMAT -> Hannover/Customer-Connect -> OCC default.
 * OCC stays the canonical default because it models end-to-end integration with AI support.
 */
import type { CustomerDspConfig } from '../types';
import { OSF_BASE_CONFIG } from './osf-config.base';

export const OSF_OCC_2026_CONFIG: CustomerDspConfig = {
  ...OSF_BASE_CONFIG,
  customerKey: 'osf-occ-2026',
  customerName: 'ORBIS Smart Factory (OCC Default)',
  bpProcesses: [
    {
      id: 'bp-erp',
      label: $localize`:@@dspArchLabelSapErpApp:ERP Application`,
      iconKey: 'erp',
      brandLogoKey: 'sap',
    },
    {
      id: 'bp-mes',
      label: $localize`:@@dspArchLabelOrbisMesApp:MES Application`,
      iconKey: 'mes',
      // Primary brand remains SAP backend context; ORBIS is shown via secondary logo.
      brandLogoKey: 'sap',
      customBrandLogoPath: 'logo-orbis',
      secondaryLogoPosition: 'top-left',
    },
    {
      id: 'bp-ewm',
      label: $localize`:@@dspArchLabelEWMApp:EWM Application`,
      iconKey: 'cloud',
      customIconPath: 'ewm-application',
      brandLogoKey: 'sap',
    },
    {
      id: 'bp-crm',
      label: $localize`:@@dspArchLabelCrmApp:CRM Application`,
      iconKey: 'cloud',
      customIconPath: 'crm-application',
      // Use microsoft logo explicitly to avoid cloud fallback semantics.
      brandLogoKey: 'microsoft',
    },
    {
      id: 'bp-analytics',
      label: $localize`:@@dspArchLabelAnalytics:Analytical Apps`,
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
};

