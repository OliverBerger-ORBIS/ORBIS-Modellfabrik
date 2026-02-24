import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatIconModule } from '@angular/material/icon';
import { CollisionWarningPopupComponent } from './collision-warning-popup.component';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MockModule, MockProvider } from 'ng-mocks';
import { TypedMqttService } from '../../futurefactory.service';
import { EMPTY } from 'rxjs';
import { TranslateModule } from '@ngx-translate/core';

describe('PopupComponent', () => {
  let fixture: ComponentFixture<CollisionWarningPopupComponent>;
  let component: CollisionWarningPopupComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatIconModule, MatDialogModule, MockModule(TranslateModule)],
      declarations: [CollisionWarningPopupComponent],
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
    fixture = TestBed.createComponent(CollisionWarningPopupComponent);
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
