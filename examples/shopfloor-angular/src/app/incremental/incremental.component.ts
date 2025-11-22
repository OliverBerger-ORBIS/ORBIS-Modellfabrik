import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface Phase {
  id: number;
  name: string;
  description: string;
  activities: string[];
  color: string;
}

@Component({
  selector: 'app-incremental',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './incremental.component.html',
  styleUrls: ['./incremental.component.scss']
})
export class IncrementalComponent {
  selectedPhase: Phase | null = null;

  phases: Phase[] = [
    {
      id: 1,
      name: 'Inception',
      description: 'Initial project setup and requirements gathering',
      activities: [
        'Define project vision and scope',
        'Identify key stakeholders',
        'Initial risk assessment',
        'Set up development environment',
        'Create project roadmap'
      ],
      color: '#4A90E2'
    },
    {
      id: 2,
      name: 'Elaboration',
      description: 'Detailed analysis and architecture design',
      activities: [
        'Detailed requirements analysis',
        'Architecture design and validation',
        'Identify and mitigate critical risks',
        'Create proof of concept',
        'Establish development infrastructure'
      ],
      color: '#7B68EE'
    },
    {
      id: 3,
      name: 'Construction',
      description: 'Iterative development and implementation',
      activities: [
        'Implement core features',
        'Continuous integration and testing',
        'Regular stakeholder reviews',
        'Iterative refinement',
        'Documentation updates'
      ],
      color: '#50C878'
    },
    {
      id: 4,
      name: 'Transition',
      description: 'Preparation for production deployment',
      activities: [
        'User acceptance testing',
        'Performance optimization',
        'User training and documentation',
        'Deployment preparation',
        'Beta testing and feedback'
      ],
      color: '#FFA500'
    },
    {
      id: 5,
      name: 'Production',
      description: 'Live operation and continuous improvement',
      activities: [
        'Monitor system performance',
        'Handle user feedback',
        'Bug fixes and patches',
        'Feature enhancements',
        'Ongoing support and maintenance'
      ],
      color: '#E74C3C'
    }
  ];

  selectPhase(phase: Phase): void {
    this.selectedPhase = this.selectedPhase?.id === phase.id ? null : phase;
  }

  getPhasePosition(index: number): { x: number; y: number } {
    const centerX = 300;
    const centerY = 200;
    const radius = 120;
    const angle = (index * 72 - 90) * (Math.PI / 180); // 72 degrees per phase (360/5), start at top
    
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    };
  }

  getConnectionPath(fromIndex: number, toIndex: number): string {
    const from = this.getPhasePosition(fromIndex);
    const to = this.getPhasePosition(toIndex);
    return `M ${from.x} ${from.y} L ${to.x} ${to.y}`;
  }
}
