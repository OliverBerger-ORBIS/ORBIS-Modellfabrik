import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

interface UseCase {
  id: string;
  title: string;
  description: string;
  highlights: string[];
  icon: string;
  expanded: boolean;
}

/**
 * DSP Use Cases Component
 * 
 * Displays the four main DSP use cases:
 * 1. Data Aggregation
 * 2. Track & Trace
 * 3. Predictive Maintenance
 * 4. Process Optimization
 */
@Component({
  standalone: true,
  selector: 'app-dsp-use-cases',
  imports: [CommonModule],
  templateUrl: './dsp-use-cases.component.html',
  styleUrl: './dsp-use-cases.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspUseCasesComponent {
  readonly sectionTitle = $localize`:@@dspUseCasesTitle:DSP Use Cases`;
  readonly sectionSubtitle = $localize`:@@dspUseCasesSubtitle:Practical applications of DSP in smart manufacturing environments.`;

  useCases: UseCase[] = [
    {
      id: 'data-aggregation',
      title: $localize`:@@dspUseCaseAggregationTitle:Data Aggregation`,
      description: $localize`:@@dspUseCaseAggregationDesc:Collection and harmonization of setup times, operational states, downtime, and energy consumption as the foundation for OEE and process optimization.`,
      highlights: [
        $localize`:@@dspUseCaseAggregationH1:Setup times and operational states`,
        $localize`:@@dspUseCaseAggregationH2:Downtime analysis and energy consumption`,
        $localize`:@@dspUseCaseAggregationH3:Foundation for OEE calculation`,
        $localize`:@@dspUseCaseAggregationH4:Process optimization insights`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-data-aggregation.svg',
      expanded: false,
    },
    {
      id: 'track-trace',
      title: $localize`:@@dspUseCaseTrackTraceTitle:Track & Trace`,
      description: $localize`:@@dspUseCaseTrackTraceDesc:Workpiece tracking via Digital Twin including AGV positions, stations, and events for complete traceability.`,
      highlights: [
        $localize`:@@dspUseCaseTrackTraceH1:Real-time workpiece location tracking`,
        $localize`:@@dspUseCaseTrackTraceH2:AGV position monitoring`,
        $localize`:@@dspUseCaseTrackTraceH3:Station event correlation`,
        $localize`:@@dspUseCaseTrackTraceH4:Complete production genealogy`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-track-trace.svg',
      expanded: false,
    },
    {
      id: 'predictive-maintenance',
      title: $localize`:@@dspUseCasePredictiveTitle:Predictive Maintenance`,
      description: $localize`:@@dspUseCasePredictiveDesc:Condition monitoring, early warning systems for machine parameters, and AI/ML models for predictive maintenance.`,
      highlights: [
        $localize`:@@dspUseCasePredictiveH1:Real-time condition monitoring`,
        $localize`:@@dspUseCasePredictiveH2:Early warning system for anomalies`,
        $localize`:@@dspUseCasePredictiveH3:AI/ML prediction models`,
        $localize`:@@dspUseCasePredictiveH4:Preventive maintenance scheduling`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-predictive-maintenance.svg',
      expanded: false,
    },
    {
      id: 'process-optimization',
      title: $localize`:@@dspUseCaseOptimizationTitle:Process Optimization`,
      description: $localize`:@@dspUseCaseOptimizationDesc:Event-based process control, dynamic planning, and autonomously responding systems for continuous optimization.`,
      highlights: [
        $localize`:@@dspUseCaseOptimizationH1:Event-driven process control`,
        $localize`:@@dspUseCaseOptimizationH2:Dynamic production planning`,
        $localize`:@@dspUseCaseOptimizationH3:Autonomous system responses`,
        $localize`:@@dspUseCaseOptimizationH4:Continuous process improvement`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-process-optimization.svg',
      expanded: false,
    },
  ];

  toggleUseCase(id: string): void {
    const useCase = this.useCases.find(uc => uc.id === id);
    if (useCase) {
      useCase.expanded = !useCase.expanded;
    }
  }

  trackById(_index: number, useCase: UseCase): string {
    return useCase.id;
  }
}
