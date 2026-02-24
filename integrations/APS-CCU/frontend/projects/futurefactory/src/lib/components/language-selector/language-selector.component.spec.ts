import { LOCALE_ID } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { I18nService } from '@fischertechnik/ft-common-ui';
import { MockProvider } from 'ng-mocks';
import { EMPTY } from 'rxjs';
import { ShowLanguageSelector } from '../../futurefactory.external.service';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { LanguageSelectorComponent } from './language-selector.component';

describe('LanguageSelectorComponent', () => {
  let fixture: ComponentFixture<LanguageSelectorComponent>;
  let component: LanguageSelectorComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [LanguageSelectorComponent],
      providers: [
        MockProvider(ShowLanguageSelector, true),
        MockProvider(I18nService, {
          use: jest.fn(() => EMPTY),
        }),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LanguageSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the language selector', () => {
    expect(fixture).toMatchSnapshot();
  });
});
