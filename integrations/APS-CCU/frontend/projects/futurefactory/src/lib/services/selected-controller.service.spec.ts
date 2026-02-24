import { TestBed } from '@angular/core/testing';
import { ControllerResponse } from '@fischertechnik/ft-api';
import { MockProvider } from 'ng-mocks';
import { EMPTY, Observable } from 'rxjs';
import { TestScheduler } from 'rxjs/testing';
import { ControllerClientService } from '../futurefactory.external.service';
import { SelectedControllerService } from './selected-controller.service';

describe('SelectedControllerService', () => {
  const testScheduler = new TestScheduler((actual, expected) => {
    expect(actual).toEqual(expected);
  });

  type RunTest = {
    onChange?: () => Observable<ControllerResponse[]>;
    loadControllers?: () => void;
  };
  const runTest = (
    { onChange = () => EMPTY, loadControllers = jest.fn() }: RunTest = {
      onChange: () => EMPTY,
      loadControllers: jest.fn(),
    }
  ): SelectedControllerService => {
    TestBed.configureTestingModule({
      providers: [
        SelectedControllerService,
        MockProvider(ControllerClientService, {
          onChange,
          loadControllers,
        }),
      ],
    });
    return TestBed.inject(SelectedControllerService);
  };

  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should be created', () => {
    const loadMock = jest.fn();
    const service = runTest({ loadControllers: loadMock });
    expect(service).toBeTruthy();
    expect(loadMock).toHaveBeenCalledTimes(1);
  });

  it('should call the load function of the controller service', () => {
    const loadMock = jest.fn();
    const service = runTest({ loadControllers: loadMock });
    service.loadControllers();
    expect(loadMock).toHaveBeenCalledTimes(2);
  });

  it('should return no controller from the available controllers, because the module does not match', () => {
    testScheduler.run(({ cold, expectObservable }) => {
      const availableControllers$ = cold<ControllerResponse[]>('e---a---b', {
        e: [],
        a: [{ controllerId: 1, name: 'controller1' }],
        b: [
          { controllerId: 1, name: 'controller1' },
          { controllerId: 2, name: 'controller2' },
        ],
      });
      const service = runTest({ onChange: () => availableControllers$ });
      expectObservable(service.selectedController$).toBe('u--------', {
        u: undefined,
        a: { controllerId: 1, name: 'controller1' },
        b: { controllerId: 1, name: 'controller1' },
      });
    });
  });

  it('should return first controller from the available controllers', () => {
    testScheduler.run(({ cold, expectObservable }) => {
      const availableControllers$ = cold<ControllerResponse[]>('e---a---b', {
        e: [],
        a: [{ controllerId: 1, targetModule: 2, name: 'controller1' }],
        b: [
          { controllerId: 1, targetModule: 2, name: 'controller1' },
          { controllerId: 2, targetModule: 3, name: 'controller2' },
        ],
      });
      const service = runTest({ onChange: () => availableControllers$ });
      expectObservable(service.selectedController$).toBe('8ms u 7ms b', {
        u: undefined,
        b: { controllerId: 2, targetModule: 3, name: 'controller2' },
      });
    });
  });
});
