import { Component, TemplateRef, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { take } from 'rxjs/operators';
import { CcuTopic } from '../../../common/protocol';
import { ResetRequest } from '../../../common/protocol/ccu';
import { TypedMqttService } from '../../services/typed-mqtt.service';

@Component({
  selector: 'ff-factory-reset',
  templateUrl: './factory-reset.component.html',
  styleUrls: ['./factory-reset.component.scss'],
})
export class FactoryResetComponent {
  @ViewChild('resetDialogContent')
  readonly resetDialogContent!: TemplateRef<any>;
  constructor(private dialog: MatDialog, private mqtt: TypedMqttService) {}

  withStorage: boolean = false;

  confirmFactoryReset() {
    this.dialog
      .open(this.resetDialogContent)
      .afterClosed()
      .pipe(take(1))
      .subscribe(() => this.clearState());
  }

  clearState() {
    this.withStorage = false;
  }

  sendFactoryReset() {
    const reset: ResetRequest = {
      timestamp: new Date(),
      withStorage: this.withStorage,
    };
    this.mqtt.publish(CcuTopic.SET_RESET, reset, { qos: 2 });
  }
}
