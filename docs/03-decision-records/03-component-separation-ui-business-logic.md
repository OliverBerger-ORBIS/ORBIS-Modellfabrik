# Decision Record: Komponenten-Trennung (UI ↔ Business-Logik)

**Datum:** 2024-12-19  
**Status:** Accepted  
**Kontext:** Das OMF-Dashboard benötigt eine klare Trennung zwischen UI-Komponenten und Business-Logik für bessere Wartbarkeit, Testbarkeit und Wiederverwendbarkeit.

---

## Entscheidung

Verwendung des **Wrapper-Pattern** mit separaten Manager-Klassen für Business-Logik und UI-Komponenten für die Darstellung.

```python
# Wrapper-Komponente (z.B. aps_overview.py)
def show_aps_overview():
    """Hauptfunktion für die APS-Übersicht mit Untertabs"""
    st.header("🏭 APS Overview")
    
    # Untertabs für verschiedene Bereiche
    tab1, tab2, tab3, tab4 = st.tabs(["📊 System Status", "🎮 Controllers", "📋 Orders", "⚡ Commands"])
    
    with tab1:
        show_aps_overview_system_status()  # UI-Komponente
    with tab2:
        show_aps_overview_controllers()    # UI-Komponente

# Business-Logik Manager (z.B. APSCommandsManager)
class APSCommandsManager:
    def send_system_command(self, mqtt_client, command, payload=None):
        """Business-Logik für System Commands"""
        result = mqtt_client.publish(command, payload, qos=1, retain=False)
        return result

# UI-Komponente (z.B. aps_overview_commands.py)
def show_aps_overview_commands():
    """UI für APS Commands"""
    manager = APSCommandsManager()
    if st.button("🔄 Factory Reset"):
        result = manager.send_system_command(client, "ccu/set/reset")
```

## Konsequenzen

### Positiv:
- **Testbarkeit:** Business-Logik isoliert testbar
- **Wiederverwendbarkeit:** Manager-Klassen in verschiedenen UI-Kontexten
- **Wartbarkeit:** Klare Trennung der Verantwortlichkeiten
- **Skalierbarkeit:** Neue UI-Komponenten einfach hinzufügbar
- **Konsistenz:** Einheitliche Business-Logik

### Negativ:
- **Komplexität:** Mehr Dateien und Abstraktionsebenen
- **Lernkurve:** Entwickler müssen Architektur verstehen

## Implementierung

- [x] Wrapper-Komponenten für Dashboard-Tabs
- [x] Manager-Klassen für Business-Logik
- [x] UI-Komponenten für Streamlit-Darstellung
- [x] Session State für Manager-Instanzen
- [x] Klare Import-Struktur (absolute/relative)

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
