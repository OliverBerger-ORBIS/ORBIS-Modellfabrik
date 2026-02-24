import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { CcuTopic } from '../../../common/protocol';
import {
  DeleteModuleRequest,
  DeviceType,
  FtsChargeRequest,
  FtsPairingRequest,
  PairedModule,
} from '../../../common/protocol/ccu';
import { FutureFactoryRoutes } from '../../futurefactory.routes';
import { FactoryLayoutService } from '../../services/factory-layout.service';
import { TypedMqttService } from '../../services/typed-mqtt.service';
import { MODULE_ICON_PATHS } from '../../utils/routes.utils';
import {
  ModuleListData,
  ModuleListDataSource,
} from './module-list.data-source';

@Component({
  selector: 'ff-module-list',
  templateUrl: './module-list.component.html',
  styleUrls: ['./module-list.component.scss'],
})
export class FutureFactoryModuleListComponent implements AfterViewInit {
  readonly MODULE_ICON_PATHS = MODULE_ICON_PATHS;
  readonly CALIBRATION_ROUTE = FutureFactoryRoutes.CALIBRATION;
  readonly DeviceType = DeviceType;
  readonly displayedColumns = [
    'icon',
    'serialNumber',
    'name',
    'connected',
    'available',
    'paired',
  ];
  readonly dataSource: ModuleListDataSource;
  @ViewChild(MatSort) sort!: MatSort;
  readonly deletionMap = new Map<string, boolean>();

  constructor(
    readonly factoryLayoutService: FactoryLayoutService,
    private translate: TranslateService,
    private mqttService: TypedMqttService,
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) {
    this.dataSource = new ModuleListDataSource(
      factoryLayoutService.pairingState$,
      translate
    );
  }

  ngAfterViewInit() {
    this.dataSource.sort = this.sort;
  }

  getMetadata(mod: ModuleListData): string {
    if (!mod.ip || !mod.version) {
      return this.translate.instant('Keine Metadaten verfügbar');
    }
    return `${mod.version} - ${mod.ip}`;
  }

  getInFactorySince(mod: ModuleListData): string {
    if (!mod.pairedSince) {
      return this.translate.instant('nicht in Fabrik eingebunden');
    }
    return this.translate.instant('In Fabrik eingebunden seit {{since}}', {
      since: mod.pairedSince,
    });
  }

  getPairedSince(mod: ModuleListData): string {
    if (!mod.pairedSince) {
      return this.translate.instant('nicht im Layout');
    }
    return this.translate.instant('im Layout seit {{since}}', {
      since: mod.pairedSince,
    });
  }

  connectFts(mod: ModuleListData) {
    const request: FtsPairingRequest = {
      serialNumber: mod.serialNumber,
    };
    this.mqttService.publish(CcuTopic.PAIRING_PAIR_FTS, request, { qos: 2 });
  }

  moduleSelected(row: ModuleListData) {
    if (row.type === DeviceType.MODULE) {
      this.router.navigate([row.serialNumber], {
        relativeTo: this.activatedRoute,
      });
    }
  }

  setFtsCharge(mod: ModuleListData, charge: boolean) {
    const request: FtsChargeRequest = {
      serialNumber: mod.serialNumber,
      charge,
    };
    this.mqttService.publish(CcuTopic.SET_CHARGE, request, { qos: 2 });
  }

  hasConfirmedDelete(mod: ModuleListData): boolean {
    return this.deletionMap.get(mod.serialNumber) === true;
  }

  confirmDelete(mod: ModuleListData) {
    this.deletionMap.set(mod.serialNumber, true);
  }

  deleteModule(mod: ModuleListData) {
    if (this.deletionMap.get(mod.serialNumber) === true) {
      const request: DeleteModuleRequest = {
        serialNumber: mod.serialNumber,
      };
      this.mqttService.publish(CcuTopic.DELETE_MODULE, request, { qos: 2 });
    }
    this.deletionMap.delete(mod.serialNumber);
  }
}
