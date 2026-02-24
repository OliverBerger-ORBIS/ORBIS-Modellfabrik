import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { TranslateService } from '@ngx-translate/core';
import { BehaviorSubject, Observable, Subscription } from 'rxjs';
import { map } from 'rxjs/operators';
import { AvailableState, DeviceType, FtsPairedModule, PairedModule, PairingState } from '../../../common/protocol/ccu';
import { ModuleType } from '../../../common/protocol/module';

export interface ModuleListData {
  type: DeviceType;
  subType: ModuleType | undefined;
  serialNumber: string;
  connected: boolean;
  available: AvailableState | undefined;
  ip: string | undefined;
  version: string | undefined;
  pairedSince: Date | undefined;
  hasCalibration: boolean | undefined;
  charging: boolean | undefined;
}

export class ModuleListDataSource extends MatTableDataSource<ModuleListData> {
  private collection$: Subscription | undefined;
  private connectionCount = 0;

  constructor(
    private pairingState$: Observable<PairingState>,
    private translate: TranslateService
  ) {
    super();
  }

  override connect(): BehaviorSubject<ModuleListData[]> {
    const isFts = (mod: PairedModule | FtsPairedModule): mod is FtsPairedModule => mod?.type === 'FTS';
    if (!this.collection$) {
      this.collection$ = this.pairingState$
        .pipe(
          map((data) => [...data.modules, ...data.transports] as const),
          map((data) =>
            data.map((mod) => {
              return {
                type: mod.type,
                subType: mod.subType,
                ip: mod.ip,
                version: mod.version,
                connected: mod.connected ?? false,
                available: mod.available,
                pairedSince: mod.pairedSince,
                serialNumber: mod.serialNumber,
                hasCalibration: mod.hasCalibration,
                charging: (isFts(mod)) ? mod.charging : undefined,
              } as ModuleListData;
            })
          )
        )
        .subscribe((data) => (this.data = data));
    }
    this.connectionCount++;
    return super.connect();
  }

  override disconnect() {
    if (this.connectionCount) {
      this.connectionCount--;
      if (this.connectionCount === 0 && this.collection$) {
        this.collection$.unsubscribe();
        this.collection$ = undefined;
      }
    }
    super.disconnect();
  }

  override readonly sortingDataAccessor = (
    data: ModuleListData,
    sortHeaderId: string
  ): string | number => {
    switch (sortHeaderId) {
      case 'serialNumber': {
        return data.serialNumber;
      }
      case 'connected': {
        return data.connected ? 1 : 0;
      }
      case 'name': {
        return this.translate.instant(
          'Produktionsschritt.' + (data.subType ?? data.type)
        );
      }
      default: {
        return '';
      }
    }
  };

  override readonly sortData = (
    data: ModuleListData[],
    sort: MatSort
  ): ModuleListData[] => {
    const active = sort.active;
    const direction = sort.direction;
    if (!active || direction === '') {
      return data;
    }

    return data.sort((a, b) => {
      const valueA = this.sortingDataAccessor(a, active);
      const valueB = this.sortingDataAccessor(b, active);

      return (valueA < valueB ? -1 : 1) * (direction === 'asc' ? 1 : -1);
    });
  };
}
