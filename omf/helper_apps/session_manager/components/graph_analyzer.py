"""
Graph Analyzer - Message Chain Analysis and Graph Visualization

Analysiert Message-Ketten basierend auf Meta-Informationen (orderId, workpieceId, nfcCode)
und erstellt gerichtete Graphen für die Visualisierung.
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import networkx as nx

from omf.tools.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MessageNode:
    """Repräsentiert einen Knoten im Message-Graph"""

    message_id: str
    timestamp: datetime
    topic: str
    payload: Dict[str, Any]
    order_id: Optional[str] = None
    workpiece_id: Optional[str] = None
    nfc_code: Optional[str] = None
    module_id: Optional[str] = None
    message_type: Optional[str] = None


@dataclass
class MessageEdge:
    """Repräsentiert eine Kante im Message-Graph"""

    source_id: str
    target_id: str
    connection_type: str  # 'order_id', 'workpiece_id', 'nfc_code', 'temporal'
    weight: float = 1.0
    metadata: Dict[str, Any] = None


class GraphAnalyzer:
    """Analysiert Message-Ketten und erstellt Graphen für Visualisierung"""

    def __init__(self):
        self.messages: List[MessageNode] = []
        self.graph: nx.DiGraph = nx.DiGraph()
        self.message_chains: List[List[MessageNode]] = []
        self.connection_stats: Dict[str, int] = defaultdict(int)

    def analyze_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Analysiert eine Session und extrahiert Message-Ketten

        Args:
            session_data: Session-Daten mit Messages

        Returns:
            True wenn erfolgreich
        """
        try:
            logger.debug("Starte Graph-Analyse der Session")

            # Messages extrahieren und parsen
            self.messages = self._extract_message_nodes(session_data)
            logger.debug(f"Extrahierte {len(self.messages)} Message-Nodes")

            # Graphen erstellen
            self.graph = self._build_message_graph()
            logger.debug(
                f"Graph erstellt mit {self.graph.number_of_nodes()} Knoten und {self.graph.number_of_edges()} Kanten"
            )

            # Message-Ketten identifizieren
            self.message_chains = self._identify_message_chains()
            logger.debug(f"Identifizierte {len(self.message_chains)} Message-Ketten")

            # Statistiken berechnen
            self._calculate_connection_stats()

            return True

        except Exception as e:
            logger.error(f"Fehler bei Graph-Analyse: {e}", exc_info=True)
            return False

    def _extract_message_nodes(self, session_data: Dict[str, Any]) -> List[MessageNode]:
        """Extrahiert Message-Nodes aus Session-Daten"""
        messages = []

        for i, msg in enumerate(session_data.get("messages", [])):
            try:
                # Payload parsen
                payload = self._parse_payload(msg.get("payload", "{}"))

                # Meta-Informationen extrahieren
                order_id = self._extract_order_id(payload)
                workpiece_id = self._extract_workpiece_id(payload)
                nfc_code = self._extract_nfc_code(payload)
                module_id = self._extract_module_id(msg.get("topic", ""))
                message_type = self._extract_message_type(msg.get("topic", ""))

                node = MessageNode(
                    message_id=f"msg_{i}",
                    timestamp=msg.get("timestamp"),
                    topic=msg.get("topic", ""),
                    payload=payload,
                    order_id=order_id,
                    workpiece_id=workpiece_id,
                    nfc_code=nfc_code,
                    module_id=module_id,
                    message_type=message_type,
                )

                messages.append(node)

            except Exception as e:
                logger.warning(f"Fehler beim Parsen von Message {i}: {e}")
                continue

        return messages

    def _parse_payload(self, payload_str: str) -> Dict[str, Any]:
        """Parst JSON-Payload"""
        try:
            if isinstance(payload_str, str):
                return json.loads(payload_str)
            elif isinstance(payload_str, dict):
                return payload_str
            else:
                return {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def _extract_order_id(self, payload: Dict[str, Any]) -> Optional[str]:
        """Extrahiert Order-ID aus Payload"""
        # Verschiedene mögliche Felder für Order-ID
        order_fields = ["orderId", "order_id", "order", "id", "orderNumber"]

        for field in order_fields:
            if field in payload:
                value = payload[field]
                if value and str(value).strip():
                    return str(value).strip()

        return None

    def _extract_workpiece_id(self, payload: Dict[str, Any]) -> Optional[str]:
        """Extrahiert Workpiece-ID aus Payload"""
        # Verschiedene mögliche Felder für Workpiece-ID
        workpiece_fields = ["workpieceId", "workpiece_id", "workpiece", "partId", "part_id"]

        for field in workpiece_fields:
            if field in payload:
                value = payload[field]
                if value and str(value).strip():
                    return str(value).strip()

        return None

    def _extract_nfc_code(self, payload: Dict[str, Any]) -> Optional[str]:
        """Extrahiert NFC-Code aus Payload"""
        # Verschiedene mögliche Felder für NFC-Code
        nfc_fields = ["nfcCode", "nfc_code", "nfc", "rfid", "tag"]

        for field in nfc_fields:
            if field in payload:
                value = payload[field]
                if value and str(value).strip():
                    return str(value).strip()

        return None

    def _extract_module_id(self, topic: str) -> Optional[str]:
        """Extrahiert Module-ID aus Topic"""
        # Topic-Pattern: module/v1/ff/{serial_number}/state
        if "/module/v1/ff/" in topic:
            parts = topic.split("/")
            if len(parts) >= 4:
                return parts[3]
        return None

    def _extract_message_type(self, topic: str) -> Optional[str]:
        """Extrahiert Message-Typ aus Topic"""
        if "/state" in topic:
            return "state"
        elif "/order" in topic:
            return "order"
        elif "/status" in topic:
            return "status"
        elif "/flow" in topic:
            return "flow"
        else:
            return "other"

    def _build_message_graph(self) -> nx.DiGraph:
        """Baut den Message-Graph auf"""
        graph = nx.DiGraph()

        # Knoten hinzufügen
        for msg in self.messages:
            graph.add_node(
                msg.message_id,
                timestamp=msg.timestamp,
                topic=msg.topic,
                order_id=msg.order_id,
                workpiece_id=msg.workpiece_id,
                nfc_code=msg.nfc_code,
                module_id=msg.module_id,
                message_type=msg.message_type,
            )

        # Kanten hinzufügen basierend auf Meta-Informationen
        for i, msg1 in enumerate(self.messages):
            for _j, msg2 in enumerate(self.messages[i + 1 :], i + 1):
                # Prüfe verschiedene Verbindungstypen
                edge = self._find_connection(msg1, msg2)
                if edge:
                    graph.add_edge(
                        edge.source_id,
                        edge.target_id,
                        connection_type=edge.connection_type,
                        weight=edge.weight,
                        metadata=edge.metadata or {},
                    )

        return graph

    def _find_connection(self, msg1: MessageNode, msg2: MessageNode) -> Optional[MessageEdge]:
        """Findet Verbindungen zwischen zwei Messages"""
        # Order-ID Verbindung
        if msg1.order_id and msg2.order_id and msg1.order_id == msg2.order_id:
            return MessageEdge(
                source_id=msg1.message_id,
                target_id=msg2.message_id,
                connection_type="order_id",
                weight=1.0,
                metadata={"order_id": msg1.order_id},
            )

        # Workpiece-ID Verbindung
        if msg1.workpiece_id and msg2.workpiece_id and msg1.workpiece_id == msg2.workpiece_id:
            return MessageEdge(
                source_id=msg1.message_id,
                target_id=msg2.message_id,
                connection_type="workpiece_id",
                weight=0.8,
                metadata={"workpiece_id": msg1.workpiece_id},
            )

        # NFC-Code Verbindung
        if msg1.nfc_code and msg2.nfc_code and msg1.nfc_code == msg2.nfc_code:
            return MessageEdge(
                source_id=msg1.message_id,
                target_id=msg2.message_id,
                connection_type="nfc_code",
                weight=0.9,
                metadata={"nfc_code": msg1.nfc_code},
            )

        # Module-ID Verbindung (gleiches Modul)
        if msg1.module_id and msg2.module_id and msg1.module_id == msg2.module_id:
            return MessageEdge(
                source_id=msg1.message_id,
                target_id=msg2.message_id,
                connection_type="module_id",
                weight=0.6,
                metadata={"module_id": msg1.module_id},
            )

        # Zeitliche Verbindung (innerhalb von 30 Sekunden)
        time_diff = abs((msg2.timestamp - msg1.timestamp).total_seconds())
        if time_diff <= 30:
            return MessageEdge(
                source_id=msg1.message_id,
                target_id=msg2.message_id,
                connection_type="temporal",
                weight=0.3,
                metadata={"time_diff": time_diff},
            )

        return None

    def _identify_message_chains(self) -> List[List[MessageNode]]:
        """Identifiziert Message-Ketten im Graph"""
        chains = []

        # Finde alle starken Komponenten (zusammenhängende Teile)
        strongly_connected = list(nx.strongly_connected_components(self.graph))

        for component in strongly_connected:
            if len(component) > 1:  # Nur Ketten mit mehr als einem Knoten
                chain_messages = [msg for msg in self.messages if msg.message_id in component]
                # Sortiere nach Zeitstempel
                chain_messages.sort(key=lambda x: x.timestamp)
                chains.append(chain_messages)

        # Sortiere Ketten nach Länge (längste zuerst)
        chains.sort(key=len, reverse=True)

        return chains

    def _calculate_connection_stats(self):
        """Berechnet Verbindungsstatistiken"""
        for edge in self.graph.edges(data=True):
            connection_type = edge[2].get("connection_type", "unknown")
            self.connection_stats[connection_type] += 1

    def get_graph_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung des Graphen zurück"""
        return {
            "total_messages": len(self.messages),
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "message_chains": len(self.message_chains),
            "connection_stats": dict(self.connection_stats),
            "graph_density": nx.density(self.graph),
            "is_connected": nx.is_weakly_connected(self.graph),
            "strongly_connected_components": nx.number_strongly_connected_components(self.graph),
        }

    def get_message_chains(self, min_length: int = 2) -> List[List[MessageNode]]:
        """Gibt Message-Ketten zurück (gefiltert nach Mindestlänge)"""
        return [chain for chain in self.message_chains if len(chain) >= min_length]

    def get_connected_messages(self, message_id: str, max_depth: int = 3) -> List[MessageNode]:
        """Gibt mit einer Message verbundene Messages zurück"""
        if message_id not in self.graph:
            return []

        # BFS bis max_depth
        visited = set()
        queue = [(message_id, 0)]
        connected = []

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            # Finde Message-Node
            message_node = next((msg for msg in self.messages if msg.message_id == current_id), None)
            if message_node:
                connected.append(message_node)

            # Füge Nachbarn zur Queue hinzu
            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))

        return connected

    def export_graph_data(self) -> Dict[str, Any]:
        """Exportiert Graph-Daten für Visualisierung"""
        # Konvertiere zu JSON-serialisierbarem Format
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append(
                {
                    "id": node_id,
                    "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None,
                    "topic": data.get("topic"),
                    "order_id": data.get("order_id"),
                    "workpiece_id": data.get("workpiece_id"),
                    "nfc_code": data.get("nfc_code"),
                    "module_id": data.get("module_id"),
                    "message_type": data.get("message_type"),
                }
            )

        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "connection_type": data.get("connection_type"),
                    "weight": data.get("weight"),
                    "metadata": data.get("metadata", {}),
                }
            )

        return {"nodes": nodes, "edges": edges, "summary": self.get_graph_summary()}
