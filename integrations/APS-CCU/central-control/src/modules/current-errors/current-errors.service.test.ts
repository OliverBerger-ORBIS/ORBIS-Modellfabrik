import { VdaError } from '../../../../common/protocol/vda';
import CurrentErrorsService from './current-errors.service';

describe('CurrentErrorsService', () => {
  const newErrors: VdaError[] = [{ errorLevel: 'WARNING', errorType: 'TEST_error', timestamp: new Date() }];

  afterEach(() => {
    const currentErrors = CurrentErrorsService.getInstance().getAllCurrentErrors();
    for (const current of currentErrors) {
      CurrentErrorsService.getInstance().removeError(current.serialNumber);
    }
  });

  it('should add and return a single error', () => {
    CurrentErrorsService.getInstance().addError('123', newErrors);
    const added = CurrentErrorsService.getInstance().getError('123');
    expect(added).toEqual(newErrors);
  });

  it('should add and return a list of errors', () => {
    CurrentErrorsService.getInstance().addError('123', newErrors[0]);
    const added = CurrentErrorsService.getInstance().getError('123');
    expect(added).toEqual(newErrors);
  });

  it('should add an error to a list of existing errors', () => {
    const hasError = CurrentErrorsService.getInstance().hasError('123');
    expect(hasError).toBeFalsy();
    CurrentErrorsService.getInstance().addError('123', newErrors);
    const oneElement = CurrentErrorsService.getInstance().getError('123');
    expect(oneElement).toEqual(newErrors);
    CurrentErrorsService.getInstance().addError('123', newErrors[0]);
    const twoElements = CurrentErrorsService.getInstance().getError('123');
    expect(twoElements).toEqual([newErrors[0], newErrors[0]]);
    CurrentErrorsService.getInstance().addError('123', newErrors);
    const added = CurrentErrorsService.getInstance().getError('123');
    expect(added).toEqual([newErrors[0], newErrors[0], newErrors[0]]);
  });

  it('should return null, if no error is found', () => {
    const added = CurrentErrorsService.getInstance().getError('123');
    expect(added).toBeNull();
  });

  it('should add and remove and error', () => {
    CurrentErrorsService.getInstance().addError('123', newErrors);
    const added = CurrentErrorsService.getInstance().hasError('123');
    expect(added).toBeTruthy();
    CurrentErrorsService.getInstance().removeError('123');
    const removed = CurrentErrorsService.getInstance().hasError('123');
    expect(removed).toBeFalsy();
  });

  it('should add and return all errors', () => {
    CurrentErrorsService.getInstance().addError('123', newErrors);
    const added = CurrentErrorsService.getInstance().getAllCurrentErrors();
    expect(added).toEqual([{ serialNumber: '123', errors: newErrors }]);
  });
});
