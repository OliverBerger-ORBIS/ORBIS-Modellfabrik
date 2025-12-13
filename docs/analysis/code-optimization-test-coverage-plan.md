# Code-Optimierung & Test-Abdeckung Plan

**Erstellt:** 2025-11-30  
**Status Update:** 2025-12-13 - Viele Punkte bereits umgesetzt  
**Fokus:** Code-Optimierung und Test-Abdeckung (Security Issues sekundär)  
**Aktueller Stand:** 49% Test Coverage (Original), 8/10 Code Quality

**⚠️ WICHTIG:** Siehe [Status Update](code-optimization-test-coverage-plan-status.md) für aktuelle Umsetzung

---

## 📊 Aktuelle Situation

### Test Coverage
- **Lines:** 49.29% (Ziel: 60%+)
- **Branches:** 16.97% (Ziel: 40%+)
- **Test-Dateien:** 4 von 40 TypeScript-Dateien haben Tests
- **Gap:** 36 Dateien ohne Tests

### Code Quality
- **Score:** 8/10 ✅
- **OnPush:** 100% (15/15 Components) ✅
- **TypeScript Strict:** ✅
- **Memory Leaks:** 3 unmanaged subscriptions in AppComponent ❌
- **Build Issues:** Gateway library TypeScript config ❌

---

## 🎯 Strategischer Plan

### Phase 1: Kritische Code-Optimierungen (Woche 1)
**Ziel:** Behebung von Memory Leaks und Build-Issues

### Phase 2: Test-Abdeckung Basis (Woche 2-3)
**Ziel:** Erreichen von 60% Line Coverage durch systematische Test-Erstellung

### Phase 3: Code-Optimierung & Refactoring (Woche 4-5)
**Ziel:** Performance-Optimierungen und Code-Qualität verbessern

### Phase 4: Erweiterte Test-Abdeckung (Woche 6-7)
**Ziel:** Branch Coverage auf 40%+ erhöhen, Edge Cases abdecken

---

## 🔴 Phase 1: Kritische Code-Optimierungen (Woche 1)

### 1.1 Memory Leaks beheben (2-3 Stunden)

**Problem:** 3 unmanaged subscriptions in AppComponent

**Datei:** `omf3/apps/ccu-ui/src/app/app.component.ts`

**Fix:**
```typescript
// Vorher (Zeilen 157-171)
constructor() {
  this.subscriptions.add(
    this.languageService.locale$.subscribe((locale) => {
      this.currentLocale = locale;
    })
  );

  // ❌ Nicht in subscriptions.add()
  this.environmentService.environment$.subscribe((environment) => {
    this.currentEnvironment = environment;
  });

  this.roleService.role$.subscribe((role) => {
    this.currentRole = role;
  });

  this.connectionService.state$.subscribe((state) => {
    this.connectionState = state;
  });
}

// Nachher
constructor() {
  this.subscriptions.add(
    this.languageService.locale$.subscribe((locale) => {
      this.currentLocale = locale;
    })
  );

  // ✅ Alle Subscriptions werden verwaltet
  this.subscriptions.add(
    this.environmentService.environment$.subscribe((environment) => {
      this.currentEnvironment = environment;
    })
  );

  this.subscriptions.add(
    this.roleService.role$.subscribe((role) => {
      this.currentRole = role;
    })
  );

  this.subscriptions.add(
    this.connectionService.state$.subscribe((state) => {
      this.connectionState = state;
    })
  );
}
```

**Effort:** 30 Minuten  
**Impact:** ✅ Verhindert Memory Leaks in langen Sessions

---

### 1.2 Gateway Library Build Issue beheben (1-2 Stunden)

**Problem:** TypeScript build error in gateway library

**Datei:** `omf3/libs/gateway/tsconfig.lib.json`

