import { Uc03SvgGeneratorService } from './uc-03-svg-generator.service';

describe('Uc03SvgGeneratorService', () => {
  it('renders process, DSP and shopfloor columns', () => {
    const svg = new Uc03SvgGeneratorService().generateSvg({
      'uc03.title': 'AI Lifecycle',
      'uc03.subtitle': 'Train & deploy',
    });

    expect(svg).toContain('<g id="uc03_root">');
    expect(svg).toContain('<g id="uc03_col_process">');
    expect(svg).toContain('<g id="uc03_container_dsp">');
    expect(svg).toContain('<g id="uc03_col_shopfloor">');
    expect(svg).toContain('Train &amp; deploy');
  });
});
