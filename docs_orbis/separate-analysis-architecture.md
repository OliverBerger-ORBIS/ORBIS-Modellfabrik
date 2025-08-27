# Separate Analysis Architecture

## Übersicht

Die Template-Analyse wurde aus dem Dashboard entfernt und in separate, unabhängige Tools ausgelagert. Das Dashboard zeigt nur noch die **Template Library** an und ermöglicht die **Dokumentation** der Templates.

## Neue Architektur

### 1. Separate Analyse-Tools

#### TXT Template Analyzer
- **Datei:** `src_orbis/mqtt/tools/txt_template_analyzer.py`
- **Ausführung:** `python3 src_orbis/mqtt/tools/txt_template_analyzer.py`
- **Funktion:** Analysiert alle TXT Controller Topics aus allen Session-Datenbanken
- **Ausgabe:** Speichert Ergebnisse in der Template Library

#### CCU Template Analyzer
- **Datei:** `src_orbis/mqtt/tools/ccu_template_analyzer.py`
- **Ausführung:** `python3 src_orbis/mqtt/tools/ccu_template_analyzer.py`
- **Funktion:** Analysiert alle CCU Topics aus allen Session-Datenbanken
- **Ausgabe:** Speichert Ergebnisse in der Template Library

#### Module Template Analyzer (geplant)
- **Datei:** `src_orbis/mqtt/tools/module_template_analyzer.py`
- **Funktion:** Analysiert Module-spezifische Topics (MILL, DRILL, AIQS, etc.)

### 2. Template Library

#### Persistente Speicherung
- **Datenbank:** `mqtt-data/template_library/template_library.db`
- **Tabellen:** `templates`, `analysis_sessions`
- **Speichert:** Templates, Beispiele, Dokumentation, Analyse-Metriken

#### Dashboard-Integration
- **Anzeige:** Alle gespeicherten Templates mit Filter-Optionen
- **Dokumentation:** Interaktiver Editor für Beschreibung, Verwendung, etc.
- **Beispiele:** Anzeige der Beispielnachrichten mit visueller Trennung

### 3. Dashboard (bereinigt)

#### Entfernte Funktionen
- ❌ Analyse-Buttons (TXT, CCU)
- ❌ `analyze_ccu_topics()` Methode
- ❌ `is_real_message()` Methode
- ❌ Live-Analyse während der Dashboard-Nutzung

#### Verbleibende Funktionen
- ✅ Template Library Anzeige
- ✅ Dokumentations-Editor
- ✅ Template-Filterung und Suche
- ✅ Beispielnachrichten-Anzeige

## Vorteile der neuen Architektur

### 1. Klare Trennung der Verantwortlichkeiten
- **Analyse-Tools:** Führen die eigentliche Arbeit aus
- **Template Library:** Speichert Ergebnisse persistent
- **Dashboard:** Zeigt und verwaltet gespeicherte Daten

### 2. Bessere Performance
- Keine Blockierung des Dashboards während der Analyse
- Analyse läuft unabhängig und kann im Hintergrund laufen
- Dashboard lädt nur gespeicherte Daten

### 3. Einfachere Wartung
- Jedes Tool hat eine klare, einzelne Aufgabe
- Fehler in der Analyse blockieren nicht das Dashboard
- Einfacheres Debugging und Testing

### 4. Schrittweise Entwicklung
- Templates werden einzeln analysiert (TXT → CCU → Module)
- Ergebnisse werden persistent gespeichert
- Dashboard zeigt immer den aktuellen Stand

## Verwendung

### 1. Neue Analyse durchführen
```bash
# TXT Templates analysieren
python3 src_orbis/mqtt/tools/txt_template_analyzer.py

# CCU Templates analysieren  
python3 src_orbis/mqtt/tools/ccu_template_analyzer.py
```

### 2. Dashboard öffnen
```bash
streamlit run src_orbis/mqtt/dashboard/aps_dashboard.py
```

### 3. Template Library nutzen
- **Einstellungen** → **MQTT Templates** Tab
- Alle gespeicherten Templates anzeigen
- Dokumentation bearbeiten und speichern
- Beispiele durchsuchen

## Status

### ✅ Abgeschlossen
- TXT Template Analyzer (separat)
- CCU Template Analyzer (separat)
- Template Library (persistent)
- Dashboard ohne Analyse-Buttons

### 🔄 In Arbeit
- Dashboard-Tests ohne Analyse-Funktionalität
- Template Library Anzeige optimieren

### 📋 Geplant
- Module Template Analyzer
- Erweiterte Template-Filter
- Export-Funktionen für Dokumentation

## Migration von der alten Architektur

### Was sich geändert hat
1. **Analyse-Buttons entfernt** - Keine Live-Analyse mehr im Dashboard
2. **Separate Tools** - Analyse läuft über Kommandozeile
3. **Persistente Speicherung** - Ergebnisse werden in SQLite gespeichert
4. **Dashboard fokussiert** - Nur noch Anzeige und Verwaltung

### Was gleich geblieben ist
1. **Template Library Anzeige** - Alle gespeicherten Templates sind sichtbar
2. **Dokumentations-Editor** - Interaktive Bearbeitung weiterhin möglich
3. **Beispielnachrichten** - Anzeige der echten Nachrichten
4. **Filter und Suche** - Durchsuchen der Template Library

## Troubleshooting

### Dashboard startet nicht
- Prüfe, ob alle Imports korrekt sind
- Entfernte Methoden sollten nicht mehr referenziert werden

### Keine Templates angezeigt
- Führe zuerst eine Analyse mit den separaten Tools durch
- Prüfe, ob die Template Library Datenbank existiert

### Analyse-Tools funktionieren nicht
- Prüfe Session-Datenbanken in `mqtt-data/sessions/`
- Prüfe Berechtigungen für Template Library Verzeichnis
- Führe Tools mit Python 3 aus
