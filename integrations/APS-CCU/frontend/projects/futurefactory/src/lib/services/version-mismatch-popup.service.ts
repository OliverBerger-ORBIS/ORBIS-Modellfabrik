import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { VersionMismatchPopupComponent } from '../components/version-mismatch-popup/version-mismatch-popup.component';
import { TypedMqttService } from './typed-mqtt.service';
import { Subscription } from 'rxjs';
import { Injectable, OnDestroy } from '@angular/core';
import { MismatchedVersionMessage } from '../../common/protocol/ccu';
import { CcuTopic } from '../../common/protocol';

@Injectable()
export class VersionMismatchPopupService implements OnDestroy {
  private dialogRef: MatDialogRef<VersionMismatchPopupComponent> | null = null;
  private subscription: Subscription | null = null;
  private lastMessageDate: Date | null = null;

  constructor(private mqttService: TypedMqttService, private dialog: MatDialog) {}

  init() {
    if (!this.subscription) {
      this.subscription = this.mqttService.subscribe<MismatchedVersionMessage>(CcuTopic.VERSION_MISMATCH).subscribe((message) => {
        if (!message.payload.mismatchedModules || message.payload.mismatchedModules.length === 0) {
          this.closeDialog();
        } else {
          this.updateDialog(message.payload);
        }
      });
    }
  }

  /**
   * Update the dialog with the new message or open a new dialog if one isn't already open.
   * If the message is older than the last displayed message, it will be ignored.
   *
   * @param message
   * @private
   */
  private updateDialog(message: MismatchedVersionMessage) {
    if (this.dialogRef) {
      // Update the data of the currently open dialog
      this.lastMessageDate = message.timestamp;
      this.dialogRef.componentInstance.data.message = message;
    } else if (!this.lastMessageDate || this.lastMessageDate < message.timestamp) {
      this.lastMessageDate = message.timestamp;
      // Open a new dialog if one isn't already open
      this.dialogRef = this.dialog.open(VersionMismatchPopupComponent, {
        data: { message: message },
        disableClose: true,
      });

      // Handle dialog close event
      this.dialogRef.afterClosed().subscribe(() => {
        this.dialogRef = null;
      });
    }
  }

  closeDialog() {
    if (this.dialogRef) {
      this.dialogRef.close();
      this.dialogRef = null;
    }
  }

  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
      this.subscription = null;
    }
    this.closeDialog();
  }
}
