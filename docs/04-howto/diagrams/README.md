# Diagramm-Dokumentation

**Zweck:** Anleitungen und Regeln für die Erstellung von Diagrammen in der OSF-Dokumentation

## 📋 Verfügbare Anleitungen

### **Mermaid Diagramme**
- **[Mermaid Setup Guide](mermaid-setup.md)** - Grundlegende Einrichtung und Workflow
- **[Mermaid Style Guide](mermaid-style-guide.md)** - Professionelle Regeln und Beispiele
- **[Cursor AI Mermaid Rules](cursor-ai-mermaid-rules.md)** - Spezielle Regeln für Cursor AI
- **[Cursor AI Mermaid Instructions](mermaid-cursor-instructions.md)** - Zusätzliche Cursor-Anweisungen

## 🎯 Schnellstart

1. **Setup:** Lies [Mermaid Setup Guide](mermaid-setup.md) für die Grundlagen
2. **Regeln:** Befolge [Mermaid Style Guide](mermaid-style-guide.md) für konsistente Diagramme
3. **Cursor AI:** Nutze [Cursor AI Rules](cursor-ai-mermaid-rules.md) für AI-generierte Diagramme

## 🎨 Farbpalette (Übersicht)

- **ORBIS (Blau):** `#e3f2fd` – OSF-UI, Session Manager
- **FT Hardware (Gelb):** `#fff8e1` - DRILL, MILL, DPS Module
- **FT Software (Rot):** `#ffebee` - Node-RED, VDA5050 (teilweise ersetzt)
- **External (Lila):** `#f3e5f5` - MQTT Broker, APIs

## 📁 Diagramm-Verzeichnisse (Hybrid-Ansatz)

### **🏗️ Zentrale Architektur-Diagramme**
- **`docs/_shared/diagrams/src/`** - Mermaid-Quelldateien für wiederverwendbare Architektur-Diagramme
- **`docs/_shared/diagrams/svg/`** - Generierte SVG-Dateien der zentralen Diagramme
- **Für:** ORBIS-Ziel-Architektur, As-Is vs. To-Be Vergleiche, Integration-Patterns
- **Build-System:** `npm run diagrams` für automatische SVG-Generierung

### **📁 Kontext-spezifische Diagramme (dezentral)**
- **`docs/06-integrations/node-red/*.mermaid`** - APS-As-Is Architektur (Node-RED Analyse)
- **`docs/04-howto/helper_apps/session-manager/*.mermaid`** - Session Manager Diagramme
- **`docs/06-integrations/mqtt/*.mermaid`** - MQTT-spezifische Diagramme

### **🎯 Wann welcher Ordner?**
- **Zentral (`docs/_shared/diagrams/src/`):** Übergreifende, wiederverwendbare Architektur-Diagramme
- **Dezentral:** Integration-spezifische, kontextbezogene Diagramme bei den entsprechenden Dokumenten

### **🔧 Build-Commands**
```bash
# Alle Diagramme generieren
npm run diagrams

# Watch-Modus (automatisch bei Änderungen)
npm run diagrams:watch

# Einzelnes Diagramm generieren
npx mmdc -i _shared/diagrams/src/example.mermaid -o _shared/diagrams/svg/example.svg
```

---

*Teil der OSF-Dokumentation | [Zurück zur Hauptdokumentation](../../../README.md)*
