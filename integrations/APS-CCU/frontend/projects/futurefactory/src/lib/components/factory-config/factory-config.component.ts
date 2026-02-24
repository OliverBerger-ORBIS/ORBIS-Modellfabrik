import { Component, Input, OnDestroy } from '@angular/core';
import { GeneralConfig } from '../../../common/protocol/ccu';
import { ReplaySubject } from 'rxjs';
import { takeUntil } from 'rxjs/internal/operators/takeUntil';
import { GeneralConfigService } from '../../services/general-config.service';
import { WORKPIECE_TYPES } from '../../utils/workpiece.utils';

@Component({
  selector: 'ff-factory-config',
  templateUrl: './factory-config.component.html',
  styleUrls: ['./factory-config.component.css'],
})
export class FactoryConfigComponent implements OnDestroy {
  @Input() editable: boolean = false;

  private destroy$ = new ReplaySubject<void>(1);

  public config: GeneralConfig | undefined;
  public originalConfig: GeneralConfig | undefined;
  public wsTypes = WORKPIECE_TYPES;

  /**
   * Indicates if the user has changed the config.
   */
  public get configChanged(): boolean {
    return JSON.stringify(this.config) !== JSON.stringify(this.originalConfig);
  }

  constructor(private generalConfigService: GeneralConfigService) {
    this.generalConfigService.config$
      .pipe(takeUntil(this.destroy$))
      .subscribe((config: GeneralConfig) => {
        this.config = config
        this.originalConfig = JSON.parse(JSON.stringify(config));
      });
  }

  saveConfig() {
    if (this.config) {
      this.generalConfigService.saveConfig(this.config);
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
