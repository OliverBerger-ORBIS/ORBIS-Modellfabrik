# **Anforderungen: Sequenzielle Steuerungsbefehle in logischer Klammer mit UI-Unterstützung (Finale Version)**

## ** Problemstellung**

Die ORBIS Modellfabrik benötigt ein System zur **sequenziellen Ausführung von Steuerungsbefehlen** mit **UI-Unterstützung in logischer Klammer**. Aktuell werden Module (MILL, DRILL, AIQS) manuell Schritt-für-Schritt gesteuert, was fehleranfällig und zeitaufwendig ist. Die Steuerungsbefehle werden in Form von **MQTT-Messages** an die Module abgesendet.

---

## ** Funktionale Anforderungen**

### **1. Logische Klammer für Sequenz-Ausführung**
- **Geschlossene Einheit**: Eine Sequenz läuft als logische Einheit (z.B. PICK → PROCESS → DROP)
- **Abbruch-Fähigkeit**: Bei Bedarf kann die Sequenz abgebrochen werden
- **Konsistente IDs**: `orderId` bleibt konstant, `orderUpdateId` wird pro Schritt inkrementiert
- **Status-Tracking**: Vollständige Nachverfolgung des Sequenz-Status

### **2. UI-Unterstützung für Sequenzen**
- **Sequenz-Fenster**: Öffnet sich bei Sequenz-Start und bleibt bis Ende offen
- **Visuelle Sequenz-Darstellung**: Schritte werden als Kette dargestellt (PICK → MILL → DROP)
- **Fortschrittsanzeige**: Aktueller Schritt wird hervorgehoben, abgeschlossene markiert
- **Manuelle Kontrolle**: User klickt selbst die Send-Buttons (keine Automatik)
- **Abbruch-Möglichkeit**: Sequenz kann jederzeit abgebrochen werden


### **3. Generische Sequenz-Definition (YML & Python)**
- **Flexible Message-Topic-Kombinationen**: Nicht nur "command"-basiert
- **Template-System**: Variablen in Topics und Payloads (z.B. `{{module_id}}`)
- **Modul-spezifische Rezepte**: Verschiedene Sequenzen für MILL, DRILL, AIQS
- **Kontext-Variablen**: IDs und Werte werden zwischen Schritten durchgereicht
- **YML und Python gleichwertig**: Sequenzen können als YML-Datei oder Python-Script definiert werden
- **Individuelle Logik**: Python-Sequenzen erlauben komplexe Bedingungen, dynamische Payloads, Callbacks

### **4. Wait-Schritte zwischen Commands**
- **Event-Waiting**: Automatisches Warten auf Bestätigungen zwischen Commands
- **Pattern-Matching**: Warten auf spezifische Topics und Payload-Bedingungen
- **ID-Durchreichung**: Werte aus Wait-Events werden in nachfolgende Commands übernommen

---

## ** Technische Anforderungen**

### **5. MQTT-Integration**
- **MQTT-Message-Versand**: Steuerungsbefehle werden als MQTT-Messages abgesendet
- **Topic-Resolution**: Variablen in Topics werden zur Laufzeit aufgelöst
- **Payload-Generierung**: Template-basierte Nachrichten-Erstellung
- **YML-Integration**: Wiederverwendung bestehender `topic_config.yml` und `topic_message_mapping.yml`
- **Semantik-Wiederverwendung**: Nutzung der bereits definierten Topic/Message-Strukturen
- **OMFMqttClient-Singleton**: Verwendung des bestehenden MQTT-Client-Singletons

### **6. Workflow-Management**
- **Singleton Pattern**: Ein `WorkflowOrderManager` für alle Sequenzen
- **ID-Management**: Konsistente `orderId`/`orderUpdateId` Verwaltung
- **Session-State**: Sequenz-Status in Streamlit Session gespeichert


### **7. UI/UX-Anforderungen**
- **Sofortige Anzeige**: Nachrichten werden unmittelbar nach Button-Klick angezeigt
- **Sequenz-Status**: "Sequenz gestartet", "Sequenz beendet", "Sequenz abgebrochen" werden klar angezeigt
- **Schritt-Darstellung**: Schritte sind vertikal ausgerichtet und mit 60px eingerückt
- **Nummerierung**: Jeder Schritt ist durchnummeriert und mit Statussymbol versehen
- **Abbruch jederzeit**: "Sequenz abbrechen" ist bis zum letzten Schritt aktiv
- **Abschlussanzeige**: Abschluss erscheint auf Höhe des Start-Buttons
- **Step-Details**: Optional einblendbare Context- und Payload-Infos pro Schritt, Expander standardmäßig geschlossen
- **Keine Trennlinien**: Keine `---` zwischen Message und Button
- **Einfaches Design**: Kein Over-Engineering, klare und intuitive Bedienung

