## Projektstruktur und Prinzipien für omf2

Dieses Dokument beschreibt die Zielstruktur, Modularisierung und zentrale Prinzipien für die Entwicklung von **omf2** innerhalb der ORBIS-Modellfabrik.  
Es dient als Referenz für alle Teammitglieder und als Vorgabe für Coding Agents.

---

## 1. Grundstruktur omf2 (nach Registry-Umzug ins Projekt-Root)
vor dem Umzug befindet sich die registry in omf2/registry

```
registry/
  model/
    v1/
      workpieces.yml
      ...
  schemas/
    workpieces.schema.json
    ...
  manager/
    registry_manager.py
    workpiece_registry_manager.py
    ...
omf2/
  assets/
    logos/
      orbis_logo.png
      ...
    icons/
      module.png
      module.svg
      ...
    templates/
      base.html
      custom_template.html
      ...
  ccu/
    ccu_gateway.py
    ccu_mqtt_client.py
    workpiece_manager.py
    helpers/
      ccu_factory_layout.py
  nodered/
    nodered_gateway.py
    nodered_pub_mqtt_client.py
    nodered_sub_mqtt_client.py
    helpers/
      nodered_utils.py
  admin/
    admin_gateway.py
    admin_mqtt_client.py
    logs_manager.py
    helpers/
      admin_utils.py
  ui/
    ccu/
      ccu_overview/
        ccu_overview_tab.py                     # aps_overview
      ccu_orders/
        ccu_orders_tab.py                       # aps_orders
      ccu_process/
        ccu_process_tab.py                      # aps_processes
      ccu_configuration/
        ccu_configuration_tab.py                # aps_configuration
        ccu_factory_configuration_subtab.py     # Untertab Konfiguration
        ccu_parameter_configuration_subtab.py   # Untertab Konfiguration
      ccu_modules/
        ccu_modules_tab.py                      # aps_modules
    nodered/
      nodered_overview/
        nodered_overview_tab.py
      nodered_processes/
        nodered_processes_tab.py
    admin/
      generic_steering/
        generic_steering_tab.py
      message_center/
        message_center_tab.py
      admin_settings/
        admin_settings_tab.py
        workpiece_subtab.py
        dashboard_subtab.py
        module_subtab.py
        mqtt_subtab.py
        topics_subtab.py
        templates_subtab.py
      logs/
        logs_tab.py
    components/
      factory_layout.py
      custom_button.py
      status_indicator.py
  config/
    mqtt_settings.yml
    user_roles.yml
    apps.yml
  factory/
    client_factory.py
    gateway_factory.py
  tests/
    ccu/
      test_ccu_gateway.py
      test_workpiece_manager.py
    nodered/
      test_nodered_gateway.py
    message_center/
      test_message_center_gateway.py
    generic_steering/
      test_generic_steering_gateway.py
    system/
      test_admin_settings.py
      test_logs.py
  common/
    i18n.py
    logger.py
    ...
```

---

## 2. Prinzipien & Verantwortlichkeiten

### **Registry (nach erfolgtem refactoring im Projekt-Root)**
- Enthält **alle fachlichen Modelle, Schemata und Registry-Manager**.
- `manager/` innerhalb von `registry/` enthält alle Klassen, die den Zugriff, das Parsen und die Validierung der Registry-Daten kapseln (z. B. `registry_manager.py`, `workpiece_registry_manager.py`).

