import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { GridsterModule } from 'angular-gridster2';
import { FutureFactoryPipesModule } from '../pipes/pipes.module';
import { UsedMaterialModule } from '../used-material.module';
import { BannerComponent } from './banner/banner.component';
import { CalibrationCaptionComponent } from './calibration-caption/calibration-caption.component';
import { CalibrationInfoComponent } from './calibration-info/calibration-info.component';
import { DebugOutputComponent } from './debug-output/debug-output.component';
import { FactoryConfigComponent } from './factory-config/factory-config.component';
import { FactoryLayoutComponent } from './factory-layout/factory-layout.component';
import { FactoryResetComponent } from './factory-reset/factory-reset.component';
import { LanguageSelectorComponent } from './language-selector/language-selector.component';
import { MissingControllerBannerComponent } from './missing-controller-banner/missing-controller-banner.component';
import { ModuleInfoComponent } from './module-info/module-info.component';
import { OrderListComponent } from './order-list/order-list.component';
import { ProductionStepsComponent } from './production-steps/production-steps.component';
import { ProductionTimeCalculatorComponent } from './production-time-calculator/production-time-calculator.component';
import { StateLogDetailsComponent } from './state-log-details/state-log-details.component';
import { VersionInfoComponent } from './version-info/version-info.component';
import { FactoryParkComponent } from './factory-park/factory-park.component';
import { VersionMismatchPopupComponent } from './version-mismatch-popup/version-mismatch-popup.component';
import { CollisionWarningPopupComponent } from './collision-warning-popup/collision-warning-popup.component';

@NgModule({
  imports: [
    CommonModule,
    UsedMaterialModule,
    GridsterModule,
    RouterModule,
    TranslateModule,
    FutureFactoryPipesModule,
    FormsModule,
  ],
  declarations: [
    FactoryResetComponent,
    FactoryParkComponent,
    MissingControllerBannerComponent,
    OrderListComponent,
    FactoryLayoutComponent,
    BannerComponent,
    ProductionTimeCalculatorComponent,
    ProductionStepsComponent,
    LanguageSelectorComponent,
    DebugOutputComponent,
    StateLogDetailsComponent,
    ModuleInfoComponent,
    CalibrationInfoComponent,
    CalibrationCaptionComponent,
    FactoryConfigComponent,
    VersionInfoComponent,
    VersionMismatchPopupComponent,
    CollisionWarningPopupComponent,
  ],
  exports: [
    FactoryResetComponent,
    FactoryParkComponent,
    MissingControllerBannerComponent,
    OrderListComponent,
    FactoryLayoutComponent,
    BannerComponent,
    ProductionTimeCalculatorComponent,
    ProductionStepsComponent,
    LanguageSelectorComponent,
    DebugOutputComponent,
    StateLogDetailsComponent,
    ModuleInfoComponent,
    CalibrationInfoComponent,
    CalibrationCaptionComponent,
    FactoryConfigComponent,
    VersionInfoComponent,
    VersionMismatchPopupComponent,
    CollisionWarningPopupComponent,
  ],
})
export class FutureFactoryComponentsModule {}
