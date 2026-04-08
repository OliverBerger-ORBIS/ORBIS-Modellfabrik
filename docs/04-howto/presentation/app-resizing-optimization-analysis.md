# App-Resizing-Optimierung für OBS-Videopräsentation – Analyse

> **Hinweis (historisch):** Dieses Dokument ist eine Planungs-/Analysebasis aus Sprint 13. Für den aktuellen operativen Ablauf und verbindliche Checks gilt die OBS-How-To-Doku `obs-video-presentation-setup.md`.

**Status:** Historische Analyse (Sprint 13)  
**Sprint:** Sprint 13  
**Ziel:** Optimierung der Angular-App für OBS-Videopräsentation mit einheitlicher Handhabung von Landscape- und Hero-Modi

---

## 🎯 Zielsetzung

Die Angular-App soll für OBS-Videopräsentation optimiert werden, wobei Ansichten je nach "Szenen"-Wahl im Landscape- und Hero-Modus angezeigt werden. Durch die Hero + 2 Ansicht ist ein Großteil der Präsentation im Hero-Modus (960px Breite). Es soll eine einheitliche Handhabung der Ansichten erreicht werden.

---

## 📋 OBS-Video-Präsentation Kontext

### Szenen-Struktur (aus `obs-video-presentation-setup.md`)

1. **S1 - Orders Vollbild (Edge InPrivate)** – 1920×1080 (Landscape)
2. **S2 - Digital-Twin Vollbild (Chrome)** – 1920×1080 (Landscape)
3. **S3 - OSF Vollbild (Chrome)** – 1920×1080 (Landscape) mit allen Tabs
4. **S4 - Kamera Vollbild** – 1920×1080 (Landscape)
5. **S5 - Hero + 2** – Komposition:
   - **OSF Hero (links):** 960×1080 (nutzt verfügbaren Platz optimal aus)
   - **Digital Twin (rechts oben):** 960×540 (16:9 Verhältnis)
   - **Kamera (rechts unten):** 960×540 (16:9 Verhältnis für Konftel Cam50)
   
   **Berechnung:**
   - OBS Output: 1920×1080px
   - Kamera (16:9): 960×540px (960/540 = 1.78 = 16:9)
   - Hero-Bereich: 1920 - 960 = 960px Breite, volle Höhe 1080px = 960×1080px
   - Digital Twin: 960×540px (gleiche Größe wie Kamera)
6. **S6 - OSF Hero (Edge)** – 960×1080 (Hero-Ansicht) als Vollbildfallback und Quelle für S5

### Herausforderung

- **Hero + 2 (S5)** ist die Standard-Szene für Präsentationen
- OSF-Hero-Bereich hat **960px Breite** (kein klassisches Porträt, aber optimaler verfügbarer Platz)
- DSP-Architektur-Animation wurde für **Landscape-Modus** optimiert (VIEWBOX_WIDTH = 1200px)
- Einheitliche Handhabung der Ansichten fehlt

---

## 🔍 Aktuelle Situation – Komponenten-Analyse

### 1. Shopfloor-Layout (✅ Bereits Resizing vorhanden)

**Komponente:** `ShopfloorPreviewComponent`  
**Datei:** `osf/apps/osf-ui/src/app/components/shopfloor-preview/shopfloor-preview.component.ts`

**Features:**
- ✅ Zoom-Funktion mit `zoomIn()`, `zoomOut()`, `resetZoom()`
- ✅ Scale-Speicherung in localStorage (getrennt für Configuration-Tab vs. Orders-Tab)
- ✅ Konfigurierbare Min/Max-Scale-Werte
- ✅ ViewBox-basiertes Scaling (SVG)

**Konfiguration:**
```json
{
  "scaling": {
    "default_percent": 100,
    "min_percent": 25,
    "max_percent": 200,
    "mode": "viewBox"
  }
}
```

**Storage-Keys:**
- `shopfloor-preview-scale` (Orders-Tab)
- `shopfloor-config-scale` (Configuration-Tab)

**Status:** ✅ Funktioniert bereits gut, kann als Referenz dienen

---

### 2. DSP Tab – Breitenbeschränkung

**Komponente:** `DspPageComponent`  
**Datei:** `osf/apps/osf-ui/src/app/pages/dsp/dsp-page.component.scss`

**Aktuelle Constraints:**
```scss
.dsp-page__content {
  padding: 2rem;
  max-width: 1400px;  // ⚠️ Potenzielle Breitenbeschränkung
  margin: 0 auto;
  width: 100%;
}
```

