import { CdkDrag, CdkDropList } from '@angular/cdk/drag-drop';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MockProvider } from 'ng-mocks';
import { BehaviorSubject, EMPTY } from 'rxjs';
import { CcuTopic, Workpiece } from '../../../common/protocol';
import { ModuleType } from '../../../common/protocol/module';
import { MissingControllerBannerComponent } from '../../components/missing-controller-banner/missing-controller-banner.component';
import { FutureFactoryTestingModule } from '../../futurefactory.testing.module';
import { OrderStatesService } from '../../services/order-states.service';
import { SelectedControllerService } from '../../services/selected-controller.service';
import { TypedMqttService } from '../../services/typed-mqtt.service';
import { FutureFactoryFlowEditorComponent } from './flow-editor.component';

describe('FutureFactoryFlowEditorComponent', () => {
  let component: FutureFactoryFlowEditorComponent;
  let fixture: ComponentFixture<FutureFactoryFlowEditorComponent>;
  let typedMqttService: jest.Mocked<TypedMqttService>;
  let hasRunningOrdersSubject: BehaviorSubject<boolean>;

  beforeEach(async () => {
    hasRunningOrdersSubject = new BehaviorSubject<boolean>(false);
    await TestBed.configureTestingModule({
      imports: [FutureFactoryTestingModule],
      declarations: [
        FutureFactoryFlowEditorComponent,
        MissingControllerBannerComponent,
      ],
      providers: [
        MockProvider(TypedMqttService, {
          subscribe: jest.fn(() => EMPTY),
          publish: jest.fn(() => Promise.resolve()),
        }),
        MockProvider(OrderStatesService, {
          hasRunningOrders$: hasRunningOrdersSubject.asObservable(),
        }),
        MockProvider(SelectedControllerService, {
          availableControllers$: EMPTY,
          availableFutureFactoryControllers$: EMPTY,
        }),
        MockProvider(MatSnackBar, {
          open: jest.fn(),
        }),
      ],
    }).compileComponents();

    typedMqttService = TestBed.inject(
      TypedMqttService
    ) as jest.Mocked<TypedMqttService>;

    fixture = TestBed.createComponent(FutureFactoryFlowEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create FutureFactoryFlowEditorComponent', () => {
    expect(component).toBeTruthy();
  });

  it('should render the component', () => {
    expect(fixture).toMatchSnapshot();
  });

  it("should save the flows if there's no running order", async () => {
    component.redSteps = [];
    component.blueSteps = [ModuleType.AIQS, ModuleType.DRILL];
    component.whiteSteps = [ModuleType.MILL];
    await component.saveFlows();
    expect(typedMqttService.publish).toHaveBeenCalledWith(
      CcuTopic.SET_FLOWS,
      {
        BLUE: { steps: ['AIQS', 'DRILL'] },
        RED: { steps: [] },
        WHITE: { steps: ['MILL'] },
      },
      { qos: 2 }
    );
  });

  it("should not save the flows if there's a running order", async () => {
    hasRunningOrdersSubject.next(true);
    fixture.detectChanges();
    component.redSteps = [];
    component.blueSteps = [ModuleType.AIQS, ModuleType.DRILL];
    component.whiteSteps = [ModuleType.MILL];
    await component.saveFlows();
    expect(typedMqttService.publish).not.toHaveBeenCalled();
  });

  describe('enterPredicate', () => {
    it('checks allowed modules for BLUE', () => {
      expect(
        component.enterPredicate(
          { data: ModuleType.AIQS } as CdkDrag,
          { id: Workpiece.BLUE, data: [] } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.enterPredicate(
          { data: ModuleType.MILL } as CdkDrag,
          { id: Workpiece.BLUE, data: [] } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.enterPredicate(
          { data: ModuleType.DRILL } as CdkDrag,
          { id: Workpiece.BLUE, data: [] } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.enterPredicate(
          { data: ModuleType.OVEN } as CdkDrag,
          { id: Workpiece.BLUE, data: [] } as CdkDropList
        )
      ).toBe(true);
    });

    it('denies AIQS for BLUE, if AIQS is already in the list', () => {
      expect(
        component.enterPredicate(
          { data: ModuleType.AIQS } as CdkDrag,
          { id: Workpiece.BLUE, data: [ModuleType.AIQS] } as CdkDropList
        )
      ).toBe(false);
    });

    it('checks allowed modules for RED', () => {
      expect(
        component.enterPredicate(
          { data: ModuleType.AIQS } as CdkDrag,
          { id: Workpiece.RED, data: [] } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.enterPredicate(
          { data: ModuleType.MILL } as CdkDrag,
          { id: Workpiece.RED, data: [] } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.enterPredicate(
          { data: ModuleType.OVEN } as CdkDrag,
          { id: Workpiece.RED, data: [] } as CdkDropList
        )
      ).toBe(true);
    });

    it('denies AIQS for RED, if AIQS is already in the list', () => {
      expect(
        component.enterPredicate(
          { data: ModuleType.AIQS } as CdkDrag,
          { id: Workpiece.RED, data: [ModuleType.AIQS] } as CdkDropList
        )
      ).toBe(false);
    });

    it('checks allowed modules for WHITE', () => {
      expect(
        component.enterPredicate(
          { data: ModuleType.AIQS } as CdkDrag,
          { id: Workpiece.WHITE, data: [] } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.enterPredicate(
          { data: ModuleType.DRILL } as CdkDrag,
          { id: Workpiece.WHITE, data: [] } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.enterPredicate(
          { data: ModuleType.OVEN } as CdkDrag,
          { id: Workpiece.WHITE, data: [] } as CdkDropList
        )
      ).toBe(true);
    });

    it('denies AIQS for WHITE, if AIQS is already in the list', () => {
      expect(
        component.enterPredicate(
          { data: ModuleType.AIQS } as CdkDrag,
          { id: Workpiece.WHITE, data: [ModuleType.AIQS] } as CdkDropList
        )
      ).toBe(false);
    });

    it('should deny to drop an AIQS module at the end, if there is already an AIQS', () => {
      expect(
        component.enterPredicate(
          { data: ModuleType.AIQS } as CdkDrag,
          { id: Workpiece.WHITE, data: [ModuleType.AIQS] } as CdkDropList
        )
      ).toBe(false);

      expect(
        component.enterPredicate(
          { data: ModuleType.AIQS } as CdkDrag,
          {
            id: Workpiece.WHITE,
            data: [ModuleType.MILL, ModuleType.AIQS],
          } as CdkDropList
        )
      ).toBe(false);
    });

    it('should allow milling a white workpiece, when extendedFlows is set to true', () => {
      component.extendedFlows = true;
      expect(
        component.enterPredicate(
          { data: ModuleType.MILL } as CdkDrag,
          { id: Workpiece.WHITE, data: [] } as CdkDropList
        )
      ).toBe(true);
    });
  });

  describe('sortPredicate', () => {
    it("should allow to drop a module at its previous index, when it's not directly before or after the same moduletype", () => {
      expect(
        component.sortPredicate(
          0,
          { data: ModuleType.DRILL } as CdkDrag,
          {
            data: [ModuleType.DRILL, ModuleType.MILL, ModuleType.AIQS],
          } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.sortPredicate(
          1,
          { data: ModuleType.DRILL } as CdkDrag,
          {
            data: [
              ModuleType.DRILL,
              ModuleType.MILL,
              ModuleType.AIQS,
            ],
          } as CdkDropList
        )
      ).toBe(true);
    });

    it('should deny to drop a module directly before or after the same moduletype', () => {
      expect(
        component.sortPredicate(
          1,
          { data: ModuleType.DRILL } as CdkDrag,
          {
            data: [ModuleType.DRILL, ModuleType.AIQS],
          } as CdkDropList
        )
      ).toBe(false);
      expect(
        component.sortPredicate(
          1,
          { data: ModuleType.MILL } as CdkDrag,
          {
            data: [ModuleType.MILL, ModuleType.AIQS],
          } as CdkDropList
        )
      ).toBe(false);
    });

    it("should allow to place a module at the new index, when it's not directly before or after the same moduletype", () => {
      expect(
        component.sortPredicate(
          1,
          { data: ModuleType.DRILL } as CdkDrag,
          {
            data: [ModuleType.DRILL, ModuleType.MILL, ModuleType.AIQS],
          } as CdkDropList
        )
      ).toBe(true);
      expect(
        component.sortPredicate(
          0,
          { data: ModuleType.MILL } as CdkDrag,
          {
            data: [ModuleType.DRILL, ModuleType.MILL, ModuleType.AIQS],
          } as CdkDropList
        )
      ).toBe(true);
    });

    it('should deny to drop a module after an AIQS', () => {
      expect(
        component.sortPredicate(
          2,
          { data: ModuleType.MILL } as CdkDrag,
          {
            data: [ModuleType.DRILL, ModuleType.MILL, ModuleType.AIQS],
          } as CdkDropList
        )
      ).toBe(false);
      expect(
        component.sortPredicate(
          2,
          { data: ModuleType.DRILL } as CdkDrag,
          {
            data: [ModuleType.DRILL, ModuleType.MILL, ModuleType.AIQS],
          } as CdkDropList
        )
      ).toBe(false);
    });

    it('should deny to drop an AIQS module somewhere in the middle', () => {
      expect(
        component.sortPredicate(
          0,
          { data: ModuleType.AIQS } as CdkDrag,
          { data: [ModuleType.DRILL, ModuleType.MILL] } as CdkDropList
        )
      ).toBe(false);
      expect(
        component.sortPredicate(
          1,
          { data: ModuleType.AIQS } as CdkDrag,
          { data: [ModuleType.DRILL, ModuleType.MILL] } as CdkDropList
        )
      ).toBe(false);
    });

    it('should allow to drop an AIQS module at the end', () => {
      expect(
        component.sortPredicate(
          2,
          { data: ModuleType.AIQS } as CdkDrag,
          { data: [ModuleType.DRILL, ModuleType.MILL] } as CdkDropList
        )
      ).toBe(true);
    });
  });

  describe('ensureChainConsistency', () => {
    it('should remove any directly adjacent modules of the same type', () => {
      const steps = [ModuleType.DRILL, ModuleType.DRILL, ModuleType.MILL];
      component.ensureChainConsistency(steps);
      expect(steps).toEqual([ModuleType.DRILL, ModuleType.MILL]);
    });
  });

  describe('deleteStepAtIndex', () => {
    it('should automatically correct the state, when a step is deleted', () => {
      const steps = [ModuleType.DRILL, ModuleType.MILL, ModuleType.DRILL];
      component.deleteStepAtIndex(1, steps);
      expect(steps).toEqual([ModuleType.DRILL]);
    });
  });
});
