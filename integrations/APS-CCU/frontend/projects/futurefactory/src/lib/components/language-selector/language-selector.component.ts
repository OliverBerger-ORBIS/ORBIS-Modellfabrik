import { Component, Inject, LOCALE_ID } from '@angular/core';
import { Router } from '@angular/router';
import { I18nService } from '@fischertechnik/ft-common-ui';
import { ShowLanguageSelector } from '../../futurefactory.external.service';

@Component({
  selector: 'ff-language-selector',
  templateUrl: './language-selector.component.html',
  styleUrls: ['./language-selector.component.scss'],
})
export class LanguageSelectorComponent {
  selectedLocale: string;
  readonly locales = ['de', 'en', 'es', 'fr', 'nl', 'pt', 'ru'];

  constructor(
    @Inject(ShowLanguageSelector) readonly showLanguageSelector: boolean,
    @Inject(LOCALE_ID) protected locale: string,
    private i18n: I18nService,
    private router: Router
  ) {
    this.selectedLocale = locale;
    this.i18n.use(locale);
  }

  setLanguage(locale: string) {
    this.selectedLocale = locale;
    this.i18n.use(locale);
    location.href = `/${locale}/aps${this.router.url}`;
  }
}
