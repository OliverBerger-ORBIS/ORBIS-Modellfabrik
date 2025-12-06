import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

interface PipelineStep {
  title: string;
  description: string;
}

/**
 * DSP Deployment Pipeline Component
 * 
 * Displays the DSP deployment pipeline flow from integration
 * through transformation, consolidation to provisioning.
 * Uses text boxes and arrows only, no SVG icons.
 */
@Component({
  standalone: true,
  selector: 'app-deployment-pipeline',
  imports: [CommonModule],
  templateUrl: './deployment-pipeline.component.html',
  styleUrl: './deployment-pipeline.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeploymentPipelineComponent {
  readonly sectionTitle = $localize`:@@deploymentPipelineTitle:DSP Deployment Pipeline`;
  readonly sectionSubtitle = $localize`:@@deploymentPipelineSubtitle:From integration and transformation to consolidation and provisioning.`;

  readonly pipelineSteps: PipelineStep[] = [
    {
      title: $localize`:@@pipelineIntegrationTitle:Integration`,
      description: $localize`:@@pipelineIntegrationDesc:Connects data sources and systems into the DSP landscape.`,
    },
    {
      title: $localize`:@@pipelineTransformationTitle:Transformation`,
      description: $localize`:@@pipelineTransformationDesc:Normalizes and enriches data for processing and analytics.`,
    },
    {
      title: $localize`:@@pipelineConsolidationTitle:Consolidation`,
      description: $localize`:@@pipelineConsolidationDesc:Combines data from multiple sources into consistent models.`,
    },
    {
      title: $localize`:@@pipelineProvisioningTitle:Provisioning`,
      description: $localize`:@@pipelineProvisioningDesc:Delivers prepared data and events to ERP, MES, cloud and analytics platforms.`,
    },
  ];

  trackByTitle(_index: number, step: PipelineStep): string {
    return step.title;
  }
}
