import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { DspIntroComponent } from './components/dsp-intro/dsp-intro.component';
import { DspArchitectureWrapperComponent } from './components/dsp-architecture/dsp-architecture-wrapper.component';
import { EdgeComponentsComponent } from './components/edge-components/edge-components.component';
import { EdgeArchitectureAnimatedComponent } from './components/edge-architecture-animated/edge-architecture-animated.component';
import { DeploymentPipelineComponent } from './components/deployment-pipeline/deployment-pipeline.component';
import { DspUseCasesComponent } from './components/dsp-use-cases/dsp-use-cases.component';
import { DspMethodologyComponent } from './components/dsp-methodology/dsp-methodology.component';
import { DspMesTeaserComponent } from './components/dsp-mes-teaser/dsp-mes-teaser.component';

/**
 * Main DSP (Distributed Shopfloor Processing) page component.
 * 
 * This page provides a comprehensive view of DSP including:
 * - Introduction to DSP concepts
 * - Interactive architecture animation (12 steps)
 * - DSP Edge Components (Legend View - card-based component overview)
 * - DSP Edge Architecture (Animated - 4-step internal component flow)
 * - DSP Deployment Pipeline (integration → transformation → consolidation → provisioning)
 * - Use cases (Data Aggregation, Track & Trace, Predictive Maintenance, Process Optimization)
 * - Methodology (Phases 1-5 with Autonomous & Adaptive Enterprise)
 * - MES/ERP Integration teaser
 */
@Component({
  standalone: true,
  selector: 'app-dsp-page',
  imports: [
    CommonModule,
    DspIntroComponent,
    DspArchitectureWrapperComponent,
    EdgeComponentsComponent,
    EdgeArchitectureAnimatedComponent,
    DeploymentPipelineComponent,
    DspUseCasesComponent,
    DspMethodologyComponent,
    DspMesTeaserComponent,
  ],
  templateUrl: './dsp-page.component.html',
  styleUrl: './dsp-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspPageComponent {
  readonly pageTitle = $localize`:@@dspPageTitle:Distributed Shopfloor Processing`;
  readonly pageSubtitle = $localize`:@@dspPageSubtitle:Edge-to-Cloud Orchestration for Smart Manufacturing`;
}
