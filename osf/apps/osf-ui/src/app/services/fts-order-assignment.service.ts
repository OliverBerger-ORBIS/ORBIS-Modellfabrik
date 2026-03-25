import { Injectable, inject } from '@angular/core';
import { Observable, combineLatest, of, BehaviorSubject } from 'rxjs';
import { map, shareReplay, startWith } from 'rxjs/operators';
import { MessageMonitorService } from './message-monitor.service';
import { ShopfloorMappingService } from './shopfloor-mapping.service';

/** FTS order payload (from fts/v1/ff/<serial>/order) */
interface FtsOrderPayload {
  orderId?: string;
  nodes?: Array<{ id?: string; action?: { id?: string; type?: string }; linkedEdges?: string[] }>;
}

const FTS_SERIALS_FALLBACK = ['5iO4', 'IeJ4'];

/**
 * Derives orderId + stepId → ftsSerial mapping from fts/v1/ff/+/order messages.
 * Used to display AGV-1/AGV-2 per NAVIGATION step when CCU does not include serialNumber (Mod 3 removed).
 */
@Injectable({ providedIn: 'root' })
export class FtsOrderAssignmentService {
  private readonly messageMonitor = inject(MessageMonitorService);
  private readonly mappingService = inject(ShopfloorMappingService);

  private readonly assignmentsSubject = new BehaviorSubject<Map<string, Map<string, string>>>(new Map());
  private subscription = this.buildAssignmentsStream().subscribe((m) => this.assignmentsSubject.next(m));

  private buildAssignmentsStream(): Observable<Map<string, Map<string, string>>> {
    const ftsSerials = this.getFtsSerials();
    if (ftsSerials.length === 0) {
      return of(new Map());
    }
    const orderStreams = ftsSerials.map((serial) =>
      this.messageMonitor.getLastMessage<unknown>(`fts/v1/ff/${serial}/order`).pipe(
        startWith(null),
        map(() => ({ serial, histories: this.messageMonitor.getHistory(`fts/v1/ff/${serial}/order`) }))
      )
    );
    return combineLatest(orderStreams).pipe(
      map((results) => {
        const map = new Map<string, Map<string, string>>();
        for (const { serial, histories } of results) {
          for (const msg of histories) {
            if (!msg?.valid || !msg?.payload) continue;
            const { orderId, stepId } = this.parseFtsOrder(msg.payload as FtsOrderPayload);
            if (orderId && stepId) {
              if (!map.has(orderId)) {
                map.set(orderId, new Map());
              }
              map.get(orderId)!.set(stepId, serial);
            }
          }
        }
        return map;
      }),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  private getFtsSerials(): string[] {
    const opts = this.mappingService.getAgvOptions();
    return opts.length > 0 ? opts.map((o) => o.serial) : FTS_SERIALS_FALLBACK;
  }

  /** Extract orderId and stepId (NAV step id) from FTS order payload. stepId = last node with action.id */
  private parseFtsOrder(payload: FtsOrderPayload): { orderId: string | null; stepId: string | null } {
    const orderId = payload.orderId ?? null;
    const nodes = payload.nodes ?? [];
    let stepId: string | null = null;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const node = nodes[i];
      const actionId = node?.action?.id;
      if (actionId) {
        stepId = actionId;
        break;
      }
    }
    return { orderId, stepId };
  }

  /** Get FTS serial for a NAVIGATION step synchronously, or null if not assigned yet. */
  getFtsSerialForStep(orderId: string | undefined, stepId: string | undefined): string | null {
    if (!orderId || !stepId) return null;
    return this.assignmentsSubject.value.get(orderId)?.get(stepId) ?? null;
  }

  /**
   * Observable of FTS serial for a given (orderId, stepId).
   * Use for reactive binding when assignment may arrive after initial render.
   */
  getFtsSerialForStep$(orderId: string | undefined, stepId: string | undefined): Observable<string | null> {
    if (!orderId || !stepId) {
      return of(null);
    }
    return this.assignmentsSubject.pipe(
      map((m) => m.get(orderId)?.get(stepId) ?? null)
    );
  }

  /** Current assignments map for advanced use. */
  getAssignments$(): Observable<Map<string, Map<string, string>>> {
    return this.assignmentsSubject.asObservable();
  }
}
