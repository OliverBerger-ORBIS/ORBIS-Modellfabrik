# DSP-Architektur Resizing – Tiefe Analyse & Lösungsoptionen

> **Hinweis (historisch):** Dieses Dokument beschreibt den Analyse- und Entscheidungsstand aus Sprint 13 inklusive verworfener Optionen. Maßgeblich für die aktuelle Präsentationspraxis ist die OBS-How-To-Doku in `obs-video-presentation-setup.md`.

**Status:** Historische Analyse (Sprint 13)  
**Datum:** 2026-01-08  
**Sprint:** Sprint 13  
**Ziel:** Komplette DSP-Architektur + Animation-Controls sichtbar ohne Scrollen

---

## 🔍 Problem-Analyse

### Kernproblem

**Aktuelles Verhalten:**
- Zoom-Control (60-160%) skaliert **nur das SVG-Diagramm** (rot umrandet)
- **Container bleibt groß** (orange umrandet) → grauer Leerraum entsteht
- Animation-Controls werden nach unten geschoben → nicht sichtbar ohne Scrollen
- Bei 60% Zoom: Diagramm klein, aber Container groß → ~300px Leerraum

**Visuell:**
```
┌─────────────────────────────────────┐
│ Header + Zoom Controls              │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ Diagramm (SVG) - 60% Zoom       │ │ ← Rot umrandet
│ │ (klein, passt in Viewport)     │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← Grauer Leerraum (~300px)
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │   (sollte verschwinden)
│                                     │
│ Animation-Controls (nicht sichtbar) │ ← Erst nach Scrollen sichtbar
└─────────────────────────────────────┘
```

**Erwartetes Verhalten:**
```
┌─────────────────────────────────────┐
│ Header + Zoom Controls              │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ Diagramm (SVG) - 60% Zoom       │ │
│ │ (klein, passt in Viewport)     │ │
│ └─────────────────────────────────┘ │
│ Animation-Controls (sofort sichtbar) │ ← Direkt unter Diagramm
└─────────────────────────────────────┘
```

### Technische Ursachen

1. **Zoom wirkt nur auf SVG:**
   - `transform: scale(zoom)` wird nur auf `.dsp-architecture__diagram` angewendet
   - Container `.dsp-architecture__diagram-wrapper` behält ursprüngliche Größe
   - SVG wird kleiner, Container bleibt groß

2. **Container-Höhe wird nicht angepasst:**
   - Aktuell: `height: auto` oder `max-height` mit statischen Werten
   - Sollte: Exakte Höhe = skalierte SVG-Höhe + minimales Padding

3. **Leerraum entsteht durch:**
   - Container-Padding (1.5rem = 24px)
   - Gap zwischen Diagramm und Controls (aktuell 0, aber Container zu groß)
   - Diagramm-Padding (0.5rem = 8px)
   - Container behält ursprüngliche Höhe trotz kleinerem SVG

---

## 💡 Lösungsoptionen

### Option 1: Reset zu v0.7.0 (max-width: 1400px)

**Beschreibung:**
- Alle Resizing-Änderungen rückgängig machen
- `max-width: 1400px` wiederherstellen
- Zoom-Control beibehalten, aber Container-Höhe anpassen

**Vorteile:**
- ✅ Bewährte Lösung, die funktioniert hat
- ✅ Schnelle Implementierung
- ✅ Keine neuen Bugs

**Nachteile:**
- ❌ Nutzt verfügbaren Platz in Landscape (1920px) nicht optimal
- ❌ Löst das Grundproblem nicht (Container-Höhe)
- ❌ Keine Verbesserung für Hero-Mode

**Aufwand:** Niedrig (1-2 Stunden)  
**Empfehlung:** ⭐⭐ (nur als Fallback)

---

### Option 2: Zoom-Control entfernen, automatisches Resizing

**Beschreibung:**
- Separate Zoom-Control (60-160%) komplett entfernen
- Automatisches Resizing basierend auf Viewport-Größe
- ViewBox wird automatisch an Viewport angepasst

**Implementierung:**
```typescript
// Automatische ViewBox-Anpassung
private calculateAutoZoom(): void {
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  
  // Berechne optimalen Zoom basierend auf verfügbarem Platz
  const availableHeight = viewportHeight - headerHeight - controlsHeight - padding;
  const aspectRatio = VIEWBOX_HEIGHT / VIEWBOX_WIDTH;
  const optimalZoom = Math.min(
    viewportWidth / VIEWBOX_WIDTH,
    availableHeight / (VIEWBOX_WIDTH * aspectRatio)
  );
  
  this.zoom = Math.max(minZoom, Math.min(maxZoom, optimalZoom));
}
```

**Vorteile:**
- ✅ Keine manuelle Zoom-Einstellung nötig
- ✅ Immer optimale Darstellung
- ✅ Container-Höhe passt sich automatisch an

**Nachteile:**
- ❌ Nutzer kann nicht manuell zoomen (wenn gewünscht)
- ❌ Keine Feinabstimmung möglich
- ❌ Verlust der Zoom-Funktionalität

