import { Routes } from '@angular/router';

export const appRoutes: Routes = [
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
    path: 'shopfloor-demo',
    loadComponent: () =>
      import('./shopfloor-demo/shopfloor-demo.component').then((m) => m.ShopfloorDemoComponent),
  },
  {
    path: '**',
    redirectTo: 'overview',
  },
];
