import { map, Observable } from 'rxjs';
import { ROUTE_TO_MODULE_ROOT } from '../futurefactory.routes';
import { ActivatedRoute } from '@angular/router';
import { DeviceType } from '../../common/protocol/ccu';
import { ModuleType } from '../../common/protocol/module';

export function getRouteToModuleRoot(activatedRoute: ActivatedRoute): Observable<string> {
  return activatedRoute.data.pipe(map(data => `${data[ROUTE_TO_MODULE_ROOT] ?? '.'}`));
}

export const MODULE_ICON_PATHS: { [t in ModuleType | DeviceType | 'undefined' | 'UNDEFINED' ]: string } = {
  [ModuleType.AIQS]: 'assets/images/ic_ft_aiqs.svg',
  [ModuleType.HBW]: 'assets/images/ic_ft_hbw.svg',
  [ModuleType.DPS]: 'assets/images/ic_ft_dps.svg',
  [ModuleType.DRILL]: 'assets/images/ic_ft_drill.svg',
  [ModuleType.MILL]: 'assets/images/ic_ft_mill.svg',
  [ModuleType.CHRG]: 'assets/images/ic_ft_chrg.svg',
  [ModuleType.OVEN]: 'assets/images/ic_ft_oven.svg',
  [ModuleType.START]: 'assets/images/placeholder.svg',
  'MODULE': 'assets/images/placeholder.svg',
  'FTS': 'assets/images/ic_ft_fts.svg',
  'UNDEFINED': 'assets/images/placeholder.svg',
  'undefined': 'assets/images/placeholder.svg'
};
