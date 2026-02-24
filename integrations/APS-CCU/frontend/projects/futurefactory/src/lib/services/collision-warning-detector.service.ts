import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { Subscription } from 'rxjs';
import { Injectable, OnDestroy } from '@angular/core';
import { PairingState } from '../../common/protocol/ccu';
import {
  CollisionWarningPopupComponent
} from '../components/collision-warning-popup/collision-warning-popup.component';
import { StatesService } from './states.service';
import { FtsErrors, FtsState } from '../../common/protocol/fts';
import { map, withLatestFrom } from 'rxjs/operators';

@Injectable()
export class CollisionWarningDetectorService implements OnDestroy {
  private dialogRef: MatDialogRef<CollisionWarningPopupComponent> | null = null;
  private subscription: Subscription | null = null;

  constructor(private statesService: StatesService, private dialog: MatDialog) {
  }

  init() {
    if (!this.subscription) {
      this.subscription = this.statesService.ftsStates$.pipe(
        // only include states with collision warnings:
        map((states) => this.getFtsWithCollisions(states)),
        withLatestFrom(this.statesService.pairingState$),
        // filter collisions array to only include paired FTS:
        map(([collisions, pairings]) =>
          collisions.filter((collision) => this.isPairedFtsSerial(collision.serialNumber, pairings))
        )
      ).subscribe((collisions) => {
        if (collisions && collisions.length > 0) {
          if (this.dialogRef) {
            this.dialogRef.componentInstance.data.collisions = collisions;
          } else {
            this.dialogRef = this.dialog.open(CollisionWarningPopupComponent, {
              data: { collisions },
              disableClose: true,
            });

            this.dialogRef.afterClosed().subscribe(() => {
              this.dialogRef = null;
            });
          }
        } else {
          this.closeDialog();
        }
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

  private hasCollisionWarning(state: FtsState) {
    return state.errors && state.errors.some((error) => error.errorType === FtsErrors.COLLISION);
  }

  private getFtsWithCollisions(states: Map<string, FtsState>): FtsState[] {
    return [...states.values()].filter((state) => this.hasCollisionWarning(state)).map((state) => state);
  }

  private isPairedFtsSerial(serialNumber: string, pairings: PairingState) {
    return pairings.transports?.some((pairing) => pairing.serialNumber === serialNumber);
  }
}
