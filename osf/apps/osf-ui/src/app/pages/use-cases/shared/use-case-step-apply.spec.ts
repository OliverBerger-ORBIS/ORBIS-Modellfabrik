import { applyStepToSvg } from './use-case-step-apply';

function buildSvg(): SVGSVGElement {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.innerHTML = `
    <g id="uc00_title"></g>
    <g id="uc00_subtitle"></g>
    <g id="uc00_step_description" style="display:none">
      <text id="uc00_step_description_title"></text>
      <text id="uc00_step_description_text"></text>
    </g>
    <g id="uc00_box_a"><rect/></g>
    <g id="uc00_box_b"><rect/></g>
    <g id="uc00_box_parent"><g id="uc00_box_child"><rect/></g></g>
    <path id="uc00_conn_ab"></path>
    <g id="uc00_other"><rect/></g>
  `;
  return svg;
}

describe('applyStepToSvg', () => {
  it('resets classes and applies hideIds on step 0 while showing title/subtitle', () => {
    const svg = buildSvg();
    svg.querySelector('#uc00_box_a')!.classList.add('hl', 'dim');
    svg.querySelector('#uc00_other')!.classList.add('dim-conn');

    applyStepToSvg({
      svgElement: svg,
      step: { highlightIds: [], hideIds: ['uc00_box_b'] },
      stepIndex: 0,
      stepPrefix: 'uc00',
      connectionIds: ['uc00_conn_ab'],
      showDescription: false,
      getStepTitle: () => 'Title',
      getStepDescription: () => 'Desc',
    });

    expect(svg.querySelector('#uc00_box_a')!.classList.contains('hl')).toBe(false);
    expect(svg.querySelector('#uc00_box_a')!.classList.contains('dim')).toBe(false);
    expect(svg.querySelector('#uc00_box_b')!.classList.contains('hidden')).toBe(true);
    expect((svg.querySelector('#uc00_title') as HTMLElement).style.display).toBe('');
    expect((svg.querySelector('#uc00_subtitle') as HTMLElement).style.display).toBe('');
    expect((svg.querySelector('#uc00_step_description') as HTMLElement).style.display).toBe(
      'none'
    );
  });

  it('highlights, hides, dims others and uses dim-conn for connections on step 1+', () => {
    const svg = buildSvg();

    applyStepToSvg({
      svgElement: svg,
      step: {
        highlightIds: ['uc00_box_child'],
        hideIds: ['uc00_box_b'],
      },
      stepIndex: 1,
      stepPrefix: 'uc00',
      connectionIds: ['uc00_conn_ab'],
      showDescription: false,
      getStepTitle: () => 'Step title',
      getStepDescription: () => 'Step desc',
    });

    expect(svg.querySelector('#uc00_box_child')!.classList.contains('hl')).toBe(true);
    expect(svg.querySelector('#uc00_box_b')!.classList.contains('hidden')).toBe(true);
    expect(svg.querySelector('#uc00_box_parent')!.classList.contains('dim')).toBe(false);
    expect(svg.querySelector('#uc00_other')!.classList.contains('dim')).toBe(true);
    expect(svg.querySelector('#uc00_conn_ab')!.classList.contains('dim-conn')).toBe(true);
    expect(svg.querySelector('#uc00_title')!.classList.contains('dim')).toBe(false);
  });

  it('fills step description when showDescription is true on step 1+', () => {
    const svg = buildSvg();

    applyStepToSvg({
      svgElement: svg,
      step: { highlightIds: ['uc00_box_a'], hideIds: [] },
      stepIndex: 2,
      stepPrefix: 'uc00',
      connectionIds: [],
      showDescription: true,
      getStepTitle: () => 'Focus title',
      getStepDescription: () => 'Focus description',
    });

    expect((svg.querySelector('#uc00_title') as HTMLElement).style.display).toBe('none');
    expect((svg.querySelector('#uc00_subtitle') as HTMLElement).style.display).toBe('none');
    expect((svg.querySelector('#uc00_step_description') as HTMLElement).style.display).toBe('');
    expect(svg.querySelector('#uc00_step_description_title')!.textContent).toBe('Focus title');
    expect(svg.querySelector('#uc00_step_description_text')!.textContent).toBe(
      'Focus description'
    );
  });
});
