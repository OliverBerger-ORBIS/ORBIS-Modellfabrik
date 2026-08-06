import { Uc01SvgGeneratorService } from './uc-01-svg-generator.service';

describe('Uc01SvgGeneratorService', () => {
  it('renders root, lanes and escapes title markup', () => {
    const svg = new Uc01SvgGeneratorService().generateSvg({
      'uc01.title': 'Track & Trace <Genealogy>',
      'uc01.subtitle': 'End-to-end visibility',
    });

    expect(svg).toContain('<g id="uc01_root">');
    expect(svg).toContain('<g id="uc01_title">');
    expect(svg).toContain('<g id="uc01_lanes">');
    expect(svg).toContain('<g id="uc01_connections">');
    expect(svg).toContain('Track &amp; Trace &lt;Genealogy&gt;');
  });
});
