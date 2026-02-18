/**
 * Shared Auto-Dim logic for Use-Case diagram step animation.
 *
 * All Use-Cases use the same approach:
 * - highlightIds → .hl
 * - hideIds → .hidden
 * - Everything else (except ancestors of highlighted) → .dim or .dim-conn
 *
 * Connection IDs receive .dim-conn (lighter opacity) for visual distinction.
 */

export interface UseCaseStepForApply {
  highlightIds: string[];
  hideIds: string[];
}

export interface ApplyStepOptions {
  svgElement: Element;
  step: UseCaseStepForApply;
  stepIndex: number;
  stepPrefix: string;
  connectionIds: readonly string[];
  showDescription: boolean;
  getStepTitle: () => string;
  getStepDescription: () => string;
}

/**
 * Apply step highlighting to SVG using Auto-Dim:
 * - Step 0: Reset all, apply hideIds, show title/subtitle, hide step description
 * - Step 1+: Apply highlightIds, hideIds, auto-dim the rest (with dim-conn for connections)
 */
export function applyStepToSvg(options: ApplyStepOptions): void {
  const {
    svgElement,
    step,
    stepIndex,
    stepPrefix,
    connectionIds,
    showDescription,
    getStepTitle,
    getStepDescription,
  } = options;

  const idPrefix = `${stepPrefix}_`;
  const selector = `[id^="${idPrefix}"]`;

  const titleEl = svgElement.querySelector(`#${stepPrefix}_title`);
  const subtitle = svgElement.querySelector(`#${stepPrefix}_subtitle`);
  const stepDesc = svgElement.querySelector(`#${stepPrefix}_step_description`);

  if (stepIndex === 0) {
    svgElement.querySelectorAll(selector).forEach((el) => {
      el.classList.remove('hl', 'dim', 'dim-conn', 'hidden');
    });
    step.hideIds.forEach((id) => {
      const el = svgElement.querySelector(`#${id}`);
      if (el) el.classList.add('hidden');
    });
    if (titleEl) (titleEl as HTMLElement).style.display = '';
    if (subtitle) (subtitle as HTMLElement).style.display = '';
    if (stepDesc) (stepDesc as HTMLElement).style.display = 'none';
  } else {
    if (showDescription) {
      if (titleEl) (titleEl as HTMLElement).style.display = 'none';
      if (subtitle) (subtitle as HTMLElement).style.display = 'none';
      if (stepDesc) {
        (stepDesc as HTMLElement).style.display = '';
        const descTitle = svgElement.querySelector(`#${stepPrefix}_step_description_title`);
        const descText = svgElement.querySelector(`#${stepPrefix}_step_description_text`);
        if (descTitle && descText) {
          descTitle.textContent = getStepTitle();
          descText.textContent = getStepDescription();
        }
      }
    } else {
      if (titleEl) (titleEl as HTMLElement).style.display = '';
      if (subtitle) (subtitle as HTMLElement).style.display = 'none';
      if (stepDesc) (stepDesc as HTMLElement).style.display = 'none';
    }

    svgElement.querySelectorAll(selector).forEach((el) => {
      el.classList.remove('hl', 'dim', 'dim-conn', 'hidden');
    });

    step.highlightIds.forEach((id) => {
      const el = svgElement.querySelector(`#${id}`);
      if (el) el.classList.add('hl');
    });

    step.hideIds.forEach((id) => {
      const el = svgElement.querySelector(`#${id}`);
      if (el) el.classList.add('hidden');
    });

    const isAncestorOfHighlighted = (el: Element): boolean =>
      step.highlightIds.some((hid) => {
        const h = svgElement.querySelector(`#${hid}`);
        return h != null && el.contains(h);
      });

    /** Title, subtitle and step description must never be dimmed. */
    const neverDimIds = new Set([
      `${stepPrefix}_title`,
      `${stepPrefix}_subtitle`,
      `${stepPrefix}_step_description`,
      `${stepPrefix}_step_description_title`,
      `${stepPrefix}_step_description_text`,
    ]);

    svgElement.querySelectorAll(selector).forEach((el) => {
      const id = el.id;
      if (!id || step.highlightIds.includes(id) || step.hideIds.includes(id)) return;
      if (neverDimIds.has(id)) return;
      if (isAncestorOfHighlighted(el)) return;
      el.classList.add(connectionIds.includes(id) ? 'dim-conn' : 'dim');
    });
  }
}
