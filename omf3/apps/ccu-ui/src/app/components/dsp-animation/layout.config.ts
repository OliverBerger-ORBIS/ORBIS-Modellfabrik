import type { DiagramConfig, ViewMode } from './types';
import { createFunctionalView } from './layout.functional.config';
import { createComponentView } from './layout.component.config';
import { createDeploymentView } from './layout.deployment.config';
export { VIEWBOX_WIDTH, VIEWBOX_HEIGHT } from './layout.shared.config';

export function createDiagramConfig(viewMode: ViewMode = 'functional'): DiagramConfig {
  switch (viewMode) {
    case 'functional':
      return createFunctionalView() as DiagramConfig;
    case 'component':
      return createComponentView() as DiagramConfig;
    case 'deployment':
      return createDeploymentView() as DiagramConfig;
    default:
      return createFunctionalView() as DiagramConfig;
  }
}
