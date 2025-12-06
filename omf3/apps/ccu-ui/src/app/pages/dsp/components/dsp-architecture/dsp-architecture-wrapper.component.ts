import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { DspArchitectureComponent } from '../../../../components/dsp-architecture/dsp-architecture.component';
import type { DspDetailView } from '../../../../tabs/configuration-detail.types';
import { ExternalLinksService } from '../../../../services/external-links.service';

/**
 * Wrapper component for DSP Architecture that provides the necessary view configuration.
 * This component integrates the reusable DspArchitectureComponent into the DSP page.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-architecture-wrapper',
  imports: [CommonModule, DspArchitectureComponent],
  templateUrl: './dsp-architecture-wrapper.component.html',
  styleUrl: './dsp-architecture-wrapper.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspArchitectureWrapperComponent implements OnInit {
  readonly sectionTitle = $localize`:@@dspArchSectionTitle:DSP Reference Architecture`;
  readonly sectionDescription = $localize`:@@dspArchSectionDesc:Interactive 12-step animation showing the complete DSP architecture from shopfloor devices to AI excellence.`;

  // Create a view configuration for the DSP Architecture component
  dspView: DspDetailView = {
    architecture: [
      {
        id: 'ux',
        title: $localize`:@@dspLayerUxTitle:SmartFactory Dashboard`,
        description: $localize`:@@dspLayerUxDescription:Visual access for operators and planners.`,
        capabilities: [],
        logoIconKey: 'logo-orbis',
        position: 'left',
      },
      {
        id: 'edge',
        title: $localize`:@@dspLayerEdgeTitle:EDGE`,
        description: $localize`:@@dspLayerEdgeDescription:Low-latency processing close to the machines.`,
        capabilities: [
          $localize`:@@dspEdgeBullet1:Low-latency processing close to the machines.`,
          $localize`:@@dspEdgeBullet2:Object-oriented choreography with decentralized control.`,
          $localize`:@@dspEdgeBullet3:Protocol conversion (OPC UA, MQTT, REST).`,
          $localize`:@@dspEdgeBullet4:Streaming analytics and buffering during connectivity issues.`,
        ],
        actionId: 'edge',
        logoIconKey: 'logo-dsp',
        functionIcons: [
          { iconKey: 'edge-data-storage', size: 48 },
          { iconKey: 'edge-digital-twin', size: 48 },
          { iconKey: 'edge-connectivity', size: 48 },
          { iconKey: 'edge-workflow', size: 48 },
          { iconKey: 'edge-analytics', size: 48 },
        ],
        position: 'center',
      },
      {
        id: 'management',
        title: $localize`:@@dspLayerManagementTitle:Management Cockpit`,
        description: $localize`:@@dspLayerManagementDescription:Cloud-based control and KPI monitoring.`,
        capabilities: [
          $localize`:@@dspManagementBullet1:Cloud-based control and KPI monitoring.`,
          $localize`:@@dspManagementBullet2:Governance, rules, and automation.`,
          $localize`:@@dspManagementBullet3:Digital twins enriched with enterprise data.`,
          $localize`:@@dspManagementBullet4:Analytics workloads for KPIs.`,
        ],
        actionId: 'management',
        logoIconKey: 'logo-dsp',
        secondaryLogoIconKey: 'logo-azure',
        position: 'right',
      },
    ],
    features: [
      $localize`:@@dspGeneralBullet1:Interoperability for IT/OT landscapes with bi-directional topics.`,
      $localize`:@@dspGeneralBullet2:Decentralized control through object-oriented process choreography.`,
      $localize`:@@dspGeneralBullet3:Digital twins mirroring assets with contextual KPIs.`,
      $localize`:@@dspGeneralBullet4:Hybrid edge–cloud processing for latency-sensitive flows.`,
      $localize`:@@dspGeneralBullet5:Built-in Industry 4.0 capabilities (IIoT, AI, analytics).`,
    ],
    actions: [],
    resources: [],
    businessProcesses: [
      {
        id: 'erp-application',
        label: $localize`:@@dspBusinessErp:ERP Applications`,
        iconKey: 'erp-application',
      },
      {
        id: 'bp-cloud-apps',
        label: $localize`:@@dspBusinessCloud:Cloud Applications`,
        iconKey: 'bp-cloud-apps',
      },
      {
        id: 'bp-analytics',
        label: $localize`:@@dspBusinessAnalytics:Analytics Applications`,
        iconKey: 'bp-analytics',
      },
      {
        id: 'bp-data-lake',
        label: $localize`:@@dspBusinessDataLake:Data Lake`,
        iconKey: 'bp-data-lake',
      },
    ],
    shopfloorPlatforms: [],
    shopfloorSystems: [],
    edgeUrl: '#',
    managementUrl: '#',
    analyticsUrl: '#',
    smartfactoryDashboardUrl: '/dashboard',
  };

  private locale = 'en';  // Default locale

  constructor(
    private readonly router: Router,
    private readonly route: ActivatedRoute,
    private readonly externalLinksService: ExternalLinksService
  ) {}

  ngOnInit(): void {
    // Get locale from route - traverse up the route tree
    let currentRoute = this.route;
    while (currentRoute.parent) {
      const localeParam = currentRoute.snapshot.paramMap.get('locale');
      if (localeParam) {
        this.locale = localeParam;
        break;
      }
      currentRoute = currentRoute.parent;
    }

    // Update URLs from external links service
    const links = this.externalLinksService.current;
    this.dspView = {
      ...this.dspView,
      edgeUrl: links.dspControlUrl,
      managementUrl: links.managementCockpitUrl,
      analyticsUrl: links.grafanaDashboardUrl,
      smartfactoryDashboardUrl: links.smartfactoryDashboardUrl,
    };
  }

  onActionTriggered(event: { id: string; url: string }): void {
    if (!event.url) {
      return;
    }

    // Check if it's an external URL (http/https)
    if (event.url.startsWith('http://') || event.url.startsWith('https://')) {
      window.open(event.url, '_blank', 'noreferrer noopener');
      return;
    }

    // Check if it's an absolute internal path
    if (event.url.startsWith('/')) {
      this.router.navigateByUrl(event.url);
      return;
    }

    // Relative path - prepend with locale
    const fullPath = `/${this.locale}/${event.url}`;
    this.router.navigateByUrl(fullPath);
  }
}
