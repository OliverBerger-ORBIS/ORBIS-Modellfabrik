import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { RouterTestingModule } from '@angular/router/testing';
import { TranslateModule } from '@ngx-translate/core';
import { GridsterModule } from 'angular-gridster2';
import { FutureFactoryComponentsModule } from './components/components.module';
import { FutureFactoryPipesModule } from './pipes/pipes.module';
import { UsedMaterialModule } from './used-material.module';

@NgModule({
  imports: [
    NoopAnimationsModule,
    TranslateModule.forRoot(),
    UsedMaterialModule,
    GridsterModule,
    FormsModule,
    RouterTestingModule,
    FutureFactoryPipesModule,
    FutureFactoryComponentsModule,
  ],
  exports: [
    NoopAnimationsModule,
    TranslateModule,
    UsedMaterialModule,
    GridsterModule,
    FormsModule,
    RouterTestingModule,
    FutureFactoryPipesModule,
    FutureFactoryComponentsModule,
  ],
})
export class FutureFactoryTestingModule {}
