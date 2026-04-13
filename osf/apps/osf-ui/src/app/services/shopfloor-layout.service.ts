import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, from, map, of, shareReplay, switchMap, tap } from 'rxjs';
import { getAssetPath } from '../assets/detail-asset-map';
import type { ShopfloorLayoutConfig } from '../components/shopfloor-preview/shopfloor-layout.types';
import { ShopfloorMappingService } from './shopfloor-mapping.service';

export interface ShopfloorLayoutSnapshot {
  config: ShopfloorLayoutConfig | null;
  /** SHA-256 hash of the raw JSON payload (hex). Null when not available. */
  hash: string | null;
  /** Resolved URL used to load the layout. */
  url: string;
}

@Injectable({ providedIn: 'root' })
export class ShopfloorLayoutService {
  private readonly http = inject(HttpClient);
  private readonly mappingService = inject(ShopfloorMappingService);

  readonly snapshot$: Observable<ShopfloorLayoutSnapshot> = this.loadLayout().pipe(
    tap((snapshot) => {
      if (snapshot.config) {
        this.mappingService.initializeLayout(snapshot.config);
      }
    }),
    shareReplay({ bufferSize: 1, refCount: false })
  );

  readonly config$ = this.snapshot$.pipe(map((s) => s.config));
  readonly hash$ = this.snapshot$.pipe(map((s) => s.hash));

  constructor() {
    // Trigger load eagerly so mapping is available even before tabs subscribe explicitly.
    this.snapshot$.subscribe();
  }

  private loadLayout(): Observable<ShopfloorLayoutSnapshot> {
    const url = getAssetPath('shopfloor/shopfloor_layout.json');
    return this.http.get<ShopfloorLayoutConfig>(url).pipe(
      switchMap((config) =>
        from(sha256Hex(JSON.stringify(config))).pipe(
          map((hash) => ({
            config,
            hash,
            url,
          }))
        )
      ),
      catchError((error) => {
        console.warn('[shopfloor-layout] Failed to load shopfloor layout:', error);
        return of({
          config: null,
          hash: null,
          url,
        });
      })
    );
  }
}

async function sha256Hex(text: string): Promise<string | null> {
  try {
    const subtle = globalThis.crypto?.subtle;
    if (!subtle) {
      return null;
    }
    const bytes = new TextEncoder().encode(text);
    const digest = await subtle.digest('SHA-256', bytes);
    const arr = Array.from(new Uint8Array(digest));
    return arr.map((b) => b.toString(16).padStart(2, '0')).join('');
  } catch {
    return null;
  }
}

