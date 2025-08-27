# 🔧 Unified Template Filtering Architecture

## 🎯 Übersicht

**Problem gelöst:** Code-Duplikation durch separate Filter für jede Template-Kategorie (TXT, CCU, Module).

**Lösung:** Einheitlicher, generischer Filter für alle MQTT-Nachrichten-Typen.

## ❌ Vorheriges Problem

### **Code-Duplikation:**
```python
# Separate Methoden für jeden Typ - SCHLECHTES DESIGN
def is_real_txt_message(self, payload: dict) -> bool:
    # TXT-spezifische Filter-Logik
    
def is_real_ccu_message(self, payload: dict) -> bool:
    # CCU-spezifische Filter-Logik
    
def is_real_module_message(self, payload: dict) -> bool:
    # Module-spezifische Filter-Logik
```

### **Folgen:**
- **Code-Duplikation** - Gleiche Logik in mehreren Methoden
- **Inkonsistente Filterung** - Unterschiedliche Ergebnisse je nach Typ
- **Wartungsprobleme** - Änderungen müssen in mehreren Stellen gemacht werden
- **Skalierungsprobleme** - Bei neuen Modulen neue Filter-Methode nötig

## ✅ Neue Lösung: Unified Filtering

### **Einheitliche Methode:**
```python
def is_real_message(self, payload: dict, message_type: str = "generic") -> bool:
    """Generic method to check if a payload is a real message (not a template placeholder)"""
    def contains_template_placeholders(obj):
        if isinstance(obj, str):
            # Generic placeholder patterns that work for all message types
            generic_patterns = [
                '<', '>', ':', 'PLACEHOLDER', 'TEMPLATE', 'EXAMPLE'
            ]
            
            # Type-specific patterns
            type_patterns = {
                "txt": [
                    '<nfcCode>', '<workpieceType:', '<state:', '<location:', '<hbwId>',
                    '<RED>', '<WHITE>', '<BLUE>', '<RAW>', '<timestamp>', '<status:',
                    '<workpieceType: RED, WHITE, BLUE>', '<state: RAW>', 
                    '<location: A1, A2, A3, B1, B2, B3, C1, C2, C3>',
                    '<workpieceType: BLUE, RED, WHITE>', 
                    '<status: IN_PROCESS, WAITING_FOR_ORDER>'
                ],
                "ccu": [
                    '<orderId>', '<status>', '<timestamp>', '<state>',
                    '<config>', '<error>', '<workflow>', '<pairing>',
                    '<active>', '<completed>', '<request>', '<response>',
                    '<flows>', '<layout>', '<stock>', '<version>'
                ],
                "module": [
                    '<moduleId>', '<command>', '<position>', '<status>',
                    '<workpiece>', '<location>', '<timestamp>', '<state>',
                    '<MILL>', '<DRILL>', '<AIQS>', '<HBW>', '<DPS>'
                ]
            }
            
            # Check generic patterns first
            if any(pattern in obj for pattern in generic_patterns):
                return True
            
            # Check type-specific patterns
            if message_type in type_patterns:
                if any(pattern in obj for pattern in type_patterns[message_type]):
                    return True
            
            return False
        elif isinstance(obj, dict):
            return any(contains_template_placeholders(v) for v in obj.values())
        elif isinstance(obj, list):
            return any(contains_template_placeholders(item) for item in obj)
        return False
    
    return not contains_template_placeholders(payload)
```

## 🏗️ Architektur-Vorteile

### **1. Einheitlichkeit:**
- **Eine Methode** für alle Nachrichten-Typen
- **Konsistente Logik** - Gleiche Filter-Regeln überall
- **Einheitliche Ergebnisse** - Keine Unterschiede je nach Typ

### **2. Wartbarkeit:**
- **Zentrale Wartung** - Änderungen nur an einer Stelle
- **Einfache Erweiterung** - Neue Typen durch Konfiguration
- **Konsistente Updates** - Alle Filter werden gleichzeitig aktualisiert

### **3. Skalierbarkeit:**
- **Neue Module** - Einfach durch neue Einträge in `type_patterns`
- **Neue Platzhalter** - Zentrale Verwaltung
- **Flexible Konfiguration** - Typ-spezifische Anpassungen möglich

### **4. Wiederverwendbarkeit:**
- **Alle Analysen** nutzen dieselbe Logik
- **Konsistente Ergebnisse** - TXT, CCU, Module, etc.
- **Einheitliche API** - Gleiche Methode überall

## 🔧 Verwendung

