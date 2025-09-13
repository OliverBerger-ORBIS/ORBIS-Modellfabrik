# OMF Modellfabrik - Entwicklungsregeln

## 🚨 KRITISCHE REGELN

### 1. KEINE COMMITS VOR TESTS
- **NIEMALS** Commits durchführen bevor alle Implementierungen vollständig getestet wurden
- Jede neue Funktionalität muss erst funktional getestet werden:
  - Dashboard startet ohne Fehler
  - Features funktionieren wie erwartet
  - Keine Runtime-Fehler
  - UI ist bedienbar
- **Tests haben absolute Priorität vor Commits**

### 2. TEST-FIRST DEVELOPMENT
- Implementierung → Test → Fix → Test → Commit
- Nur bei 100% funktionierenden Features committen
- Bei Fehlern: Fix implementieren, erneut testen

### 3. TEST-KATEGORIEN (KRITISCH)
- **Unit-Tests**: Automatische Tests für einzelne Funktionen
- **Integration-Tests**: Tests für Komponenten-Interaktion
- **UI-Tests**: Manuelle Tests der Benutzeroberfläche (KRITISCH)
  - Session Manager: Graph-Visualisierung, alle Tabs funktional
  - OMF-Dashboard: Module Control, alle Komponenten laden
  - Logging-System: Keine Spam-Logs, saubere Ausgabe
- **UI-Tests werden vom Benutzer durchgeführt und Ergebnisse mitgeteilt**

## 📋 AKTUELLE IMPLEMENTIERUNGEN ZUM TESTEN

### ✅ Session Manager:
- [x] Graph-Visualisierung implementiert
- [x] Timezone-Fehler behoben
- [x] Debug-Info hinzugefügt
- [x] **Unit-Tests**: 18 Tests bestehen
- [x] **Integration-Tests**: Läuft ohne Fehler
- [ ] **UI-TESTS**: Session laden, Graph-Features nutzen (Benutzer-Test erforderlich)

### ✅ ModuleStateManager:
- [x] Kern-Logik implementiert
- [x] Dashboard-Integration
- [x] **Unit-Tests**: 18 Tests bestehen
- [x] **Integration-Tests**: Läuft ohne Fehler
- [ ] **UI-TESTS**: Module Control Tab im OMF-Dashboard (Benutzer-Test erforderlich)

### ✅ Logging-System:
- [x] Thread-sicheres Logging implementiert
- [x] Log-Level reduziert
- [x] **Integration-Tests**: Läuft ohne Fehler
- [ ] **UI-TESTS**: Saubere Log-Ausgabe (Benutzer-Test erforderlich)

## 🎯 NÄCHSTE SCHRITTE
1. **UI-TESTS durch Benutzer**: Session Manager, OMF-Dashboard, Logging-System
2. **Benutzer teilt Testergebnisse mit**
3. **Bei erfolgreichen UI-Tests**: Alle Änderungen committen
4. **Bei UI-Test-Fehlern**: Fix implementieren, erneut testen

## 🚨 KRITISCHE REGEL FÜR UI-TESTS
- **UI-Tests sind der kritischste Test-Typ**
- **Nur der Benutzer kann UI-Tests durchführen**
- **Ergebnisse müssen explizit mitgeteilt werden**
- **Kein Commit ohne erfolgreiche UI-Tests**

