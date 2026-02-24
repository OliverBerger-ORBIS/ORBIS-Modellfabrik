import { FallbackValuePipe } from './fallback-value.pipe';

describe('FallbackValuePipe', () => {
  let pipe: FallbackValuePipe;

  beforeEach(() => {
    pipe = new FallbackValuePipe();
  });

  it('create an instance', () => {
    expect(pipe).toBeTruthy();
  });

  it('should return fallback value if value is null', () => {
    expect(pipe.transform(null, 'fallback')).toEqual('fallback');
  });

  it('should return fallback value if value is undefined', () => {
    expect(pipe.transform(undefined, 'fallback')).toEqual('fallback');
  });

  it("should return undefined if value and fallback are null or undefined", () => {
    expect(pipe.transform(null, null)).toEqual(undefined);
    expect(pipe.transform(undefined, undefined)).toEqual(undefined);
  });

  it('should return value if value is not null or undefined', () => {
    expect(pipe.transform('value')).toEqual('value');
    expect(pipe.transform(1)).toEqual(1);
    expect(pipe.transform(0)).toEqual(0);
    expect(pipe.transform(false)).toEqual(false);
    expect(pipe.transform(true)).toEqual(true);
    expect(pipe.transform('')).toEqual('');
    expect(pipe.transform([])).toEqual([]);
  });
});