**Fix:**
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "../../../dist/out-tsc"
    // Entferne "rootDir": "." wenn vorhanden
  }
}
```

**Effort:** 1-2 Stunden  
**Impact:** ✅ Ermöglicht Production Builds

---

### 1.3 ESLint Rules verschärfen (1-2 Stunden)

**Ziel:** Proaktive Erkennung von Code-Qualitätsproblemen

**Datei:** `omf3/apps/ccu-ui/eslint.config.js`

**Hinzufügen:**
```javascript
rules: {
  // Bestehende Rules...
  
  // Subscription Management
  'rxjs/no-ignored-subscription': 'error',
  'rxjs/no-unused-subscribe': 'error',
  
  // Type Safety
  '@typescript-eslint/no-explicit-any': 'warn', // Aktuell 1 usage
  '@typescript-eslint/explicit-function-return-type': ['warn', {
    allowExpressions: true,
    allowTypedFunctionExpressions: true
  }],
  
  // Angular Best Practices
  '@angular-eslint/prefer-on-push-component-change-detection': 'error',
}
```

**Effort:** 1-2 Stunden  
**Impact:** ✅ Verhindert zukünftige Memory Leaks durch Linting

---

## 🟠 Phase 2: Test-Abdeckung Basis (Woche 2-3)

**Ziel:** 60% Line Coverage erreichen

### 2.1 Service Tests (Priorität 1) - 8-10 Stunden

#### ConnectionService (Aktuell: ~30% Coverage)

**Datei:** `omf3/apps/ccu-ui/src/app/services/connection.service.spec.ts`

**Fehlende Tests:**
```typescript
describe('ConnectionService', () => {
  describe('Retry Logic', () => {
    it('should retry connection on failure when retryEnabled is true', async () => {
      // Test retry mechanism
    });
    
    it('should not retry when retryEnabled is false', async () => {
      // Test no retry
    });
    
    it('should respect retryIntervalMs setting', async () => {
      // Test retry timing
    });
  });

  describe('Error Handling', () => {
    it('should emit error state when connection fails', () => {
      // Test error emission
    });
    
    it('should clear error on successful connection', () => {
      // Test error clearing
    });
  });

  describe('Subscription Management', () => {
    it('should unsubscribe from MQTT on disconnect', () => {
      // Test cleanup
    });
    
    it('should resubscribe to topics after reconnection', () => {
      // Test reconnection
    });
  });
});
```

**Effort:** 4-6 Stunden  
**Coverage Impact:** +15-20%

---

#### EnvironmentService, LanguageService, RoleService

**Datei:** `omf3/apps/ccu-ui/src/app/services/*.spec.ts` (neu erstellen)

**Basis-Tests für jeden Service:**
```typescript
describe('EnvironmentService', () => {
  it('should provide default environment', () => {});
  it('should update environment on change', () => {});
  it('should persist environment to localStorage', () => {});
});

describe('LanguageService', () => {
  it('should provide default locale', () => {});
  it('should update locale on change', () => {});
  it('should persist locale to localStorage', () => {});
});

describe('RoleService', () => {
  it('should provide default role', () => {});
  it('should update role on change', () => {});
});
```

**Effort:** 4-6 Stunden  
**Coverage Impact:** +10-15%

---

### 2.2 View Component Tests (Priorität 2) - 6-8 Stunden

**Aktuell:** 0% Coverage für View Components

**Zu testende Components:**
- `orders-view.component.ts`
- `fts-view.component.ts`
- `stock-view.component.ts`
- `module-map.component.ts`

**Basis-Test-Template:**
```typescript
describe('OrdersViewComponent', () => {
  let component: OrdersViewComponent;
  let fixture: ComponentFixture<OrdersViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrdersViewComponent],
      providers: [
        // Mock DashboardController
        {
          provide: 'DASHBOARD_CONTROLLER',
          useValue: {
            streams: {
              orders$: of([]),
            },
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OrdersViewComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display order cards from stream', () => {
    // Test order rendering
  });

  it('should handle empty orders list', () => {
    // Test empty state
  });

  it('should filter orders by status', () => {
    // Test filtering
  });
});
```

**Effort:** 6-8 Stunden (1.5-2h pro Component)  
**Coverage Impact:** +10-15%

---

### 2.3 Tab Component Tests (Priorität 3) - 8-10 Stunden

**Zu testende Tabs:**
- `order-tab.component.ts` ✅
- `process-tab.component.ts` ✅
- `sensor-tab.component.ts` ✅
- `module-tab.component.ts` ✅
- `configuration-tab.component.ts` ✅
- `message-monitor-tab.component.ts` ✅
- `settings-tab.component.ts` ✅
- `fts-tab.component.ts` ✅ **2025-12-13**
- `track-trace-tab.component.ts` ✅ **2025-12-13** (direct-access, nicht in Navigation)
- `dsp-action-tab.component.ts` ✅ (direct-access, nicht in Navigation)

**Wichtige Test-Aspekte:**
```typescript
describe('OrderTabComponent', () => {
  it('should initialize streams on construction', () => {
    // Test Tab Stream Pattern
  });

  it('should use refCount: false pattern', () => {
    // Test RxJS pattern compliance
  });

  it('should display orders from dashboard', () => {
    // Test data flow
  });

  it('should handle stream errors gracefully', () => {
    // Test error handling
  });
});
```

**Effort:** 8-10 Stunden (1-1.5h pro Tab)  
**Coverage Impact:** +10-12%

**Status:** ✅ **ABGESCHLOSSEN** (2025-12-13)
- Alle Tab Components haben Tests
- Direct-access Pages (nicht in Navigation) haben Tests:
  - `fts-tab.component.spec.ts` ✅
  - `track-trace-tab.component.spec.ts` ✅
  - `dsp-action-tab.component.spec.ts` ✅
  - `presentation-page.component.spec.ts` ✅
  - `dsp-architecture.component.spec.ts` ✅

---

### 2.4 Test Coverage Monitoring Setup (1-2 Stunden)

**Ziel:** Automatisches Monitoring der Test-Abdeckung

**Datei:** `omf3/apps/ccu-ui/jest.config.ts`

**Erweitern:**
```typescript
export default {
  coverageThreshold: {
    global: {
      branches: 40,
      functions: 60,
      lines: 60,
      statements: 60,
    },
  },
  collectCoverageFrom: [
    'src/app/**/*.ts',
    '!src/app/**/*.spec.ts',
    '!src/app/**/*.mock.ts',
    '!src/app/**/__tests__/**',
  ],
};
```

**CI/CD Integration:**
```yaml
# .github/workflows/test-coverage.yml
- name: Test Coverage
  run: |
    npm run test:coverage
    npm run test:coverage:check
