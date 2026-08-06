import { Uc04SvgGeneratorService } from './uc-04-svg-generator.service';

describe('Uc04SvgGeneratorService', () => {
  it('renders process, mixed and shopfloor lanes with feedback', () => {
    const svg = new Uc04SvgGeneratorService().generateSvg({
      'uc04.title': 'Closed-Loop Quality',
      'uc04.subtitle': 'Detect & act',
    });

    expect(svg).toContain('<g id="uc04_root">');
    expect(svg).toContain('<g id="uc04_col_process">');
    expect(svg).toContain('<g id="uc04_container_mixed">');
    expect(svg).toContain('<g id="uc04_col_shopfloor">');
    expect(svg).toContain('<g id="uc04_feedback">');
    expect(svg).toContain('Detect &amp; act');
  });
});
