"""
Message Handler for Message Center
Handles message processing, formatting, and filtering
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MessageRow:
    """Data class for message table rows"""
    topic: str
    payload: Any
    message_type: str  # "sent" or "received"
    timestamp: float
    qos: int = 0
    retain: bool = False
    
    def get_formatted_timestamp(self) -> str:
        """Get formatted timestamp string"""
        return datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def get_formatted_payload(self) -> str:
        """Get formatted payload string"""
        if isinstance(self.payload, dict):
            import json
            return json.dumps(self.payload, indent=2, ensure_ascii=False)
        elif isinstance(self.payload, list):
            import json  
            return json.dumps(self.payload, indent=2, ensure_ascii=False)
        else:
            return str(self.payload)
    
    def get_topic_display_name(self) -> str:
        """Get friendly display name for topic"""
        # Map common topics to friendly names
        topic_mapping = {
            "f/i/order": "📋 Orders",
            "f/i/state": "🔄 State",
            "f/i/visualization": "📊 Visualization",
            "f/i/instantActions": "⚡ Instant Actions",
            "omf/hbw": "🏭 HBW",
            "omf/fts": "🚚 FTS",
            "omf/mill": "⚙️ Mill",
            "omf/drill": "🔩 Drill",
            "omf/oven": "🔥 Oven",
            "nodered": "🔴 Node-RED",
            "ccu": "🖥️ CCU",
            "txt": "📝 TXT"
        }
        
        # Check for exact match first
        if self.topic in topic_mapping:
            return topic_mapping[self.topic]
        
        # Check for partial matches
        for key, display_name in topic_mapping.items():
            if key in self.topic.lower():
                return f"{display_name} ({self.topic})"
        
        return self.topic


class MessageHandler:
    """
    Handles message processing, formatting, and filtering for the message center
    """
    
    def __init__(self):
        self.logger = logging.getLogger("omf2.message_center.message_handler")
    
    def convert_messages_to_rows(self, messages: List[Dict[str, Any]]) -> List[MessageRow]:
        """
        Convert raw message dictionaries to MessageRow objects
        
        Args:
            messages: List of raw message dictionaries
            
        Returns:
            List[MessageRow]: Converted message rows
        """
        rows = []
        for msg in messages:
            try:
                row = MessageRow(
                    topic=msg.get("topic", ""),
                    payload=msg.get("payload", {}),
                    message_type=msg.get("type", "received"),
                    timestamp=msg.get("timestamp", 0),
                    qos=msg.get("qos", 0),
                    retain=msg.get("retain", False)
                )
                rows.append(row)
            except Exception as e:
                self.logger.error(f"Error converting message to row: {e}")
        
        return rows
    
    def filter_messages_by_topic(self, messages: List[MessageRow], topic_filter: str) -> List[MessageRow]:
        """
        Filter messages by topic pattern
        
        Args:
            messages: List of message rows
            topic_filter: Topic filter pattern (case-insensitive)
            
        Returns:
            List[MessageRow]: Filtered messages
        """
        if not topic_filter.strip():
            return messages
        
        filter_lower = topic_filter.lower().strip()
        filtered = []
        
        for msg in messages:
            if filter_lower in msg.topic.lower():
                filtered.append(msg)
        
        return filtered
    
    def filter_messages_by_type(self, messages: List[MessageRow], message_type: str) -> List[MessageRow]:
        """
        Filter messages by type (sent/received)
        
        Args:
            messages: List of message rows
            message_type: "sent", "received", or "all"
            
        Returns:
            List[MessageRow]: Filtered messages
        """
        if message_type == "all":
            return messages
        
        return [msg for msg in messages if msg.message_type == message_type]
    
    def filter_messages_by_module(self, messages: List[MessageRow], module_filter: str) -> List[MessageRow]:
        """
        Filter messages by module (HBW, FTS, MILL, etc.)
        
        Args:
            messages: List of message rows
            module_filter: Module name or "all"
            
        Returns:
            List[MessageRow]: Filtered messages
        """
        if module_filter == "all":
            return messages
        
        module_mapping = {
            "HBW": "hbw",
            "FTS": "fts", 
            "MILL": "mill",
            "DRILL": "drill",
            "OVEN": "oven",
            "AIQS": "aiqs",
            "CCU": "ccu",
            "TXT": "txt",
            "Node-RED": "nodered"
        }
        
        search_term = module_mapping.get(module_filter, module_filter.lower())
        return [msg for msg in messages if search_term in msg.topic.lower()]
    
    def sort_messages(self, messages: List[MessageRow], sort_by: str = "timestamp", ascending: bool = False) -> List[MessageRow]:
        """
        Sort messages by specified field
        
        Args:
            messages: List of message rows
            sort_by: Field to sort by ("timestamp", "topic", "type")
            ascending: Sort order (True for ascending, False for descending)
            
        Returns:
            List[MessageRow]: Sorted messages
        """
        try:
            if sort_by == "timestamp":
                return sorted(messages, key=lambda x: x.timestamp, reverse=not ascending)
            elif sort_by == "topic":
                return sorted(messages, key=lambda x: x.topic, reverse=not ascending)
            elif sort_by == "type":
                return sorted(messages, key=lambda x: x.message_type, reverse=not ascending)
            else:
                self.logger.warning(f"Unknown sort field: {sort_by}")
                return messages
        except Exception as e:
            self.logger.error(f"Error sorting messages: {e}")
            return messages
    
    def get_message_statistics(self, messages: List[MessageRow]) -> Dict[str, Any]:
        """
        Calculate statistics for message list
        
        Args:
            messages: List of message rows
            
        Returns:
            Dict: Statistics including counts, topics, etc.
        """
        if not messages:
            return {
                "total": 0,
                "sent": 0,
                "received": 0,
                "unique_topics": 0,
                "topics": [],
                "modules": []
            }
        
        # Count by type
        sent_count = sum(1 for msg in messages if msg.message_type == "sent")
        received_count = len(messages) - sent_count
        
        # Get unique topics
        unique_topics = list(set(msg.topic for msg in messages))
        
        # Extract modules from topics
        modules = set()
        for topic in unique_topics:
            topic_lower = topic.lower()
            if "hbw" in topic_lower:
                modules.add("HBW")
            elif "fts" in topic_lower:
                modules.add("FTS")
            elif "mill" in topic_lower:
                modules.add("MILL")
            elif "drill" in topic_lower:
                modules.add("DRILL")
            elif "oven" in topic_lower:
                modules.add("OVEN")
            elif "aiqs" in topic_lower:
                modules.add("AIQS")
            elif "ccu" in topic_lower:
                modules.add("CCU")
            elif "txt" in topic_lower:
                modules.add("TXT")
            elif "nodered" in topic_lower:
                modules.add("Node-RED")
        
        return {
            "total": len(messages),
            "sent": sent_count,
            "received": received_count,
            "unique_topics": len(unique_topics),
            "topics": unique_topics[:20],  # Limit to first 20 topics
            "modules": sorted(list(modules))
        }
    
    def create_table_data(self, messages: List[MessageRow]) -> Tuple[List[str], List[List[str]]]:
        """
        Create table data for display
        
        Args:
            messages: List of message rows
            
        Returns:
            Tuple[List[str], List[List[str]]]: Headers and data rows
        """
        headers = ["Zeit", "Typ", "Topic", "Payload", "QoS", "Retain"]
        
        rows = []
        for msg in messages:
            row = [
                msg.get_formatted_timestamp(),
                "📤" if msg.message_type == "sent" else "📥",
                msg.get_topic_display_name(),
                msg.get_formatted_payload()[:100] + "..." if len(msg.get_formatted_payload()) > 100 else msg.get_formatted_payload(),
                str(msg.qos),
                "✓" if msg.retain else ""
            ]
            rows.append(row)
        
        return headers, rows
    
    def get_recent_activity_summary(self, messages: List[MessageRow], minutes: int = 5) -> Dict[str, Any]:
        """
        Get summary of recent activity
        
        Args:
            messages: List of message rows
            minutes: Time window in minutes
            
        Returns:
            Dict: Summary of recent activity
        """
        import time
        cutoff_time = time.time() - (minutes * 60)
        
        recent_messages = [msg for msg in messages if msg.timestamp > cutoff_time]
        
        if not recent_messages:
            return {
                "count": 0,
                "sent": 0,
                "received": 0,
                "active_topics": []
            }
        
        sent_count = sum(1 for msg in recent_messages if msg.message_type == "sent")
        received_count = len(recent_messages) - sent_count
        active_topics = list(set(msg.topic for msg in recent_messages))
        
        return {
            "count": len(recent_messages),
            "sent": sent_count,
            "received": received_count,
            "active_topics": active_topics[:10]  # Limit to 10 most recent topics
        }