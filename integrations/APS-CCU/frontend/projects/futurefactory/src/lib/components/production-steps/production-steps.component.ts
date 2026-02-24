import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { OrderResponse } from '../../../common/protocol';
import { OrderState } from '../../../common/protocol/ccu';
import { ModuleCommandType } from '../../../common/protocol/module';
import { MODULE_ICON_PATHS } from '../../utils/routes.utils';

@Component({
  selector: 'ff-production-steps',
  templateUrl: './production-steps.component.html',
  styleUrls: ['./production-steps.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProductionStepsComponent {
  readonly MODULE_ICON_PATHS = MODULE_ICON_PATHS;
  readonly actionHtmlStrings: { [t in ModuleCommandType]: string } = {
    [ModuleCommandType.CHECK_QUALITY]: 'Qualitätsprüfung',
    [ModuleCommandType.PICK]: 'FTS entladen',
    [ModuleCommandType.DROP]: 'FTS beladen',
    [ModuleCommandType.MILL]: 'Fräsen',
    [ModuleCommandType.DRILL]: 'Bohren',
    [ModuleCommandType.FIRE]: 'Erhitzen',
  };
  readonly stateIcons: { [t in OrderState]: string } = {
    [OrderState.ENQUEUED]: 'hourglass_empty',
    [OrderState.IN_PROGRESS]: 'play_circle',
    [OrderState.FINISHED]: 'check_circle',
    [OrderState.ERROR]: 'error',
    [OrderState.CANCELLED]: 'hourglass_disabled',
  };

  @Input() order: OrderResponse | undefined = undefined;
}
