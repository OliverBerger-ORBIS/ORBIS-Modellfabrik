# Refactoring-Backlog: OMF Dashboard → omf2 (Streamlit-App)

Dieses Dokument unterstützt das Refactoring des bestehenden OMF Dashboards (Altanwendung) zur neuen, modularen und rollenbasierten Streamlit-App **omf2**.  
Die Tabelle zeigt, wie alte Komponenten/Funktionen in die neue Architektur überführt werden sollen und dokumentiert offene Aufgaben, Prinzipien und Besonderheiten.

---

## Übersicht: Mapping Alt → Neu (Backlog)

| **Alt-Funktion / Komponente**              | **Ziel (omf2 / neue Struktur)**         | **Status** | **Prinzipien / Besonderheiten**                              | **Verantwortlich** |
|--------------------------------------------|-----------------------------------------|------------|-------------------------------------------------------------|--------------------|
| **Rollenbasierte Haupttabs**               | Dynamische Tab-Generierung mit Rollen   |  ✅        | Rollen in config/user_roles.yml, Tabs dynamisch initiiert    | ✅ |
| Operator Tabs (APS Module) | `ui/ccu/modules/ccu_modules_tab.py`     |      ✅         | Modular, Icons, MQ-Integration, Availability Status (READY/BUSY/BLOCKED) | ✅ |
| Operator Tabs (APS Overview) | `ui/ccu/overview/ccu_overview_tab.py`     | offen      | Modular, Icons, i18n, MQ-Integration                        |                    |
| Operator Tabs (APS Aufträge.) | `ui/ccu/orders/ccu_orers_tab.py`     | offen      | Modular, Icons, i18n, MQ-Integration                        |                    |
| Operator Tabs (APS Prozesse.) | `ui/ccu/process/ccu_process_tab.py`     | offen      | Modular, Icons, i18n, MQ-Integration                        |                    |
| Operator Tabs (APS Konfiguration) | `ui/ccu/configuration/ccu_configuration_tab.py`     | offen      | Modular, Icons, i18n, MQ-Integration                        |                    |
| Supervisor-Erweiterungen                   | `ui/nodered/*`, WL Module/System Ctrl| Phase 3      | Tab-Freischaltung via Rolle, modular                         |                    |
| Admin-Tabs (Steering, Message Center, ...) | `ui/admin/steering_tab.py`, ...         | ✅         | Subtabs modular, Fehlerbehandlung, Logging                   |                    |
| **Untertabs**                              | Separate Module in jeweiligem Tab-Ordner| ✅         | z.B. `ui/admin/steering/factory_tab.py`                      |                    |
| Werkstück-Konfiguration                    | `ui/admin/admin_settings/workpiece_subtab.py` | ✅ | Registry Manager, id/nfc_code Struktur, WorkpieceManager | ✅ |
| MQTT-Konfiguration (Settings)              | `ui/admin/admin_settings/dashboard_subtab.py` | ✅ | Registry Manager, Environment-Info, Read-Only | ✅ |
| Topic-/Schema-Konfiguration               | `ui/admin/admin_settings/topics_subtab.py` | ✅ | Registry Manager, Category-basierte Anzeige | ✅ |
| Dynamische Tab-Generierung                 | Zentraler Tab-Renderer                  | offen      | Tabs/Subtabs nach Rolle, i18n, Fehlerfallback                |                    |
| Internationalisierung (DE/EN/FR)           | `common/i18n.py` + UI-Integration       | Phase 2    | Keine Hardcodierung, dynamische Sprachwahl (nach Grundarchitektur) |                    |
| Icons pro Tab                              | `ui/common/symbols.py` (UISymbols)    | ✅         | Zentrale UISymbols-Klasse, konsistente Symbol-Verwendung    | ✅ |
| Komponenten-Loading mit Dummy-Fallback     | Fehlerbehandlung im UI-Loader           | ✅         | Error-Handling in UI-Komponenten, Fallback-Messages        | ✅ |
| MQTT-Client (Singleton, Session State)     | `factory/client_factory.py` + Session   | ✅       | Singleton-Pattern, Threadsafe                                |                    |
| UI-Refresh, Thread-sicher                  | Streamlit request_refresh + Locks       | ✅       | Threadsafe, keine Race Conditions                            |                    |
| Logging (Ring-Buffer)                      | `common/logger.py`, ggf. Buffer-Modul   | ✅       | Modular, strukturierte Logs, anzeigbar im UI                 |                    |
| Umgebungs-Modi (Live/Replay/Mock)          | Sidebar-Radio, session/env-Handling     | ✅       | Default: replay, Einfluss auf Datenquellen                   |                    |

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
- **Assets:**  
  Alle Bilder und Icons zentral in `assets/`.
- **Umgebungsmodi (live/replay/mock):**  
  Umschaltbar, beeinflusst Datenquellen und Verbindungen (z.B. MQTT).

---

## Hinweise zur Umsetzung

- **Status** kann fortlaufend gepflegt werden (offen, in Arbeit, erledigt).
- **Verantwortlich** dient zur Aufgabenverteilung im Team.
- Prinzipien gelten für alle neuen und migrierten Komponenten.
- Bei Unsicherheiten zu Mapping oder Modularisierung dieses Dokument konsultieren.

---

## ✅ ABGESCHLOSSENE PUNKTE (2025-10-02)

### **🎯 VOLLSTÄNDIG IMPLEMENTIERT:**
- ✅ **Rollenbasierte Haupttabs** (Dynamische Tab-Generierung mit Rollen)
- ✅ **Admin-Tabs** (Steering, Message Center, Admin Settings)
- ✅ **Untertabs** (Modulare Struktur in Tab-Ordnern)
- ✅ **Werkstück-Konfiguration** (Registry Manager Integration)
- ✅ **MQTT-Konfiguration** (Registry Manager, Environment-Info)
- ✅ **Topic-/Schema-Konfiguration** (Registry Manager, Category-basierte Anzeige)
- ✅ **Icons pro Tab** (UISymbols-Klasse, konsistente Symbol-Verwendung)
- ✅ **Komponenten-Loading** (Error-Handling, Fallback-Messages)
- ✅ **MQTT-Client** (Singleton-Pattern, Threadsafe)
- ✅ **UI-Refresh** (Threadsafe, keine Race Conditions)
- ✅ **Logging** (Modular, strukturierte Logs)
- ✅ **Umgebungs-Modi** (Live/Replay/Mock, Default: replay)
- ✅ **CCU Modules Tab** (Availability Status: READY/BUSY/BLOCKED, Connection Status, UISymbols)

### **📊 FORTSCHRITT:**
- **Abgeschlossen:** 13/15 technische Punkte (87%)
- **Verbleibend:** 2 Punkte (Dynamische Tab-Generierung, i18n)

---

**Letzte Aktualisierung:** 2025-10-03