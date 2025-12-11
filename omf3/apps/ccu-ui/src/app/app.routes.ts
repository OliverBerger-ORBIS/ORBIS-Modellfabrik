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
        path: 'overview',
        loadComponent: () =>
          import('./tabs/overview-tab.component').then((m) => m.OverviewTabComponent),
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
        path: 'module',
        loadComponent: () =>
          import('./tabs/module-tab.component').then((m) => m.ModuleTabComponent),
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
        path: 'fts',
        loadComponent: () =>
          import('./tabs/fts-tab.component').then((m) => m.FtsTabComponent),
      },
      {
        path: 'track-trace',
        loadComponent: () =>
          import('./tabs/track-trace-tab.component').then((m) => m.TrackTraceTabComponent),
      },
      {
        path: 'dsp-architecture',
        loadComponent: () =>
          import('./pages/refactor-demo/dsp-architecture.component').then((m) => m.DspArchitecturePageComponent),
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
    redirectTo: 'en/overview',
  },
];
