# OMF Documentation Hub

**Orbis Modellfabrik - "Code as Doc" Documentation**

## 🎯 Quick Start

- **Neue Teammitglieder:** Starte mit [Strategy Vision](01-strategy/vision.md) → [System Context](02-architecture/system-context.md)
- **Entwickler:** [Registry Model](02-architecture/registry-model.md) → [How-Tos](04-howto/)
- **Architekten:** [Decision Records](03-decision-records/) → [Architecture](02-architecture/)

## 📚 Documentation Structure

### 01-Strategy
- [Vision](01-strategy/vision.md) - MQTT-first Leitidee & v1-Zielbild
- [Goals](01-strategy/goals.md) - Erfolgskriterien & Qualitätsmerkmale
- [Scope](01-strategy/scope.md) - v1 vs. v1.1/2.0 Ausblick

### 02-Architecture
- [System Context](02-architecture/system-context.md) - Kontextdiagramm (CCU, Module, Node-RED, OMF)
- [Message Flow](02-architecture/message-flow.md) - End-to-End-Flows (Order→Module, State→Dashboard)
- [APS Physical Architecture](02-architecture/aps-physical-architecture.md) - Fischertechnik Netzwerk & Hardware
- [APS Data Flow](02-architecture/aps-data-flow.md) - Datenverarbeitung & Storage
- [Registry Model](02-architecture/registry-model.md) - Registry-Prinzipien & Versionierung
- [Naming Conventions](02-architecture/naming-conventions.md) - Topics, Template-Keys, IDs

### 03-Decision Records (ADRs)
- [ADR-0001: Topic-free Templates](03-decision-records/ADR-0001-registry-topic-free-templates.md)
- [ADR-0002: Exact Overrides per Serial](03-decision-records/ADR-0002-exact-overrides-per-serial.md)

### 04-How-To
- [Add a New Module](04-howto/add-a-new-module.md) - Template → Mapping → Tests
- [Define a New Topic](04-howto/define-a-new-topic.md) - Pattern vs. Exact
- [Build and Run](04-howto/build-and-run.md) - OMF Dashboard & Session-Manager
- [Validate and Release](04-howto/validate-and-release.md) - Make-Targets & Versioning

#### Communication
- [MQTT Integration](04-howto/communication/mqtt/dashboard-mqtt-integration.md) - Dashboard MQTT-Integration
- [MQTT Replay Pattern](04-howto/communication/mqtt-replay-pattern.md) - Replay-Workflow-Dokumentation

#### Configuration
- [Module Configuration](04-howto/configuration/module-configuration-guide.md) - Modul-Konfiguration und Icons
- [NFC Code Configuration](04-howto/configuration/nfc-code-configuration-guide.md) - NFC-Code-Konfiguration
- [Topic Configuration](04-howto/configuration/topic-configuration-guide.md) - Topic-Konfiguration und Priority-Filter

#### Troubleshooting
- [Black/Ruff Loop Problem](04-howto/troubleshooting/BLACK_RUFF_LOOP_PROBLEM.md) - Code-Formatierung-Probleme
- [Critical Bug Fix](04-howto/troubleshooting/critical-bug-fix-module-id-mapping.md) - Modul-ID-Mapping-Fix

### 05-Reference
- [Topics](05-reference/topics.md) - Logische Topic-Gruppen
- [Templates](05-reference/templates.md) - Template-Index & Migration Mapping
- [Enums](05-reference/enums.md) - Zentrale Listen (Availability/Action/Workpiece)

### 99-Glossary
- [Glossary](99-glossary.md) - Eindeutige Begrifflichkeiten & IDs

## 🔗 Quick Links

- **Registry:** `registry/model/v1/` - Single Source of Truth
- **Source Code:** `src_orbis/` - Runtime & Tools
- **Legacy Docs:** [Archive](archive/) - Veraltete Dokumentation

## 🚀 Getting Started

1. **Verstehe das System:** [Vision](01-strategy/vision.md) (5 Min)
2. **Architektur verstehen:** [System Context](02-architecture/system-context.md) (10 Min)
3. **Registry-Prinzipien:** [Registry Model](02-architecture/registry-model.md) (5 Min)
4. **Praktisch arbeiten:** [How-Tos](04-howto/) (je nach Aufgabe)

---

**"Code as Doc" - Registry ist die Quelle der Wahrheit, Docs erklären das Warum und Wie.**