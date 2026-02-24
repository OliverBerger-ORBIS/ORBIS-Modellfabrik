import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { GridsterModule } from 'angular-gridster2';
import { FutureFactoryComponentsModule } from '../components/components.module';
import { FutureFactoryPipesModule } from '../pipes/pipes.module';
import { UsedMaterialModule } from '../used-material.module';
import { FutureFactoryFlowEditorComponent } from './flow-editor/flow-editor.component';
import { FutureFactoryLayoutEditorComponent } from './layout-editor/layout-editor.component';
import { FutureFactoryModuleDetailsComponent } from './module-details/module-details.component';
import { FutureFactoryModuleListComponent } from './module-list/module-list.component';
import { FutureFactoryOrderListComponent } from './order-list/order-list.component';
import { FutureFactorySimulationLayoutComponent } from './simulation-layout/simulation-layout.component';
import { FutureFactoryStatusLogComponent } from './status-log/status-log.component';
import { FutureFactoryModuleCalibrationComponent } from './module-calibration/module-calibration.component';
import { FormsModule } from '@angular/forms';

@NgModule({
  imports: [
    CommonModule,
    UsedMaterialModule,
    FormsModule,
    GridsterModule,
    RouterModule,
    TranslateModule,
    FutureFactoryComponentsModule,
    FutureFactoryPipesModule,
  ],
  declarations: [
    FutureFactoryOrderListComponent,
    FutureFactoryStatusLogComponent,
    FutureFactoryLayoutEditorComponent,
    FutureFactoryFlowEditorComponent,
    FutureFactoryModuleDetailsComponent,
    FutureFactoryModuleCalibrationComponent,
    FutureFactoryModuleListComponent,
    FutureFactorySimulationLayoutComponent,
  ],
  exports: [
    FutureFactoryOrderListComponent,
    FutureFactoryStatusLogComponent,
    FutureFactoryLayoutEditorComponent,
    FutureFactoryFlowEditorComponent,
    FutureFactoryModuleDetailsComponent,
    FutureFactoryModuleCalibrationComponent,
    FutureFactoryModuleListComponent,
    FutureFactorySimulationLayoutComponent,
  ],
})
export class FutureFactoryPagesModule {}
