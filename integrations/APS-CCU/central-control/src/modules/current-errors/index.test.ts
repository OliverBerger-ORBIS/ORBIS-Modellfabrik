import { VdaError } from '../../../../common/protocol/vda';
import CurrentErrorsService from './current-errors.service';
import { handleCurrentErrorsMessage } from './index';

describe('handleCurrentErrorsMessage', () => {
  let addErrorSpy: jest.SpyInstance<void, [serialNumber: string, error: VdaError | VdaError[]], unknown>;
  let removeErrorSpy: jest.SpyInstance<void, [serialNumber: string], unknown>;

  beforeEach(() => {
    jest.restoreAllMocks();
    addErrorSpy = jest.spyOn(CurrentErrorsService.getInstance(), 'addError');
    removeErrorSpy = jest.spyOn(CurrentErrorsService.getInstance(), 'removeError');
  });

  it('should ignore empty message', async () => {
    await handleCurrentErrorsMessage('');
    expect(addErrorSpy).not.toHaveBeenCalled();
  });

  it('should ignore message with missing serialNumber', async () => {
    await handleCurrentErrorsMessage('{}');
    expect(addErrorSpy).not.toHaveBeenCalled();
  });

  it('should not try to add errors for message with missing errors', async () => {
    await handleCurrentErrorsMessage('{"serialNumber":"123"}');
    expect(addErrorSpy).not.toHaveBeenCalled();
  });

  it('should delete errors for a message without errors', async () => {
    await handleCurrentErrorsMessage('{"serialNumber":"123"}');
    expect(removeErrorSpy).toHaveBeenCalled();
  });

  it('should not delete errors for a message with errors', async () => {
    await handleCurrentErrorsMessage('{"serialNumber":"123", "errors": [{"errorType": "TEST_error", "errorLevel": "WARNING"}]}');
    expect(removeErrorSpy).not.toHaveBeenCalled();
  });
});
