import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'overview',
  },
  // Note: Locale prefix (/:locale) is handled by Angular's --localize build
  // Each locale gets its own build with baseHref set to /:locale/
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
    path: '**',
    redirectTo: 'overview',
  },
];
