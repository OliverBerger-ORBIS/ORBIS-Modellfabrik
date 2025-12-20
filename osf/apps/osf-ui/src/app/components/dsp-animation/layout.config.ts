import type { DiagramConfig, ViewMode } from './types';
import { createFunctionalView } from './layout.functional.config';
import { createComponentView } from './layout.component.config';
import { createDeploymentView } from './layout.deployment.config';
import type { CustomerDspConfig } from './configs/types';
export { VIEWBOX_WIDTH, VIEWBOX_HEIGHT } from './layout.shared.config';

export function createDiagramConfig(viewMode: ViewMode = 'functional', customerConfig?: CustomerDspConfig): DiagramConfig {
  switch (viewMode) {
    case 'functional':
      return createFunctionalView(customerConfig) as DiagramConfig;
    case 'component':
      return createComponentView(customerConfig) as DiagramConfig;
    case 'deployment':
      return createDeploymentView(customerConfig) as DiagramConfig;
    default:
      return createFunctionalView(customerConfig) as DiagramConfig;
  }
}
