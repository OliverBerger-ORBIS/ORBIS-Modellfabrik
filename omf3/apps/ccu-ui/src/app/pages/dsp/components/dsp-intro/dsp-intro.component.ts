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
  readonly sectionSubtitle = $localize`:@@dspIntroSubtitle:Distributed Shopfloor Processing (DSP) enables manufacturer-independent, event-driven communication between machines, systems and IT platforms — creating a fully interoperable Smart Factory.`;

  readonly introCards: IntroCard[] = [
    {
      title: $localize`:@@dspIntroInteroperabilityTitle:Interoperability`,
      description: $localize`:@@dspIntroInteroperabilityDesc:DSP enables manufacturer-independent, event-driven communication between machines, shopfloor systems and IT platforms — the core foundation of an interoperable Smart Factory.`,
      icon: 'assets/svg/dsp/functions/edge-interoperability.svg',
    },
    {
      title: $localize`:@@dspIntroEdgeRuntimeTitle:Edge Runtime`,
      description: $localize`:@@dspIntroEdgeRuntimeDesc:The DSP Edge provides local, real-time process execution, data buffering, semantic preprocessing and Digital Twin synchronization — independent from cloud availability.`,
      icon: 'assets/svg/dsp/architecture/dsp-edge-box.svg',
    },
    {
      title: $localize`:@@dspIntroManagementCockpitTitle:Management Cockpit`,
      description: $localize`:@@dspIntroManagementCockpitDesc:The cloud-based Management Cockpit models processes, manages shopfloor organization, and orchestrates all Edge nodes centrally across sites.`,
      icon: 'assets/svg/dsp/architecture/dsp-mc-box.svg',
    },
    {
      title: $localize`:@@dspIntroDigitalTwinTitle:Digital Twin`,
      description: $localize`:@@dspIntroDigitalTwinDesc:DSP creates a unified Digital Twin capturing machine states, process parameters and workpiece lifecycle data in real time.`,
      icon: 'assets/svg/dsp/functions/edge-digital-twin.svg',
    },
    {
      title: $localize`:@@dspIntroItOtConvergenceTitle:IT/OT Convergence`,
      description: $localize`:@@dspIntroItOtConvergenceDesc:DSP connects shopfloor events with ERP, MES, IoT platforms, data lakes and analytics services — enabling true IT/OT convergence.`,
      icon: 'assets/svg/orbis/integration.svg',
    },
    {
      title: $localize`:@@dspIntroBestOfBreedTitle:Best-of-Breed Integration`,
      description: $localize`:@@dspIntroBestOfBreedDesc:DSP integrates seamlessly with SAP Digital Manufacturing, SAP S/4HANA, SAP BTP, Azure IoT, Power BI, SAC and other best-of-breed systems.`,
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
