import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'en/overview',
  },
  {
    path: ':locale',
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'overview',
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
    ],
  },
  {
    path: '**',
    redirectTo: 'en/overview',
  },
];
