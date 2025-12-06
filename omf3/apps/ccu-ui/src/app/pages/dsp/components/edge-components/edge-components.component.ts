import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

interface EdgeComponent {
  title: string;
  description: string;
  icon: string;
}

/**
 * DSP Edge Components Component
 * 
 * Displays technical architecture drill-down into the internal
 * components of the DSP Edge infrastructure.
 */
@Component({
  standalone: true,
  selector: 'app-edge-components',
  imports: [CommonModule],
  templateUrl: './edge-components.component.html',
  styleUrl: './edge-components.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EdgeComponentsComponent {
  readonly sectionTitle = $localize`:@@edgeComponentsTitle:DSP Edge Components`;
  readonly sectionSubtitle = $localize`:@@edgeComponentsSubtitle:Technical drill-down into the internal architecture of the DSP Edge.`;

  readonly edgeComponents: EdgeComponent[] = [
    {
      title: $localize`:@@edgeDiscTitle:DISC – Distributed Shopfloor Controller`,
      description: $localize`:@@edgeDiscDesc:Executes decentralized process logic, event handling and orchestration at the shopfloor.`,
      icon: 'assets/svg/dsp/edge-components/edge-disc.svg',
    },
    {
      title: $localize`:@@edgeDisiTitle:DISI – Distributed Shopfloor Integration`,
      description: $localize`:@@edgeDisiDesc:Provides connectivity and integration between shopfloor assets, back-end systems and platforms.`,
      icon: 'assets/svg/dsp/edge-components/edge-disi.svg',
    },
    {
      title: $localize`:@@edgeRouterTitle:Edge Router`,
      description: $localize`:@@edgeRouterDesc:Routes messages and events between agents, services and external systems.`,
      icon: 'assets/svg/dsp/edge-components/edge-router.svg',
    },
    {
      title: $localize`:@@edgeAgentTitle:Edge Agent`,
      description: $localize`:@@edgeAgentDesc:Executes tasks and process objects close to machines and sensors.`,
      icon: 'assets/svg/dsp/edge-components/edge-agent.svg',
    },
    {
      title: $localize`:@@edgeAppServerTitle:App Server`,
      description: $localize`:@@edgeAppServerDesc:Hosts local applications, APIs and visualizations at the edge.`,
      icon: 'assets/svg/dsp/edge-components/edge-app-server.svg',
    },
    {
      title: $localize`:@@edgeLogServerTitle:Log Server`,
      description: $localize`:@@edgeLogServerDesc:Collects and persists logs and telemetry for monitoring and troubleshooting.`,
      icon: 'assets/svg/dsp/edge-components/edge-log-server.svg',
    },
    {
      title: $localize`:@@edgeDatabaseTitle:Edge Database`,
      description: $localize`:@@edgeDatabaseDesc:Stores buffered and time-series data close to the shopfloor.`,
      icon: 'assets/svg/dsp/edge-components/edge-database.svg',
    },
    {
      title: $localize`:@@edgeEventBusTitle:Event Bus`,
      description: $localize`:@@edgeEventBusDesc:Implements pub/sub messaging between distributed edge components.`,
      icon: 'assets/svg/dsp/edge-components/edge-event-bus.svg',
    },
  ];

  trackByTitle(_index: number, component: EdgeComponent): string {
    return component.title;
  }
}
