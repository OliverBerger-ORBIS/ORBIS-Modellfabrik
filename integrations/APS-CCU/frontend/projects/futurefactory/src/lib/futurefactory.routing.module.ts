import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FtWindowModule } from '@fischertechnik/ft-window';
import { FutureFactoryComponent } from './futurefactory.component';
import {
  CloudRoutes,
  FutureFactoryRoutes,
  ROUTE_TO_MODULE_ROOT,
} from './futurefactory.routes';
import { FutureFactoryFlowEditorComponent } from './pages/flow-editor/flow-editor.component';
import { FutureFactoryLayoutEditorComponent } from './pages/layout-editor/layout-editor.component';
import { FutureFactoryModuleCalibrationComponent } from './pages/module-calibration/module-calibration.component';
import { FutureFactoryModuleDetailsComponent } from './pages/module-details/module-details.component';
import { FutureFactoryModuleListComponent } from './pages/module-list/module-list.component';
import { FutureFactoryOrderListComponent } from './pages/order-list/order-list.component';
import { FutureFactorySimulationLayoutComponent } from './pages/simulation-layout/simulation-layout.component';
import { FutureFactoryStatusLogComponent } from './pages/status-log/status-log.component';

const routes: Routes = [
  {
    path: '',
    component: FutureFactoryComponent,
    children: [
      {
        path: CloudRoutes.DASHBOARD,
        loadChildren: () => FtWindowModule,
      },
      {
        path: FutureFactoryRoutes.ROOT,
        redirectTo: FutureFactoryRoutes.DASHBOARD,
        data: { [ROUTE_TO_MODULE_ROOT]: '.' },
        pathMatch: 'full',
      },
      {
        path: FutureFactoryRoutes.MODULE,
        component: FutureFactoryModuleListComponent,
        data: { [ROUTE_TO_MODULE_ROOT]: '..' },
      },
      {
        path: FutureFactoryRoutes.MODULE + '/:moduleId',
        component: FutureFactoryModuleDetailsComponent,
        data: { [ROUTE_TO_MODULE_ROOT]: '../..' },
      },
      {
        path: `${FutureFactoryRoutes.MODULE}/:moduleId/${FutureFactoryRoutes.CALIBRATION}`,
        component: FutureFactoryModuleCalibrationComponent,
        data: { [ROUTE_TO_MODULE_ROOT]: '../../..' },
      },
      {
        path: FutureFactoryRoutes.ORDERS,
        component: FutureFactoryOrderListComponent,
        pathMatch: 'full',
        data: { [ROUTE_TO_MODULE_ROOT]: '..' },
      },
      {
        path: FutureFactoryRoutes.ORDERS + '/:orderId',
        component: FutureFactoryOrderListComponent,
        data: { [ROUTE_TO_MODULE_ROOT]: '../..' },
      },
      {
        path: FutureFactoryRoutes.PRODUCTION_FLOWS,
        component: FutureFactoryFlowEditorComponent,
        data: { [ROUTE_TO_MODULE_ROOT]: '..' },
      },
      {
        path: FutureFactoryRoutes.LAYOUT,
        component: FutureFactoryLayoutEditorComponent,
        data: { [ROUTE_TO_MODULE_ROOT]: '..' },
      },
      {
        path: FutureFactoryRoutes.SIMULATION,
        component: FutureFactorySimulationLayoutComponent,
        data: { [ROUTE_TO_MODULE_ROOT]: '..' },
      },
      {
        path: FutureFactoryRoutes.LOGS,
        component: FutureFactoryStatusLogComponent,
        data: { [ROUTE_TO_MODULE_ROOT]: '..' },
      },
      {
        path: '**',
        redirectTo: './',
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class FutureFactoryRoutingModule {}
