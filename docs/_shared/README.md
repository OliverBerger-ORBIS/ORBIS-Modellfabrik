# Shared Diagrams

**Zweck:** Zentrale Bibliothek für wiederverwendbare Diagramme

## 📁 Struktur

```
_shared/
├── diagrams/
│   ├── src/           # .mermaid Quellen
│   └── svg/           # generierte SVGs
└── README.md          # Diese Datei
```

## 🎯 Verwendung

### **In Markdown referenzieren:**
```markdown
<!-- Von einer anderen Sektion -->
![Systemübersicht](../_shared/diagrams/svg/system-overview.svg)

<!-- Von einer Untersektion -->
![Systemübersicht](../../_shared/diagrams/svg/system-overview.svg)
```

### **Neue Diagramme hinzufügen:**
1. **.mermaid Datei** in `diagrams/src/` erstellen
2. **SVG generieren:** `npm run diagrams`
3. **In Markdown referenzieren**

## 🔧 Build-Commands

```bash
# Alle Diagramme generieren
npm run diagrams

# Watch-Modus (automatisch bei Änderungen)
npm run diagrams:watch

# Einzelnes Diagramm generieren
npx mmdc -i diagrams/src/example.mermaid -o diagrams/svg/example.svg
```

## 📋 Naming Convention

- **Dateien:** `kebab-case.mermaid` → `kebab-case.svg`
- **Beispiele:** `system-overview.mermaid`, `message-flow.mermaid`
- **Versionierung:** `deployment_v2.mermaid` oder `deployment_2025-09.mermaid`

---

*Teil der OMF-Dokumentation | [Zurück zur README](../../README.md)*
