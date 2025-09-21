# Cursor AI Mermaid Diagramm Regeln

**Zielgruppe:** Cursor AI Assistant  
**Letzte Aktualisierung:** 20.09.2025

## 🎯 Ziel

Konsistente Mermaid-Diagramme für die OMF-Dokumentation erstellen mit klarer Farbzuordnung zwischen ORBIS-Komponenten, Fischertechnik Hardware/Software und externen Systemen.

## 🎨 Farbpalette (4-Farb-System)

### **1. ORBIS-Komponenten (Blau-Ton mit Nuancen)**
- `#90caf9` - Dunkelblau (Zentrale Komponenten, Hauptfunktionen)
- `#bbdefb` - Mittelblau (Kern-Komponenten, direkte Abhängigkeiten)
- `#e3f2fd` - Hellblau (Standard-Komponenten, UI, Helper Apps)

### **2. Fischertechnik Hardware - BEHALTEN (Gelb-Ton)**
- `#fff8e1` - Sehr helles Gelb (DRILL, MILL, DPS Module)
- `#ffecb3` - Mittleres Gelb (TXT Controller, Raspberry Pi)
- `#ffc107` - Dunkleres Gelb (Kritische Hardware-Komponenten)

### **3. Fischertechnik Software - TEILWEISE ERSETZEN (Rot-Ton)**
- `#ffebee` - Sehr helles Rot (Node-RED Flows)
- `#ffcdd2` - Mittleres Rot (VDA5050 Implementation)
- `#ef5350` - Dunkleres Rot (Legacy Software)

### **4. Externe/Neutrale Systeme (Grau-Ton)**
- `#f5f5f5` - Sehr helles Grau (MQTT Broker, Datenbanken)
- `#e0e0e0` - Mittleres Grau (APIs, Interfaces)
- `#bdbdbd` - Dunkleres Grau (Externe Services)

## 📋 Cursor AI Regeln

### **Farbzuordnung:**
- **ORBIS Komponenten:** Blau-Töne mit Hierarchie-Nuancen
  - `#90caf9` - Zentrale Komponenten (dunkelblau)
  - `#bbdefb` - Kern-Komponenten (mittelblau)  
  - `#e3f2fd` - Standard-Komponenten (hellblau)
- **Fischertechnik Hardware (BEHALTEN):** Immer Gelb-Töne (#fff8e1, #ffecb3, #ffc107)
- **Fischertechnik Software (TEILWEISE ERSETZEN):** Immer Rot-Töne (#ffebee, #ffcdd2, #ef5350)
- **Externe/Neutrale Systeme:** Immer Grau-Töne (#f5f5f5, #e0e0e0, #bdbdbd)

### **Hardware vs Software Unterscheidung:**
- **Hardware (Gelb):** DRILL, MILL, DPS Module, TXT Controller, Raspberry Pi
- **Software (Rot):** Node-RED Flows, VDA5050 Implementation, Legacy Software

### **Regeln:**
1. **Maximal 4 Farben** pro Diagramm
2. **Konsistente Zuordnung** - nie ORBIS in Gelb/Rot
3. **Helle Töne verwenden** - nicht zu bunt
4. **Hardware vs Software klar unterscheiden**
5. **Styling am Ende** - alle style-Definitionen nach dem Graph
6. **KEINE Kommentare in style-Zeilen** - Mermaid unterstützt keine Kommentare nach `fill:#color`

## 🎯 Standard-Template

```markdown
# Diagramm-Name

```mermaid
graph TD
    A[ORBIS Component] -->|Steuert| B[FT Hardware]
    A -->|Ersetzt| C[FT Software]
    B --> D[External System]
    
            style A fill:#90caf9,stroke:#1976d2,stroke-width:3px  # ORBIS Zentrale (dunkelblau)
            style B fill:#fff8e1  # FT Hardware Gelb
            style C fill:#ffebee  # FT Software Rot
            style D fill:#f5f5f5  # External/Neutral Grau
```
```

**Vollständiger Style-Guide:** Siehe `mermaid-style-guide.md` für professionelle Diagramm-Regeln  
**Standard-Templates:** Siehe `mermaid-templates.md` für vorgefertigte Diagramm-Templates  
**Bestehende Diagramme:** Siehe `docs/06-integrations/node-red/*.mermaid` für Beispiele

## 🔧 Praktische Beispiele

### **Beispiel 1: Aktuelle Architektur**
```markdown
# Aktuelle APS Architektur

```mermaid
graph TD
    A[Node-RED] -->|Steuert| B[DRILL Module]
    A -->|Steuert| C[MILL Module]
    A -->|Läuft auf| D[Raspberry Pi]
    
    style A fill:#ffebee  # FT Software (wird ersetzt)
    style B fill:#fff8e1  # FT Hardware (bleibt)
    style C fill:#fff8e1  # FT Hardware (bleibt)
    style D fill:#fff8e1  # FT Hardware (bleibt)
```
```

### **Beispiel 2: Ziel-Architektur**
```markdown
# Ziel-Architektur mit OMF

```mermaid
graph TD
    A[OMF Dashboard] -->|Steuert| B[DRILL Module]
    A -->|Steuert| C[MILL Module]
    A -->|Läuft auf| D[Raspberry Pi]
    
    style A fill:#e3f2fd  # ORBIS (neue Lösung)
    style B fill:#fff8e1  # FT Hardware (bleibt)
    style C fill:#fff8e1  # FT Hardware (bleibt)
    style D fill:#fff8e1  # FT Hardware (bleibt)
```
```

## 🚨 Wichtige Hinweise für Cursor AI

### **NIEMALS:**
- ORBIS-Komponenten in Gelb oder Rot färben
- Fischertechnik Hardware in Rot färben (nur Software wird ersetzt)
- Mehr als 4 Farben in einem Diagramm verwenden
- Zu dunkle oder zu bunte Farben verwenden

### **IMMER:**
- Klare Hardware vs Software Unterscheidung
- Konsistente Farbzuordnung über alle Diagramme
- Helle, dezente Farbtöne verwenden
- Style-Definitionen am Ende des Diagramms

### **Bei Unsicherheit:**
- **Standard-Templates** aus `mermaid-templates.md` verwenden
- Diese Regeln als Referenz nutzen
- Bei Fragen: User fragen statt raten

---

*Teil der OMF-Dokumentation | [Zurück zur Hauptdokumentation](../../../README.md)*
