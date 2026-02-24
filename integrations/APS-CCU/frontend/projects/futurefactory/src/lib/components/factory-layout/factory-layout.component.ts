import {
  AfterViewInit,
  Component,
  ElementRef,
  Input,
  NgZone,
  OnDestroy,
  OnInit, TemplateRef,
  ViewChild,
} from '@angular/core';
import { MatDrawer } from '@angular/material/sidenav';
import { ActivatedRoute, Router } from '@angular/router';
import { GridsterComponent, GridsterConfig, GridsterItem, } from 'angular-gridster2';
import {
  BehaviorSubject,
  Observable,
  ReplaySubject,
  combineLatest,
  combineLatestWith,
  filter,
  firstValueFrom,
  map,
  shareReplay,
  startWith,
  takeUntil,
} from 'rxjs';
import { CcuTopic } from '../../../common/protocol';
import { AvailableState, PairedModule, RoadDirection } from '../../../common/protocol/ccu';
import { ModuleType } from '../../../common/protocol/module';
import { FutureFactoryRoutes } from '../../futurefactory.routes';
import { TypedMqttService } from '../../futurefactory.service';
import {
  GridItem,
  LayoutEditorService,
} from '../../services/layout-editor.service';
import { OrderStatesService } from '../../services/order-states.service';
import { getRouteToModuleRoot } from '../../utils/routes.utils';
import { StatesService } from '../../services/states.service';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'ff-factory-layout',
  templateUrl: './factory-layout.component.html',
  styleUrls: ['./factory-layout.component.scss'],
})
export class FactoryLayoutComponent
  implements OnInit, AfterViewInit, OnDestroy
{
  private readonly destroy$ = new ReplaySubject<void>(1);
  private readonly resizeObserver;
  private readonly width$ = new BehaviorSubject<number>(0);
  private readonly zoomScale$ = new BehaviorSubject<number>(1);
  private readonly _editable$ = new BehaviorSubject<boolean>(false);
  private readonly offlineModules = new Map<string, boolean>();

  @ViewChild('drawer')
  private drawer!: MatDrawer;

  @ViewChild('gridZoomContainer', { static: true })
  private gridZoomContainer!: ElementRef;

  @ViewChild('gridster')
  gridster!: GridsterComponent;

  @ViewChild("defaultLayoutDialogContent")
  readonly defaultLayoutDialogContent!: TemplateRef<any>;

  readonly gridContents$: Observable<GridItem[]>;
  readonly widthScaleStyle$: Observable<Object>;
  readonly isValidLayout$: Observable<boolean>;
  readonly routeToRoot$: Observable<string>;
  readonly hasRunningOrders$: Observable<boolean>;
  readonly FutureFactoryRoutes = FutureFactoryRoutes;
  readonly ModuleType = ModuleType;

  @Input()
  set editable(editable: boolean) {
    this._editable$.next(editable);
  }

  get editable() {
    return this._editable$.value;
  }

  @Input()
  highlightedId?: string | null;

  @Input()
  startZoom?: number;

  constructor(
    private mqtt: TypedMqttService,
    private orderStatesService: OrderStatesService,
    private factoryStateService: StatesService,
    public layoutEditor: LayoutEditorService,
    private dialog: MatDialog,
    private zone: NgZone,
    private router: Router,
    private activatedRoute: ActivatedRoute
  ) {
    this.routeToRoot$ = getRouteToModuleRoot(activatedRoute);
    this.isValidLayout$ = layoutEditor.editorGrid$.pipe(
      map((grid) =>
        layoutEditor.validateGridLayout(
          layoutEditor.convertGridToGridLayout(grid)
        )
      )
    );
    this.hasRunningOrders$ = this.orderStatesService.hasRunningOrders$;

    if (window.ResizeObserver) {
      this.resizeObserver = new ResizeObserver((entries) => {
        this.zone.run(() => {
          this.width$.next(entries[0].contentRect.width);
        });
      });
    }

    this.widthScaleStyle$ = this.getWidthScaleStyle$();

    this.gridContents$ = layoutEditor.editorGrid$.pipe(
      // combineLatestWith this is the replacement for the deprecated combineLatest operator
      combineLatestWith(this._editable$),
      map(([grid, editable]) =>
        grid.map((tile) => (editable ? tile : { ...tile, dragEnabled: false }))
      )
    );
    this.setupOfflineModules(this.factoryStateService.pairedModules$);
  }

  public isLargeModule(moduleType: ModuleType): boolean {
    return this.layoutEditor.isLargeModule(moduleType);
  }

  public isOffline(moduleId: string): boolean {
    return this.offlineModules.get(moduleId) ?? false;
  }

  private getWidthScaleStyle$() {
    return combineLatest([
      this.zoomScale$,
      this.width$,
      this.layoutEditor.editorGrid$,
    ]).pipe(
      map(([zoomScale, width, editorGrid]) => {
        const gridWidth =
          (2 + Math.max(...editorGrid.map((item) => item.x))) *
            (this.options.margin! + this.options.fixedColWidth!) +
          this.options.margin!;
        const gridHeight =
          (2 + Math.max(...editorGrid.map((item) => item.y))) *
            (this.options.margin! + this.options.fixedRowHeight!) +
          this.options.margin!;
        const baseScale = Math.min(1, width / gridWidth);
        const startZoom = this.startZoom || 1;
        const scale = baseScale * zoomScale * startZoom;

        if (this.gridster) {
          this.gridster.options.scale = scale;
          this.gridster.optionsChanged();
        }

        return {
          transform: 'scale(' + scale + ')',
          height: scale * gridHeight + 'px',
        };
      }),
      startWith({}),
      shareReplay(1)
    );
  }

  private dragStopped = (item: GridsterItem): void => {
    // use setTimeout to reorder the execution after the drag stop event has completed
    // and the new coordinates are available.
    setTimeout(() => {
      const changed = item as GridItem;
      this.layoutEditor.updateMovedGridItem(changed);
    });
  };

  readonly options: GridsterConfig = {
    scale: 1, // external zoom should set that.
    //gridType: 'scrollVertical',
    gridType: 'fixed',
    fixedColWidth: 200,
    fixedRowHeight: 200,
    setGridSize: true,
    minRows: 3,
    margin: 10,
    minCols: 3,
    swap: false,
    mobileBreakpoint: 0,
    swapWhileDragging: false,
    pushItems: false,
    disablePushOnDrag: true,
    disablePushOnResize: true,
    draggable: {
      dropOverItems: true,
      enabled: true,
      stop: this.dragStopped,
    },
  };

  ngOnInit(): void {
    this.layoutEditor.resetLayout();
    if (this.resizeObserver) {
      this.resizeObserver.observe(this.gridZoomContainer.nativeElement);
    }
  }

  ngAfterViewInit() {
    this.orderStatesService.hasRunningOrders$
      .pipe(
        filter((hasRunningOrders) => hasRunningOrders),
        takeUntil(this.destroy$)
      )
      .subscribe(() => this.drawer.close());
  }

  ngOnDestroy() {
    if (this.resizeObserver) {
      this.resizeObserver.unobserve(this.gridZoomContainer.nativeElement);
    }
    this.zoomScale$.complete();
    this.width$.complete();
    this._editable$.complete();
    this.destroy$.next();
    this.destroy$.complete();
  }

  add_intersection() {
    const item: GridItem = {
      cols: 1,
      rows: 1,
      x: 0,
      y: 0,
      tile: {
        type: 'ROAD',
        x: 0,
        y: 0,
        road: {},
        id: this.layoutEditor.getNextId(),
      },
    };
    item.x = this.gridster.getFirstPossiblePosition(item).x;
    item.y = this.gridster.getFirstPossiblePosition(item).y;
    item.tile.x = item.x;
    item.tile.y = item.y;
    this.layoutEditor.addItem(item);
  }


  add_charger() {
    let index = 0;
    let prefix = 'CHRG';
    while (this.layoutEditor.hasGridItemId(prefix+index)) {
      index++;
    }
    this.add_production({
      type: 'MODULE',
      subType: ModuleType.CHRG,
      serialNumber: prefix+index,
      available: AvailableState.READY,
      connected: true,
    })
  }

  add_production(mod: PairedModule) {
    const item: GridItem = {
      cols: 1,
      rows:
        mod.subType! === ModuleType.HBW || mod.subType! === ModuleType.DPS
          ? 2
          : 1,
      x: 0,
      y: 0,
      tile: {
        type: 'MODULE',
        x: 0,
        y: 0,
        id: mod.serialNumber,
        connected: true,
        moduleType: mod.subType!,
        direction:
          mod.subType! === ModuleType.HBW
            ? RoadDirection.WEST
            : RoadDirection.EAST,
      },
    };
    item.x = this.gridster.getFirstPossiblePosition(item).x;
    item.y = this.gridster.getFirstPossiblePosition(item).y;
    item.tile.x = item.x;
    item.tile.y = item.y;
    this.layoutEditor.addItem(item);
  }

  delete_item(item: GridItem) {
    this.layoutEditor.deleteGridItem(item);
  }

  rotate_module(item: GridItem) {
    this.layoutEditor.rotateModuleConnection(item);
  }

  async saveLayout(): Promise<void> {
    const hasRunningOrders = await firstValueFrom(this.hasRunningOrders$);
    if (hasRunningOrders) {
      return;
    }
    const grid = await this.layoutEditor.getNewGridLayout();
    if (!this.layoutEditor.validateGridLayout(grid)) {
      alert('WRONG LAYOUT');
    } else {
      const layout = this.layoutEditor.convertGridLayoutToLayout(grid);
      this.layoutEditor.setLayoutSaved();
      return this.mqtt.publish(CcuTopic.SET_LAYOUT, layout);
    }
  }

  resetLayout() {
    this.layoutEditor.resetLayout();
  }

  zoomIn() {
    if (this.zoomScale$.value < 4) {
      this.zoomScale$.next(this.zoomScale$.value + 0.2);
    }
  }

  zoomOut() {
    if (this.zoomScale$.value > 0.3) {
      this.zoomScale$.next(this.zoomScale$.value - 0.2);
    }
  }

  async item_clicked(item: GridItem) {
    if (!this.editable && item.tile.type === 'MODULE' && item.tile.moduleType !== ModuleType.CHRG) {
      const root = await firstValueFrom(this.routeToRoot$);
      await this.router.navigate(
        [root, FutureFactoryRoutes.MODULE, item.tile.id],
        { relativeTo: this.activatedRoute }
      );
    }
  }

  private setupOfflineModules(pairedModules$: Observable<PairedModule[]>) {
    pairedModules$
      .pipe(
        startWith([]),
        map((modules): [string, boolean][] => modules.map(module => [module.serialNumber, module.connected ?? false])),
        takeUntil(this.destroy$)
      )
      .subscribe((modules) => {
        for (let [id, online] of modules) {
          this.offlineModules.set(id, !online);
        }
      });
  }

  resetDefaultLayout() {
    this.dialog.open(this.defaultLayoutDialogContent);
  }

  sendDefaultLayoutReset() {
    this.mqtt.publish(CcuTopic.SET_DEFAULT_LAYOUT, { timestamp: new Date() })
  }
}
