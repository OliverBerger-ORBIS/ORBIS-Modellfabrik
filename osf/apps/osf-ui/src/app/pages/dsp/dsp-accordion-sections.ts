/**
 * Accordion section ids on {@link DspPageComponent} (must match template toggleSection keys).
 */
export const DSP_ACCORDION_SECTION_IDS = [
  'overview',
  'architecture-functional',
  'components',
  'deployment',
  'use-cases',
  'methodology',
] as const;

export type DspAccordionSectionId = (typeof DSP_ACCORDION_SECTION_IDS)[number];

/** sessionStorage: return target when opening a use-case from the embedded DSP accordion. */
export const DSP_RETURN_SECTION_SESSION_KEY = 'osf.dsp.return-accordion-section';

export function isDspAccordionSectionId(value: string | null | undefined): value is DspAccordionSectionId {
  return !!value && (DSP_ACCORDION_SECTION_IDS as readonly string[]).includes(value);
}
