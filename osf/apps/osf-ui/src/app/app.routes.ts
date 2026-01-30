import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'en/dsp',
  },
  {
    path: ':locale',
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'dsp',
      },
      {
        path: 'dsp',
        loadComponent: () =>
          import('./pages/dsp/dsp-page.component').then((m) => m.DspPageComponent),
      },
      {
        path: 'dsp/use-case/track-trace-genealogy',
        loadComponent: () =>
          import('./pages/use-cases/track-trace-genealogy/track-trace-genealogy-use-case.component').then(
            (m) => m.TrackTraceGenealogyUseCaseComponent
          ),
      },
      {
        path: 'dsp/use-case/track-trace',
        loadComponent: () =>
          import('./tabs/track-trace-tab.component').then((m) => m.TrackTraceTabComponent),
      },
      {
        path: 'dsp/use-case/interoperability',
        loadComponent: () =>
          import('./pages/use-cases/interoperability/interoperability-use-case.component').then(
            (m) => m.InteroperabilityUseCaseComponent
          ),
      },
      {
        path: 'dsp/use-case',
        loadComponent: () =>
          import('./pages/use-cases/use-case-selector-page.component').then((m) => m.UseCaseSelectorPageComponent),
      },
      {
        path: 'order',
        loadComponent: () =>
          import('./tabs/order-tab.component').then((m) => m.OrderTabComponent),
      },
      {
        path: 'process',
        loadComponent: () =>
          import('./tabs/process-tab.component').then((m) => m.ProcessTabComponent),
      },
      {
        path: 'sensor',
        loadComponent: () =>
          import('./tabs/sensor-tab.component').then((m) => m.SensorTabComponent),
      },
      {
        path: 'configuration',
        loadComponent: () =>
          import('./tabs/configuration-tab.component').then((m) => m.ConfigurationTabComponent),
      },
      {
        path: 'shopfloor',
        loadComponent: () =>
          import('./tabs/shopfloor-tab.component').then((m) => m.ShopfloorTabComponent),
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('./tabs/settings-tab.component').then((m) => m.SettingsTabComponent),
      },
      {
        path: 'message-monitor',
        loadComponent: () =>
          import('./tabs/message-monitor-tab.component').then((m) => m.MessageMonitorTabComponent),
      },
      {
        path: 'dsp-action',
        loadComponent: () =>
          import('./tabs/dsp-action-tab.component').then((m) => m.DspActionTabComponent),
      },
      {
        path: 'agv',
        loadComponent: () =>
          import('./tabs/agv-tab.component').then((m) => m.AgvTabComponent),
      },
      {
        path: 'dps',
        loadComponent: () =>
          import('./tabs/dps-tab.component').then((m) => m.DpsTabComponent),
      },
      {
        path: 'aiqs',
        loadComponent: () =>
          import('./tabs/aiqs-tab.component').then((m) => m.AiqsTabComponent),
      },
      {
        path: 'hbw',
        loadComponent: () =>
          import('./tabs/hbw-tab.component').then((m) => m.HbwTabComponent),
      },
      {
        path: 'drill',
        loadComponent: () =>
          import('./tabs/drill-tab.component').then((m) => m.DrillTabComponent),
      },
      {
        path: 'mill',
        loadComponent: () =>
          import('./tabs/mill-tab.component').then((m) => m.MillTabComponent),
      },
      {
        path: 'dsp-animation',
        loadComponent: () =>
          import('./pages/dsp-animation/dsp-architecture.component').then((m) => m.DspArchitecturePageComponent),
      },
      {
        path: 'dsp/customer',
        loadComponent: () =>
          import('./pages/dsp/customer/customer-selector-page.component').then((m) => m.CustomerSelectorPageComponent),
      },
      {
        path: 'dsp/customer/fmf',
        loadComponent: () =>
          import('./pages/dsp/customer/fmf/fmf-dsp-page.component').then((m) => m.FmfDspPageComponent),
      },
      {
        path: 'dsp/customer/ecme',
        loadComponent: () =>
          import('./pages/dsp/customer/ecme/ecme-dsp-page.component').then((m) => m.EcmeDspPageComponent),
      },
      {
        path: 'presentation',
        loadComponent: () =>
          import('./pages/presentation/presentation-page.component').then((m) => m.PresentationPageComponent),
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'en/dsp',
  },
];
