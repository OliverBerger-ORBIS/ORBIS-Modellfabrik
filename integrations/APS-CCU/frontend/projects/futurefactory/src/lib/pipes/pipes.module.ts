import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FallbackValuePipe } from './fallback-value/fallback-value.pipe';
import { FilterRefPipe } from './filter-ref/filter-ref.pipe';
import { ToIconPipe } from './to-icon/to-icon.pipe';
import { ToLabelPipe } from './to-label/to-label.pipe';
import { ToSecondsPipe } from './to-seconds/to-seconds.pipe';
import { IsErrorLevelPipe } from './is-errorlevel/is-errorlevel.pipe';

@NgModule({
  imports: [CommonModule],
  declarations: [
    FallbackValuePipe,
    ToIconPipe,
    ToLabelPipe,
    ToSecondsPipe,
    IsErrorLevelPipe,
    FilterRefPipe,
  ],
  exports: [
    FallbackValuePipe,
    ToIconPipe,
    ToLabelPipe,
    ToSecondsPipe,
    IsErrorLevelPipe,
    FilterRefPipe,
  ],
})
export class FutureFactoryPipesModule {}
