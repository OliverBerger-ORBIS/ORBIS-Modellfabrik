# OMF Dashboard - Modulare Streamlit-App

Eine modulare Streamlit-Dashboard-Anwendung für die ORBIS Modellfabrik mit Logging, Internationalisierung (i18n), Registry-/Config-Struktur und umfassender Testabdeckung.

## 🚀 Schnellstart

### Installation und Start

1. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Dashboard starten:**
   ```bash
   streamlit run omf_dashboard.py
   ```

3. **Zugriff:** Die App ist verfügbar unter `http://localhost:8501`

## 🏗️ Architektur

### Hauptkomponenten

- **`omf_dashboard.py`** - Haupteinstiegspunkt der Anwendung
- **`omf2/ui/system/`** - System-UI-Komponenten (Settings, Logs)
- **`omf2/ui/message_center/`** - Message Center Komponenten
- **`omf2/common/i18n.py`** - Internationalisierung
- **`omf2/registry/`** - Registry-Struktur für fachliche Modelle
- **`omf2/config/`** - Konfigurationsdateien
- **`omf2/tests/`** - Test-Suite

### Modularität

Jeder Tab ist als eigenständiges Modul implementiert:

```
omf2/ui/
├── system/
│   ├── settings_tab.py      # Einstellungen-Tab
│   ├── logs_tab.py          # Protokoll-Tab
│   └── workpiece_subtab.py  # Werkstück-Subtab
└── message_center/
    └── message_center_tab.py # Nachrichten-Zentrale
```

## 📋 Tabs und Features

### 1. Settings Tab (⚙️ Einstellungen)
- **Workpiece Subtab:** Werkstück-Konfiguration mit Registry-Integration
- **General Subtab:** Allgemeine App-Einstellungen
- **System Subtab:** System-spezifische Konfiguration

### 2. Logs Tab (📋 Protokolle)
- Live-Log-Anzeige mit Filterung nach Log-Level
- Auto-Refresh-Funktionalität
- Log-History mit Ring-Buffer
- Farbcodierte Log-Ausgabe

### 3. Message Center Tab (💬 Nachrichten-Zentrale)
- Interne Nachrichten-Kommunikation
- Nachrichtentypen: Info, Warnung, Fehler, Anfrage
- Prioritätsstufen und Archivierung
- Statistiken und Schnell-Aktionen

## 🔧 Logging-System

### Zentrale Konfiguration
Das Logging wird zentral in der `main()`-Funktion konfiguriert:

```python
def setup_logging():
    """Zentrales Logging-Setup"""
    root_logger, listener = configure_logging(
        app_name="omf_dashboard",
        level=logging.INFO,
        log_dir="logs",
        console_pretty=True
    )
```

### Logger-Ausgaben
Jede Tab-Komponente gibt beim ersten Rendern eine Startmeldung aus:

```python
def show_settings_tab(logger: logging.Logger):
    logger.info("Settings Tab geöffnet")
```

### Log-Anzeige
- Logs werden in Echtzeit im **Logs-Tab** angezeigt
- Ring-Buffer speichert die letzten 1000 Log-Einträge
- Filterung nach Log-Level (DEBUG, INFO, WARNING, ERROR)

## 🌍 Internationalisierung (i18n)

### Sprachunterstützung
- **Deutsch (de)** - Standard
- **Englisch (en)** - Vollständig unterstützt

### Übersetzungsmodul
```python
from omf2.common.i18n import translate, get_current_language, set_language

# Übersetzung abrufen
title = translate("settings_title", current_lang)

# Sprache ändern
set_language("en")
```

### Sprachauswahl
Benutzer können die Sprache über die Sidebar ändern. Die Einstellung wird in der Session persistiert.

## 🗄️ Registry-Struktur

### Registry-Modell v1
```
omf2/registry/model/v1/
├── manifest.yml              # Version und Kompatibilität
├── entities/
│   └── workpieces.yml        # Werkstück-Definitionen
├── mappings/                 # Topic-Template-Mappings
├── templates/                # Message-Templates
└── schemas/                  # JSON-Schemas für Validierung
```