**Aufwand:** Mittel (4-6 Stunden)  
**Empfehlung:** ⭐⭐⭐ (wenn manuelle Zoom nicht benötigt)

---

### Option 3: Controls oben anordnen

**Beschreibung:**
- Zoom-Control und Animation-Controls **vor** dem Diagramm platzieren
- Beide immer am oberen Ende sichtbar
- Diagramm darunter, scrollbar wenn nötig

**Layout-Änderung:**
```
┌─────────────────────────────────────┐
│ Header                               │
├─────────────────────────────────────┤
│ Zoom Controls (oben)                 │
│ Animation Controls (oben)            │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ Diagramm (scrollbar wenn nötig) │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Vorteile:**
- ✅ Controls immer sichtbar
- ✅ Keine Scroll-Probleme für Controls
- ✅ Einfache Implementierung

**Nachteile:**
- ❌ Ungewöhnliche UX (Controls normalerweise unten)
- ❌ Diagramm muss scrollbar sein
- ❌ Nicht intuitiv für Nutzer

**Aufwand:** Niedrig (2-3 Stunden)  
**Empfehlung:** ⭐⭐ (nur wenn UX akzeptabel)

---

### Option 4: Resizing betrifft Diagramm + Container (EMPFOHLEN)

**Beschreibung:**
- Zoom skaliert **sowohl SVG als auch Container**
- Container-Höhe wird exakt auf skalierte SVG-Höhe gesetzt
- Grauer Leerraum verschwindet komplett

**Implementierung:**

#### 4.1 Container-Höhe dynamisch berechnen
```typescript
private calculateDiagramWrapperHeight(): void {
  // Warte auf SVG-Rendering
  setTimeout(() => {
    const svgElement = document.querySelector('.diagram-svg') as SVGSVGElement;
    if (!svgElement) return;
    
    // Gemessene SVG-Höhe nach Zoom
    const svgRect = svgElement.getBoundingClientRect();
    const actualSvgHeight = svgRect.height;
    
    // Container-Höhe = SVG-Höhe + minimales Padding
    const diagramPadding = 16; // 0.5rem * 2
    const totalHeight = actualSvgHeight + diagramPadding;
    
    // Setze exakte Höhe (nicht max-height!)
    this.diagramWrapperHeight = `${totalHeight}px`;
    
    this.cdr.markForCheck();
  }, 100);
}
```

#### 4.2 Zoom aktualisiert Container-Höhe
```typescript
protected zoomIn(): void {
  this.zoom = Math.min(this.maxZoom, this.zoom + this.zoomStep);
  this.saveZoom();
  // Container-Höhe neu berechnen nach Zoom
  setTimeout(() => this.calculateDiagramWrapperHeight(), 150);
}
```

#### 4.3 CSS-Anpassungen
```scss
&__diagram-wrapper {
  // height statt max-height für exakte Größe
  height: var(--diagram-wrapper-height); // Dynamisch gesetzt
  overflow: hidden; // Kein Scrollen im Container
  padding: 0; // Kein Padding
  display: flex;
  flex-direction: column;
}

&__diagram {
  padding: 0.5rem; // Minimal
  flex-shrink: 0;
  
  .diagram-svg {
    width: 100%;
    height: auto;
    flex-shrink: 0;
  }
}

&__controls {
  margin-top: 0; // Kein Gap
  padding-top: 0.5rem; // Minimal
}
```

**Vorteile:**
- ✅ Löst das Kernproblem vollständig
- ✅ Kein Leerraum mehr
- ✅ Controls immer sichtbar
- ✅ Zoom funktioniert wie erwartet
- ✅ Behält bestehende UX bei

**Nachteile:**
- ⚠️ Komplexere Implementierung (Messung + Timing)
- ⚠️ Muss bei jedem Zoom neu berechnen

**Aufwand:** Mittel-Hoch (6-8 Stunden)  
**Empfehlung:** ⭐⭐⭐⭐⭐ (Beste Lösung)

---

## 🎯 Empfohlene Lösung: Option 4 (mit Optimierungen)

### Kombinierte Strategie

**Phase 1: Container-Höhe dynamisch (Option 4)**
- Container-Höhe = exakte SVG-Höhe nach Zoom
- Kein Leerraum mehr
- Controls immer sichtbar

**Phase 2: Automatischer Zoom-Vorschlag (Option 2 ergänzend)**
- Bei Initial-Load: Optimalen Zoom automatisch berechnen
- Nutzer kann manuell anpassen
- Beste UX: Automatisch optimal, aber anpassbar

**Phase 3: ViewBox-Anpassung für Hero-Mode**
- Hero-Mode (< 1000px): ViewBox auf 960px skalieren
- Landscape-Mode: ViewBox 1200px beibehalten
- Automatische Anpassung

---

## 📋 Implementierungsplan

### Schritt 1: Container-Höhe exakt messen und setzen

**Datei:** `dsp-architecture.component.ts`

```typescript
// 1. SVG-Höhe nach Rendering messen
private measureSvgHeight(): number {
  const svgElement = document.querySelector('.diagram-svg') as SVGSVGElement;
  if (!svgElement) return 0;
  return svgElement.getBoundingClientRect().height;
}

