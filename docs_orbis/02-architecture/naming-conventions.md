# Naming Conventions

Version: 0.1 (Draft)  
Last updated: 2025-09-14  
Author: OMF Development Team  

---

## 📑 Overview
Dieses Dokument beschreibt die Namenskonventionen im OMF Projekt.  

---

## 🧩 Topics
- `ccu/...`
- `module/v1/ff/{serial}/...`
- `fts/v1/ff/{id}/...`
- `module/v1/ff/NodeRed/{serial}/...`

---

## 📂 Template Keys
- `template_structure`
- `examples`
- `validation_rules`

---

## 🆔 IDs
- **orderId** – UUID, global konsistent
- **subOrderId** – fortlaufende Sequenznummer
- **actionId** – eindeutige ID je Aktion
- **workpieceId** – NFC-Code (friendly_id nur Anzeige)
- **moduleId** – Seriennummer des Moduls

---

## 📄 Dateinamen
- Kleinbuchstaben, snake_case (`module_state.yml`)
- Versionen in `metadata.version` pflegen
