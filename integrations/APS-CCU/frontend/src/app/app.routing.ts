import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FutureFactoryModule } from '@ft/futurefactory';
import { RoutePaths } from './app.routes';

const routes: Routes = [
  {
    path: RoutePaths.ROOT,
    redirectTo: RoutePaths.FACTORY,
    pathMatch: 'full',
  },
  {
    path: RoutePaths.FACTORY,
    loadChildren: () => FutureFactoryModule,
  },
  {
    path: RoutePaths.WILDCARD,
    redirectTo: RoutePaths.FACTORY,
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { relativeLinkResolution: 'legacy' })],
  exports: [RouterModule],
})
export class AppRoutingModule {}