// 2. Container-Höhe exakt setzen
private calculateDiagramWrapperHeight(): void {
  setTimeout(() => {
    const svgHeight = this.measureSvgHeight();
    if (svgHeight === 0) return;
    
    const diagramPadding = 16; // 0.5rem * 2
    const exactHeight = svgHeight + diagramPadding;
    
    // Setze exakte Höhe
    this.diagramWrapperHeight = `${exactHeight}px`;
    this.cdr.markForCheck();
  }, 100);
}
```

### Schritt 2: Zoom aktualisiert Container-Höhe

```typescript
protected zoomIn(): void {
  this.zoom = Math.min(this.maxZoom, this.zoom + this.zoomStep);
  this.saveZoom();
  // Warte auf SVG-Transform, dann Höhe neu berechnen
  setTimeout(() => this.calculateDiagramWrapperHeight(), 200);
}

protected zoomOut(): void {
  this.zoom = Math.max(this.minZoom, this.zoom - this.zoomStep);
  this.saveZoom();
  setTimeout(() => this.calculateDiagramWrapperHeight(), 200);
}
```

### Schritt 3: CSS optimieren

**Datei:** `dsp-architecture.component.scss`

```scss
&__diagram-wrapper {
  // height statt max-height
  height: var(--diagram-wrapper-height); // Wird dynamisch gesetzt
  overflow: hidden; // Kein Scrollen
  padding: 0;
  display: flex;
  flex-direction: column;
}

.dsp-architecture {
  gap: 0; // Kein Gap zwischen Diagramm und Controls
}
```

### Schritt 4: Automatischer Zoom-Vorschlag (Optional)

```typescript
private calculateOptimalZoom(): void {
  const viewportHeight = window.innerHeight;
  const viewportWidth = window.innerWidth;
  
  // Verfügbarer Platz für Diagramm
  const availableHeight = viewportHeight - this.headerHeight - this.controlsHeight - 48;
  const availableWidth = viewportWidth - 48;
  
  // Optimaler Zoom basierend auf verfügbarem Platz
  const widthZoom = availableWidth / this.dynamicViewBoxWidth;
  const heightZoom = availableHeight / (this.dynamicViewBoxHeight * 1.1); // 10% Puffer
  
  const optimalZoom = Math.min(widthZoom, heightZoom);
  
  // Setze Zoom wenn noch nicht gesetzt
  if (!localStorage.getItem(this.zoomStorageKey)) {
    this.zoom = Math.max(this.minZoom, Math.min(this.maxZoom, optimalZoom));
    this.saveZoom();
  }
}
```

---

## ✅ Akzeptanzkriterien

### Landscape-Mode (1920×1080)
- [ ] Komplette DSP-Architektur (alle 3 Layers) sichtbar
- [ ] Grüne Highlighting-Beschreibung sichtbar
- [ ] Animation-Controls sichtbar
- [ ] **Kein Scrollen nötig**
- [ ] **Kein grauer Leerraum** zwischen Diagramm und Controls

### Hero-Mode (1040×1080)
- [ ] Komplette DSP-Architektur sichtbar
- [ ] Animation-Controls sichtbar
- [ ] **Kein Scrollen nötig**
- [ ] **Kein grauer Leerraum** zwischen Diagramm und Controls

### Zoom-Verhalten
- [ ] Bei 60% Zoom: Container wird kleiner, kein Leerraum
- [ ] Bei 100% Zoom: Container passt sich an
- [ ] Bei 160% Zoom: Container wird größer, aber passt in Viewport
- [ ] Controls bleiben immer sichtbar

---

## 🔄 Alternative: Hybrid-Lösung (Option 2 + 4)

**Kombination:**
- Automatisches Resizing (Option 2) als Standard
- Manuelle Zoom-Control als Override (falls gewünscht)
- Container-Höhe passt sich immer an (Option 4)

**Vorteil:** Beste UX - automatisch optimal, aber anpassbar

---

## 📝 Nächste Schritte

1. **Entscheidung:** Welche Option bevorzugst du?
2. **Implementierung:** Option 4 empfohlen
3. **Testing:** In Landscape und Hero-Mode testen
4. **Feinabstimmung:** Padding/Gap-Werte optimieren

---

## 🎨 Visuelle Darstellung der Lösung

### Vorher (aktuell):
```
┌─────────────────────────────────────┐
│ Header + Zoom (70%)                 │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ SVG Diagramm (klein, 70%)         │ │
│ └─────────────────────────────────┘ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← 300px Leerraum
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ [Scroll nötig]                      │
│ Animation-Controls (nicht sichtbar)  │
└─────────────────────────────────────┘
```

### Nachher (Option 4):
```
┌─────────────────────────────────────┐
│ Header + Zoom (70%)                 │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ SVG Diagramm (klein, 70%)         │ │
│ └─────────────────────────────────┘ │
│ Animation-Controls (sofort sichtbar) │ ← Kein Leerraum
└─────────────────────────────────────┘
```

---

**Empfehlung:** Option 4 implementieren, da sie das Kernproblem löst und die beste UX bietet.
