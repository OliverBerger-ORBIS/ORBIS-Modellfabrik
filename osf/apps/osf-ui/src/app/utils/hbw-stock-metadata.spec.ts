import { extractHbwStockColumn, extractHbwStockRow } from './hbw-stock-metadata';

describe('hbw-stock-metadata', () => {
  it('extractHbwStockRow prefers metadata.row', () => {
    expect(
      extractHbwStockRow({
        actionState: { metadata: { row: 2, slot: 'B3' } },
        loads: [{ loadId: 'wp-1', loadPosition: 'A5' }],
      })
    ).toBe(2);
  });

  it('extractHbwStockRow falls back to loads loadPosition and slot prefix', () => {
    expect(
      extractHbwStockRow({
        actionState: { metadata: { workpieceId: 'wp-9' } },
        loads: [{ loadId: 'wp-9', loadPosition: 'C4' }],
      })
    ).toBe('C');
    expect(extractHbwStockRow({ actionState: { metadata: { slot: 'A2' } } })).toBe('A');
  });

  it('extractHbwStockColumn prefers metadata.column and parses slot suffix', () => {
    expect(
      extractHbwStockColumn({
        actionState: { metadata: { column: 3, slot: 'B3' } },
      })
    ).toBe(3);
    expect(
      extractHbwStockColumn({
        actionState: { metadata: { workpieceId: 'wp-9' } },
        loads: [{ loadId: 'wp-9', loadPosition: 'C4' }],
      })
    ).toBe('4');
  });
});