```

**Effort:** 1-2 Stunden  
**Impact:** ✅ Kontinuierliches Monitoring

---

## 🟡 Phase 3: Code-Optimierung & Refactoring (Woche 4-5)

### 3.1 Lazy Loading implementieren (2-3 Stunden)

**Ziel:** Reduzierung der initialen Bundle-Größe

**Datei:** `omf3/apps/ccu-ui/src/app/app.routes.ts`

**Implementation:**
```typescript
export const routes: Routes = [
  {
    path: 'order',
    loadComponent: () => import('./tabs/order-tab.component')
      .then(m => m.OrderTabComponent)
  },
  {
    path: 'process',
    loadComponent: () => import('./tabs/process-tab.component')
      .then(m => m.ProcessTabComponent)
  },
  // ... weitere Tabs
];
```

**Effort:** 2-3 Stunden  
**Impact:** ✅ -20-30% initial bundle size

---

### 3.2 Test Fixtures aus Production Build entfernen (1 Stunde)

**Datei:** `omf3/apps/ccu-ui/project.json`

**Fix:**
```json
{
  "configurations": {
    "production": {
      "assets": [
        { "glob": "**/*", "input": "omf3/apps/ccu-ui/public" }
        // Keine Fixtures in Production
      ]
    },
    "development": {
      "assets": [
        { "glob": "**/*", "input": "omf3/apps/ccu-ui/public" },
        { "glob": "**/*.log", "input": "omf3/testing/fixtures/orders", "output": "fixtures/orders" }
        // Fixtures nur in Development
      ]
    }
  }
}
```

**Effort:** 1 Stunde  
**Impact:** ✅ -2-5 MB production bundle

---

### 3.3 Service Refactoring (4-6 Stunden)

**Ziel:** Komplexe Services aufteilen und testbarer machen

**Kandidaten:**
- `MessageMonitorService` (384 Zeilen) - Aufteilen in:
  - `MessageMonitorService` (Core)
  - `MessagePersistenceService` (LocalStorage)
  - `MessageValidationService` (Schema validation)

**Effort:** 4-6 Stunden  
**Impact:** ✅ Bessere Testbarkeit, Single Responsibility

---

## 🟢 Phase 4: Erweiterte Test-Abdeckung (Woche 6-7)

### 4.1 Branch Coverage erhöhen (6-8 Stunden)

**Ziel:** 40%+ Branch Coverage

**Fokus auf:**
- Error Handling Paths
- Conditional Logic
- Edge Cases

**Beispiel:**
```typescript
describe('MessageMonitorService - Edge Cases', () => {
  it('should handle null payload gracefully', () => {});
  it('should handle invalid JSON payload', () => {});
  it('should handle missing schema gracefully', () => {});
  it('should handle localStorage quota exceeded', () => {});
});
```

**Effort:** 6-8 Stunden  
**Coverage Impact:** +15-20% branches

---

### 4.2 Integration Tests (4-6 Stunden)

**Ziel:** Component-Service Integration testen

**Beispiel:**
```typescript
describe('OrderTabComponent Integration', () => {
  it('should display orders from MessageMonitorService', () => {
    // Test full data flow
  });

  it('should update when new order arrives', () => {
    // Test reactive updates
  });
});
```

**Effort:** 4-6 Stunden  
**Coverage Impact:** +5-10%

---

## 📈 Erwartete Ergebnisse

### Nach Phase 1 (Woche 1)
- ✅ Keine Memory Leaks mehr
- ✅ Production Build funktioniert
- ✅ ESLint Rules verschärft

### Nach Phase 2 (Woche 3)
- ✅ **60%+ Line Coverage** erreicht
- ✅ Alle Services getestet
- ✅ View Components getestet
- ✅ Tab Components getestet

### Nach Phase 3 (Woche 5)
- ✅ -20-30% Bundle Size
- ✅ Services refactored
- ✅ Production Build optimiert

### Nach Phase 4 (Woche 7)
- ✅ **40%+ Branch Coverage** erreicht
- ✅ Edge Cases abgedeckt
- ✅ Integration Tests vorhanden

---

## 📋 Checkliste

### Phase 1: Code-Optimierung
- [x] Memory Leaks in AppComponent beheben ✅
- [ ] Gateway Library Build Issue beheben ⚠️ Zu prüfen
- [ ] ESLint Rules verschärfen ⚠️ Zu prüfen

### Phase 2: Test-Abdeckung Basis
- [x] ConnectionService Tests (4-6h) ✅
- [x] EnvironmentService Tests (1-2h) ✅
- [x] LanguageService Tests (1-2h) ✅
- [x] RoleService Tests (1-2h) ✅
- [x] OrdersViewComponent Tests (1.5-2h) ✅
- [x] FtsViewComponent Tests (1.5-2h) ✅
- [x] StockViewComponent Tests (1.5-2h) ✅
- [x] ModuleMapComponent Tests (1.5-2h) ✅
- [x] OrderTabComponent Tests (1-1.5h) ✅
- [x] ProcessTabComponent Tests (1-1.5h) ✅
- [x] SensorTabComponent Tests (1-1.5h) ✅
- [x] ModuleTabComponent Tests (1-1.5h) ✅
- [x] ConfigurationTabComponent Tests (1-1.5h) ✅
- [x] MessageMonitorTabComponent Tests (1-1.5h) ✅
- [x] SettingsTabComponent Tests (1-1.5h) ✅
- [x] Coverage Monitoring Setup (1-2h) ✅ **2025-12-13**

### Phase 3: Code-Optimierung
- [ ] Lazy Loading implementieren ⚠️ Zu prüfen
- [ ] Test Fixtures aus Production entfernen ⚠️ Zu prüfen
- [x] MessageMonitorService refactoring ✅

### Phase 4: Erweiterte Tests
- [ ] Branch Coverage Tests
- [ ] Edge Case Tests
- [ ] Integration Tests

---

## 🎯 Priorisierung

### Must-Have (Sprint 1-2)
1. Memory Leaks beheben
2. Gateway Build Issue beheben
3. Service Tests (ConnectionService, EnvironmentService, etc.)
4. View Component Tests

### Should-Have (Sprint 3-4)
5. Tab Component Tests
6. Lazy Loading
7. Test Fixtures aus Production entfernen

### Nice-to-Have (Sprint 5+)
8. Service Refactoring
9. Branch Coverage erhöhen
10. Integration Tests

---

## 📊 Zeitaufwand Übersicht

| Phase | Dauer | Aufwand | Priorität |
|-------|-------|---------|-----------|
| Phase 1: Code-Optimierung | 1 Woche | 4-7 Stunden | 🔴 Kritisch |
| Phase 2: Test-Abdeckung Basis | 2 Wochen | 22-30 Stunden | 🟠 Hoch |
| Phase 3: Code-Optimierung | 2 Wochen | 7-10 Stunden | 🟡 Mittel |
| Phase 4: Erweiterte Tests | 2 Wochen | 10-14 Stunden | 🟢 Niedrig |
| **Gesamt** | **7 Wochen** | **43-61 Stunden** | |

---

## 🔗 Verwandte Dokumente

- [Code Quality Report](./omf3-code-quality-report.md)
- [Optimization Suggestions](./omf3-optimization-suggestions.md)
- [Tab Stream Pattern](../../03-decision-records/11-tab-stream-initialization-pattern.md)

---

**Nächste Schritte:** Beginne mit Phase 1, Item 1.1 (Memory Leaks beheben)

