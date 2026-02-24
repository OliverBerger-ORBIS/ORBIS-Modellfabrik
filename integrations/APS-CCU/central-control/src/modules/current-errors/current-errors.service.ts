import { VdaError } from '../../../../common/protocol/vda';

export type CurrentError = {
  serialNumber: string;
  errors: Array<VdaError> | null;
};

class CurrentErrorsService {
  private static instance: CurrentErrorsService;
  private readonly currentErrors: Map<string, Array<VdaError> | null>;

  private constructor() {
    this.currentErrors = new Map<string, Array<VdaError> | null>();
  }

  public static getInstance(): CurrentErrorsService {
    if (!CurrentErrorsService.instance) {
      CurrentErrorsService.instance = new CurrentErrorsService();
    }
    return CurrentErrorsService.instance;
  }

  public hasError(serialNumber: string): boolean {
    return this.currentErrors.has(serialNumber);
  }

  public getAllCurrentErrors(): Array<CurrentError> {
    const currentErrors: Array<CurrentError> = [];
    for (const [serialNumber, errors] of this.currentErrors.entries()) {
      currentErrors.push({ serialNumber, errors: errors });
    }
    return currentErrors;
  }

  public getError(serialNumber: string): Array<VdaError> | null {
    return this.currentErrors.get(serialNumber) ?? null;
  }

  public addError(serialNumber: string, error: VdaError | Array<VdaError>): void {
    const existing = this.currentErrors.get(serialNumber);
    const newErrors = Array.isArray(error) ? [...error] : [error];
    this.currentErrors.set(serialNumber, existing ? [...existing, ...newErrors] : newErrors);
  }

  public removeError(serialNumber: string): void {
    this.currentErrors.delete(serialNumber);
  }
}

export default CurrentErrorsService;
