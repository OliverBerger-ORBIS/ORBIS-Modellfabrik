# Angular-App Resizing-Optimierung für OBS-Videopräsentation

> **Hinweis (historisch):** Dieses Task-Dokument stammt aus der Umsetzungsplanung (Sprint 13). Für den aktuellen Präsentations-Runbook-Stand ist `obs-video-presentation-setup.md` maßgeblich.

**Status:** Historisches Task-Dokument (Sprint 13)  
**Sprint:** Sprint 13  
**Priority:** Medium-High  
**Type:** Feature Enhancement

---

## 🎯 Zielsetzung

Die Angular-App soll für OBS-Videopräsentation optimiert werden, wobei Ansichten je nach "Szenen"-Wahl im Landscape- und Hero-Modus angezeigt werden. Durch die Hero + 2 Ansicht ist ein Großteil der Präsentation im Hero-Modus (960px Breite). Es soll eine einheitliche Handhabung der Ansichten erreicht werden.

---

## 📋 Kontext & Hintergrund

### OBS-Video-Präsentation Setup

Die App wird in OBS Studio für Videopräsentationen verwendet. Die wichtigsten Szenen:

- **S3 - OSF Vollbild (Chrome):** 1920×1080 (Landscape)
- **S5 - Hero + 2:** Komposition aus OSF Hero (960×1080) + Digital Twin (960×540) + Kamera (960×540)
- **S6 - OSF Hero (Edge):** 960×1080 (Hero-Ansicht)

**Berechnung für Hero + 2:**
- OBS Output: 1920×1080px
- Kamera (Konftel Cam50, 16:9): 960×540px (960/540 = 1.78 = 16:9)
- Hero-Bereich links: 1920 - 960 = **960px Breite**, volle Höhe **1080px** = 960×1080px
- Digital Twin rechts oben: 960×540px (gleiche Größe wie Kamera)
- Kamera rechts unten: 960×540px (16:9 Verhältnis beibehalten)

### Herausforderung

- **Hero + 2 (S5)** ist die Standard-Szene für Präsentationen
- OSF-Hero-Bereich hat **960px Breite** (kein klassisches Porträt, aber optimaler verfügbarer Platz)
- DSP-Architektur-Animation wurde für **Landscape-Modus** optimiert (VIEWBOX_WIDTH = 1200px)
- Einheitliche Handhabung der Ansichten fehlt

---

## 🔍 Identifizierte Probleme

### Problem 1: Tabs mit max-width: 1400px – Unnötige Breitenbeschränkung

**Betroffene Tabs:**
- **DSP Tab** (`osf/apps/osf-ui/src/app/pages/dsp/dsp-page.component.scss`): `max-width: 1400px`
- **Message Monitor Tab** (`osf/apps/osf-ui/src/app/tabs/message-monitor-tab.component.scss`): `max-width: 1400px`
- **DSP Action Tab** (`osf/apps/osf-ui/src/app/tabs/dsp-action-tab.component.scss`): `max-width: 1400px`

**Lage:**
- In Landscape-Modus (1920px) wird Platz verschenkt
- DSP-Architektur-Animation könnte breiter dargestellt werden
- Message Monitor Tab könnte mehr Platz für Tabellen nutzen

**Impact:** Mittel  
**Priorität:** Mittel

---

### Problem 2: DSP-Architektur-Animation – Hero-Modus ungeeignet

**Komponente:** `DspArchitectureComponent`  
**Datei:** `osf/apps/osf-ui/src/app/components/dsp-architecture/`

**Lage:**
- VIEWBOX_WIDTH = 1200px ist für Landscape (1920px) optimiert
- In Hero-Modus (960px) wird die Animation zu klein/ungeeignet
- Zoom-Funktion vorhanden, aber keine automatische Anpassung an Viewport-Breite

**Impact:** Hoch (Hero + 2 ist Standard-Szene)  
**Priorität:** Hoch

---

### Problem 3: Fehlende einheitliche Handhabung

**Lage:**
- Shopfloor-Layout hat Resizing (✅ Referenz-Implementierung)
- DSP-Architektur-Animation hat Zoom, aber keine Orientierungs-Anpassung
- Andere Tabs haben keine Resizing-Funktion
- Keine einheitliche Strategie für Landscape vs. Hero

**Impact:** Hoch  
**Priorität:** Hoch

---

## 💡 Lösungsansätze

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

### Phase 2: Einheitliche Handhabung (Optional)

3. **Viewport-Service implementieren**
   - Automatische Orientierungs-Erkennung
   - Breakpoint-basierte Anpassung
   - Event-basierte Updates

