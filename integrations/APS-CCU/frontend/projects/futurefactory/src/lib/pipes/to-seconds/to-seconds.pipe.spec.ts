import { ToSecondsPipe } from './to-seconds.pipe';

describe('ToSecondsPipe', () => {
  let pipe: ToSecondsPipe;

  beforeEach(() => {
    pipe = new ToSecondsPipe();
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
    expect(pipe.transform(0)).toEqual('0s');
  });

  it('should return value / 1000 if value is a number', () => {
    expect(pipe.transform(1000)).toEqual('1s');
  });
});
