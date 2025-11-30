# Risiko-Analyse: Mock-Environment vs. Fixtures entfernen

## 📊 Aktuelle Situation

**Aktueller Build:** `nx serve ccu-ui` (Development Build)  
**Production Build:** Nicht vorhanden  
**Ziel:** Production Build ohne Mock-Environment und Fixtures

## 🔍 Option 1: Nur Fixtures entfernen (Mock-Environment bleibt)

### Implementierung

**Datei:** `omf3/apps/ccu-ui/project.json`

```json
{
  "targets": {
    "build": {
      "configurations": {
        "production": {
          "assets": [
            {
              "glob": "**/*",
              "input": "omf3/apps/ccu-ui/public"
            }
            // Fixtures werden hier entfernt
          ]
        },
        "development": {
          "assets": [
            {
              "glob": "**/*",
              "input": "omf3/apps/ccu-ui/public"
            },
            // Fixtures bleiben für Development
            {
              "glob": "**/*.log",
              "input": "omf3/testing/fixtures/orders",
              "output": "fixtures/orders"
            }
            // ... weitere Fixtures
          ]
        }
      }
    }
  }
}
```

### ✅ Vorteile

1. **Einfache Implementierung:** Nur `project.json` ändern
2. **Mock-Environment bleibt:** Entwicklung weiterhin möglich
3. **Keine Code-Änderungen:** Alle `isMockMode` Checks bleiben
4. **Sicher:** Keine Breaking Changes

### ⚠️ Risiken

#### 🟢 **Niedrige Risiken**

1. **Mock-Environment ohne Fixtures**
   - **Risiko:** ⚠️ Niedrig
   - **Beschreibung:** Mock-Environment kann keine Fixtures laden
   - **Impact:** Mock-Environment funktioniert nicht mehr
   - **Mitigation:** 
     - Mock-Environment in Production Build deaktivieren
     - Oder: Mock-Environment zeigt leere/Fehler-State

2. **Bundle-Größe**
   - **Risiko:** ⚠️ Sehr niedrig
   - **Beschreibung:** Fixtures werden nicht in Bundle eingebunden
   - **Impact:** ✅ Kleinere Bundle-Größe (2-5 MB weniger)
   - **Mitigation:** Keine nötig, das ist das Ziel

#### 🟡 **Mittlere Risiken**

3. **Code-Referenzen auf Fixtures**
   - **Risiko:** ⚠️ Niedrig-Mittel
   - **Beschreibung:** Code könnte versuchen, Fixtures zu laden
   - **Impact:** Runtime-Fehler wenn Fixtures nicht gefunden werden
   - **Mitigation:**
     ```typescript
     // In mock-dashboard.ts oder Tab Components
     if (this.isMockMode && !this.fixturesAvailable) {
       console.warn('Fixtures not available in production build');
       return; // Graceful degradation
     }
     ```

4. **Tests könnten betroffen sein**
   - **Risiko:** ⚠️ Niedrig
   - **Beschreibung:** Tests die Fixtures verwenden könnten fehlschlagen
   - **Impact:** Tests müssen angepasst werden
   - **Mitigation:** Tests sollten Mocks verwenden, nicht echte Fixtures

### 📊 Code-Impact-Analyse

**Betroffene Dateien:**
- `omf3/apps/ccu-ui/project.json` (Assets-Konfiguration)
- Alle Tab Components mit `loadFixture()` Calls (9 Dateien)
- `omf3/apps/ccu-ui/src/app/mock-dashboard.ts` (Fixture-Loading-Logik)

**Code-Änderungen nötig:**
- ✅ Minimal: Nur `project.json` für Production Build
- ⚠️ Optional: Graceful Degradation wenn Fixtures fehlen

---

## 🔍 Option 2: Mock-Environment komplett entfernen

### Implementierung

**Datei:** `omf3/apps/ccu-ui/src/app/services/environment.service.ts`