4. **Resizing-Service (optional)**
   - Zentraler Service für Resizing
   - Einheitliche API
   - Wiederverwendbar für alle Komponenten

### Phase 3: OBS-spezifische Optimierungen (Optional)

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

### Referenz-Implementierung

**Shopfloor-Layout Resizing** (`osf/apps/osf-ui/src/app/components/shopfloor-preview/shopfloor-preview.component.ts`):
- ✅ Zoom-Funktion mit `zoomIn()`, `zoomOut()`, `resetZoom()`
- ✅ Scale-Speicherung in localStorage (getrennt für Configuration-Tab vs. Orders-Tab)
- ✅ ViewBox-basiertes Scaling (SVG)
- ✅ Kann als Referenz für DSP-Architektur-Animation dienen

---

## 📝 Implementierungs-Anforderungen

### Must-Have (Phase 1)

1. ✅ **Tabs mit max-width: 1400px optimieren**
   - Dateien:
     - `osf/apps/osf-ui/src/app/pages/dsp/dsp-page.component.scss`
     - `osf/apps/osf-ui/src/app/tabs/message-monitor-tab.component.scss`
     - `osf/apps/osf-ui/src/app/tabs/dsp-action-tab.component.scss`
   - Änderung: `max-width: 1400px` → `max-width: 100%` oder responsive Alternative
   - Test: Prüfen in Landscape (1920px) und Hero (960px)

2. ✅ **DSP-Architektur-Animation – Hero-Optimierung**
   - Dateien:
     - `osf/apps/osf-ui/src/app/components/dsp-architecture/dsp-architecture.component.ts`
     - `osf/apps/osf-ui/src/app/components/dsp-architecture/dsp-architecture.component.scss`
     - `osf/apps/osf-ui/src/app/components/dsp-animation/layout.shared.config.ts`
   - Änderung: Automatische Anpassung des VIEWBOX-Scaling basierend auf Viewport-Breite
   - Viewport < 1000px: Angepasstes Scaling für Hero-Modus
   - Zoom-Funktion beibehalten
   - Test: Prüfen in Hero (960px) und Landscape (1920px)

### Nice-to-Have (Phase 2 & 3)

3. **Viewport-Service implementieren** (Optional)
4. **Resizing-Service** (Optional)
5. **Query-Parameter für OBS-Modus** (Optional)

---

## ✅ Akzeptanzkriterien

### Phase 1 (Must-Have)

- [ ] Alle Tabs mit `max-width: 1400px` optimiert
- [ ] DSP Tab nutzt vollständige Breite in Landscape (1920px)
- [ ] Message Monitor Tab nutzt vollständige Breite in Landscape (1920px)
- [ ] DSP Action Tab nutzt vollständige Breite in Landscape (1920px)
- [ ] DSP-Architektur-Animation passt sich automatisch an Hero-Modus (960px) an
- [ ] Zoom-Funktion funktioniert weiterhin korrekt
- [ ] Keine visuellen Regressionen in bestehenden Ansichten
- [ ] Responsive Verhalten bleibt erhalten

### Tests

- [ ] Manuell testen in Landscape (1920px)
- [ ] Manuell testen in Hero (960px)
- [ ] Manuell testen in OBS-Szenen (S3, S5, S6)
- [ ] Alle Tabs prüfen auf korrekte Darstellung

---

## 📚 Referenzen

- [Vollständige Analyse-Dokumentation](./app-resizing-optimization-analysis.md)
- [OBS Video-Präsentation Setup](./obs-video-presentation-setup.md)
- [Shopfloor Preview Component](../../../osf/apps/osf-ui/src/app/components/shopfloor-preview/shopfloor-preview.component.ts) (Referenz-Implementierung)
- [DSP Architecture Component](../../../osf/apps/osf-ui/src/app/components/dsp-architecture/dsp-architecture.component.ts)
- [DSP Layout Config](../../../osf/apps/osf-ui/src/app/components/dsp-animation/layout.shared.config.ts)

---

## 🚀 Nächste Schritte

1. ✅ Analyse abgeschlossen
2. ✅ Task-Beschreibung erstellt
3. ⏳ GitHub Agents PR erstellen
4. ⏳ Implementierung Phase 1 (Must-Have)
5. ⏳ Testing & Verifizierung
6. ⏳ Phase 2 & 3 (Optional, falls Zeit vorhanden)

---

*Erstellt: 08.01.2026*  
*Basierend auf: [App-Resizing-Optimierung Analyse](./app-resizing-optimization-analysis.md)*
