import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

interface UseCase {
  id: string;
  title: string;
  description: string;
  actions: string[];
  smartFactory: string[];
  icon: string;
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

  activeUseCaseId = 'data-aggregation';

  useCases: UseCase[] = [
    {
      id: 'data-aggregation',
      title: $localize`:@@dspUseCaseAggregationTitle:Data Aggregation`,
      description: $localize`:@@dspUseCaseAggregationDesc:Collection and harmonization of setup times, operational states, downtime, and energy consumption as the foundation for OEE and process optimization.`,
      actions: [
        $localize`:@@dspUseCaseAggregationH1:Setup times and operational states`,
        $localize`:@@dspUseCaseAggregationH2:Downtime analysis and energy consumption`,
        $localize`:@@dspUseCaseAggregationH3:Foundation for OEE (Overall Equipment Effectiveness) calculation`,
        $localize`:@@dspUseCaseAggregationH4:Process optimization insights`,
      ],
      smartFactory: [
        $localize`:@@orbisUseCaseAggregationDescription:Harmonize business, shopfloor, and sensor data for a single contextual production view.`,
        $localize`:@@orbisUseCaseAggregationHighlight1:ERP order streams enriched with MES execution events and machine states.`,
        $localize`:@@orbisUseCaseAggregationHighlight2:Machine telemetry correlated with single-part identifiers (NFC) and process parameters.`,
        $localize`:@@orbisUseCaseAggregationHighlight3:Environmental data (temperature, humidity, air quality) linked to production sequences and genealogy.`,
        $localize`:@@orbisUseCaseAggregationHighlight4:Process optimization via analysis of cycle times, takt variability, energy consumption, and machine utilization.`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-data-aggregation.svg',
    },
    {
      id: 'track-trace',
      title: $localize`:@@dspUseCaseTrackTraceTitle:Track & Trace`,
      description: $localize`:@@dspUseCaseTrackTraceDesc:Workpiece tracking via Digital Twin including AGV positions, stations, and events for complete traceability.`,
      actions: [
        $localize`:@@dspUseCaseTrackTraceH1:Real-time workpiece location tracking`,
        $localize`:@@dspUseCaseTrackTraceH2:AGV position monitoring`,
        $localize`:@@dspUseCaseTrackTraceH3:Station event correlation`,
        $localize`:@@dspUseCaseTrackTraceH4:Complete production genealogy`,
      ],
      smartFactory: [
        $localize`:@@orbisUseCaseTrackTraceDescription:Complete object genealogy with real-time traceability and quality correlation.`,
        $localize`:@@orbisUseCaseTrackTraceHighlight1:Object-level location tracking across conveyors, modules, and high-bay storage (HBW).`,
        $localize`:@@orbisUseCaseTrackTraceHighlight2:Correlation of process parameters (DRILL, MILL, AIQS) with ERP/MES customer orders.`,
        $localize`:@@orbisUseCaseTrackTraceHighlight3:Sensor and telemetry data linked to quality outcomes, rework decisions, and root-cause analysis.`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-track-trace.svg',
    },
    {
      id: 'predictive-maintenance',
      title: $localize`:@@dspUseCasePredictiveTitle:Predictive Maintenance`,
      description: $localize`:@@dspUseCasePredictiveDesc:Condition monitoring, early warning systems for machine parameters, and AI/ML models for predictive maintenance.`,
      actions: [
        $localize`:@@dspUseCasePredictiveH1:Real-time condition monitoring`,
        $localize`:@@dspUseCasePredictiveH2:Early warning system for anomalies`,
        $localize`:@@dspUseCasePredictiveH3:AI/ML prediction models`,
        $localize`:@@dspUseCasePredictiveH4:Preventive maintenance scheduling`,
      ],
      smartFactory: [
        $localize`:@@orbisUseCasePredictiveDescription:AI-driven detection of anomalies, wear patterns, and optimal service windows.`,
        $localize`:@@orbisUseCasePredictiveHighlight1:Pattern recognition on spindle load, vibration, cycle duration, and energy usage.`,
        $localize`:@@orbisUseCasePredictiveHighlight2:Anomaly scoring with automated escalation to maintenance bots or SAP notifications.`,
        $localize`:@@orbisUseCasePredictiveHighlight3:Predictive forecasts feeding SAP maintenance plans, spare-part logistics, and operator guidance.`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-predictive-maintenance.svg',
    },
    {
      id: 'process-optimization',
      title: $localize`:@@dspUseCaseOptimizationTitle:Process Optimization`,
      description: $localize`:@@dspUseCaseOptimizationDesc:Event-based process control, dynamic planning, and autonomously responding systems for continuous optimization.`,
      actions: [
        $localize`:@@dspUseCaseOptimizationH1:Event-driven process control`,
        $localize`:@@dspUseCaseOptimizationH2:Dynamic production planning`,
        $localize`:@@dspUseCaseOptimizationH3:Autonomous system responses`,
        $localize`:@@dspUseCaseOptimizationH4:Continuous process improvement`,
      ],
      smartFactory: [
        $localize`:@@orbisUseCaseOptimizationDescription:Continuous optimization of manufacturing processes using real-time and historical data.`,
        $localize`:@@orbisUseCaseOptimizationHighlight1:Bottleneck and cycle-time analysis across DRILL, MILL, AIQS, FTS, and HBW.`,
        $localize`:@@orbisUseCaseOptimizationHighlight2:Optimization of machine utilization, takt stability, and conveyor flow.`,
        $localize`:@@orbisUseCaseOptimizationHighlight3:Energy and resource optimization using spindle load, vibration, and consumption data.`,
        $localize`:@@orbisUseCaseOptimizationHighlight4:AI recommendations for parameters such as feed rate or spindle speed.`,
        $localize`:@@orbisUseCaseOptimizationHighlight5:Simulation of what-if scenarios before applying changes to the physical line.`,
        $localize`:@@orbisUseCaseOptimizationHighlight6:Closed-loop improvements via DSP executors and MES/DSP workflows.`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-process-optimization.svg',
    },
  ];

  setActiveUseCase(id: string): void {
    this.activeUseCaseId = id;
  }

  trackById(_index: number, useCase: UseCase): string {
    return useCase.id;
  }

  get activeUseCase(): UseCase | undefined {
    return this.useCases.find((uc) => uc.id === this.activeUseCaseId);
  }
}
