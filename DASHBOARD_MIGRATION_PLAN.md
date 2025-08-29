# **Plan: Systematische Lösung der Dashboard-Indentation-Probleme**

## **Ziel**
Eine funktionierende `v2.0.0` Dashboard-Version mit allen gewünschten Features, ohne Indentation-Fehler.

## **1. Präventive Maßnahmen gegen Indentation-Probleme**

### **Formatierungstools installieren:**
```bash
pip install ruff black pre-commit
```

### **Git-Konfiguration:**
- `.gitattributes` ins Repo legen:
```
* text=auto eol=lf
*.py text eol=lf
*.sh text eol=lf
```

### **Editor-Konfiguration:**
- `.editorconfig` für alle IDEs:
```
root = true
[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
```

### **Cursor/VS Code Settings:**
```json
{
  "editor.insertSpaces": true,
  "editor.tabSize": 4,
  "editor.detectIndentation": false,
  "files.eol": "\n",
  "files.trimTrailingWhitespace": true,
  "python.analysis.autoFormatStrings": true,
  "editor.formatOnSave": true
}
```

### **Pre-commit Hooks:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks: [{id: black}]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.8
    hooks: [{id: ruff, args: ["--fix"]}, {id: ruff-format}]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

## **2. Implementierung der Checks**

### **Vor jedem Commit:**
```bash
ruff check . --fix
black .
pre-commit run --all-files
```

### **Streamlit-spezifisch:**
```bash
streamlit run app.py --server.runOnSave=false
```

## **3. Suche nach funktionierender Version**

### **Git-Historie analysieren:**
- Finde die letzte funktionierende Version von heute morgen
- Vergleiche mit `v2.0.0` Tag
- Identifiziere Unterschiede in der Tab-Struktur

## **4. Struktur-Analyse**

### **Gegenüberstellung:**
- **Funktionierende Version:** Aktuelle Tab-Struktur
- **Version (v2.0.0):
  - Overview (mit Sub-Tabs)
  - MQTT Control
  - Node-RED Analysis (eigener Haupt-Tab)
  - Template Library
  - Settings
  - Statistics
  ** Neue Tab-Struktur siehe Abschnitt ganz unten

## **5. Schrittweise Migration**

### **Für jeden Tab:**
1. **Backup** der funktionierenden Version
2. **Implementierung** des neuen Tabs
3. **Test** der Funktionalität
4. **Commit** bei Erfolg
5. **Rollback** bei Fehlern

## **6. Test-Strategie**

### **Nach jeder Änderung:**
```bash
python -m py_compile src_orbis/mqtt/dashboard/aps_dashboard.py
python test_dashboard_startup.py
streamlit run src_orbis/mqtt/dashboard/aps_dashboard.py --server.port=8506
```

## **7. Integration des OrderManagers**

### **Nach erfolgreicher Dashboard-Migration:**
- OrderManager aus dem Stash holen
- Integration in die neue Dashboard-Struktur
- Tests der Order-Funktionalität

## **8. Finale Version**

### **Ziel:**
- Funktionierende `v2.0.0` Dashboard-Version
- Alle gewünschten Features implementiert
- Keine Indentation-Fehler
- Vollständige Test-Abdeckung

## **Commit-Strategie**

### **Häufige Commits:**
- Nach jedem erfolgreichen Tab-Migration
- Nach jeder Formatierung
- Nach jeder Tool-Installation
- **Ziel:** Immer einen funktionierenden Stand haben

---

**Status:** ✅ Tools installiert, Konfiguration erstellt
**Nächster Schritt:** Suche nach funktionierender Version


# ORBIS Modellfabrik Dashboard (OMF)
## Beschreibung der Tab-Struktur
- Overview, 
-- Modul-Status (Modul Info mit aktuellem Status )
-- Bestellung   ( )
-- Bestellung-Rohware
-- Lagerbestand
- Aufträge (Orders)
-- Auftragsverwaltung (Mapping omf-id aus ERP auf aps-ID aus Modellfabrik)
-- Laufende Aufträge (Ongoing Orders mit Production Steps)
- Messages-Monitor (Anzeige der Messages, die über MQTT empfangen werden, (Und die über OMF versendet werden))
- Message-Controls  (Steuerung der Fabrik, Module, etc durch Senden von MQTT-Messages)
- Settings
-- dashboard-Setings
-- Modul-config
-- NFC-Config
-- Topic-Config
-- Messages-Templates (Darstellung und Filterung MessageTemplateManager)

---------
# Analysis-Tabs for Enhanced Users (kann im Dashboard ausgeblendet werden?)
- Session Analyse (Möglichkeit, die Session.db und logs auszuwerten, und aufzunehmen)
- Template-Analyse ( Analyse der Nachrichten aus den Sessions zur ERstellung der MessageTemplate.YAML)
- Replay: Möglichkeit (aufgenommene Session.db auszuwählen und abzuspielen, so als ob tatsächlche Messages eintrudeln)
