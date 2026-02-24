import { ToNumberFormatPipe } from './to-number-format.pipe';

describe('ToNumberFormatPipe', () => {
  let pipe: ToNumberFormatPipe;

  beforeEach(() => {
    pipe = new ToNumberFormatPipe();
  });

  it('create an instance', () => {
    expect(pipe).toBeTruthy();
  });

  it('should return value if value is not a number', () => {
    expect(pipe.transform('test')).toEqual('test');
  });

  it('should return value if value is NaN', () => {
    expect(pipe.transform(NaN)).toEqual(NaN);
  });

  it('should return value if value is undefined', () => {
    expect(pipe.transform(undefined)).toEqual(undefined);
  });

  it('should return value if value is null', () => {
    expect(pipe.transform(null)).toEqual(null);
  });

  it('should return value if value is empty string', () => {
    expect(pipe.transform('')).toEqual('');
  });

  it('should return 0 if value is 0', () => {
    expect(pipe.transform(0)).toEqual('0');
  });

  it('should return 1,000 if value is 1000', () => {
    expect(pipe.transform(1000)).toEqual('1,000');
  });
});
