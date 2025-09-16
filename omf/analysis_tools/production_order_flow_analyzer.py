#!/usr/bin/env python3
"""
Production Order Message Flow Analyzer

Analysiert den Message-Flow von Customer Orders zu Production Orders:
1. Customer Order → Production Order (CCU Transformation)
2. Initial Message: ccu/order/request mit {type: "RED", orderType: "PRODUCTION"} (ohne orderId)
3. Message Enrichment: Nachfolgende Messages bekommen eine orderId hinzugefügt
4. Graph Building: Alle Messages mit derselben orderId verknüpfen

Usage:
    python -m omf.analysis_tools.production_order_flow_analyzer
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import networkx as nx


@dataclass
class Message:
    """Repräsentiert eine MQTT Message aus der Session."""
    timestamp: str
    topic: str
    payload: Dict[str, Any]
    message_type: str
    module_type: str
    serial_number: str
    status: str
    
    @property
    def parsed_timestamp(self) -> datetime:
        """Parsed timestamp für Zeitvergleiche."""
        return datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))


class ProductionOrderFlowAnalyzer:
    """Analysiert Production Order Message Flows."""
    
    def __init__(self, session_file: Path):
        """Initialisiert den Analyzer mit einer Session-Datei."""
        self.session_file = session_file
        self.messages: List[Message] = []
        self.graph = nx.DiGraph()
        
    def load_session(self) -> None:
        """Lädt die Session-Datei und parst alle Messages."""
        print(f"📁 Lade Session: {self.session_file}")
        
        with open(self.session_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    message = Message(
                        timestamp=data['timestamp'],
                        topic=data['topic'],
                        payload=json.loads(data['payload']) if isinstance(data['payload'], str) else data['payload'],
                        message_type=data.get('message_type', 'unknown'),
                        module_type=data.get('module_type', 'unknown'),
                        serial_number=data.get('serial_number', 'unknown'),
                        status=data.get('status', 'unknown')
                    )
                    self.messages.append(message)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"⚠️  Zeile {line_num}: {e}")
                    continue
        
        print(f"✅ {len(self.messages)} Messages geladen")
    
    def find_production_order_requests(self) -> List[Message]:
        """Findet alle ccu/order/request Messages mit Production Order Pattern."""
        production_orders = []
        
        for message in self.messages:
            if message.topic == "ccu/order/request":
                payload = message.payload
                if (payload.get('orderType') == "PRODUCTION" and 
                    payload.get('type') in ["RED", "WHITE", "BLUE"]):
                    production_orders.append(message)
        
        print(f"🔍 {len(production_orders)} Production Order Requests gefunden")
        return production_orders
    
    def find_first_red_message(self, production_order: Message) -> Optional[Message]:
        """Findet die erste Message nach dem Production Order Request mit type = 'RED'."""
        production_time = production_order.parsed_timestamp
        
        for message in self.messages:
            if message.parsed_timestamp <= production_time:
                continue
                
            # Suche nach type = "RED" in verschiedenen Feldern
            payload = message.payload
            if (payload.get('type') == 'RED' or 
                payload.get('message_type') == 'RED' or
                (isinstance(payload, dict) and any(str(v) == 'RED' for v in payload.values() if isinstance(v, str)))):
                print(f"🔴 Erste RED Message gefunden: {message.topic} -> {message.timestamp}")
                return message
        
        return None
    
    def find_order_id_enrichment(self, production_order: Message) -> Optional[Message]:
        """Findet die erste Message nach dem Production Order Request, die eine orderId hinzufügt."""
        production_time = production_order.parsed_timestamp
        
        for message in self.messages:
            if message.parsed_timestamp <= production_time:
                continue
                
            # Suche nach orderId in verschiedenen Formaten
            order_id = self._extract_order_id(message)
            if order_id and order_id not in ['', '0', 0, None]:
                print(f"🎯 OrderId Enrichment gefunden: {message.topic} -> {order_id}")
                return message
        
        return None
    
    def _extract_order_id(self, message: Message) -> Optional[str]:
        """Extrahiert orderId aus einer Message."""
        payload = message.payload
        
        # Verschiedene mögliche orderId Felder
        for field in ['orderId', 'order_id', 'orderUuid', 'orderUuid']:
            if field in payload:
                value = payload[field]
                if value and value not in ['', '0', 0, None]:
                    return str(value)
        
        # Suche in verschachtelten Objekten
        if 'action' in payload and 'id' in payload['action']:
            action_id = payload['action']['id']
            if action_id and action_id not in ['', '0', 0, None]:
                return str(action_id)
        
        return None
    
    def find_related_messages(self, production_order: Message, order_id: str) -> List[Message]:
        """Findet alle Messages, die dieselbe orderId haben."""
        related_messages = []
        
        for message in self.messages:
            extracted_order_id = self._extract_order_id(message)
            if extracted_order_id == order_id:
                related_messages.append(message)
        
        print(f"🔗 {len(related_messages)} verwandte Messages für orderId {order_id}")
        return related_messages
    
    def build_message_graph(self) -> None:
        """Baut einen Graph des Message-Flows."""
        production_orders = self.find_production_order_requests()
        
        for i, prod_order in enumerate(production_orders):
            print(f"\n📊 Analysiere Production Order {i+1}:")
            print(f"   Zeitpunkt: {prod_order.timestamp}")
            print(f"   Topic: {prod_order.topic}")
            print(f"   Payload: {prod_order.payload}")
            
            # Finde Enrichment
            enrichment = self.find_order_id_enrichment(prod_order)
            if not enrichment:
                print("   ❌ Keine orderId Enrichment gefunden")
                continue
            
            order_id = self._extract_order_id(enrichment)
            if not order_id:
                print("   ❌ Keine orderId extrahiert")
                continue
            
            # Finde verwandte Messages
            related_messages = self.find_related_messages(prod_order, order_id)
            
            # Baue Graph
            self._build_graph_for_order(prod_order, enrichment, related_messages, order_id)
    
    def _build_graph_for_order(self, prod_order: Message, enrichment: Message, 
                              related_messages: List[Message], order_id: str) -> None:
        """Baut den Graph für eine spezifische Production Order."""
        # Root Node
        self.graph.add_node(f"prod_order_{order_id}", 
                           type="production_order", 
                           timestamp=prod_order.timestamp,
                           topic=prod_order.topic,
                           payload=prod_order.payload)
        
        # Suche nach erster RED Message
        first_red = self.find_first_red_message(prod_order)
        
        # Enrichment Node
        self.graph.add_node(f"enrichment_{order_id}",
                           type="order_id_enrichment",
                           timestamp=enrichment.timestamp,
                           topic=enrichment.topic,
                           payload=enrichment.payload,
                           order_id=order_id)
        
        # Verbinde Production Order mit Enrichment
        self.graph.add_edge(f"prod_order_{order_id}", f"enrichment_{order_id}",
                           relationship="enriches_with_order_id")
        
        # Füge erste RED Message hinzu (falls gefunden)
        if first_red:
            self.graph.add_node(f"first_red_{order_id}",
                               type="first_red_message",
                               timestamp=first_red.timestamp,
                               topic=first_red.topic,
                               payload=first_red.payload)
            
            # Verbinde Production Order mit erster RED Message
            self.graph.add_edge(f"prod_order_{order_id}", f"first_red_{order_id}",
                               relationship="triggers_red_message")
        
        # Füge verwandte Messages hinzu
        for i, msg in enumerate(related_messages):
            node_id = f"related_{order_id}_{i}"
            self.graph.add_node(node_id,
                               type="related_message",
                               timestamp=msg.timestamp,
                               topic=msg.topic,
                               payload=msg.payload,
                               order_id=order_id)
            
            # Verbinde mit Enrichment
            self.graph.add_edge(f"enrichment_{order_id}", node_id,
                               relationship="related_message")
        
        print(f"   ✅ Graph erstellt: {len(related_messages)} verwandte Messages")
    
    def generate_mermaid_diagram(self) -> str:
        """Generiert ein Mermaid Swimlane-Diagramm mit Zeitachse."""
        if not self.graph.nodes():
            return "graph LR\n    A[Keine Messages gefunden]"
        
        # Sammle alle Messages und gruppiere nach Topic
        messages_by_topic = {}
        production_orders = []
        enrichments = []
        first_red_messages = []
        
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            topic = data.get('topic', 'unknown')
            timestamp = data.get('timestamp', 'unknown')
            
            if node_type == "production_order":
                production_orders.append((node_id, data))
            elif node_type == "order_id_enrichment":
                enrichments.append((node_id, data))
            elif node_type == "first_red_message":
                first_red_messages.append((node_id, data))
            elif node_type == "related_message":
                if topic not in messages_by_topic:
                    messages_by_topic[topic] = []
                messages_by_topic[topic].append((node_id, data))
        
        # Sortiere Messages nach Zeitstempel
        for topic in messages_by_topic:
            messages_by_topic[topic].sort(key=lambda x: x[1].get('timestamp', ''))
        
        # Erstelle Swimlane-Diagramm
        mermaid_lines = ["graph LR"]
        
        # Definiere Swimlanes (Topics)
        swimlanes = []
        if production_orders:
            swimlanes.append("Production Orders")
        if first_red_messages:
            swimlanes.append("First RED Messages")
        if enrichments:
            swimlanes.append("OrderId Enrichment")
        
        # Füge alle Topics als Swimlanes hinzu
        for topic in sorted(messages_by_topic.keys()):
            # Kürze lange Topic-Namen
            short_topic = topic.replace('/j1/txt/1/f/', 'TXT/').replace('ccu/', 'CCU/').replace('fts/v1/ff/', 'FTS/')
            if len(short_topic) > 20:
                short_topic = short_topic[:17] + "..."
            swimlanes.append(short_topic)
        
        # Erstelle Subgraph für jede Swimlane
        for i, lane in enumerate(swimlanes):
            mermaid_lines.append(f"    subgraph {lane.replace(' ', '_').replace('/', '_')}[\"{lane}\"]")
            
            if lane == "Production Orders":
                for node_id, data in production_orders:
                    timestamp = data.get('timestamp', '')[:19]  # Kürze Timestamp
                    mermaid_lines.append(f"        {node_id}[\"🎯 PROD<br/>{timestamp}\"]")
            elif lane == "First RED Messages":
                for node_id, data in first_red_messages:
                    timestamp = data.get('timestamp', '')[:19]
                    mermaid_lines.append(f"        {node_id}[\"🔴 RED<br/>{timestamp}\"]")
            elif lane == "OrderId Enrichment":
                for node_id, data in enrichments:
                    timestamp = data.get('timestamp', '')[:19]
                    mermaid_lines.append(f"        {node_id}[\"🎯 ENRICH<br/>{timestamp}\"]")
            else:
                # Topic-spezifische Messages
                topic_key = None
                for topic in messages_by_topic.keys():
                    if topic.replace('/j1/txt/1/f/', 'TXT/').replace('ccu/', 'CCU/').replace('fts/v1/ff/', 'FTS/') == lane or \
                       (len(lane) > 17 and topic.replace('/j1/txt/1/f/', 'TXT/').replace('ccu/', 'CCU/').replace('fts/v1/ff/', 'FTS/').startswith(lane[:17])):
                        topic_key = topic
                        break
                
                if topic_key and topic_key in messages_by_topic:
                    # Zeige nur die ersten 5 Messages pro Topic (um Diagramm übersichtlich zu halten)
                    for j, (node_id, data) in enumerate(messages_by_topic[topic_key][:5]):
                        timestamp = data.get('timestamp', '')[:19]
                        mermaid_lines.append(f"        {node_id}[\"📨 {j+1}<br/>{timestamp}\"]")
                    
                    # Falls mehr als 5 Messages, zeige "..." Node
                    if len(messages_by_topic[topic_key]) > 5:
                        more_node = f"more_{i}"
                        mermaid_lines.append(f"        {more_node}[\"... +{len(messages_by_topic[topic_key])-5} more\"]")
            
            mermaid_lines.append("    end")
        
        # Erstelle Verbindungen zwischen den wichtigsten Knoten
        # Production Order -> First RED Message
        if production_orders and first_red_messages:
            prod_id = production_orders[0][0]
            red_id = first_red_messages[0][0]
            mermaid_lines.append(f"    {prod_id} -.-> {red_id}")
        
        # First RED Message -> OrderId Enrichment
        if first_red_messages and enrichments:
            red_id = first_red_messages[0][0]
            enrich_id = enrichments[0][0]
            mermaid_lines.append(f"    {red_id} -.-> {enrich_id}")
        
        # OrderId Enrichment -> erste Messages in anderen Topics
        if enrichments:
            enrich_id = enrichments[0][0]
            for topic in list(messages_by_topic.keys())[:3]:  # Verbinde nur mit ersten 3 Topics
                if messages_by_topic[topic]:
                    first_msg_id = messages_by_topic[topic][0][0]
                    mermaid_lines.append(f"    {enrich_id} -.-> {first_msg_id}")
        
        return '\n'.join(mermaid_lines)
    
    def analyze(self) -> Dict[str, Any]:
        """Führt die komplette Analyse durch und gibt Ergebnisse zurück."""
        # Lade Session falls noch nicht geladen
        if not self.messages:
            self.load_session()
        
        # Baue Graph
        self.build_message_graph()
        
        # Sammle beteiligte Topics
        involved_topics = self._get_involved_topics()
        
        # Sammle Ergebnisse
        production_orders = self.find_production_order_requests()
        results = {
            "production_orders": production_orders,
            "graph_nodes": self.graph.number_of_nodes(),
            "graph_edges": self.graph.number_of_edges(),
            "mermaid_diagram": self.generate_mermaid_diagram(),
            "involved_topics": involved_topics
        }
        
        return results
    
    def _get_involved_topics(self) -> List[Dict[str, Any]]:
        """Sammelt alle beteiligten Topics mit Statistiken."""
        topics = {}
        
        for node_id, data in self.graph.nodes(data=True):
            topic = data.get('topic', 'unknown')
            node_type = data.get('type', 'unknown')
            timestamp = data.get('timestamp', '')
            
            if topic not in topics:
                topics[topic] = {
                    'topic': topic,
                    'message_count': 0,
                    'first_timestamp': timestamp,
                    'last_timestamp': timestamp,
                    'types': set()
                }
            
            topics[topic]['message_count'] += 1
            topics[topic]['types'].add(node_type)
            
            # Aktualisiere Zeitstempel
            if timestamp < topics[topic]['first_timestamp']:
                topics[topic]['first_timestamp'] = timestamp
            if timestamp > topics[topic]['last_timestamp']:
                topics[topic]['last_timestamp'] = timestamp
        
        # Konvertiere zu Liste und sortiere nach erster Message
        topic_list = []
        for topic_data in topics.values():
            topic_data['types'] = list(topic_data['types'])
            topic_list.append(topic_data)
        
        # Sortiere nach erstem Zeitstempel
        topic_list.sort(key=lambda x: x['first_timestamp'])
        
        return topic_list
    
    def print_analysis_summary(self) -> None:
        """Druckt eine Zusammenfassung der Analyse."""
        print("\n" + "="*60)
        print("📊 PRODUCTION ORDER FLOW ANALYSIS SUMMARY")
        print("="*60)
        
        production_orders = self.find_production_order_requests()
        print(f"🔍 Production Order Requests: {len(production_orders)}")
        
        if production_orders:
            for i, prod_order in enumerate(production_orders):
                print(f"\n📋 Production Order {i+1}:")
                print(f"   Zeitpunkt: {prod_order.timestamp}")
                print(f"   Topic: {prod_order.topic}")
                print(f"   Type: {prod_order.payload.get('type')}")
                print(f"   OrderType: {prod_order.payload.get('orderType')}")
                
                # Suche nach erster RED Message
                first_red = self.find_first_red_message(prod_order)
                if first_red:
                    print(f"   🔴 Erste RED Message: {first_red.topic} -> {first_red.timestamp}")
                else:
                    print(f"   ❌ Keine RED Message gefunden")
                
                enrichment = self.find_order_id_enrichment(prod_order)
                if enrichment:
                    order_id = self._extract_order_id(enrichment)
                    print(f"   ✅ OrderId Enrichment: {enrichment.topic} -> {order_id}")
                    
                    related = self.find_related_messages(prod_order, order_id)
                    print(f"   🔗 Verwandte Messages: {len(related)}")
                else:
                    print(f"   ❌ Keine OrderId Enrichment gefunden")
        
        print(f"\n📈 Graph Statistiken:")
        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {self.graph.number_of_edges()}")


def main():
    """Hauptfunktion für CLI-Usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Order Message Flow Analyzer")
    parser.add_argument("--session", "-s", 
                       default="data/omf-data/sessions/auftrag-rot_1.log",
                       help="Pfad zur Session-Datei")
    parser.add_argument("--output", "-o", 
                       help="Ausgabedatei für Mermaid-Diagramm")
    
    args = parser.parse_args()
    
    session_file = Path(args.session)
    if not session_file.exists():
        print(f"❌ Session-Datei nicht gefunden: {session_file}")
        return 1
    
    analyzer = ProductionOrderFlowAnalyzer(session_file)
    
    try:
        analyzer.load_session()
        analyzer.build_message_graph()
        analyzer.print_analysis_summary()
        
        # Generiere Mermaid-Diagramm
        mermaid = analyzer.generate_mermaid_diagram()
        print(f"\n🎨 MERMAID DIAGRAMM:")
        print("-" * 40)
        print(mermaid)
        
        if args.output:
            output_file = Path(args.output)
            output_file.write_text(mermaid, encoding='utf-8')
            print(f"\n💾 Mermaid-Diagramm gespeichert: {output_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Fehler bei der Analyse: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