**Problem:**
- `max-width: 1400px` könnte in Landscape-Modus (1920px) unnötig Platz verschenken
- In Hero-Modus (960px) ist dies weniger kritisch, aber in Landscape könnte mehr Platz genutzt werden

**Status:** ⚠️ Potenzielle Optimierung möglich

---

### 3. DSP-Architektur-Animation – Landscape-optimiert

**Komponente:** `DspArchitectureComponent`  
**Datei:** `osf/apps/osf-ui/src/app/components/dsp-architecture/`

**Layout-Konfiguration:**
```typescript
// layout.shared.config.ts
export const VIEWBOX_WIDTH = 1200;  // Landscape-optimiert
export const VIEWBOX_HEIGHT = 1140;
```

**SCSS-Constraints:**
```scss
.dsp-architecture {
  // Keine explizite max-width, aber:
  &__diagram-wrapper {
    max-height: 70vh;
    overflow: auto;
  }
  
  &__diagram {
    .diagram-svg {
      width: 100%;
      height: auto;
      min-height: 400px;
    }
  }
}

// Responsive Media Queries:
@media (max-width: 768px) {
  .dsp-architecture__diagram {
    transform: scale(0.7) !important;  // Auto-scale down
  }
}
```

**Problem:**
- VIEWBOX_WIDTH = 1200px ist für Landscape (1920px) optimiert
- In Hero-Modus (960px) wird die Animation zu klein/ungeeignet
- Zoom-Funktion vorhanden, aber keine automatische Anpassung an Viewport-Breite

**Status:** ⚠️ Benötigt Anpassung für Hero-Modus

---

### 4. App-Layout-Struktur

**Komponente:** `AppComponent`  
**Datei:** `osf/apps/osf-ui/src/app/app.component.scss`

**Layout:**
```scss
.app-frame {
  display: grid;
  grid-template-columns: 280px 1fr;  // Sidebar + Content
  min-height: 100vh;
}

.app-frame--collapsed {
  grid-template-columns: 88px 1fr;  // Collapsed Sidebar
}
```

**Status:** ✅ Responsive Grid-Layout vorhanden

---

### 5. Weitere Tabs – Vollständige Übersicht

#### Tabs mit max-width: 1400px (⚠️ Potenzielle Optimierung)

**Message Monitor Tab:**
```scss
.message-monitor-tab {
  padding: 1.5rem;
  max-width: 1400px;  // ⚠️ Wie DSP Tab
  margin: 0 auto;
}
```

**DSP Action Tab:**
```scss
.dsp-action-tab {
  max-width: 1400px;  // ⚠️ Wie DSP Tab
}
```

**Status:** ⚠️ Potenzielle Optimierung möglich (wie DSP Tab)

---

#### Tabs mit max-width: 100% (✅ Keine Beschränkung)

**DPS Tab:**
```scss
.dps-tab {
  width: 100%;
  max-width: 100%;  // ✅ Keine Beschränkung
}
```

**AGV Tab:**
```scss
.fts-tab {
  width: 100%;
  max-width: 100%;  // ✅ Keine Beschränkung
}
```

**HBW Tab:**
```scss
.hbw-tab {
  width: 100%;
  max-width: 100%;  // ✅ Keine Beschränkung
}
```

**Mill Tab:**
```scss
.mill-tab {
  width: 100%;
  max-width: 100%;  // ✅ Keine Beschränkung
}
```

**Drill Tab:**
```scss
.drill-tab {
  width: 100%;
  max-width: 100%;  // ✅ Keine Beschränkung
}
```

**AIQS Tab:**
```scss
.aiqs-tab {
  width: 100%;
  max-width: 100%;  // ✅ Keine Beschränkung
}
```

**Track Trace Tab:**
```scss
.track-trace-tab {
  width: 100%;
  max-width: 100%;  // ✅ Keine Beschränkung
}
```

**Status:** ✅ Keine Breitenbeschränkungen

---

#### Tabs ohne explizite max-width (✅ Responsive)

**Process Tab:**
```scss
.process-tab {
  padding: 2rem;
  width: 100%;  // ✅ Responsive, keine max-width
}
```

**Order Tab:**
```scss
.order-tab {
  display: grid;
  gap: 2rem;
  // ✅ Keine max-width, nur max-width: 32rem für p-Tag
}
```

**Sensor Tab:**
```scss
.sensor-tab {
  // ✅ Responsive, keine max-width
}
```

**Configuration Tab:**
```scss
.configuration-tab {
  display: grid;
  gap: 2rem;
  // ✅ Responsive, keine max-width
}
```

