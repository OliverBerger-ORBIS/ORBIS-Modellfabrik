import { Uc02SvgGeneratorLanesService } from './uc-02-svg-generator-lanes.service';

describe('Uc02SvgGeneratorLanesService', () => {
  it('renders analytics, DSP and data lanes', () => {
    const svg = new Uc02SvgGeneratorLanesService().generateSvg({
      'uc02.title': 'Three Data Pools',
      'uc02.subtitle': 'Architecture lanes',
      'uc02.lane.analytics': 'Analytics',
    });

    expect(svg).toContain('<g id="uc02_root">');
    expect(svg).toContain('<g id="uc02_col_targets">');
    expect(svg).toContain('id="uc02_lanes_layer_analytics"');
    expect(svg).toContain('<g id="uc02_title">');
  });
});
