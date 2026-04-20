import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { LanguageService } from '../../../../services/language.service';
import {
  DSP_RETURN_SECTION_SESSION_KEY,
  isDspAccordionSectionId,
} from '../../dsp-accordion-sections';

interface UseCase {
  id: string; // Route id (e.g. 'interoperability')
  useCaseTitle: string; // Display title on tiles and detail header (e.g. "Interoperability (Event-to-Process)")
  useCaseCode?: string; // Optional UC code for label (e.g. "UC-00" → "Use Case UC-00")
  reference?: string; // Optional full reference for action row (e.g. "UC-00: Interoperability")
  description: string;
  actions: string[];
  smartFactory: string[];
  icon: string;
  footer?: string;
  /** Concept / diagram page (DR-22) */
  conceptRoute?: string;
  /** Live demo route; omit if UC has no separate live entry (e.g. UC-05 embeds Live in one page) */
  liveDemoRoute?: string;
}

const USE_CASE_LABEL = $localize`:@@dspUseCaseLabel:Use Case`;

/**
 * DSP Use Cases Component
 * 
 * Displays the main DSP use cases (Reihenfolge wie im Blog-Artikel):
 * 1. UC-00 Interoperability (Event-to-Process, Grundlage)
 * 2. UC-01 Track & Trace (Genealogy, Live)
 * 3. UC-02 Data Aggregation
 * 4. UC-03 AI Lifecycle
 * 5. UC-04 Closed Loop Quality
 * 6. UC-05 Predictive Maintenance
 * 7. UC-06 Process Optimization
 * 
 * Supports:
 * - Single click: Highlight and show details
 * - Double click: Navigate to detail page (if implemented)
 * - "Concept" / "Live Demo" buttons (DR-22); UCs with only concept show one button
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
  @Input() enableNavigation = false; // Enable double-click navigation and Concept / Live Demo buttons

  /**
   * When set (e.g. `use-cases` on the main DSP page), opening a concept/live route records
   * this accordion section so Back returns to `/{locale}/dsp?section=…`.
   * Omit on standalone pages (e.g. use-case selector) so Back keeps the previous behaviour.
   */
  @Input() recordDspReturnSection: string | null = null;

  readonly sectionTitle = $localize`:@@dspUseCasesTitle:DSP Use Cases`;
  readonly sectionSubtitle = $localize`:@@dspUseCasesSubtitle:Practical applications of DSP in smart manufacturing environments.`;
  readonly doubleClickHint = $localize`:@@dspUseCaseDoubleClickHintOpenConcept:Double-click to open Concept`;

  activeUseCaseId = 'interoperability';

  useCases: UseCase[] = [
    {
      id: 'interoperability',
      useCaseTitle: $localize`:@@dspUseCaseInteroperabilityTileTitle:Interoperability (Event-to-Process)`,
      useCaseCode: 'UC-00',
      reference: $localize`:@@dspUseCaseInteroperabilityRef:UC-00: Interoperability`,
      description: $localize`:@@dspUseCaseInteroperabilityDesc:Normalize shopfloor events and enrich them with context to create a shared process view for OT and IT.`,
      actions: [
        $localize`:@@dspUseCaseInteroperabilityH1:Normalize and harmonize events across machines, stations, AGVs, and quality systems`,
        $localize`:@@dspUseCaseInteroperabilityH2:Add context (order, workpiece, station, time) to make events "process-ready"`,
        $localize`:@@dspUseCaseInteroperabilityH3:Correlate event chains into interpretable process steps (event-to-process mapping)`,
        $localize`:@@dspUseCaseInteroperabilityH4:Enable reuse: one integration pattern for multiple use cases instead of point-to-point wiring`,
      ],
      smartFactory: [
        $localize`:@@orbisUseCaseInteroperabilityHighlight1:Create a shared process view that aligns OT signals with IT process context`,
        $localize`:@@orbisUseCaseInteroperabilityHighlight2:Provide a consistent basis for traceability, KPIs, and closed-loop orchestration`,
        $localize`:@@orbisUseCaseInteroperabilityHighlight3:Integrate best-of-breed target systems (ERP / MES / analytics) without rebuilding shopfloor integration`,
        $localize`:@@orbisUseCaseInteroperabilityHighlight4:SAP can be a target example, but is not a prerequisite`,
      ],
      footer: $localize`:@@dspUseCaseInteroperabilityFooter:OSF is a demonstrator showcasing integration principles; productive implementations depend on the customer's target landscape.`,
      icon: 'assets/svg/dsp/functions/edge-interoperability.svg',
      conceptRoute: '/dsp/use-case/interoperability',
    },
    {
      id: 'track-trace',
      useCaseTitle: $localize`:@@dspUseCaseTrackTraceUnifiedTitle:Track & Trace`,
      useCaseCode: 'UC-01',
      reference: $localize`:@@dspUseCaseTrackTraceUnifiedRef:UC-01: Track & Trace`,
      description: $localize`:@@dspUseCaseTrackTraceUnifiedDesc:Genealogy concept (correlated events, plan vs. actual) and live workpiece tracking with stations, AGVs, and quality correlation.`,
      actions: [
        $localize`:@@dspUseCaseTrackTraceUnifiedH1:Concept diagram: NFC join key, business context, plan vs. actual path`,
        $localize`:@@dspUseCaseTrackTraceUnifiedH2:Live Digital Twin: workpiece location, AGV positions, station events`,
        $localize`:@@dspUseCaseTrackTraceUnifiedH3:Correlated timeline and order context for full genealogy`,
        $localize`:@@dspUseCaseTrackTraceUnifiedH4:ERP/MES and quality linkage for traceability and root-cause analysis`,
      ],
      smartFactory: [
        $localize`:@@orbisUseCaseTrackTraceUnifiedSf1:One integration pattern: from normalized events to object-level traceability.`,
        $localize`:@@orbisUseCaseTrackTraceUnifiedSf2:Combines conceptual genealogy with real-time shopfloor and quality data.`,
        $localize`:@@orbisUseCaseTrackTraceUnifiedSf3:Supports demonstrator and customer storytelling without duplicate tiles.`,
        $localize`:@@orbisUseCaseTrackTraceUnifiedSf4:Scales with additional stations or AGVs via the same event model.`,
      ],
      icon: 'assets/svg/dsp/use-cases/use-case-track-trace.svg',
      conceptRoute: '/dsp/use-case/track-trace',
      liveDemoRoute: '/dsp/use-case/track-trace',
    },
    {
      id: 'data-aggregation',
      useCaseTitle: $localize`:@@dspUseCaseAggregationTitle:Data Aggregation`,
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
      conceptRoute: '/dsp/use-case/three-data-pools',
    },
    {
      id: 'ai-lifecycle',
      useCaseTitle: $localize`:@@dspUseCaseAiLifecycleTitle:AI Lifecycle`,
      description: $localize`:@@dspUseCaseAiLifecycleDesc:Industrial AI as a lifecycle: data capture, cloud training, governed rollout to multiple stations, and continuous improvement through monitoring and feedback.`,
      actions: [
        $localize`:@@dspUseCaseAiLifecycleH1:Real-time inference at the edge where decisions are needed`,
        $localize`:@@dspUseCaseAiLifecycleH2:Governed deployment with versioning, approval, rollout and rollback`,
        $localize`:@@dspUseCaseAiLifecycleH3:Data capture and context enrichment for ML-ready pipelines`,
        $localize`:@@dspUseCaseAiLifecycleH4:Monitor, feedback and retraining loop`,
      ],
      smartFactory: [
        $localize`:@@orbisUseCaseAiLifecycleDescription:Train centrally, deploy to multiple stations via DSP Management Cockpit and DSP Edge.`,
        $localize`:@@orbisUseCaseAiLifecycleHighlight1:Data capture & context from shopfloor events, business context and sensors.`,
        $localize`:@@orbisUseCaseAiLifecycleHighlight2:Cloud training and validation with model packaging.`,
        $localize`:@@orbisUseCaseAiLifecycleHighlight3:DSP Edge for model runtime and provisioning to stations.`,
        $localize`:@@orbisUseCaseAiLifecycleHighlight4:Monitoring, telemetry and retrain triggers for continuous improvement.`,
      ],
      icon: 'assets/svg/dsp/methodology/phase4-automation-orchestration.svg',
      conceptRoute: '/dsp/use-case/ai-lifecycle',
    },
    {
      id: 'closed-loop-quality',
      useCaseTitle: $localize`:@@dspUseCaseClosedLoopQualityTitle:Closed Loop Quality`,
      description: $localize`:@@dspUseCaseClosedLoopQualityDesc:Quality inspection events leading to decisions and actions – block, rework, rebuild, conditional release – with feedback to MES/ERP/Analytics.`,
      actions: [
        $localize`:@@dspUseCaseClosedLoopQualityH1:Inspection result as quality event`,
        $localize`:@@dspUseCaseClosedLoopQualityH2:Context-enriched events (order, workpiece, station)`,
        $localize`:@@dspUseCaseClosedLoopQualityH3:Rules and policies for decisions`,
        $localize`:@@dspUseCaseClosedLoopQualityH4:Auditable feedback to target systems`,
      ],
      smartFactory: [
        $localize`:@@orbisUseCaseClosedLoopQualityDescription:Quality becomes manageable when inspection result → decision → action is implemented as a closed loop.`,
        $localize`:@@orbisUseCaseClosedLoopQualityHighlight1:AIQS and quality stations emit events with context.`,
        $localize`:@@orbisUseCaseClosedLoopQualityHighlight2:DSP Edge normalizes and enriches events for process-ready integration.`,
        $localize`:@@orbisUseCaseClosedLoopQualityHighlight3:Actions: block, rework, rebuild, conditional release – based on rules and context.`,
        $localize`:@@orbisUseCaseClosedLoopQualityHighlight4:Feedback to MES/ERP/Analytics for traceability and maintenance scheduling.`,
      ],
      icon: 'assets/svg/dsp/functions/edge-analytics.svg',
      conceptRoute: '/dsp/use-case/closed-loop-quality',
    },
    {
      id: 'predictive-maintenance',
      useCaseTitle: $localize`:@@dspUseCasePredictiveTitle:Predictive Maintenance`,
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
      conceptRoute: '/dsp/use-case/predictive-maintenance',
    },
    {
      id: 'process-optimization',
      useCaseTitle: $localize`:@@dspUseCaseOptimizationTitle:Process Optimization`,
      useCaseCode: 'UC-06',
      reference: $localize`:@@dspUseCaseOptimizationRef:UC-06: Process Optimization`,
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
      conceptRoute: '/dsp/use-case/process-optimization',
    },
  ];

  constructor(
    private readonly router: Router,
    private readonly languageService: LanguageService
  ) {}

  setActiveUseCase(id: string): void {
    this.activeUseCaseId = id;
  }

  /**
   * Double-click opens Concept (same as DR-22 primary entry)
   */
  onUseCaseDoubleClick(useCase: UseCase): void {
    if (!this.enableNavigation || !useCase.conceptRoute) {
      return;
    }
    this.navigateToConcept(useCase);
  }

  navigateToConcept(useCase: UseCase): void {
    const path = useCase.conceptRoute;
    if (!path) {
      return;
    }
    this.persistDspReturnSectionForBack();
    const locale = this.languageService.current;
    const routeParts = path.split('/').filter(Boolean);
    const extras =
      useCase.id === 'track-trace' && useCase.liveDemoRoute
        ? { queryParams: { tab: 'concept' } }
        : {};
    void this.router.navigate([locale, ...routeParts], extras);
  }

  navigateToLive(useCase: UseCase): void {
    const path = useCase.liveDemoRoute;
    if (!path) {
      return;
    }
    this.persistDspReturnSectionForBack();
    const locale = this.languageService.current;
    const routeParts = path.split('/').filter(Boolean);
    void this.router.navigate([locale, ...routeParts], { queryParams: { tab: 'live' } });
  }

  private persistDspReturnSectionForBack(): void {
    try {
      if (typeof sessionStorage === 'undefined') {
        return;
      }
      if (this.recordDspReturnSection && isDspAccordionSectionId(this.recordDspReturnSection)) {
        sessionStorage.setItem(DSP_RETURN_SECTION_SESSION_KEY, this.recordDspReturnSection);
      } else {
        sessionStorage.removeItem(DSP_RETURN_SECTION_SESSION_KEY);
      }
    } catch {
      // ignore quota / private mode
    }
  }

  /**
   * Concept and/or Live Demo navigation available
   */
  hasDetailPage(useCase: UseCase): boolean {
    return !!(useCase.conceptRoute || useCase.liveDemoRoute);
  }

  trackById(_index: number, useCase: UseCase): string {
    return useCase.id;
  }

  getDetailLabel(useCase: UseCase): string {
    return useCase.useCaseCode ? `${USE_CASE_LABEL} ${useCase.useCaseCode}` : USE_CASE_LABEL;
  }

  get activeUseCase(): UseCase | undefined {
    return this.useCases.find((uc) => uc.id === this.activeUseCaseId);
  }
}