**Shopfloor Tab:**
```scss
.shopfloor-tab {
  width: 100%;  // ✅ Responsive, keine max-width
}
```

**Settings Tab:**
```scss
// ✅ Responsive, keine max-width
```

**Status:** ✅ Responsive, keine Breitenbeschränkungen

---

## 🎨 Design-Patterns & Best Practices

### 1. Shopfloor-Layout Resizing (Referenz-Implementierung)

**Pattern:**
- ViewBox-basiertes SVG-Scaling
- localStorage für Persistenz
- Kontext-spezifische Storage-Keys
- Min/Max-Constraints

**Übertragbarkeit:**
- ✅ Kann für DSP-Architektur-Animation adaptiert werden
- ✅ ViewBox-basiertes Scaling ist bereits vorhanden

### 2. Responsive Media Queries

**Aktuelle Patterns:**
```scss
@media (max-width: 768px) {
  // Mobile/Portrait
}

@media (min-width: 1024px) and (max-width: 1440px) {
  // Medium Laptop
}

@media (min-width: 2560px) {
  // 4K/Large Screens
}
```

**Fehlend:**
- ❌ Orientierung-spezifische Queries (`@media (orientation: portrait)`)
- ❌ Viewport-Breite-spezifische Anpassungen für OBS-Szenen

---

## 🚨 Identifizierte Probleme

### Problem 1: Tabs mit max-width: 1400px – Unnötige Breitenbeschränkung

**Betroffene Tabs:**
- **DSP Tab** (`dsp-page.component.scss`): `max-width: 1400px`
- **Message Monitor Tab** (`message-monitor-tab.component.scss`): `max-width: 1400px`
- **DSP Action Tab** (`dsp-action-tab.component.scss`): `max-width: 1400px`

**Lage:**
- In Landscape-Modus (1920px) wird Platz verschenkt
- DSP-Architektur-Animation könnte breiter dargestellt werden
- Message Monitor Tab könnte mehr Platz für Tabellen nutzen

**Impact:** Mittel  
**Priorität:** Mittel

---

### Problem 2: DSP-Architektur-Animation – Hero-Modus ungeeignet

**Lage:**
- VIEWBOX_WIDTH = 1200px ist für Landscape optimiert
- In Hero-Modus (960px) wird die Animation zu klein/ungeeignet
- Zoom-Funktion vorhanden, aber keine automatische Anpassung an Viewport-Breite

**Impact:** Hoch (Hero + 2 ist Standard-Szene)  
**Priorität:** Hoch

---

### Problem 3: Fehlende einheitliche Handhabung

**Lage:**
- Shopfloor-Layout hat Resizing
- DSP-Architektur-Animation hat Zoom, aber keine Orientierungs-Anpassung
- Andere Tabs haben keine Resizing-Funktion
- Keine einheitliche Strategie für Landscape vs. Porträt

**Impact:** Hoch  
**Priorität:** Hoch

---

### Problem 4: Keine automatische Orientierungs-Erkennung

**Lage:**
- Keine Viewport-Orientierungs-Erkennung
- Keine automatische Anpassung an OBS-Szenen-Breite
- Manuelle Anpassung erforderlich

**Impact:** Mittel  
**Priorität:** Mittel

---

## 💡 Lösungsansätze (Vorschläge)

### Ansatz 1: Viewport-Orientierungs-Erkennung

**Implementierung:**
- Service für Viewport-Orientierung (`PortraitService` oder `ViewportService`)
- Automatische Erkennung via `window.matchMedia('(orientation: portrait)')`
- Event-basierte Updates bei Orientierungswechsel

**Vorteile:**
- Automatische Anpassung
- Einheitliche Handhabung

**Nachteile:**
- OBS-Szenen haben feste Dimensionen (kein echter Orientierungswechsel)
- Benötigt manuelle Konfiguration für OBS-Szenen

---

### Ansatz 2: Query-Parameter für OBS-Modus

**Implementierung:**
- Route-Parameter `?obs-mode=portrait` oder `?obs-mode=landscape`
- CSS-Klassen basierend auf Parameter
- Automatische Anpassung der Layouts

**Vorteile:**
- Explizite Kontrolle
- OBS-spezifische Optimierungen möglich

**Nachteile:**
- Manuelle Konfiguration in OBS-Szenen erforderlich

---

### Ansatz 3: Viewport-Breite-basierte Anpassung

**Implementierung:**
- Automatische Erkennung der Viewport-Breite
- Breakpoints für OBS-Szenen (960px = Hero, 1920px = Landscape)
- Automatische Layout-Anpassung

**Vorteile:**
- Automatisch
- Keine manuelle Konfiguration

