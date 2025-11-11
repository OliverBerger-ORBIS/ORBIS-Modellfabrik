import { TestBed } from '@angular/core/testing';
import { AppComponent } from './app.component';

describe('AppComponent', () => {
  const mockFixtureResponse =
    '{"topic":"ccu/order/active","payload":"[]","timestamp":"2025-01-01T00:00:00Z"}\n';

  let originalFetch: typeof fetch | undefined;

  beforeAll(() => {
    originalFetch = global.fetch;
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        statusText: 'OK',
        text: () => Promise.resolve(mockFixtureResponse),
      } as Response)
    );
  });

  afterAll(() => {
    (global.fetch as unknown as jest.Mock).mockReset();
    if (originalFetch) {
      global.fetch = originalFetch;
    }
  });

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
    }).compileComponents();
  });

  it('should render dashboard header', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain(
      'CCU Mock Dashboard'
    );
    expect(
      compiled.querySelector('.badge')?.textContent?.toLowerCase()
    ).toContain('mock data');
  });
});