```typescript
// Entfernen von 'mock' aus EnvironmentKey
export type EnvironmentKey = 'replay' | 'live'; // 'mock' entfernt

const DEFAULT_CONNECTIONS: Record<EnvironmentKey, EnvironmentConnection> = {
  // mock entfernt
  replay: { ... },
  live: { ... },
};

// In constructor:
this.definitions = {
  // mock entfernt
  replay: { ... },
  live: { ... },
};
```

**Zusätzlich:** Alle `isMockMode` Checks müssen angepasst werden.

### ✅ Vorteile

1. **Sauberer Code:** Keine Mock-Logik in Production
2. **Kleinere Bundle-Größe:** Mock-Code wird nicht eingebunden (Tree-Shaking)
3. **Klare Trennung:** Development vs. Production klar getrennt

### ⚠️ Risiken

#### 🔴 **Hohe Risiken**

1. **Breaking Changes in allen Tab Components**
   - **Risiko:** ⚠️ Hoch
   - **Beschreibung:** Alle 9 Tab Components haben `isMockMode` Checks
   - **Impact:** 
     - Code muss angepasst werden
     - Tests müssen angepasst werden
     - Mögliche Runtime-Fehler
   - **Betroffene Dateien:**
     ```
     - overview-tab.component.ts
     - order-tab.component.ts
     - process-tab.component.ts
     - sensor-tab.component.ts
     - configuration-tab.component.ts
     - module-tab.component.ts
     - message-monitor-tab.component.ts
     - dsp-action-tab.component.ts
     - settings-tab.component.ts
     ```
   - **Mitigation:**
     ```typescript
     // Statt:
     if (this.isMockMode) {
       void this.loadFixture(this.activeFixture);
     }
     
     // Option A: Conditional Compilation (komplex)
     // Option B: Environment-Variable Check
     if (environment.production === false && this.isMockMode) {
       void this.loadFixture(this.activeFixture);
     }
     ```

2. **Development-Workflow beeinträchtigt**
   - **Risiko:** ⚠️ Hoch
   - **Beschreibung:** Entwickler können nicht mehr mit Mock-Environment arbeiten
   - **Impact:** 
     - Entwicklung wird schwieriger
     - Neue Features können nicht getestet werden ohne echte MQTT-Verbindung
     - CI/CD Tests könnten betroffen sein
   - **Mitigation:**
     - Mock-Environment nur in Development Build behalten
     - Conditional Compilation verwenden

3. **Tests müssen angepasst werden**
   - **Risiko:** ⚠️ Mittel-Hoch
   - **Beschreibung:** Viele Tests verwenden `isMockMode` oder Mock-Environment
   - **Impact:** 
     - Tests müssen refactored werden
     - Mock-Services müssen angepasst werden
   - **Betroffene Tests:**
     - Alle Tab Component Tests (9 Dateien)
     - Service Tests die Mock-Environment verwenden
   - **Mitigation:**
     ```typescript
     // Tests müssen Mock-Environment anders mocken
     const environmentServiceMock = {
       current: { key: 'replay' }, // Statt 'mock'
       // ...
     };
     ```

4. **TypeScript Type Errors**
   - **Risiko:** ⚠️ Mittel
   - **Beschreibung:** `EnvironmentKey` Type ändert sich
   - **Impact:** 
     - TypeScript Compiler-Fehler
     - Alle Stellen die `'mock'` verwenden müssen angepasst werden
   - **Mitigation:**
     - TypeScript wird Fehler zeigen
     - Systematisches Refactoring nötig

#### 🟡 **Mittlere Risiken**

5. **AppComponent Initialisierung**
   - **Risiko:** ⚠️ Mittel
   - **Beschreibung:** `app.component.ts` initialisiert Dashboard Controller für Mock
   - **Impact:** 
     ```typescript
     // Aktuell:
     if (this.environmentService.current.key === 'mock') {
       getDashboardController(undefined, this.dashboardMessageMonitor);
     }
     ```
     - Muss angepasst werden
   - **Mitigation:**
     ```typescript
     // Entweder entfernen oder conditional:
     if (!environment.production && this.environmentService.current.key === 'mock') {
       getDashboardController(undefined, this.dashboardMessageMonitor);
     }
     ```