### Workpiece-Definition
```yaml
workpiece_types:
  standard_a:
    name: "Standard Werkstück A"
    dimensions: "100x50x25"
    weight: 250
    material: "aluminium"
    processing_steps: ["drill", "mill", "inspect"]
    nfc_codes: ["NFC_STD_A_001", "NFC_STD_A_002"]
```

## ⚙️ Konfiguration

### Konfigurationsdateien
```
omf2/config/
├── settings.yml        # App-Grundeinstellungen
├── user_roles.yml      # Benutzerrollen und Berechtigungen
├── feature_flags.yml   # Feature-Flags für A/B-Testing
└── secrets.env         # Secrets (nicht in VCS)
```

### Beispiel: settings.yml
```yaml
app:
  name: "OMF Dashboard"
  version: "2.0.0"
  debug: false
  log_level: "INFO"

dashboard:
  theme: "light"
  auto_refresh: true
  language: "de"
```

## 🧪 Test-Suite

### Test-Struktur
```
omf2/tests/
├── test_settings.py        # Settings-Tab Tests
├── test_logs.py           # Logs-Tab Tests
├── test_message_center.py # Message Center Tests
└── test_i18n.py          # i18n Tests
```

### Tests ausführen
```bash
# Alle Tests
pytest omf2/tests/

# Spezifische Tests
pytest omf2/tests/test_settings.py -v

# Mit Coverage
pytest omf2/tests/ --cov=omf2
```

### Test-Kategorien
- **Import-Tests:** Überprüfen Module-Importe
- **Rendering-Tests:** UI-Komponenten-Rendering
- **Funktionalitäts-Tests:** Geschäftslogik-Validierung
- **Integration-Tests:** Komponentenübergreifende Tests

## 🔒 Sicherheit

### Secrets-Management
- Secrets werden in `omf2/config/secrets.env` verwaltet
- **Wichtig:** `secrets.env` niemals in Version Control committen
- Environment-spezifische Konfiguration über Umgebungsvariablen

### User-Rollen
Unterstützte Rollen in `user_roles.yml`:
- **Operator:** Basis-Zugriff (Logs, Messages)
- **Supervisor:** Erweitert (+ Settings, Workpiece)
- **Admin:** Vollzugriff (alle Features)

## 🚀 Deployment

### Lokale Entwicklung
```bash
streamlit run omf_dashboard.py
```

### Production
```bash
streamlit run omf_dashboard.py --server.port 8501 --server.address 0.0.0.0
```

### Docker (optional)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "omf_dashboard.py", "--server.address", "0.0.0.0"]
```

## 📊 Monitoring

### Health-Check
- **Logs-Tab:** Zeigt System-Status und Logs
- **Message Center:** Interne Kommunikation und Benachrichtigungen
- **Settings:** System-Diagnostics verfügbar

### Performance
- Ring-Buffer für Logs (max 1000 Einträge)
- Lazy-Loading für UI-Komponenten
- Session-State-Management für persistente Daten

## 🔧 Entwicklung

### Code-Struktur
- **Modulare Komponenten:** Jeder Tab als eigenständiges Modul
- **Dependency Injection:** Logger wird an Komponenten übergeben
- **Separation of Concerns:** UI, Business Logic, Konfiguration getrennt

### Erweiterungen
Neue Tabs hinzufügen:

1. **Tab-Modul erstellen:** `omf2/ui/new_component/new_tab.py`
2. **Import hinzufügen:** In `omf_dashboard.py`
3. **Tab-Konfiguration:** Tab-Liste in `main()` erweitern
4. **Tests schreiben:** `omf2/tests/test_new_component.py`

### Debugging
- Debug-Logs über `logger.debug()`
- Streamlit-Debug-Mode: `streamlit run --logger.level debug`
- Browser-Konsole für Frontend-Debugging

## 📚 Weitere Ressourcen

- **Streamlit Docs:** https://docs.streamlit.io/
- **Python Logging:** https://docs.python.org/3/library/logging.html
- **YAML Configuration:** https://pyyaml.org/wiki/PyYAMLDocumentation
- **pytest Testing:** https://docs.pytest.org/

---

**Version:** 2.0.0  
**Erstellt:** 2025-01-25  
**Autor:** OMF Development Team