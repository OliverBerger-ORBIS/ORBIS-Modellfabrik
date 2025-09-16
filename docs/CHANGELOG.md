# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Geplant
- MessageGenerator Integration
- Replay Station für Dashboard-Tests
- Template-Analyse erweitern

## [3.3.1] - 2025-01-XX

### Hinzugefügt
- Session Manager: Session Analyse
- Timeline-Visualisierung mit Plotly
- Topic-Filterung (Kategorie, Sub-Kategorie, Friendly Name, Topic Name)
- Vorfilter-System für uninteressante Topics
- Zeitfilter für Timeline-Analyse
- Settings-Management für Vorfilter-Konfiguration
- Payload-Analyse und Message-Details

### Geändert
- Projekt-Struktur aufgeräumt
- Dokumentation konsolidiert
- Import-Standards vereinheitlicht

### Behoben
- ImportError für OmfTopicManager
- Vorfilter-Loop-Problem
- Struktur-Validierung implementiert

## [3.3.0] - 2025-01-XX

### Hinzugefügt
- Per-Topic-Buffer Architektur
- MQTT-Singleton Pattern
- Hybrid-Architektur für Publishing
- MessageGenerator Integration
- WorkflowOrderManager

### Geändert
- MessageMonitorService durch OMFMqttClient ersetzt
- Dashboard-Architektur modernisiert
- Template-System erweitert

## [3.2.0] - 2025-01-XX

### Hinzugefügt
- Central Configuration Managers
- YAML-basierte Konfiguration
- NFC Code Manager
- Module Manager
- Topic Manager

### Geändert
- Dashboard auf Streamlit-Basis
- Modulare Architektur implementiert
- Trennung: Produktiv vs. Helper-Apps

## [3.1.2] - 2025-01-XX

### Hinzugefügt
- Erste funktionierende Dashboard-Version
- MQTT-Integration
- Factory Control

### Behoben
- Grundlegende Verbindungsprobleme
- UI-Stabilität

## [3.0.0] - 2025-01-XX

### Hinzugefügt
- Projekt-Restrukturierung
- Orbis-spezifische Komponenten
- Helper-Apps für Session-Management
- Analyse-Tools

### Geändert
- Komplette Architektur-Überarbeitung
- Trennung von Original Fischertechnik
- Moderne Python-Entwicklung

## [2.x.x] - 2024-XX-XX

### Hinzugefügt
- Original Fischertechnik Integration
- Erste MQTT-Experimente
- Grundlegende Dashboard-Entwicklung

### Geändert
- Projekt-Setup
- Entwicklungsumgebung

## [1.x.x] - 2024-XX-XX

### Hinzugefügt
- Initiales Projekt-Setup
- Fischertechnik APS Integration
- Grundlegende Dokumentation

---

## Legende

- **Hinzugefügt** für neue Features
- **Geändert** für Änderungen an bestehenden Funktionalitäten
- **Veraltet** für bald entfernte Features
- **Entfernt** für entfernte Features
- **Behoben** für Bug-Fixes
- **Sicherheit** für Sicherheits-Updates