6. **Default Environment**
   - **Risiko:** ⚠️ Niedrig-Mittel
   - **Beschreibung:** `loadInitialEnvironment()` gibt `'mock'` als Default zurück
   - **Impact:** 
     ```typescript
     // Aktuell:
     return 'mock';
     
     // Muss geändert werden zu:
     return 'replay'; // oder 'live'
     ```
   - **Mitigation:** Einfach zu ändern

7. **Settings Tab**
   - **Risiko:** ⚠️ Niedrig
   - **Beschreibung:** Settings Tab zeigt Mock-Environment als readOnly
   - **Impact:** 
     - Mock-Environment wird nicht mehr angezeigt
     - Keine Breaking Changes, nur UI-Änderung
   - **Mitigation:** Keine nötig

#### 🟢 **Niedrige Risiken**

8. **Bundle-Größe**
   - **Risiko:** ⚠️ Sehr niedrig
   - **Beschreibung:** Mock-Code wird durch Tree-Shaking entfernt
   - **Impact:** ✅ Kleinere Bundle-Größe
   - **Mitigation:** Keine nötig

9. **LocalStorage Migration**
   - **Risiko:** ⚠️ Niedrig
   - **Beschreibung:** Benutzer mit gespeichertem `'mock'` Environment
   - **Impact:** 
     - App könnte versuchen, auf `'mock'` zuzugreifen
     - Fallback zu Default nötig
   - **Mitigation:**
     ```typescript
     private loadInitialEnvironment(): EnvironmentKey {
       const stored = localStorage?.getItem(STORAGE_KEY) as EnvironmentKey | null;
       if (stored === 'mock') {
         // Migration: Mock -> Replay
         localStorage?.setItem(STORAGE_KEY, 'replay');
         return 'replay';
       }
       if (stored && this.definitions?.[stored]) {
         return stored;
       }
       return 'replay'; // Neuer Default
     }
     ```

### 📊 Code-Impact-Analyse

**Betroffene Dateien:**
- `environment.service.ts` (Hauptänderung)
- Alle 9 Tab Components (isMockMode Checks)
- `app.component.ts` (Dashboard Controller Initialisierung)
- `mock-dashboard.ts` (könnte entfernt werden, aber wird von Tests verwendet)
- Alle Tests die Mock-Environment verwenden

**Code-Änderungen nötig:**
- ⚠️ Hoch: ~15-20 Dateien müssen angepasst werden
- ⚠️ Tests: ~10-15 Test-Dateien müssen angepasst werden

---

## 🎯 Empfehlung: Option 1 (Nur Fixtures entfernen)

### Warum Option 1?

1. **Minimales Risiko:** ⚠️ Niedrig
   - Nur `project.json` ändern
   - Keine Code-Änderungen nötig
   - Keine Breaking Changes

2. **Schnelle Implementierung:** 15-30 Minuten
   - Nur Assets-Konfiguration anpassen
   - Optional: Graceful Degradation hinzufügen

3. **Flexibilität:** 
   - Mock-Environment bleibt für Development
   - Production Build ohne Fixtures
   - Development Build mit Fixtures

4. **Keine Test-Änderungen:**
   - Tests funktionieren weiterhin
   - Mock-Environment bleibt verfügbar

### Implementierung Option 1

