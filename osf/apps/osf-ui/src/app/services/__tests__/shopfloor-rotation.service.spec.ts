import { TestBed } from '@angular/core/testing';
import { ShopfloorRotationService } from '../shopfloor-rotation.service';

const STORAGE_KEY = 'OSF.shopfloorRotation';

describe('ShopfloorRotationService', () => {
  beforeEach(() => {
    localStorage.removeItem(STORAGE_KEY);
    TestBed.configureTestingModule({
      providers: [ShopfloorRotationService],
    });
  });

  afterEach(() => {
    localStorage.removeItem(STORAGE_KEY);
  });

  it('defaults to none when storage is empty', () => {
    const service = TestBed.inject(ShopfloorRotationService);
    expect(service.current).toBe('none');
  });

  it('persists rotation and skips no-op updates', () => {
    const service = TestBed.inject(ShopfloorRotationService);
    const seen: string[] = [];
    const sub = service.rotation$.subscribe((value) => seen.push(value));

    service.setRotation('cw90');
    expect(service.current).toBe('cw90');
    expect(localStorage.getItem(STORAGE_KEY)).toBe('cw90');

    service.setRotation('cw90');
    expect(seen.filter((value) => value === 'cw90')).toHaveLength(1);
    sub.unsubscribe();
  });

  it('loads a stored rotation on construct', () => {
    localStorage.setItem(STORAGE_KEY, 'rot180');
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [ShopfloorRotationService],
    });
    expect(TestBed.inject(ShopfloorRotationService).current).toBe('rot180');
  });

  it('falls back to none for invalid stored values', () => {
    localStorage.setItem(STORAGE_KEY, 'upside-down');
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [ShopfloorRotationService],
    });
    expect(TestBed.inject(ShopfloorRotationService).current).toBe('none');
  });
});
