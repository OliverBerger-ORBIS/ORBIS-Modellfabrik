import { OSF_CONFIG } from './configs/osf/osf-config';
import { createComponentView } from './layout.component.config';
import { createDeploymentView } from './layout.deployment.config';

describe('OCC BP lane consistency across views', () => {
  it('uses OCC business process containers and connections in deployment view', () => {
    const deployment = createDeploymentView(OSF_CONFIG);
    const fullStep = deployment.steps.find((step) => step.id === 'deployment-step-6');

    expect(fullStep).toBeDefined();
    expect(fullStep?.visibleContainerIds).toEqual(
      expect.arrayContaining(['bp-erp', 'bp-mes', 'bp-ewm', 'bp-crm', 'bp-analytics', 'bp-data-lake']),
    );
    expect(fullStep?.visibleContainerIds).not.toContain('bp-cloud');
    expect(fullStep?.visibleConnectionIds).toEqual(
      expect.arrayContaining([
        'conn_bp-erp_dsp-edge',
        'conn_bp-mes_dsp-edge',
        'conn_bp-ewm_dsp-edge',
        'conn_bp-crm_dsp-edge',
        'conn_bp-analytics_dsp-edge',
        'conn_bp-data-lake_dsp-edge',
      ]),
    );
    expect(fullStep?.visibleConnectionIds).not.toContain('conn_bp-cloud_dsp-edge');
  });

  it('uses OCC business process containers in component view', () => {
    const component = createComponentView(OSF_CONFIG);
    const fullStep = component.steps.find((step) => step.id === 'component-step-8');

    expect(fullStep).toBeDefined();
    expect(fullStep?.visibleContainerIds).toEqual(
      expect.arrayContaining(['bp-erp', 'bp-mes', 'bp-ewm', 'bp-crm', 'bp-analytics', 'bp-data-lake']),
    );
    expect(fullStep?.visibleContainerIds).not.toContain('bp-cloud');
    expect(fullStep?.visibleConnectionIds).toEqual(
      expect.arrayContaining(['conn_bp-ewm_dsp-edge', 'conn_bp-crm_dsp-edge']),
    );
  });
});

