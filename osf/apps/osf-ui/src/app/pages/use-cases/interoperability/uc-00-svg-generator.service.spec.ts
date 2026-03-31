import { Uc00SvgGeneratorService } from './uc-00-svg-generator.service';

describe('Uc00SvgGeneratorService', () => {
  it('wraps DSP step title and description with tspans inside the normalize step box', () => {
    const svc = new Uc00SvgGeneratorService();
    const longDesc =
      'Canonicalize events across protocols and data models so downstream consumers receive stable identifiers and timing';
    const svg = svc.generateSvg({
      'uc00.step.normalize.titleLine1': 'Normalize,',
      'uc00.step.normalize.titleLine2': '(semantics & format)',
      'uc00.step.normalize.description': longDesc,
    });
    const afterId = svg.split('id="uc00_step_normalize"')[1];
    expect(afterId).toBeDefined();
    const stepInner = afterId!.split('</g>')[0];
    const tspans = stepInner.match(/<tspan/g);
    expect(tspans?.length).toBeGreaterThanOrEqual(3);
  });
});
