import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { TranslateService } from '@ngx-translate/core';
import { AppComponent } from './app.component';
import { UsedMaterialModule } from './used-material.module';
import { of } from 'rxjs';

describe('AppComponent', () => {
  let fixture: ComponentFixture<AppComponent>;
  let component: AppComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, UsedMaterialModule],
      declarations: [AppComponent],
      providers: [
        {
          provide: TranslateService,
          useValue: {
            getStreamOnTranslationChange: () => of('Bestellung'),
          },
        },
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AppComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the app', () => {
    expect(component).toBeTruthy();
  });

  it('should render the app', () => {
    expect(fixture).toMatchSnapshot();
  });
});
