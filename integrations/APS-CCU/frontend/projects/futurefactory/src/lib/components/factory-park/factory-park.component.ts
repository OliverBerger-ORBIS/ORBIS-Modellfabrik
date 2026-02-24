import { Component, TemplateRef, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { CcuTopic } from '../../../common/protocol';
import { ParkRequest } from '../../../common/protocol/ccu';
import { TypedMqttService } from '../../services/typed-mqtt.service';

@Component({
  selector: 'ff-factory-park',
  templateUrl: './factory-park.component.html',
  styleUrls: ['./factory-park.component.scss'],
})
export class FactoryParkComponent {
  @ViewChild('parkDialogContent')
  readonly parkDialogContent!: TemplateRef<any>;
  constructor(private dialog: MatDialog, private mqtt: TypedMqttService) {}

  confirmFactoryPark() {
    this.dialog.open(this.parkDialogContent);
  }

  sendFactoryPark() {
    const park: ParkRequest = {
      timestamp: new Date(),
    };
    this.mqtt.publish(CcuTopic.SET_PARK, park, { qos: 2 });
  }
}
