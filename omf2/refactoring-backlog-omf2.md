# Refactoring-Backlog: OMF Dashboard → omf2 (Streamlit-App)

Dieses Dokument unterstützt das Refactoring des bestehenden OMF Dashboards (Altanwendung) zur neuen, modularen und rollenbasierten Streamlit-App **omf2**.  
Die Tabelle zeigt, wie alte Komponenten/Funktionen in die neue Architektur überführt werden sollen und dokumentiert offene Aufgaben, Prinzipien und Besonderheiten.

---

## Übersicht: Mapping Alt → Neu (Backlog)

| **Alt-Funktion / Komponente**              | **Ziel (omf2 / neue Struktur)**         | **Status** | **Prinzipien / Besonderheiten**                              | **Verantwortlich** |
|--------------------------------------------|-----------------------------------------|------------|-------------------------------------------------------------|--------------------|
| **Rollenbasierte Haupttabs**               | Dynamische Tab-Generierung mit Rollen   | offen      | Rollen in config/user_roles.yml, Tabs dynamisch initiiert    |                    |
| Operator Tabs (APS Overview, Orders, etc.) | `ui/operator/overview_tab.py` etc.      | offen      | Modular, Icons, i18n, MQ-Integration                        |                    |
| Supervisor-Erweiterungen                   | `ui/supervisor/*`, WL Module/System Ctrl| offen      | Tab-Freischaltung via Rolle, modular                         |                    |
| Admin-Tabs (Steering, Message Center, ...) | `ui/admin/steering_tab.py`, ...         | offen      | Subtabs modular, Fehlerbehandlung, Logging                   |                    |
| **Untertabs**                              | Separate Module in jeweiligem Tab-Ordner| offen      | z.B. `ui/admin/steering/factory_tab.py`                      |                    |
| Werkstück-Konfiguration                    | `ui/admin/admin_settings/workpiece_subtab.py` | ✅ | Registry Manager, id/nfc_code Struktur, WorkpieceManager | ✅ |
| MQTT-Konfiguration (Settings)              | `ui/admin/admin_settings/dashboard_subtab.py` | ✅ | Registry Manager, Environment-Info, Read-Only | ✅ |
| Topic-/Template-Konfiguration              | `ui/admin/admin_settings/topics_subtab.py` | ✅ | Registry Manager, Category-basierte Anzeige | ✅ |
| Dynamische Tab-Generierung                 | Zentraler Tab-Renderer                  | offen      | Tabs/Subtabs nach Rolle, i18n, Fehlerfallback                |                    |
| Internationalisierung (DE/EN/FR)           | `common/i18n.py` + UI-Integration       | offen      | Keine Hardcodierung, dynamische Sprachwahl                   |                    |
| Icons pro Tab                              | `assets/icons/`                         | offen      | UI lädt Icons dynamisch, fallback bei fehlenden Icons        |                    |
| Komponenten-Loading mit Dummy-Fallback     | Fehlerbehandlung im UI-Loader           | offen      | Dummy-Komponenten bei Fehlermeldung                          |                    |
| MQTT-Client (Singleton, Session State)     | `factory/client_factory.py` + Session   | offen      | Singleton-Pattern, Threadsafe                                |                    |
| UI-Refresh, Thread-sicher                  | Streamlit request_refresh + Locks       | offen      | Threadsafe, keine Race Conditions                            |                    |
| Logging (Ring-Buffer)                      | `common/logger.py`, ggf. Buffer-Modul   | offen      | Modular, strukturierte Logs, anzeigbar im UI                 |                    |
| Umgebungs-Modi (Live/Replay/Mock)          | Sidebar-Radio, session/env-Handling     | offen      | Default: replay, Einfluss auf Datenquellen                   |                    |

---

## Technische Architektur-Prinzipien (im Refactoring zu beachten)

- **Rollenbasierte Zugriffe:**  
  Tab- und Funktionsfreischaltung strikt nach Rolle – Definition in `config/user_roles.yml`.
- **Modularer, getrennter Tab/Subtab-Aufbau:**  
  Jede Funktion/Tab/Subtab als eigenes, wiederverwendbares Modul.
- **Dynamische Tab-Generierung:**  
  Tabs und Subtabs werden abhängig von User-Rolle, Sprache und Kontext dynamisch gerendert.
- **Internationalisierung:**  
  Alle UI-Strings über i18n-Mechanismus, keine Hardcodierung.
- **Fehlertoleranz & Dummy-Fallback:**  
  UI-Komponenten laden fehlertolerant, bei Fehlern Dummy-Komponente darstellen.
- **Singleton/Session für technische Komponenten:**  
  z.B. MQTT-Client per Factory und Singleton, Session-State-Verwaltung.
- **Logging:**  
  Strukturiertes, modular nutzbares Logging mit Ring-Buffer, Anzeige im Log-Tab.
- **Assets & Templates:**  
  Alle Bilder, Templates und Icons zentral in `assets/`.
- **Umgebungsmodi (live/replay/mock):**  
  Umschaltbar, beeinflusst Datenquellen und Verbindungen (z.B. MQTT).

---

## Hinweise zur Umsetzung

- **Status** kann fortlaufend gepflegt werden (offen, in Arbeit, erledigt).
- **Verantwortlich** dient zur Aufgabenverteilung im Team.
- Prinzipien gelten für alle neuen und migrierten Komponenten.
- Bei Unsicherheiten zu Mapping oder Modularisierung dieses Dokument konsultieren.

---

**Letzte Aktualisierung:** 2025-09-27