**Nachteile:**
- Könnte bei anderen Viewport-Größen Probleme verursachen

---

### Ansatz 4: Einheitliches Resizing-System

**Implementierung:**
- Zentraler Service für Resizing (`ResizingService`)
- Komponenten registrieren sich für Resizing
- Einheitliche API für Zoom/Scale

**Vorteile:**
- Einheitliche Handhabung
- Wiederverwendbar

**Nachteile:**
- Größerer Refactoring-Aufwand

---

## 📊 Empfohlene Lösung (Kombination)

### Phase 1: Sofort-Maßnahmen

1. **Tabs mit max-width: 1400px optimieren**
   - **DSP Tab:** `max-width: 1400px` → `max-width: 100%` oder responsive
   - **Message Monitor Tab:** `max-width: 1400px` → `max-width: 100%` oder responsive
   - **DSP Action Tab:** `max-width: 1400px` → `max-width: 100%` oder responsive
   - Bessere Nutzung des verfügbaren Platzes in Landscape (1920px)

2. **DSP-Architektur-Animation – Hero-Optimierung**
   - Automatische Erkennung der Viewport-Breite
   - Anpassung des VIEWBOX-Scaling für Hero-Modus (< 1000px)
   - Zoom-Funktion beibehalten, aber intelligenter

### Phase 2: Einheitliche Handhabung

3. **Viewport-Service implementieren**
   - Automatische Orientierungs-Erkennung
   - Breakpoint-basierte Anpassung
   - Event-basierte Updates

4. **Resizing-Service (optional)**
   - Zentraler Service für Resizing
   - Einheitliche API
   - Wiederverwendbar für alle Komponenten

### Phase 3: OBS-spezifische Optimierungen

5. **Query-Parameter für OBS-Modus**
   - `?obs-mode=hero` / `?obs-mode=landscape`
   - OBS-spezifische CSS-Klassen
   - Automatische Layout-Anpassung

---

## 🔧 Technische Details

### Viewport-Breiten für OBS-Szenen

- **Landscape (S3):** 1920px
- **Hero (S6):** 960px (960×1080)
- **Hero + 2 Hero-Bereich (S5):** 960px (960×1080)
- **Hero + 2 Digital Twin/Kamera (S5):** 960px (je 960×540px)

**Berechnung für Hero + 2:**
- OBS Output: 1920×1080px
- Kamera (Konftel Cam50, 16:9): 960×540px (960/540 = 1.78 = 16:9)
- Hero-Bereich links: 1920 - 960 = **960px Breite**, volle Höhe **1080px** = 960×1080px
- Digital Twin rechts oben: 960×540px (gleiche Größe wie Kamera)
- Kamera rechts unten: 960×540px (16:9 Verhältnis beibehalten)

✅ **Korrekt:** Die Dimensionen orientieren sich am 16:9 Verhältnis der Konftel Cam50 und nutzen den verfügbaren Platz optimal aus.

### Breakpoints

```scss
// OBS-spezifische Breakpoints
$obs-hero-width: 960px;         // S5/S6 - Hero-Bereich (960×1080)
$obs-landscape-width: 1920px;  // S3 - OSF Vollbild
$obs-hero-camera-width: 960px; // S5 - Kamera/Digital Twin (rechts, je 960×540px)

// Responsive Breakpoints
@media (max-width: 1000px) {
  // Hero-Modus (960px Breite)
}

@media (min-width: 1000px) {
  // Landscape-Modus (1920px Breite)
}
```

---

## 📝 Nächste Schritte

1. ✅ **Analyse abgeschlossen** (dieses Dokument)
2. ⏳ **User-Freigabe** für Implementierung
3. ⏳ **GitHub Agents PR** (geplant)
4. ⏳ **Implementierung Phase 1** (Sofort-Maßnahmen)
5. ⏳ **Implementierung Phase 2** (Einheitliche Handhabung)
6. ⏳ **Implementierung Phase 3** (OBS-Optimierungen)

---

## 📚 Referenzen

- [OBS Video-Präsentation Setup](../presentation/obs-video-presentation-setup.md)
- [Shopfloor Preview Component](../../../osf/apps/osf-ui/src/app/components/shopfloor-preview/shopfloor-preview.component.ts)
- [DSP Architecture Component](../../../osf/apps/osf-ui/src/app/components/dsp-architecture/dsp-architecture.component.ts)
- [DSP Layout Config](../../../osf/apps/osf-ui/src/app/components/dsp-animation/layout.shared.config.ts)

---

*Letzte Aktualisierung: 08.01.2026*
