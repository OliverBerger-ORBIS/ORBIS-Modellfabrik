# UI Architecture Rules - Cursor AI Regeln

## 🎯 ZENTRALE UI-ARCHITEKTUR-REGELN

### Logging-Standards (KRITISCH)
- **Logger verwenden:** `logger.debug("message")` statt `st.debug("message")` ✅
- **Logger importieren:** `from omf2.common.logger import get_logger` ✅
- **Logger initialisieren:** `logger = get_logger(__name__)` ✅
- **KEINE st.debug:** `st.debug()` ❌
- **Logging-Level:** `logger.info()`, `logger.error()`, `logger.warning()`, `logger.debug()` ✅

### Tab/Subtab-Architektur (KRITISCH)
- **Maximale Dateigröße:** 200 Zeilen pro Tab/Subtab-Datei ✅
- **Modulare Komponenten:** Komplexe Logik in separate Components auslagern ✅
- **Components-Verzeichnis:** `omf2/ui/common/components/` für wiederverwendbare UI-Komponenten ✅
- **Domain-spezifische Components:** Nur in `omf2/ui/admin/` wenn ausschließlich Admin-spezifisch ✅
- **Single Responsibility:** Jede Komponente hat einen klaren Zweck ✅

### Tab-Struktur-Standards (KRITISCH)
- **Tab-Dateien:** `*_tab.py` (z.B. `generic_steering_tab.py`) ✅
- **Subtab-Dateien:** `*_subtab.py` (z.B. `topic_steering_subtab.py`) ✅
- **Component-Dateien:** `*_component.py` oder `*_generator.py` (z.B. `payload_generator.py`) ✅
- **Maximale Zeilen:** 200 Zeilen pro Datei ✅
- **Bei Überschreitung:** Sofort in Components aufteilen ✅

### Component-Architektur (KRITISCH)
- **Wiederverwendbare Components:** `omf2/ui/common/components/` ✅
- **Domain-spezifische Components:** `omf2/ui/admin/components/` oder `omf2/ui/user/components/` ✅
- **Component-Imports:** Absolute Pfade verwenden ✅
- **Component-Initialisierung:** Im Tab/Subtab, nicht in Component ✅
- **Component-Dependencies:** Minimale Abhängigkeiten zwischen Components ✅

### Import-Standards für UI (KRITISCH)
- **Absolute Imports:** `from omf2.ui.common.components.payload_generator import PayloadGenerator` ✅
- **Registry Manager:** `from omf2.registry.manager.registry_manager import get_registry_manager` ✅
- **Logger:** `from omf2.common.logger import get_logger` ✅
- **Streamlit:** `import streamlit as st` ✅
- **KEINE relativen Imports:** `from .component import Component` ❌

### Function-Signature-Standards (KRITISCH)
- **Tab-Functions:** `render_*_tab()` ✅
- **Subtab-Functions:** `render_*_subtab(admin_gateway=None, registry_manager=None)` ✅
- **Component-Functions:** `__init__(registry_manager)` oder `__init__(admin_gateway, registry_manager)` ✅
- **Parameter-Weitergabe:** Immer `admin_gateway` und `registry_manager` als Parameter ✅
- **Session State:** Nur als Fallback, nicht als primäre Datenquelle ✅

### Error-Handling-Standards (KRITISCH)
- **Try-Catch:** Alle UI-Functions mit try-catch umschließen ✅
- **Logger-Errors:** `logger.error(f"❌ Error: {e}")` ✅
- **User-Feedback:** `st.error(f"❌ User-friendly message")` ✅
- **Graceful Degradation:** UI funktioniert auch bei Fehlern ✅
- **Debug-Info:** `logger.debug()` statt `st.debug()` ✅

### UI-Refresh-Standards (KRITISCH)
- **Session State:** Für persistente UI-Zustände ✅
- **Key-Uniqueness:** Einzigartige Keys für alle UI-Elemente ✅
- **Key-Pattern:** `{tab}_{subtab}_{component}_{element}` ✅
- **Radio Buttons:** Statt Selectbox für bessere UX ✅
- **State-Persistence:** UI-Zustand bleibt bei Reruns erhalten ✅

### Performance-Standards (KRITISCH)
- **Lazy Loading:** Components nur bei Bedarf laden ✅
- **Caching:** Registry Manager in Session State cachen ✅
- **Minimale Reruns:** UI-Änderungen minimieren ✅
- **Efficient Rendering:** Nur notwendige UI-Elemente rendern ✅
- **Background Processing:** Schwere Operationen im Hintergrund ✅

## 🚨 AUTOMATISCHE REGEL-BEFOLGUNG (KRITISCH)

### MANDATORY COMPLIANCE
- **JEDE UI-Änderung** MUSS diese Regeln automatisch befolgen
- **KEINE Ausnahmen** ohne explizite User-Freigabe
- **Immer prüfen** vor jeder UI-Implementierung:
  - ✅ Logger statt st.debug verwendet?
  - ✅ Dateigröße unter 200 Zeilen?
  - ✅ Components in ui/common/ für Wiederverwendung?
  - ✅ Absolute Imports verwendet?
  - ✅ Function-Signature korrekt?
  - ✅ Error-Handling implementiert?

### AUTOMATISCHE VALIDIERUNG
- **Vor jeder UI-Implementierung:** Regeln prüfen
- **Nach jeder Änderung:** Linting/Formatting prüfen
- **Bei Fehlern:** Sofort korrigieren, nicht ignorieren
- **Bei Überschreitung:** Sofort refactoren

### ENTWICKLUNGSPROZESS (MANDATORY)
1. **Analyse:** UI-Anforderungen verstehen
2. **Regel-Check:** Alle relevanten Regeln prüfen
3. **Implementierung:** Regeln automatisch befolgen
4. **Validierung:** Pre-commit Hooks, Tests, Linting
5. **Freigabe:** User-Bestätigung vor Commit

### ZWINGENDE REGELN (NIEMALS IGNORIEREN)
- **Logging:** `logger.debug()` statt `st.debug()`
- **Dateigröße:** Maximal 200 Zeilen pro Tab/Subtab
- **Components:** Wiederverwendbare in `ui/common/`
- **Imports:** Absolute Pfade für alle UI-Imports
- **Function-Signature:** Korrekte Parameter für alle UI-Functions
- **Error-Handling:** Try-catch für alle UI-Functions

## 🚨 WICHTIG
Bei jeder UI-Änderung diese Regeln befolgen!
