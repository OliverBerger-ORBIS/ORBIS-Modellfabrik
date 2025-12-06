import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

interface IntroCard {
  title: string;
  description: string;
  icon: string;
}

/**
 * DSP Introduction Component
 * 
 * Displays key concepts and benefits of DSP based on content from
 * ORBIS DSP webpage and blog posts.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-intro',
  imports: [CommonModule],
  templateUrl: './dsp-intro.component.html',
  styleUrl: './dsp-intro.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspIntroComponent {
  readonly sectionTitle = $localize`:@@dspIntroTitle:What is DSP?`;
  readonly sectionSubtitle = $localize`:@@dspIntroSubtitle:Distributed Shopfloor Processing enables manufacturer-independent communication between machines, systems, and IT platforms – the foundation for the connected Smart Factory.`;

  readonly introCards: IntroCard[] = [
    {
      title: $localize`:@@dspIntroInteroperabilityTitle:Interoperability`,
      description: $localize`:@@dspIntroInteroperabilityDesc:DSP enables manufacturer-independent communication between machines, systems, and IT platforms – the foundation for the connected Smart Factory.`,
      icon: 'assets/svg/dsp/functions/connectivity.svg',
    },
    {
      title: $localize`:@@dspIntroEdgeRuntimeTitle:Edge Runtime`,
      description: $localize`:@@dspIntroEdgeRuntimeDesc:The DSP Edge enables local, real-time capable process logic, data buffering, and Digital Twin mapping independent of cloud connections.`,
      icon: 'assets/svg/dsp/architecture/dsp-edge-box.svg',
    },
    {
      title: $localize`:@@dspIntroManagementCockpitTitle:Management Cockpit`,
      description: $localize`:@@dspIntroManagementCockpitDesc:Models processes, manages organization, orchestrates all Edge nodes centrally in the cloud.`,
      icon: 'assets/svg/dsp/architecture/dsp-cockpit-box.svg',
    },
    {
      title: $localize`:@@dspIntroDigitalTwinTitle:Digital Twin`,
      description: $localize`:@@dspIntroDigitalTwinDesc:Maps machine states, process parameters, and workpiece status in real-time for complete visibility.`,
      icon: 'assets/svg/dsp/functions/digital-twin.svg',
    },
    {
      title: $localize`:@@dspIntroItOtConvergenceTitle:IT/OT Convergence`,
      description: $localize`:@@dspIntroItOtConvergenceDesc:DSP connects shopfloor events with ERP, MES, Data Lakes, and Cloud Analytics for seamless integration.`,
      icon: 'assets/svg/orbis/integration.svg',
    },
    {
      title: $localize`:@@dspIntroBestOfBreedTitle:Best-of-Breed Integration`,
      description: $localize`:@@dspIntroBestOfBreedDesc:Connection to SAP Digital Manufacturing, SAP S/4HANA, Azure IoT, Power BI, SAC, and more.`,
      icon: 'assets/svg/orbis/consolidate.svg',
    },
    {
      title: $localize`:@@dspIntroAutonomousAdaptiveTitle:Autonomous & Adaptive Enterprise`,
      description: $localize`:@@dspIntroAutonomousAdaptiveDesc:Phase 5 represents the fully connected, autonomous and adaptive enterprise where data from shopfloor, Edge, ERP, analytics and data lakes enables self-optimizing workflows.`,
      icon: 'assets/svg/orbis/ai-algorithm.svg',
    },
  ];

  trackByTitle(_index: number, card: IntroCard): string {
    return card.title;
  }
}