### **Assets**
- Der Ordner `omf2/assets/` dient als zentrale Ablage für alle statischen Ressourcen, die in der UI verwendet werden.
  - **logos/**: Firmen- und Produktlogos.
  - **icons/**: PNG, SVG, und andere Icon-Grafiken (z. B. für Module oder Statusanzeigen).
  - **templates/**: HTML-Templates für UI, Reports, E-Mails etc.
- Assets werden in der UI direkt aus diesem Verzeichnis geladen und versioniert.

### **Factory-Pattern**
- Zentral für die Erzeugung/Verwaltung von Singleton-Clients und Gateways.
- Ablage in `omf2/factory/` (z. B. `client_factory.py`, `gateway_factory.py`).
- Nutze Factories immer, wenn Clients/Gateways domänenübergreifend oder konfigurierbar erstellt werden sollen.

### **Modulare Domänenstruktur**
- Jede Domäne (`ccu`, `nodered`, `admin`) erhält ein eigenes Verzeichnis in `omf2/`
- `nodered/` enthält zwei MQTT-Clients: `nodered_pub_mqtt_client.py` und `nodered_sub_mqtt_client.py`.
- Wiederverwendbare, aber **nur domänenintern** genutzte Komponenten in `helpers/`-Unterordner innerhalb der jeweiligen Domäne.
  - **MQTT-Client (Singleton):** `<domäne>_mqtt_client.py`
  - **Gateway:** `<domäne>_gateway.py`
  - **(optional) Manager:** Für Entitäten, z. B. `workpiece_manager.py`

### **Spezialisierte Manager vs. Registry-Manager**
- **Registry-Manager** (z. B. `registry/manager/workpiece_registry_manager.py`):
  - Zuständig für das Laden, Validieren und reine Daten-Handling von Entitäten aus der Registry.
  - Kennt nur die Struktur und Schemata der Registry, ist *nicht* domänenspezifisch.
  - Stellt Methoden bereit wie `get_workpiece_definition()`, `validate_against_schema()`, etc.
- **Domänenspezifische Manager** (z. B. `omf2/ccu/workpiece_manager.py`):
  - Übernehmen die fachliche/geschäftslogische Verwaltung der Entitäten im Anwendungskontext (z. B. Lebenszyklus, Statuswechsel, Zuordnung, Abläufe).
  - Arbeiten mit Instanzen/Objekten, steuern Abläufe/Prozesse und nutzen dazu ggf. die Registry-Manager als Datenquelle.
  - Stellt Methoden bereit wie `add_workpiece()`, `assign_to_machine()`, `update_workpiece_state()`, etc.

**Beispiel:**  
- Der Registry-Manager lädt und validiert alle Workpiece-Definitionen aus YAML/JSON.
- Der domänenspezifische Manager (z. B. im CCU-Modul) nutzt diese Definitionen, um konkrete Workpieces im Betriebsablauf zu verwalten und zu steuern.

### **UI**
- **Jeder Haupt-Tab und Subtab liegt immer in einem eigenen Unterordner** im jeweiligen Bereich unter `ui/`.  
  Das gilt auch für Tabs ohne Subtabs – damit bleibt die Struktur konsistent und zukunftssicher.
- Beispiel:
    - `ui/ccu/ccu_overview/ccu_overview_tab.py`
    - `ui/ccu/ccu_configuration/ccu_configuration_tab.py`
    - `ui/ccu/ccu_configuration/ccu_factory_configuration_subtab.py`
    - `ui/admin/admin_settings/workpiece_subtab.py`
- **Wiederverwendbare UI-Komponenten** (z.B. `factory_layout.py`, `status_indicator.py`) liegen in `ui/components/`.

### **Config**
- Technische, betreiberspezifische und laufzeitveränderliche Einstellungen in `omf2/config/`.

### **Tests**
- Tests werden nach Domänen/Modulen in `omf2/tests/<domäne>/` abgelegt.
- Wo sinnvoll, Trennung von Unit- und Integration-Tests.

### **Common**
- Gemeinsame Utilities, Logger, i18n etc. zentral unter `omf2/common/`.

---

## 3. Migration und Übertrag von Quellen

- **Bei Bedarf** können Sourcen (z.B. Gateways, Manager, Modelle) aus `omf/`, `registry/model/v1/` oder anderen Alt-Verzeichnissen übernommen werden.
- Die Übernahme erfolgt ggf. als Kopie, Anpassung an die neue Struktur und Benennung.
- Die Migration von Workpieces und Schemata erfolgt von `registry/model/v1/workpieces.yml` und `registry/schemas/workpieces.schema.json` nach `omf2/registry/model/v2/` bzw. `omf2/registry/schemas/`.

---

## 4. Namenskonventionen
- Siehe Beispiele in der Struktur oben.
- Keine Bindestriche, sondern Unterstriche.
- Klar sprechende Namen.

- **Dateien:** `<domäne>_mqtt_[pub|sub]_client.py`, `<domäne>_gateway.py`, `workpiece_manager.py` usw.
- **Klassen:** `CCUGateway`, `NodeRedGateway`, `MessageCenterGateway`, `WorkpieceManager` etc.
- **Configs/Schemas:** Klar sprechende Namen, z. B. `mqtt_settings.yml`, `user_roles.yml`, `workpieces.schema.json`.

---

## 5. Prinzipien für zukünftige Aufgaben und Coding Agents

- **Strukturierte Ablage:** Jede neue Komponente/Manager/Client wird nach diesem Muster angelegt.
- **Modularität:** Domänenübergreifende oder -spezifische Logik strikt trennen.
- **Referenzmigration:** Bei neuen Aufgaben prüfen, ob Altbestand übernommen werden muss (siehe Punkt 3).
- **Tests & Dokumentation:** Jede neue Komponente wird mit passenden Tests und Docstrings/README versehen.
- **Referenz auf dieses Dokument:** Jede Aufgabenbeschreibung für Coding Agents, die die Projektstruktur betreffen, soll auf dieses Dokument verweisen.

---

## 6. Beispiel für die Referenz in Coding-Agent-Aufgaben

> **Bitte beachte die Vorgaben aus `omf2/projekt-struktur-omf2.md` für die Ablage, Benennung und Modularisierung!**

---

**Letzte Aktualisierung:** 2025-09-27