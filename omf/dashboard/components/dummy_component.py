"""
Dummy-Komponente für fehlende Dashboard-Komponenten

Diese Komponente wird angezeigt, wenn eine Komponente nicht geladen werden kann.
Sie stellt sicher, dass das Dashboard trotzdem funktioniert.
"""

import streamlit as st


def show_dummy_component(component_name: str, error_message: str = None):
    """
    Zeigt eine Dummy-Komponente für fehlende Komponenten an

    Args:
        component_name: Name der fehlenden Komponente
        error_message: Optional: Detaillierte Fehlermeldung
    """
    st.header(f"🚧 {component_name}")

    # Fehler-Info
    st.error(f"❌ Komponente '{component_name}' konnte nicht geladen werden")

    if error_message:
        st.code(error_message, language="python")

    # Platzhalter-Content
    st.info("🔧 Diese Komponente ist derzeit nicht verfügbar")

    # Debug-Informationen
    with st.expander("🔍 Debug-Informationen"):
        st.write(f"**Fehlende Komponente:** `{component_name}`")
        st.write("**Mögliche Ursachen:**")
        st.markdown("- Datei existiert nicht")
        st.markdown("- Import-Fehler in der Komponente")
        st.markdown("- Syntax-Fehler in der Komponente")
        st.markdown("- Fehlende Abhängigkeiten")

        if error_message:
            st.write("**Fehlermeldung:**")
            st.code(error_message)

    # Hinweise für Entwickler
    st.markdown("### 🛠️ Für Entwickler:")
    st.markdown("- Überprüfen Sie, ob die Komponente existiert")
    st.markdown("- Prüfen Sie die Import-Pfade")
    st.markdown("- Testen Sie die Komponente isoliert")
    st.markdown("- Überprüfen Sie die Abhängigkeiten")
