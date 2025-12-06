import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';

interface EdgeBox {
  id: 'disc' | 'router' | 'agent' | 'app-server' | 'log-server' | 'disi' | 'db' | 'event-bus';
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface EdgeConnection {
  from: EdgeBox['id'];
  to: EdgeBox['id'];
  bidirectional?: boolean;
}

/**
 * DSP Edge Architecture Component
 * 
 * Displays a static diagram showing the internal structure of the DSP Edge,
 * including components (DISC, DISI, Router, Agent, etc.) and their connections.
 * This provides a "Structure View" complementing the "Legend View" of edge-components.
 */
@Component({
  standalone: true,
  selector: 'app-edge-architecture',
  imports: [CommonModule],
  templateUrl: './edge-architecture.component.html',
  styleUrl: './edge-architecture.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EdgeArchitectureComponent {
  readonly sectionTitle = $localize`:@@edgeArchitectureTitle:DSP Edge Architecture`;
  readonly sectionSubtitle = $localize`:@@edgeArchitectureSubtitle:How DISC, DISI, router, agents and services interact inside the Edge.`;
  readonly caption = $localize`:@@edgeArchitectureCaption:Edge processes and routes events between shopfloor devices and business systems using DISC, DISI, router, agents, logging and local storage.`;

  // SVG viewBox dimensions
  readonly viewBox = '0 0 1200 500';
  
  // Edge container box (main green box)
  readonly edgeContainer = {
    x: 50,
    y: 50,
    width: 1100,
    height: 400,
  };

  // Component boxes inside the Edge
  readonly edgeBoxes: EdgeBox[] = [
    // Top row: DISC (centered)
    {
      id: 'disc',
      label: 'DISC',
      x: 500,
      y: 100,
      width: 200,
      height: 60,
    },
    // Middle row: App Server, Router, Agent
    {
      id: 'app-server',
      label: 'App Server',
      x: 200,
      y: 200,
      width: 160,
      height: 60,
    },
    {
      id: 'router',
      label: 'Router',
      x: 520,
      y: 200,
      width: 160,
      height: 60,
    },
    {
      id: 'agent',
      label: 'Agent',
      x: 840,
      y: 200,
      width: 160,
      height: 60,
    },
    // Bottom row: Log Server, DISI, Edge DB, Event Bus
    {
      id: 'log-server',
      label: 'Log Server',
      x: 120,
      y: 320,
      width: 140,
      height: 60,
    },
    {
      id: 'disi',
      label: 'DISI',
      x: 380,
      y: 320,
      width: 140,
      height: 60,
    },
    {
      id: 'db',
      label: 'Edge Database',
      x: 640,
      y: 320,
      width: 140,
      height: 60,
    },
    {
      id: 'event-bus',
      label: 'Event Bus',
      x: 900,
      y: 320,
      width: 140,
      height: 60,
    },
  ];

  // Connections between components
  readonly connections: EdgeConnection[] = [
    { from: 'disc', to: 'router', bidirectional: true },
    { from: 'router', to: 'agent', bidirectional: true },
    { from: 'app-server', to: 'router', bidirectional: true },
    { from: 'log-server', to: 'router', bidirectional: true },
    { from: 'disi', to: 'router', bidirectional: true },
    { from: 'router', to: 'db', bidirectional: true },
    { from: 'router', to: 'event-bus', bidirectional: true },
  ];

  /**
   * Get center point of a box for connection lines
   */
  getBoxCenter(boxId: EdgeBox['id']): { x: number; y: number } {
    const box = this.edgeBoxes.find(b => b.id === boxId);
    if (!box) return { x: 0, y: 0 };
    return {
      x: box.x + box.width / 2,
      y: box.y + box.height / 2,
    };
  }

  /**
   * Generate SVG path for a connection between two boxes
   */
  getConnectionPath(connection: EdgeConnection): string {
    const from = this.getBoxCenter(connection.from);
    const to = this.getBoxCenter(connection.to);
    
    // Simple straight line for now
    return `M ${from.x} ${from.y} L ${to.x} ${to.y}`;
  }

  /**
   * Get connection points at the edge of boxes (for cleaner arrow placement)
   */
  getConnectionPoints(connection: EdgeConnection): { x1: number; y1: number; x2: number; y2: number } {
    const fromBox = this.edgeBoxes.find(b => b.id === connection.from);
    const toBox = this.edgeBoxes.find(b => b.id === connection.to);
    
    if (!fromBox || !toBox) return { x1: 0, y1: 0, x2: 0, y2: 0 };

    const fromCenter = this.getBoxCenter(connection.from);
    const toCenter = this.getBoxCenter(connection.to);

    // Calculate intersection points with box edges
    const dx = toCenter.x - fromCenter.x;
    const dy = toCenter.y - fromCenter.y;
    const angle = Math.atan2(dy, dx);

    // From box edge point
    const fromEdge = this.getEdgePoint(fromBox, angle);
    // To box edge point (opposite direction)
    const toEdge = this.getEdgePoint(toBox, angle + Math.PI);

    return {
      x1: fromEdge.x,
      y1: fromEdge.y,
      x2: toEdge.x,
      y2: toEdge.y,
    };
  }

  /**
   * Get point on box edge at given angle from center
   */
  private getEdgePoint(box: EdgeBox, angle: number): { x: number; y: number } {
    const centerX = box.x + box.width / 2;
    const centerY = box.y + box.height / 2;
    const halfWidth = box.width / 2;
    const halfHeight = box.height / 2;

    // Normalize angle to 0-2π
    const normalizedAngle = ((angle % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);

    // Determine which edge to intersect
    const cos = Math.cos(normalizedAngle);
    const sin = Math.sin(normalizedAngle);

    // Check intersection with each edge
    const t = Math.min(
      Math.abs(halfWidth / cos),
      Math.abs(halfHeight / sin)
    );

    return {
      x: centerX + t * cos,
      y: centerY + t * sin,
    };
  }
}