### **8. Testbarkeit**
- **Unit-Tests**: Einfache Unit-Tests ohne Dashboard-Start möglich
- **Mock-Support**: MQTT-Client kann gemockt werden
- **Isolierte Tests**: Sequenz-Logik testbar ohne UI-Komponenten
- **CI/CD-fähig**: Tests können in automatisierten Pipelines laufen

---

## ** Beispiel-Szenarien**

### **Szenario 1: MILL-Sequenz mit Wait-Schritten**
```
1. User klickt " Komplette Sequenz MILL"
2. Sequenz-Fenster öffnet sich
3. Sequenz wird angezeigt: 📥 PICK(SEND) → ⏳ WAIT → ⚙️ MILL(SEND) → ⏳ WAIT → DROP(SEND)
4. User klickt "Senden" für PICK
5. MQTT-Message wird an module/v1/ff/MILL-01/order gesendet
6. System wartet automatisch auf PICK-Bestätigung
7. Nach Bestätigung wird MILL zu MILL(SEND), User klickt erneut
8. MQTT-Message wird an module/v1/ff/MILL-01/order gesendet
9. System wartet auf MILL-Bestätigung
10. Nach DROP wird "Ende Sequenz" angezeigt
```

### **Szenario 2: Fehlerbehandlung ohne Timeout**
```
1. Sequenz läuft, PICK erfolgreich
2. MILL-Befehl wird als MQTT-Message gesendet
3. User kann "Sequenz abbrechen" klicken
4. Alle offenen Workflows werden beendet
```

---

## ** Akzeptanzkriterien**


### **✅ Must-Have**
- [ ] Sequenz-Fenster öffnet sich bei Sequenz-Start
- [ ] Sequenz bleibt offen bis Ende oder Abbruch
- [ ] Manuelle Send-Button-Kontrolle (keine Automatik)
- [ ] Konsistente `orderId`/`orderUpdateId` Verwaltung
- [ ] Visuelle Fortschrittsanzeige mit Nummerierung und Symbolen
- [ ] Abbruch-Möglichkeit jederzeit
- [ ] Wait-Schritte zwischen Commands
- [ ] OMFMqttClient-Singleton Verwendung
- [ ] MQTT-Message-Versand für Steuerungsbefehle
- [ ] Unit-Tests ohne Dashboard-Start möglich
- [ ] Step-Details (Context/Payload) optional pro Schritt
- [ ] Sequenzdefinitionen als YML und Python möglich

### **✅ Could-Have**
- [ ] Generische Topic/Message-Template-Definition
- [ ] Payload-Anzeige ein-/ausschaltbar
- [ ] Modul-spezifische Rezepte (MILL, DRILL, AIQS)
- [ ] YML-Integration für Topic/Message-Mapping
- [ ] Thread-Sicherheit für parallele Sequenzen

### **❌ Must-Not-Have**
- [ ] ACK-Ereignisse und Timeout Retry-Mechanismen
- [ ] Automatische Retry-Mechanismen
- [ ] Erweiterte Fehlerbehandlung
- [ ] Sequenz-Historie und Logging
- [ ] Drag & Drop Sequenz-Editor
- [ ] Over-Engineering oder komplexe UI-Elemente
- [ ] Transaktionale Sicherheit (ACID-Properties)

---

## ** Technische Constraints**

- **Streamlit-basiert**: UI muss in Streamlit funktionieren
- **MQTT-Protokoll**: Kommunikation über MQTT-Broker
- **Python 3.8+**: Kompatibilität mit bestehender Architektur
- **Session-State**: Nutzt Streamlit Session State für Persistenz
- **Singleton Pattern**: MQTT-Client und Workflow-Manager als Singletons
- **YML-Integration**: Wiederverwendung bestehender Konfigurationsdateien
- **Einfaches Design**: Keine unnötige Komplexität
- **Testbarkeit**: Unit-Tests ohne Dashboard-Start

---

## ** Erwartete Lösung**

Eine **einfache, robuste Lösung** die:
1. **Manuelle Steuerung** mit automatischen Wait-Schritten kombiniert
2. **Template-basierte** Rezept-Definitionen unterstützt
3. **YML-Semantik** wiederverwendet
4. **UI in logischer Klammer** mit visueller Fortschrittsanzeige implementiert
5. **Einfaches Design** ohne Over-Engineering
6. **OMFMqttClient-Singleton** nutzt
7. **MQTT-Messages** für Steuerungsbefehle verwendet
8. **Unit-Tests** ohne Dashboard-Start ermöglicht

**Ziel**: Ein intuitives, robustes System für die sequenzielle Steuerung der ORBIS Modellfabrik mit vollständiger UI-Unterstützung in logischer Klammer und einfacher Bedienung über MQTT-Messages, das einfach testbar ist.

---

## ** Dokumentations-Status**

- **Erstellt**: 2025-01-XX
- **Version**: 1.0
- **Status**: Anforderungen definiert
- **Nächste Schritte**: Implementierung der Sequenz-Steuerung
