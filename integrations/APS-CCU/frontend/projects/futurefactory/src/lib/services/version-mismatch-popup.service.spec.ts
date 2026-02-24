import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { of } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { VersionMismatchPopupComponent } from '../components/version-mismatch-popup/version-mismatch-popup.component';
import { TypedMqttService } from './typed-mqtt.service';
import { VersionMismatchPopupService } from './version-mismatch-popup.service';
import { MismatchedModule } from '../../common/protocol/ccu';
import { ModuleType } from '../../common/protocol/module';

describe('VersionMismatchPopupService', () => {
  let service: VersionMismatchPopupService;
  let mqttService: TypedMqttService;
  let dialog: MatDialog;
  let mismatchedModule: MismatchedModule;

  beforeEach(() => {
    mismatchedModule = {
      is24V: false,
      isTXT: false,
      moduleType: ModuleType.AIQS,
      deviceType: 'MODULE',
      version: '1.0.0',
      serialNumber: '123456',
      seriesName: 'test',
      seriesUnknown: false,
      requiredVersion: '1.0.0',
    };
    TestBed.configureTestingModule({
      providers: [
        VersionMismatchPopupService,
        MockProvider(TypedMqttService, {
          subscribe: jest.fn(() => of({ payload: { mismatchedModules: [mismatchedModule] } } as any)),
        }),
        MockProvider(MatDialog, {
          open: jest.fn(() => ({
            afterClosed: jest.fn(() => of(null)),
            componentInstance: { data: {} },
          })),
        } as any),
      ],
    });

    service = TestBed.inject(VersionMismatchPopupService);
    mqttService = TestBed.inject(TypedMqttService);
    dialog = TestBed.inject(MatDialog);
  });

  it('should initialize and subscribe to mqttService', () => {
    service.init();
    expect(mqttService.subscribe).toHaveBeenCalled();
  });

  it('should open a new dialog when receiving a message with mismatched modules', () => {
    service.init();
    expect(dialog.open).toHaveBeenCalledWith(VersionMismatchPopupComponent, {
      data: { message: { mismatchedModules: [mismatchedModule] } },
      disableClose: true,
    });
  });

  it('should close the dialog when receiving a message without mismatched modules', () => {
    jest.spyOn(mqttService, 'subscribe').mockReturnValueOnce(of({ payload: { mismatchedModules: [] } } as any));
    service.init();
    expect(dialog.open).not.toHaveBeenCalled();
  });
});
