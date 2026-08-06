import { Uc05SvgGeneratorService } from './uc-05-svg-generator.service';

describe('Uc05SvgGeneratorService', () => {
  it('renders process, mixed and shopfloor lanes', () => {
    const svg = new Uc05SvgGeneratorService().generateSvg({
      'uc05.title': 'Predictive Maintenance',
      'uc05.subtitle': 'Sense & predict',
      'uc05.lane.process': 'Process',
    });

    expect(svg).toContain('<g id="uc05_root">');
    expect(svg).toContain('<g id="uc05_col_process">');
    expect(svg).toContain('<g id="uc05_container_mixed">');
    expect(svg).toContain('<g id="uc05_col_shopfloor">');
    expect(svg).toContain('Sense &amp; predict');
  });
});
