import {
  DSP_ARCHITECTURE_LABEL_CHAR_WIDTH_FACTOR,
  escapeXmlForSvgText,
  maxCharsPerLineFromInnerWidth,
  wrapWordsToLinesSimple,
} from './svg-text-utils';

describe('svg-text-utils', () => {
  describe('escapeXmlForSvgText', () => {
    it('escapes XML special characters', () => {
      expect(escapeXmlForSvgText(`a & b < c > "d"'e`)).toBe(
        'a &amp; b &lt; c &gt; &quot;d&quot;&apos;e',
      );
    });

    it('returns empty string for empty input', () => {
      expect(escapeXmlForSvgText('')).toBe('');
    });
  });

  describe('maxCharsPerLineFromInnerWidth', () => {
    it('matches DSP-Architecture style (width 100, fs 10, factor 0.6)', () => {
      const inner = 100 - 16; // device box padding convention
      const fs = 10;
      const n = maxCharsPerLineFromInnerWidth(inner, fs, DSP_ARCHITECTURE_LABEL_CHAR_WIDTH_FACTOR);
      expect(n).toBe(Math.floor(84 / 6));
    });
  });

  describe('wrapWordsToLinesSimple', () => {
    it('returns single line when short enough', () => {
      expect(wrapWordsToLinesSimple('Drill', 20, 2)).toEqual(['Drill']);
    });

    it('wraps at spaces and limits lines', () => {
      expect(wrapWordsToLinesSimple('one two three four', 4, 2)).toEqual(['one', 'two']);
    });

    it('returns empty array for whitespace-only', () => {
      expect(wrapWordsToLinesSimple('   ', 10, 2)).toEqual([]);
    });
  });
});
