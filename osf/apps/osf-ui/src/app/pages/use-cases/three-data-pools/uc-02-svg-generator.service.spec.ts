import { Uc02SvgGeneratorService } from './uc-02-svg-generator.service';

describe('Uc02SvgGeneratorService', () => {
  it('renders sources, DSP container and targets lanes', () => {
    const svg = new Uc02SvgGeneratorService().generateSvg({
      'uc02.title': 'Three Data Pools',
      'uc02.subtitle': 'Sources & targets',
    });

    expect(svg).toContain('<g id="uc02_root">');
    expect(svg).toContain('<g id="uc02_col_sources">');
    expect(svg).toContain('<g id="uc02_container_dsp">');
    expect(svg).toContain('<g id="uc02_col_targets">');
    expect(svg).toContain('<g id="uc02_connections">');
    expect(svg).toContain('Sources &amp; targets');
  });
});
