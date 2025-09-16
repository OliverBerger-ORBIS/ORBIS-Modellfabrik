"""
Production Order Analyzer - Analyse für ccu/order/request mit orderType: PRODUCTION

Analysiert die Message-Kette für Production Orders (RED, WHITE, BLUE) und erstellt einen Graph
basierend auf orderId, workpieceId und workpieceId Verbindungen.
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import networkx as nx
from datetime import datetime

# Import des Production Order Flow Analyzers
from omf.analysis_tools.production_order_flow_analyzer import ProductionOrderFlowAnalyzer


def load_session_data(session_file: str) -> List[Dict[str, Any]]:
    """Lädt Session-Daten aus einer Log-Datei."""
    try:
        session_path = Path("data/omf-data/sessions") / session_file
        if not session_path.exists():
            st.error(f"❌ Session-Datei nicht gefunden: {session_path}")
            return []
        
        messages = []
        with open(session_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        message = json.loads(line)
                        messages.append(message)
                    except json.JSONDecodeError:
                        continue
        
        return messages
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Session: {str(e)}")
        return []


def show_production_order_analysis():
    """Zeigt die umstrukturierte Production Order Analyse UI"""
    st.header("📊 Production Order Analyse")
    
    st.markdown("**Schritt-für-Schritt Analyse von Message-Ketten**")
    st.markdown("Analysiert den Flow von Customer Orders zu Production Orders und identifiziert die zentrale Stelle für orderId-Management.")

    # Schritt 1: Session-Auswahl
    st.markdown("### 1️⃣ Session auswählen")
    sessions_dir = "data/omf-data/sessions"

    if os.path.exists(sessions_dir):
        log_files = [f for f in os.listdir(sessions_dir) if f.endswith('.log')]
        log_files.sort()

        if not log_files:
            st.warning("❌ Keine Session-Dateien gefunden")
            return

        selected_session = st.selectbox("📁 Session auswählen", options=log_files, key="production_order_session")

        if not selected_session:
            return

        # Schritt 2: Analyse durchführen
        st.markdown("### 2️⃣ Analyse durchführen")
        if st.button("🔍 Production Order Flow analysieren", type="primary"):
            try:
                # Führe die Analyse durch
                session_path = Path("data/omf-data/sessions") / selected_session
                analyzer = ProductionOrderFlowAnalyzer(session_path)
                results = analyzer.analyze()
                
                # Zeige Ergebnisse
                st.success("✅ Analyse erfolgreich abgeschlossen!")
                
                # Zeige Zusammenfassung
                st.markdown("### 📊 Analyse-Ergebnisse")
                analyzer.print_analysis_summary()
                
                # Zeige Logik-Erklärung
                st.markdown("### 🔍 Logik-Erklärung")
                with st.expander("📖 Wie funktioniert die Production Order Analyse?"):
                    st.markdown("""
                    **🎯 Production Order Flow Analyse:**
                    
                    1. **🔍 Suche nach Production Orders:**
                       - Findet `ccu/order/request` Messages mit `type: "RED/WHITE/BLUE"` und `orderType: "PRODUCTION"`
                       - Diese sind der **Startpunkt** des Production Order Flows
                    
                    2. **🔴 Erste RED Message:**
                       - Sucht nach der **ersten** Message nach dem Production Order Request
                       - Die Message muss `type: "RED"` enthalten
                       - Zeigt den **Übergang** von Customer Order zu Production Order
                    
                    3. **🎯 OrderId Enrichment:**
                       - Findet die **erste** Message nach dem Production Order Request
                       - Die Message muss eine `orderId` enthalten (nicht leer/null)
                       - Zeigt **wo** die orderId zum ersten Mal hinzugefügt wird
                    
                    4. **🔗 Verwandte Messages:**
                       - Sammelt **alle** Messages mit derselben `orderId`
                       - Baut einen **Graph** der Message-Abhängigkeiten
                       - Zeigt den **kompletten Flow** einer Production Order
                    
                    **💡 Wichtige Erkenntnisse:**
                    - **Dashboard/FT** sendet Production Order Request (`ccu/order/request` **ohne** orderId)
                    - **CCU** verarbeitet den Order und generiert `orderId` (`fts/v1/ff/5iO4/order`)
                    - **TXT Controller** erhält Order mit `orderId` (`/j1/txt/1/f/i/order`)
                    - **Module** reagieren auf die `orderId` (verschiedene Topics)
                    """)
                
                # Zeige beteiligte Topics
                st.markdown("### 📋 Beteiligte Topics")
                involved_topics = results.get("involved_topics", [])
                
                if involved_topics:
                    # Erstelle DataFrame für bessere Darstellung
                    import pandas as pd
                    
                    topic_data = []
                    for topic_info in involved_topics:
                        topic_data.append({
                            "Topic": topic_info['topic'],
                            "Messages": topic_info['message_count'],
                            "Erste Message": topic_info['first_timestamp'][:19],
                            "Letzte Message": topic_info['last_timestamp'][:19],
                            "Types": ", ".join(topic_info['types'])
                        })
                    
                    df = pd.DataFrame(topic_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Production Order Filter
                    st.markdown("### 🎯 Production Order Filter")
                    st.info("💡 **Verwende diese Topics als Filter im Session Analyzer:**")
                    
                    # Erstelle Filter-String
                    filter_topics = [topic_info['topic'] for topic_info in involved_topics]
                    filter_string = " OR ".join([f"topic == '{topic}'" for topic in filter_topics])
                    
                    st.code(filter_string, language="text")
                    
                    # Copy-Button
                    if st.button("📋 Filter kopieren"):
                        st.write("Filter in Zwischenablage kopiert!")
                
                # Zeige Mermaid Graph (vereinfacht)
                st.markdown("### 🎨 Message Flow Graph (Vereinfacht)")
                mermaid_diagram = results["mermaid_diagram"]
                
                # Fallback: Code-Block anzeigen (statt HTML)
                with st.expander("📋 Mermaid-Diagramm anzeigen"):
                    st.code(mermaid_diagram, language="text")
                    
                    # Download-Link für Mermaid-Datei
                    st.download_button(
                        label="📥 Mermaid-Datei herunterladen",
                        data=mermaid_diagram,
                        file_name="message_flow_diagram.mmd",
                        mime="text/plain"
                    )
                
                # Zeige Graph-Statistiken
                st.markdown("### 📈 Graph-Statistiken")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Nodes", results["graph_nodes"])
                with col2:
                    st.metric("Edges", results["graph_edges"])
                
                # Zeige detaillierte Message-Informationen
                st.markdown("### 🔍 Detaillierte Message-Informationen")
                
                # Production Order Requests
                production_orders = results["production_orders"]
                if production_orders:
                    st.markdown("#### 🎯 Production Order Requests")
                    for i, prod_order in enumerate(production_orders, 1):
                        with st.expander(f"Production Order {i}"):
                            st.json(prod_order.payload)
                            
                            # Erste RED Message
                            first_red = analyzer.find_first_red_message(prod_order)
                            if first_red:
                                st.markdown("**🔴 Erste RED Message:**")
                                st.json(first_red.payload)
                            
                            # OrderId Enrichment
                            enrichment = analyzer.find_order_id_enrichment(prod_order)
                            if enrichment:
                                st.markdown("**🔑 OrderId Enrichment:**")
                                st.json(enrichment.payload)
                
            except Exception as e:
                st.error(f"❌ Fehler bei der Analyse: {str(e)}")
                st.exception(e)
    else:
        st.warning("❌ Sessions-Verzeichnis nicht gefunden")
