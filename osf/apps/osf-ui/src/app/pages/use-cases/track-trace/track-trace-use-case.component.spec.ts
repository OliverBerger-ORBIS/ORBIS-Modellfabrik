import { ChangeDetectionStrategy, Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter, Router } from '@angular/router';
import { By } from '@angular/platform-browser';
import { BehaviorSubject } from 'rxjs';
import { TrackTraceUseCaseComponent } from './track-trace-use-case.component';
import { TrackTraceGenealogyUseCaseComponent } from '../track-trace-genealogy/track-trace-genealogy-use-case.component';
import { TrackTraceTabComponent } from '../../../tabs/track-trace-tab.component';

@Component({
  selector: 'app-track-trace-genealogy-use-case',
  standalone: true,
  template: '<div class="mock-genealogy"></div>',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
class MockGenealogyComponent {}

@Component({
  selector: 'app-track-trace-tab',
  standalone: true,
  template: '<div class="mock-live"></div>',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
class MockTrackTraceTabComponent {}

describe('TrackTraceUseCaseComponent', () => {
  let fixture: ComponentFixture<TrackTraceUseCaseComponent>;
  let component: TrackTraceUseCaseComponent;
  let queryParams$: BehaviorSubject<ReturnType<typeof convertToParamMap>>;
  let router: Router;

  beforeEach(async () => {
    queryParams$ = new BehaviorSubject(convertToParamMap({}));
    await TestBed.configureTestingModule({
      imports: [TrackTraceUseCaseComponent],
      providers: [
        provideRouter([]),
        {
          provide: ActivatedRoute,
          useValue: {
            queryParamMap: queryParams$.asObservable(),
            snapshot: { queryParamMap: convertToParamMap({}) },
          },
        },
      ],
    })
      .overrideComponent(TrackTraceUseCaseComponent, {
        remove: { imports: [TrackTraceGenealogyUseCaseComponent, TrackTraceTabComponent] },
        add: { imports: [MockGenealogyComponent, MockTrackTraceTabComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(TrackTraceUseCaseComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    jest.spyOn(router, 'navigate').mockResolvedValue(true);
    fixture.detectChanges();
  });

  it('should create with concept tab by default', () => {
    expect(component).toBeTruthy();
    expect(component.activeTab).toBe('concept');
    expect(fixture.debugElement.query(By.css('.mock-genealogy'))).toBeTruthy();
  });

  it('should switch to live-demo when tab=live query param is set', () => {
    queryParams$.next(convertToParamMap({ tab: 'live' }));
    fixture.detectChanges();
    expect(component.activeTab).toBe('live-demo');
  });

  it('should navigate with tab query when setTab is called', async () => {
    component.setTab('live-demo');
    expect(component.activeTab).toBe('live-demo');
    expect(router.navigate).toHaveBeenCalledWith(
      [],
      expect.objectContaining({
        queryParams: { tab: 'live' },
        replaceUrl: true,
      })
    );
  });
});
