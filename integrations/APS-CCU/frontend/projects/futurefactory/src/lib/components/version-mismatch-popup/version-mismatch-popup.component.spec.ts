import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatIconModule } from '@angular/material/icon';
import { VersionMismatchPopupComponent } from './version-mismatch-popup.component';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MockModule, MockProvider } from 'ng-mocks';
import { TypedMqttService } from '../../futurefactory.service';
import { EMPTY } from 'rxjs';
import { TranslateModule } from '@ngx-translate/core';

describe('PopupComponent', () => {
  let fixture: ComponentFixture<VersionMismatchPopupComponent>;
  let component: VersionMismatchPopupComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatIconModule, MatDialogModule, MockModule(TranslateModule)],
      declarations: [VersionMismatchPopupComponent],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: () => EMPTY,
        }),
        {
          provide: MAT_DIALOG_DATA,
          useValue: {}
        },
      ]
    }).compileComponents();

    jest.useFakeTimers().setSystemTime(1699604177818);
    fixture = TestBed.createComponent(VersionMismatchPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
