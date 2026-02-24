import { ToLabelPipe } from './to-label.pipe';

describe('ToLabelPipe', () => {
  let pipe: ToLabelPipe;

  beforeEach(() => {
    pipe = new ToLabelPipe();
  });

  it('create an instance', () => {
    expect(pipe).toBeTruthy();
  });

  it('should return the value if no label set is provided', () => {
    expect(pipe.transform('foo')).toEqual('foo');
  });

  it('should return the value if the value is not in the label set', () => {
    expect(pipe.transform('foo', { bar: 'baz' })).toEqual('foo');
  });

  it('should return the icon if the value is in the label set', () => {
    expect(pipe.transform('foo', { foo: 'bar' })).toEqual('bar');
  });
});
