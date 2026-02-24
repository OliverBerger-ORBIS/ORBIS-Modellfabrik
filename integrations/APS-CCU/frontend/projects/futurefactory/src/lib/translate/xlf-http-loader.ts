import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { TranslateLoader } from '@ngx-translate/core';
import { ValidationError, XMLParser, XMLValidator } from 'fast-xml-parser';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

export type TranslationUnit = {
  '@_id': string;
  '@_datatype': string;
  source: string;
  target: {
    '#text': string;
    '@_state': string;
  };
  'context-group'?: {
    '@_purpose': string;
    context: Array<{
      '#text': string;
      '@_context-type': string;
    }>;
  };
};

export class TranslateXlfHttpLoader implements TranslateLoader {
  constructor(
    private http: HttpClient,
    public prefix: string = 'assets/i18n/messages.',
    public suffix: string = '.xlf'
  ) {}

  /**
   * Gets the translations from the server
   */
  public getTranslation(lang: string): Observable<Object> {
    const targetFile = `${this.prefix}${lang}${this.suffix}`;
    return this.http
      .get(targetFile, {
        responseType: 'text',
        observe: 'body',
      })
      .pipe(
        map((raw) => {
          const validationResult: boolean | ValidationError =
            XMLValidator.validate(raw);
          if (validationResult !== true) {
            throw new Error(
              `Invalid XML: ${validationResult.err.msg} at ${validationResult.err.line}:${validationResult.err.col}`
            );
          }
          return raw;
        }),
        map((raw) => {
          const parser: XMLParser = new XMLParser({
            ignoreAttributes: false,
          });
          return parser.parse(raw);
        }),
        map((translations) => {
          if (!translations.xliff) {
            throw new Error(`Invalid XLIFF: missing xliff root element`);
          }
          if (!translations.xliff.file) {
            throw new Error(`Invalid XLIFF: missing xliff.file element`);
          }
          if (!translations.xliff.file.body) {
            throw new Error(`Invalid XLIFF: missing xliff.file.body element`);
          }
          return translations.xliff.file.body['trans-unit'];
        }),
        map((translationUnits: TranslationUnit[]) =>
          translationUnits.reduce((acc, unit) => {
            const id = unit['@_id'];
            if (!id || !unit.target) {
              return acc;
            }
            if (typeof unit.target === 'string') {
              acc[id] = unit.target;
            } else if (typeof unit.target === 'object') {
              acc[id] = unit.target['#text'];
            }
            return acc;
          }, {} as Record<string, string>)
        ),
        tap(translations => {
          console.groupCollapsed(`Loaded ${Object.keys(translations).length} translations for targetFile ${targetFile}`);
          console.table(translations);
          console.groupEnd();
        }),
        catchError((error) => {
          console.error(`Failed to load translation for targetFile ${targetFile}:`, error);
          // if the translation file cannot be loaded, return an empty object
          return of({});
        }),
      );
  }
}
