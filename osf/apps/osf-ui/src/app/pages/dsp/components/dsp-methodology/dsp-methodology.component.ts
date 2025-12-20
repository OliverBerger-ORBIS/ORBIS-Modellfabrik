import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

interface Phase {
  id: string;
  number: number;
  title: string;
  summary: string;
  activities: string[];
  outcome: string;
  icon: string;
  isAutonomousAdaptive: boolean;
}

/**
 * DSP Methodology Component
 * 
 * Displays the 5-phase DSP implementation methodology with special
 * emphasis on Phase 5 (Autonomous & Adaptive Enterprise).
 */
@Component({
  standalone: true,
  selector: 'app-dsp-methodology',
  imports: [CommonModule],
  templateUrl: './dsp-methodology.component.html',
  styleUrl: './dsp-methodology.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspMethodologyComponent {
  readonly sectionTitle = $localize`:@@dspMethodologyTitle:DSP Implementation Methodology`;
  readonly sectionSubtitle = $localize`:@@dspMethodologySubtitle:A structured 5-phase approach from data foundation to AI-driven autonomous operations.`;

  phases: Phase[] = [
    {
      id: 'phase1',
      number: 1,
      title: $localize`:@@dspPhase1TitleNew:Data Foundation & Connectivity`,
      summary: $localize`:@@dspPhase1SummaryNew:Connectivity & Signal Acquisition`,
      activities: [
        $localize`:@@dspPhase1Activity1:Connect machines, sensors, ERP, MES, and quality systems`,
        $localize`:@@dspPhase1Activity2:Standardize data via OPC UA, MQTT, and ISA-95`,
        $localize`:@@dspPhase1Activity3:Build data lake architecture (Azure Data Lake, SAP Edge, IoT Hub)`,
        $localize`:@@dspPhase1Activity4:Ensure secure, scalable data ingestion pipelines`,
      ],
      outcome: $localize`:@@dspPhase1Outcome:End-to-end visibility and data availability`,
      icon: 'assets/svg/dsp/methodology/phase1-data-foundation.svg',
      isAutonomousAdaptive: false,
    },
    {
      id: 'phase2',
      number: 2,
      title: $localize`:@@dspPhase2TitleNew:Data Integration & Modeling`,
      summary: $localize`:@@dspPhase2SummaryNew:Digital Twin & Semantic Data Model`,
      activities: [
        $localize`:@@dspPhase2Activity1:Combine OT + IT data into a single semantic layer`,
        $localize`:@@dspPhase2Activity2:Establish master data management and governance`,
        $localize`:@@dspPhase2Activity3:Model production, inventory, and quality data relationships`,
        $localize`:@@dspPhase2Activity4:Deploy SAP Datasphere, Azure Synapse, or Databricks for harmonization`,
      ],
      outcome: $localize`:@@dspPhase2Outcome:Trusted, consistent single source of truth`,
      icon: 'assets/svg/dsp/methodology/phase2-data-integration.svg',
      isAutonomousAdaptive: false,
    },
    {
      id: 'phase3',
      number: 3,
      title: $localize`:@@dspPhase3TitleNew:Advanced Analytics & Intelligence`,
      summary: $localize`:@@dspPhase3SummaryNew:Real-time Dashboards & Predictive Analytics`,
      activities: [
        $localize`:@@dspPhase3Activity1:Implement real-time dashboards and KPI monitoring (e.g., Power BI, SAP Analytics Cloud).`,
        $localize`:@@dspPhase3Activity2:Develop predictive models for maintenance, quality, and demand forecasting.`,
        $localize`:@@dspPhase3Activity3:Enable self-service analytics for business users to find patterns.`,
        $localize`:@@dspPhase3Activity4:Apply Machine Learning algorithms to identify anomalies in production data.`,
      ],
      outcome: $localize`:@@dspPhase3Outcome:Data-driven decision making, predictive insights, and transparency.`,
      icon: 'assets/svg/dsp/methodology/phase3-advanced-analytics.svg',
      isAutonomousAdaptive: false,
    },
    {
      id: 'phase4',
      number: 4,
      title: $localize`:@@dspPhase4TitleNew:Automation & Orchestration`,
      summary: $localize`:@@dspPhase4SummaryNew:Process Objects, Decentralized Orchestration`,
      activities: [
        $localize`:@@dspPhase4Activity1:Connect analytics outputs to workflows and RPA bots`,
        $localize`:@@dspPhase4Activity2:Automate repetitive tasks across SAP and Azure ecosystems`,
        $localize`:@@dspPhase4Activity3:Use event-driven triggers for maintenance, quality, or logistics actions`,
        $localize`:@@dspPhase4Activity4:Deploy Power Automate, SAP Build Process Automation, Logic Apps`,
      ],
      outcome: $localize`:@@dspPhase4Outcome:Closed-loop automation, faster reaction time, reduced manual effort`,
      icon: 'assets/svg/dsp/methodology/phase4-automation-orchestration.svg',
      isAutonomousAdaptive: false,
    },
    {
      id: 'phase5',
      number: 5,
      title: $localize`:@@dspPhase5Title:Autonomous & Adaptive Enterprise`,
      summary: $localize`:@@dspPhase5Summary:Autonomous Decisions, ML/AI, Data Lake + ERP + Edge Integration`,
      activities: [
        $localize`:@@dspPhase5Activity1:Deploy agentic AI to reason, plan, and act autonomously`,
        $localize`:@@dspPhase5Activity2:Integrate digital twins, LLMs, and reinforcement learning`,
        $localize`:@@dspPhase5Activity3:Continuously self-optimize production, energy, and supply chain flows`,
        $localize`:@@dspPhase5Activity4:Enable AI copilots for operators, planners, and engineers`,
      ],
      outcome: $localize`:@@dspPhase5Outcome:Self-learning, adaptive, intelligent manufacturing enterprise`,
      icon: 'assets/svg/dsp/methodology/phase5-autonomous-enterprise.svg',
      isAutonomousAdaptive: true,
    },
  ];

  activePhaseId = 'phase1';

  setActive(phaseId: string): void {
    this.activePhaseId = phaseId;
  }

  get activePhase(): Phase | undefined {
    return this.phases.find((p) => p.id === this.activePhaseId);
  }

  trackById(_index: number, phase: Phase): string {
    return phase.id;
  }
}