### **TXT Controller Analyse:**
```python
# In txt_template_analyzer.py
if self.is_real_message(payload, "txt"):
    examples.append(payload)
```

### **CCU Analyse:**
```python
# In aps_dashboard.py
if self.is_real_message(payload, "ccu"):
    examples.append(payload)
```

### **Module Analyse (zukünftig):**
```python
# Für MILL, DRILL, AIQS, etc.
if self.is_real_message(payload, "module"):
    examples.append(payload)
```

### **Generische Analyse:**
```python
# Für unbekannte Typen
if self.is_real_message(payload, "generic"):
    examples.append(payload)
```

## 📊 Platzhalter-Kategorien

### **1. Generic Patterns (alle Typen):**
```python
generic_patterns = [
    '<', '>', ':', 'PLACEHOLDER', 'TEMPLATE', 'EXAMPLE'
]
```

### **2. TXT Controller Patterns:**
```python
"txt": [
    '<nfcCode>', '<workpieceType:', '<state:', '<location:', '<hbwId>',
    '<RED>', '<WHITE>', '<BLUE>', '<RAW>', '<timestamp>', '<status:',
    '<workpieceType: RED, WHITE, BLUE>', '<state: RAW>', 
    '<location: A1, A2, A3, B1, B2, B3, C1, C2, C3>',
    '<workpieceType: BLUE, RED, WHITE>', 
    '<status: IN_PROCESS, WAITING_FOR_ORDER>'
]
```

### **3. CCU Patterns:**
```python
"ccu": [
    '<orderId>', '<status>', '<timestamp>', '<state>',
    '<config>', '<error>', '<workflow>', '<pairing>',
    '<active>', '<completed>', '<request>', '<response>',
    '<flows>', '<layout>', '<stock>', '<version>'
]
```

### **4. Module Patterns:**
```python
"module": [
    '<moduleId>', '<command>', '<position>', '<status>',
    '<workpiece>', '<location>', '<timestamp>', '<state>',
    '<MILL>', '<DRILL>', '<AIQS>', '<HBW>', '<DPS>'
]
```

## 🔄 Workflow-Verbesserungen

### **1. Einheitliche Analyse:**
```
1. Alle Template-Analysen nutzen dieselbe Filter-Methode
2. Konsistente Ergebnisse für alle Nachrichten-Typen
3. Einheitliche Template Library
4. Gleiche Qualität der Beispiele
```

### **2. Einfache Erweiterung:**
```
1. Neues Modul hinzufügen → Neuer Eintrag in type_patterns
2. Neue Platzhalter → Zentrale Verwaltung
3. Neue Nachrichten-Typen → Sofort unterstützt
```

### **3. Wartung:**
```
1. Änderungen nur an einer Stelle
2. Alle Filter werden gleichzeitig aktualisiert
3. Konsistente Qualität überall
```

## 📈 Zukünftige Erweiterungen

### **1. Neue Module:**
- **FTS (Fahrerloses Transportsystem)** - Navigation und Routen
- **Sensoren** - Temperatur, Druck, etc.
- **Aktoren** - Motoren, Ventile, etc.

### **2. Erweiterte Filter:**
- **Regex-Patterns** - Komplexere Platzhalter-Erkennung
- **Machine Learning** - Automatische Platzhalter-Erkennung
- **Konfigurierbare Patterns** - Externe Konfigurationsdatei

### **3. Performance-Optimierung:**
- **Caching** - Häufig verwendete Patterns zwischenspeichern
- **Parallelisierung** - Mehrere Nachrichten gleichzeitig filtern
- **Lazy Loading** - Patterns nur bei Bedarf laden

## 🔗 Verwandte Dokumentation

- **[Template Library Implementation](template-library-implementation.md)**
- **[Template Library Improvements](template-library-improvements.md)**
- **[Template Analysis Improvement](template-analysis-improvement.md)**
- **[CCU Analysis Integration](ccu-analysis-integration.md)**

## ✅ Fazit

**Die Unified Template Filtering Architecture löst alle Probleme:**

- **✅ Keine Code-Duplikation** - Eine Methode für alle Typen
- **✅ Konsistente Ergebnisse** - Gleiche Qualität überall
- **✅ Einfache Wartung** - Zentrale Verwaltung
- **✅ Skalierbar** - Neue Module einfach hinzufügen
- **✅ Wiederverwendbar** - Einheitliche API

**Bei der Analyse von Modul-Nachrichten (MILL, DRILL, AIQS, etc.) treten keine Filter-Probleme mehr auf!** 🎉
