/**
 * Shared constants for DSP customer pages
 */
import type { ViewMode } from '../../../../components/dsp-animation/types';

/**
 * Available view modes for DSP animation
 */
export const VIEW_MODES: ReadonlyArray<{ value: ViewMode; label: string }> = [
  { value: 'functional', label: 'Functional View' },
  { value: 'component', label: 'Component View' },
  { value: 'deployment', label: 'Deployment View' },
] as const;
