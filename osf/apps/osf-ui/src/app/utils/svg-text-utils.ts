/**
 * Shared helpers for programmatic SVG `<text>` / `<tspan>` content.
 * Context-specific behaviour (DSP-Animation ` / ` hints, UC-01 compounds) stays in those modules.
 * @see docs/04-howto/osf-ui-svg-label-text-conventions.md
 */

/** DSP-Architecture device labels — `getWrappedLabelLines` in `dsp-architecture.component.ts`. */
export const DSP_ARCHITECTURE_LABEL_CHAR_WIDTH_FACTOR = 0.6;

/** DSP-Animation shopfloor box labels — `getWrappedLabelLines` in `dsp-animation.component.ts`. */
export const DSP_ANIMATION_LABEL_CHAR_WIDTH_FACTOR = 0.58;

export function escapeXmlForSvgText(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * @param innerWidthPx — usable width inside the box (already subtract padding).
 */
export function maxCharsPerLineFromInnerWidth(
  innerWidthPx: number,
  fontSize: number,
  charWidthFactor: number,
): number {
  const safeInner = Math.max(0, innerWidthPx);
  const fs = Math.max(1, fontSize);
  const factor = charWidthFactor > 0 ? charWidthFactor : DSP_ARCHITECTURE_LABEL_CHAR_WIDTH_FACTOR;
  return Math.max(1, Math.floor(safeInner / (fs * factor)));
}

/**
 * Word-wrap at ASCII whitespace only. Long single tokens stay on one line (may overflow visually).
 * Truncates to `maxLines` (same semantics as legacy DSP-Architecture wrapping).
 */
export function wrapWordsToLinesSimple(text: string, maxCharsPerLine: number, maxLines: number): string[] {
  const maxChars = Math.max(1, maxCharsPerLine);
  const limit = Math.max(1, maxLines);

  const trimmed = text.trim();
  if (!trimmed) {
    return [];
  }
  if (trimmed.length <= maxChars) {
    return [trimmed];
  }

  const words = trimmed.split(/\s+/);
  const lines: string[] = [];
  let currentLine = '';

  for (const word of words) {
    const testLine = currentLine ? `${currentLine} ${word}` : word;
    if (testLine.length > maxChars && currentLine) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = testLine;
    }
  }

  if (currentLine) {
    lines.push(currentLine);
  }

  return lines.slice(0, limit);
}
