import { Pipe, PipeTransform } from '@angular/core';
import { StateLog } from '../../services/states.service';
import { ConnectionState } from '../../../common/protocol/vda';

export type ErrorLevel = 'NONE' | 'FATAL' | 'WARNING';

@Pipe({
  name: 'isErrorLevel'
})
export class IsErrorLevelPipe implements PipeTransform {
  transform(log: StateLog, severity: ErrorLevel): boolean {
    if (log.type === 'MODULE' || log.type === 'FTS') {
      if (log.state?.errors?.find(err => err.errorLevel == 'FATAL')) {
        return severity === 'FATAL';
      } else if (log.state?.errors?.find(err => err.errorLevel == 'WARNING')) {
        return severity === 'WARNING';
      }
    } else if (log.type === 'CONNECTION') {
      if (log.state.connectionState === ConnectionState.CONNECTIONBROKEN) {
        return severity === 'WARNING';
      }
    }
    return severity === 'NONE';
  }
}
