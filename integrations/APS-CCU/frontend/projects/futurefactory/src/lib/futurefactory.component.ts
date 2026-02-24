import { Component, OnDestroy } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import { ReplaySubject, takeUntil } from 'rxjs';
import { ModuleTopic, getModuleTopic } from '../common/protocol';
import { ConnectionState } from '../common/protocol/vda';
import { FutureFactoryRoutes } from './futurefactory.routes';
import { TypedMqttService } from './services/typed-mqtt.service';
import { getPayload } from './utils/rx.utils';
import { CollisionWarningDetectorService } from './services/collision-warning-detector.service';

type NodeRedConnectionStatus = { connectionState: ConnectionState };

@Component({
  selector: 'ff-futurefactory',
  templateUrl: './futurefactory.component.html',
  styleUrls: [
    './futurefactory.component.scss',
    // Included the fonts definitions here, that were taken from the cloud-based google fonts
    './futurefactory.fonts.scss',
  ],
  providers: [CollisionWarningDetectorService],
})
export class FutureFactoryComponent implements OnDestroy {
  private readonly destroy$ = new ReplaySubject<boolean>(1);
  readonly FutureFactoryRoutes = FutureFactoryRoutes;

  constructor(
    private mqttService: TypedMqttService,
    private translate: TranslateService,
    private notification: MatSnackBar,
    private collisionWarningDetectorService: CollisionWarningDetectorService
  ) {
    this.mqttService
      .subscribe<NodeRedConnectionStatus>(
        getModuleTopic('NodeRed', 'status' as ModuleTopic)
      )
      .pipe(getPayload(), takeUntil(this.destroy$))
      .subscribe((status) => {
        if (status.connectionState === ConnectionState.ONLINE) {
          this.notification.dismiss();
        } else {
          this.notification.open(
            this.translate.instant(
              'Die zentrale Steuerung hat die Verbindung zur APS verloren. Bitte starten Sie die zentrale Steuerung neu.'
            ),
            undefined,
            {
              duration: 0,
              panelClass: 'error-snackbar',
              horizontalPosition: 'center',
              verticalPosition: 'top',
            }
          );
        }
      });
    collisionWarningDetectorService.init();
  }

  ngOnDestroy(): void {
    this.destroy$.next(true);
    this.destroy$.complete();
  }
}
