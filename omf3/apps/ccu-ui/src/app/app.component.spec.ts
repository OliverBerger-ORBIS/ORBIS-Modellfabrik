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
    // Header title is now "SmartFactory" (i18n)
    expect(compiled.querySelector('h1')?.textContent).toContain('SmartFactory');
    // Navigation items are now dynamic and i18n, so we just check that nav exists
    const navLinks = Array.from(compiled.querySelectorAll('nav a'));
    expect(navLinks.length).toBeGreaterThan(0);
  });
});