```json
// omf3/apps/ccu-ui/project.json
{
  "targets": {
    "build": {
      "options": {
        "assets": [
          {
            "glob": "**/*",
            "input": "omf3/apps/ccu-ui/public"
          }
          // Fixtures werden hier entfernt (nur für Production)
        ]
      },
      "configurations": {
        "production": {
          // Production: Keine Fixtures
          "assets": [
            {
              "glob": "**/*",
              "input": "omf3/apps/ccu-ui/public"
            }
          ]
        },
        "development": {
          // Development: Fixtures bleiben
          "assets": [
            {
              "glob": "**/*",
              "input": "omf3/apps/ccu-ui/public"
            },
            {
              "glob": "**/*.log",
              "input": "omf3/testing/fixtures/orders",
              "output": "fixtures/orders"
            },
            {
              "glob": "**/*.json",
              "input": "omf3/testing/fixtures/orders",
              "output": "fixtures/orders"
            }
            // ... weitere Fixtures
          ]
        }
      }
    }
  }
}
```

### Optional: Graceful Degradation

Falls Mock-Environment in Production Build verwendet wird (z.B. für Demos):

```typescript
// In Tab Components
async loadFixture(fixture: OrderFixtureName) {
  if (!this.isMockMode) {
    return;
  }
  
  // Check if fixtures are available
  try {
    const response = await fetch('fixtures/orders/white/step3.json');
    if (!response.ok) {
      console.warn('Fixtures not available in production build');
      return;
    }
  } catch (error) {
    console.warn('Fixtures not available', error);
    return;
  }
  
  // Load fixture...
}
```

---

## 📋 Zusammenfassung der Implementierung

**Durchgeführt:** Fixtures wurden aus Production Build entfernt ✅

### Vorher:
- Fixtures waren in den **Base Options** definiert
- Wurden in **allen** Builds eingebunden (Production + Development)

### Nachher:
- Fixtures wurden aus **Base Options** entfernt
- Fixtures nur noch in **Development Configuration** definiert
- **Production Configuration** hat explizit keine Fixtures

### Ergebnis:
- **Production Build:** Nur `public/` Assets, **KEINE Fixtures** (2-5 MB kleiner)
- **Development Build:** Alle Fixtures verfügbar für lokale Entwicklung
- **Development Server:** Verwendet Development Build (Standard), Fixtures verfügbar

Siehe auch: [Build Commands Guide](./build-commands-guide.md) für Details zu Build-Konfigurationen.

---

## 🚫 Warum NICHT Option 2 (Mock-Environment entfernen)?

1. **Zu hohes Risiko:** ⚠️ Hoch
   - Breaking Changes in vielen Dateien
   - Tests müssen refactored werden
   - Entwicklung wird schwieriger

2. **Zu viel Aufwand:** 4-6 Stunden
   - Code-Änderungen in ~20 Dateien
   - Test-Anpassungen
   - Risiko von Fehlern

3. **Verliert Flexibilität:**
   - Mock-Environment ist nützlich für Development
   - Kann für Demos/Präsentationen nützlich sein
   - Conditional Compilation wäre komplexer

4. **Nicht nötig:**
   - Tree-Shaking entfernt ungenutzten Code automatisch
   - Mock-Environment Code wird nicht in Production eingebunden wenn nicht verwendet

---

## 📋 Fazit

### **Option 1: Nur Fixtures entfernen** ✅ EMPFOHLEN

- **Risiko:** 🟢 Niedrig
- **Aufwand:** 15-30 Minuten
- **Impact:** ✅ Production Build ohne Fixtures (2-5 MB kleiner)
- **Breaking Changes:** Keine

### **Option 2: Mock-Environment entfernen** ❌ NICHT EMPFOHLEN

- **Risiko:** 🔴 Hoch
- **Aufwand:** 4-6 Stunden
- **Impact:** ⚠️ Viele Code-Änderungen, Tests müssen angepasst werden
- **Breaking Changes:** Ja, in vielen Dateien

### **Finale Empfehlung:**

**Implementiere Option 1** - Entferne Fixtures nur aus Production Build, behalte Mock-Environment.

**Optional:** Falls Mock-Environment wirklich nicht in Production benötigt wird, kann es später mit Conditional Compilation entfernt werden, aber das ist nicht nötig für den ersten Production Build.

