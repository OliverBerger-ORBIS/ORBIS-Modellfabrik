# **OMF Dashboard - Entwicklungsregeln**

## **🎯 Grundprinzipien**

### **1. Einfaches Grundgerüst**
- **Keine Überladung** mit nicht notwendiger Funktionalität
- **Minimaler Code** für maximale Übersichtlichkeit
- **Schritt-für-Schritt** Entwicklung
- **Tests nach jeder Änderung**

### **2. Sichere Vorgehensweise**
- **DASHBOARD_MIGRATION_PLAN** befolgen
- **Häufige Commits** nach jedem erfolgreichen Schritt
- **Rollback bei Fehlern** möglich
- **Immer funktionierenden Stand** haben

### **3. Saubere Architektur**
- **Trennung:** Produktiv-Dashboard vs. Analysis-Tools
- **Modulare Komponenten** in separaten Dateien
- **Klare Import-Pfade** und Abhängigkeiten
- **Zweisprachigkeit:** Source-Namen EN, UI-Namen DE

### **4. Datenstruktur**
- **Neue `omf-data/`** Struktur verwenden
- **Session-Daten** organisiert ablegen
- **Git-freundlich** (große Dateien ignorieren)

## **📋 Dashboard-Tab-Struktur (Aktuell)**

### **Produktiv-Dashboard (OMF)**
1. **Übersicht**
   - Modul-Status
   - Lagerbestand
   - Kundenaufträge
   - Rohmaterial-Bestellungen
2. **Fertigungsaufträge**
   - Fertigungsauftrags-Verwaltung
   - Laufende Fertigungsaufträge
3. **Nachrichtenzentrale**
   - MQTT-Messages anzeigen
4. **Steuerung**
   - Factory-Steuerung
   - Generic-Steuerung
5. **Einstellungen**
   - Dashboard-Settings
   - Modul-Config
   - NFC-Config
   - MQTT-Config
   - Topic-Config
   - Messages-Templates

### **Analysis-Tools (Separate Anwendung)**
- Session Analyse
- Template-Analyse
- Replay-Tool

## **🔧 Entwicklungsphasen**

### **Phase 1: Grundgerüst** ✅
- [x] Verzeichnisstruktur erstellen
- [x] Dokumentation erstellen
- [x] Einfaches Dashboard-Grundgerüst
- [x] Basis-Tab-Struktur
- [x] Konfiguration

### **Phase 2: Komponenten-Migration** ✅
- [x] Module Status aus V2.0.0 übernehmen
- [x] MessageTemplate Manager integrieren
- [x] MQTT-Integration
- [x] Dashboard2 → Dashboard Migration

### **Phase 3: Neue Features** ✅
- [x] Overview Components (Lagerbestand, Kundenaufträge, Rohmaterial-Bestellungen)
- [x] Production Order Components (Auftragsverwaltung, Laufende Aufträge)
- [x] HTML Templates für visuelle Darstellung
- [x] Namenskonvention (Customer/Purchase/Production Orders)

### **Phase 4: Aktuelle Entwicklung** 🔄
- [ ] Production Order Management vollständig implementieren
- [ ] Production Order Current vollständig implementieren
- [ ] Topic-Dokumentation für alle Module
- [ ] Advanced Workflow Management

## **🧪 Test-Strategie**

### **Nach jeder Änderung:**
```bash
python -m py_compile src_orbis/omf/dashboard/omf_dashboard.py
streamlit run src_orbis/omf/dashboard/omf_dashboard.py --server.port=8506
```

### **Commit-Strategie**
- Häufige Commits nach jedem erfolgreichen Schritt
- Immer einen funktionierenden Stand haben
- Rollback bei Fehlern möglich

## **❌ Was NICHT machen:**
- **Überladung** mit nicht notwendiger Funktionalität
- **Komplexe Abhängigkeiten** ohne Tests
- **Große Änderungen** ohne Zwischencommits
- **Analysis-Tools** ins Haupt-Dashboard

## **✅ Was machen:**
- **Einfaches Grundgerüst** erstellen
- **Schritt-für-Schritt** entwickeln
- **Tests nach jeder Änderung**
- **Saubere Komponenten-Trennung**

---

**Status:** ✅ Regeln definiert und aktualisiert
**Nächster Schritt:** Production Order Management vollständig implementieren
