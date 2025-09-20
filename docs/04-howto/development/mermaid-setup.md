# Mermaid Setup Guide

**Zielgruppe:** Entwickler  
**Letzte Aktualisierung:** 20.09.2025

## 🎯 Ziel

Mermaid-Diagramme in separate `.mermaid` Dateien auslagern und IDE-Einrichtung für optimales Arbeiten mit Diagrammen.

## 🔧 VSCode Extensions

### **Empfohlene Extension:**

**"Markdown Preview Mermaid Support"** (`bierner.markdown-mermaid`)
- **Zweck:** Mermaid in Markdown-Dateien
- **Features:** 
  - ✅ Mermaid-Rendering in Markdown Preview
  - ✅ Syntax-Highlighting für Mermaid-Code-Blöcke
  - ✅ Live Preview mit Strg+Shift+V
  - ✅ Funktioniert zuverlässig
  - ✅ Keine CLI-Installation nötig

### **Installation:**
```bash
# Über VSCode Extensions Panel
# Suche nach: "Markdown Preview Mermaid Support"
# Installiere: bierner.markdown-mermaid
```

### **Hinweis:**
- **Separate .mermaid Dateien funktionieren nicht** zuverlässig in VSCode
- **Markdown-Dateien mit Mermaid-Code-Blöcken** sind die beste Lösung

## 📁 Dateistruktur (Einfaches Modell)

### **Mermaid-Dateien:**
```
docs/
├── 01-strategy/
│   ├── diagrams/              # Lokale Diagramme (Markdown)
│   └── strategy.md
├── 02-architecture/
│   ├── diagrams/              # Lokale Diagramme (Markdown)
│   └── architecture.md
├── 04-howto/
│   ├── diagrams/              # Lokale Diagramme (Markdown)
│   └── pairing.md
├── _shared/
│   └── diagrams/              # Shared Diagramme (Markdown)
└── 04-howto/development/
    └── mermaid-setup.md       # Diese Anleitung
```

### **Naming Convention:**
- **Dateien:** `kebab-case.md`
- **Beispiele:** `system-overview.md`, `message-flow.md`
- **Verzeichnisse:** `kebab-case/`

## 🎨 Styling-Standards

### **OMF-Farbpalette:**
```mermaid
graph TD
    A[OMF-Komponenten] -->|Action| B[MQTT-Broker]
    style A fill:#e1f5fe  # Blau
    style B fill:#f3e5f5  # Lila
```

### **Standard-Farben:**
- **OMF-Komponenten:** `#e1f5fe` (Blau)
- **MQTT-Broker:** `#f3e5f5` (Lila)
- **Session-Tools:** `#e8f5e8` (Grün)
- **Data-Storage:** `#fff3e0` (Orange)
- **Analysis-Tools:** `#fff3e0` (Orange)
- **External Systems:** `#fce4ec` (Pink)

## 🔄 Workflow

### **1. Diagramm erstellen:**
```bash
# Neue Markdown-Datei erstellen
touch docs/_shared/diagrams/system-overview.md
```

### **2. Mermaid-Code schreiben:**
```markdown
# System Overview

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
    
    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style C fill:#fff3e0
```
```

### **3. Preview testen:**
- **Strg+Shift+V** für Markdown Preview
- **Diagramm wird gerendert** ✅

### **4. In anderen Dateien referenzieren:**
```markdown
![System Overview](../_shared/diagrams/system-overview.md)
```

## 🧪 Testing

### **Test-Diagramme:**
- **Session Manager:** `docs/mermaid-test/test-hybrid.md`
- **Farben:** Alle Standard-Farben testen
- **Preview:** Strg+Shift+V testen

### **Cross-Platform Testing:**
- **macOS:** VSCode mit "Markdown Preview Mermaid Support"
- **Windows:** VSCode mit "Markdown Preview Mermaid Support"
- **Linux:** VSCode mit "Markdown Preview Mermaid Support"

## 📋 Cursor-Anweisungen

### **Für Mermaid-Diagramm-Erstellung:**

1. **Markdown-Datei erstellen:** `.md` Extension verwenden
2. **Mermaid-Code in Code-Block** schreiben
3. **Farben anwenden:** OMF-Farbpalette verwenden
4. **Styling:** Konsistent mit Standards
5. **Naming:** Kebab-case für Dateien

### **Standard-Template:**
```markdown
# Diagramm-Name

```mermaid
graph TD
    A[Source] -->|Action| B[Target]
    style A fill:#e1f5fe
    style B fill:#f3e5f5
```
```

## 🔗 Verweise

- **Test-Directory:** `docs/mermaid-test/`
- **Shared Diagramme:** `docs/_shared/diagrams/`
- **Lokale Diagramme:** `docs/<section>/diagrams/`
- **Styling-Standards:** Diese Datei

---

*Teil der OMF-Dokumentation | [Zurück zur README](../../README.md)*
