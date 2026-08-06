import { Uc07SvgGeneratorService } from './uc-07-svg-generator.service';

describe('Uc07SvgGeneratorService', () => {
  it('renders process, mixed and shopfloor lanes', () => {
    const svg = new Uc07SvgGeneratorService().generateSvg({
      'uc07.title': 'Anomaly Detection',
      'uc07.subtitle': 'Detect & escalate',
    });

    expect(svg).toContain('<g id="uc07_root">');
    expect(svg).toContain('<g id="uc07_col_process">');
    expect(svg).toContain('<g id="uc07_container_mixed">');
    expect(svg).toContain('<g id="uc07_col_shopfloor">');
    expect(svg).toContain('Detect &amp; escalate');
  });
});
