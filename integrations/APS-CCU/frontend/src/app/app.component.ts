import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { map } from 'rxjs/operators';
import { RoutePaths } from './app.routes';
import { APP_TITLE } from './constants';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  readonly APP_TITLE = APP_TITLE;
  readonly RoutePaths = RoutePaths;

  readonly i18nIsFullyLoaded$ = this.translate
    .getStreamOnTranslationChange('dashboardOrder')
    .pipe(map((value) => value !== 'dashboardOrder'));

  constructor(private translate: TranslateService) {}
}
