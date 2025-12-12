import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

/**
 * DSP MES/ERP Integration Teaser Component
 * 
 * Provides a preview of upcoming MES and ERP integration features.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-mes-teaser',
  imports: [CommonModule],
  templateUrl: './dsp-mes-teaser.component.html',
  styleUrl: './dsp-mes-teaser.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspMesTeaserComponent {
  readonly sectionTitle = $localize`:@@dspMesTeaserTitle:Coming Soon: MES & ERP Integration`;
  readonly sectionDescription = $localize`:@@dspMesTeaserDesc:In the next version, the integration of ORBIS MES and SAP ERP into DSP will be demonstrated. Production, warehouse, quality data, and process models will be directly connected.`;

  readonly features = [
    {
      title: $localize`:@@dspMesTeaserErpTitle:ERP Integration`,
      description: $localize`:@@dspMesTeaserErpDesc:Direct connection to SAP S/4HANA for order management and material flow`,
      icon: 'assets/svg/brand/sap-logo.svg',
    },
    {
      title: $localize`:@@dspMesTeaserAnalyticsTitle:Analytics Platform`,
      description: $localize`:@@dspMesTeaserAnalyticsDesc:Integration with Power BI and SAP Analytics Cloud for advanced reporting`,
      icon: 'assets/svg/business/analytics-application.svg',
    },
    {
      title: $localize`:@@dspMesTeaserDataLakeTitle:Data Lake`,
      description: $localize`:@@dspMesTeaserDataLakeDesc:Centralized data repository for historical analysis and ML training`,
      icon: 'assets/svg/business/data-lake.svg',
    },
  ];

  trackByTitle(_index: number, feature: typeof this.features[0]): string {
    return feature.title;
  }
}
