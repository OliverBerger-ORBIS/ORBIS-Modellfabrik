import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app.component';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideRouter([])],
    }).compileComponents();
  });

  it('should render dashboard header', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain(
      'SmartFactory'
    );
    expect(
      Array.from(compiled.querySelectorAll('nav a')).map((el) => el.textContent?.trim())
    ).toEqual(['Overview', 'Order', 'Process', 'Sensor Data', 'Module', 'Configuration', 'Settings']);
  });
});
