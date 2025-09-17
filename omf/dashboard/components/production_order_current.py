"""
OMF Dashboard Production Order - Laufende Production Orders
"""

import streamlit as st


def show_production_order_current():
    """Zeigt die laufenden Production Orders"""
    st.subheader("🔄 Laufende Fertigungsaufträge (Production Orders)")

    # TODO: Implementierung der laufenden Fertigungsaufträge
    st.info("🚧 **In Entwicklung:** Laufende Fertigungsaufträge werden implementiert")

    # Platzhalter für zukünftige Funktionalitäten
    st.markdown("### Geplante Funktionalitäten:")
    st.markdown("- **Aktive Aufträge:** Anzeige aller laufenden Fertigungsaufträge")
    st.markdown("- **Fortschrittsanzeige:** Visueller Fortschritt der Produktionsschritte")
    st.markdown("- **Modul-Status:** Welche Module sind aktuell beschäftigt")
    st.markdown("- **Werkstück-Verfolgung:** Position der Werkstücke in der Fabrik")
    st.markdown("- **Echtzeit-Updates:** Live-Aktualisierung der Auftragsstatus")

    # Beispiel-Daten für zukünftige Implementierung
    st.markdown("### Beispiel-Aufträge (Mock-Daten):")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔴 ROT ProductionOrder #PO-001**")
        st.markdown("- Status: In Bearbeitung")
        st.markdown("- Aktueller Schritt: Fräsen in MILL")
        st.markdown("- Geschätzte Fertigstellung: 14:30")

    with col2:
        st.markdown("**🔵 BLAU ProductionOrder #PO-002**")
        st.markdown("- Status: Wartend")
        st.markdown("- Aktueller Schritt: Bereit für Start")
        st.markdown("- Geschätzte Fertigstellung: 15:45")
