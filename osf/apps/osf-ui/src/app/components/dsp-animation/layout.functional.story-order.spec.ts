import { OSF_CONFIG } from './configs/osf/osf-config';
import { createDefaultSteps } from './layout.functional.config';

describe('functional story order', () => {
  it('moves interoperability summary to step 12', () => {
    const steps = createDefaultSteps(OSF_CONFIG);
    const step4 = steps.find((step) => step.id === 'step-4');
    const step12 = steps.find((step) => step.id === 'step-12');

    expect(step4?.highlightedFunctionIcons).toEqual(['edge-network']);
    expect(step12?.highlightedFunctionIcons).toEqual(['edge-interoperability']);
    expect(step12?.visibleConnectionIds).toEqual(
      expect.arrayContaining([
        'conn_bp-mes_dsp-edge',
        'conn_bp-ewm_dsp-edge',
        'conn_bp-crm_dsp-edge',
        'conn_dsp-edge_sf-system-fts',
        'conn_dsp-edge_sf-device-aiqs',
        'conn_dsp-edge_sf-device-hbw',
      ]),
    );
  });

  it('applies requested highlights for steps 7 to 9', () => {
    const steps = createDefaultSteps(OSF_CONFIG);
    const step7 = steps.find((step) => step.id === 'step-7');
    const step8 = steps.find((step) => step.id === 'step-8');
    const step9 = steps.find((step) => step.id === 'step-9');

    expect(step7?.visibleContainerIds).toEqual(expect.arrayContaining(['bp-erp', 'bp-mes', 'bp-ewm']));
    expect(step7?.highlightedContainerIds).toEqual(expect.arrayContaining(['bp-mes', 'bp-ewm']));
    expect(step7?.highlightedContainerIds).not.toContain('bp-erp');
    expect(step7?.visibleConnectionIds).toEqual(
      expect.arrayContaining([
        'conn_dsp-edge_sf-system-fts',
        'conn_dsp-edge_sf-device-aiqs',
        'conn_dsp-edge_sf-device-hbw',
      ]),
    );
    expect(
      step7?.visibleConnectionIds?.some(
        (id) => id === 'conn_dsp-edge_sf-system-any' || id === 'conn_dsp-edge_sf-system-sensor',
      ),
    ).toBe(true);
    expect(step7?.highlightedConnectionIds).not.toEqual(
      expect.arrayContaining(['conn_dsp-edge_sf-system-fts', 'conn_dsp-edge_sf-device-aiqs', 'conn_dsp-edge_sf-device-hbw']),
    );
    expect(
      step7?.highlightedConnectionIds?.includes('conn_dsp-edge_sf-system-any') ||
      step7?.highlightedConnectionIds?.includes('conn_dsp-edge_sf-system-sensor'),
    ).toBe(false);

    expect(step8?.highlightedContainerIds).toEqual(
      expect.arrayContaining(['bp-erp', 'bp-mes', 'bp-ewm', 'bp-crm']),
    );
    expect(step8?.visibleContainerIds).not.toEqual(expect.arrayContaining(['bp-analytics', 'bp-data-lake']));
    expect(step8?.highlightedConnectionIds).toEqual(
      expect.arrayContaining([
        'conn_bp-erp_dsp-edge',
        'conn_bp-mes_dsp-edge',
        'conn_bp-ewm_dsp-edge',
        'conn_bp-crm_dsp-edge',
      ]),
    );

    expect(step9?.highlightedContainerIds).toEqual(['bp-analytics']);
    expect(step9?.visibleContainerIds).not.toContain('bp-data-lake');
  });

  it('starts mc story with center icon before progressive function reveal', () => {
    const steps = createDefaultSteps(OSF_CONFIG);
    const step13 = steps.find((step) => step.id === 'step-13');
    const step14 = steps.find((step) => step.id === 'step-14');
    const step15 = steps.find((step) => step.id === 'step-15');
    const step16 = steps.find((step) => step.id === 'step-16');
    const step19 = steps.find((step) => step.id === 'step-19');

    expect(step13?.showFunctionIcons).toBe(false);
    expect(step14?.highlightedContainerIds).toEqual(expect.arrayContaining(['dsp-mc', 'sf-devices-group', 'bp-erp']));
    expect(step14?.highlightedFunctionIcons).toEqual(['mc-hierarchical-structure']);
    expect(step15?.highlightedContainerIds).toEqual(expect.arrayContaining(['dsp-mc', 'bp-mes', 'sf-system-fts']));
    expect(step15?.highlightedFunctionIcons).toEqual(['mc-orchestration']);
    expect(step16?.highlightedContainerIds).toEqual(['dsp-mc']);
    expect(step16?.highlightedFunctionIcons).toEqual(['mc-governance']);
    expect(step19?.visibleConnectionIds).toEqual(expect.arrayContaining(['conn_dsp-edge_dsp-mc']));
    expect(step19?.highlightedConnectionIds).not.toEqual(expect.arrayContaining(['conn_dsp-edge_dsp-mc']));
  });
});

