import { ToIconPipe } from './to-icon.pipe';

describe('ToIconPipe', () => {
  let pipe: ToIconPipe;

  beforeEach(() => {
    pipe = new ToIconPipe();
  });

  it('create an instance', () => {
    expect(pipe).toBeTruthy();
  });

  it('should return the value if no icon set is provided', () => {
    expect(pipe.transform('foo')).toEqual('foo');
  });

  it('should return the value if the value is not in the icon set', () => {
    expect(pipe.transform('foo', { bar: 'baz' })).toEqual('foo');
  });

  it('should return the icon if the value is in the icon set', () => {
    expect(pipe.transform('foo', { foo: 'bar' })).toEqual('bar');
  });
});
