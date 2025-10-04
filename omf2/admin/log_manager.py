#!/usr/bin/env python3
"""
Log Manager - System log management and analysis
Business logic layer that uses the central log buffer from omf2.common.logger
"""

import logging
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Deque
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry:
    """Represents a single log entry parsed from the central log buffer"""
    
    def __init__(self, timestamp: datetime, level: LogLevel, component: str, 
                 message: str, raw_line: str = ""):
        self.timestamp = timestamp
        self.level = level
        self.component = component
        self.message = message
        self.raw_line = raw_line  # Original log line from buffer
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "component": self.component,
            "message": self.message
        }
    
    @classmethod
    def from_log_line(cls, log_line: str) -> Optional['LogEntry']:
        """
        Parse a log entry from a formatted log line.
        Expected format: "YYYY-MM-DD HH:MM:SS [LEVEL] component.name: message"
        """
        try:
            # Parse format: "2025-01-01 12:00:00 [INFO] omf2.dashboard: Test message"
            pattern = r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})[,\s]+\[(\w+)\]\s+([\w\.]+):\s+(.*)$'
            match = re.match(pattern, log_line)
            
            if match:
                timestamp_str, level_str, component, message = match.groups()
                
                # Parse timestamp (handle both formats)
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # Try alternative format with milliseconds
                    timestamp = datetime.strptime(timestamp_str.split(',')[0], "%Y-%m-%d %H:%M:%S")
                
                # Parse level
                try:
                    level = LogLevel(level_str.upper())
                except ValueError:
                    level = LogLevel.INFO  # Default fallback
                
                return cls(
                    timestamp=timestamp,
                    level=level,
                    component=component,
                    message=message.strip(),
                    raw_line=log_line
                )
        except Exception as e:
            logger.debug(f"Failed to parse log line: {log_line[:50]}... Error: {e}")
        
        return None


class LogManager:
    """
    Log Manager - Handles system log analysis and access to central log buffer
    Business logic layer that reads from the central log buffer
    """
    
    def __init__(self, log_buffer: Optional[Deque[str]] = None, logs_dir: Path = None):
        """
        Initialize LogManager with central log buffer.
        
        Args:
            log_buffer: Central log buffer (deque of log strings)
            logs_dir: Directory for log file exports
        """
        self.log_buffer = log_buffer  # Central log buffer from omf2.common.logger
        self.logs_dir = logs_dir or Path(__file__).parent.parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        logger.info(f"📝 Log Manager initialized with logs dir: {self.logs_dir}")
    
    def set_log_buffer(self, log_buffer: Deque[str]):
        """Set the central log buffer (for late initialization)"""
        self.log_buffer = log_buffer
        logger.info("📝 Log buffer connected to LogManager")
    
    def _parse_log_entries(self, raw_lines: List[str]) -> List[LogEntry]:
        """Parse raw log lines into LogEntry objects"""
        entries = []
        for line in raw_lines:
            entry = LogEntry.from_log_line(line)
            if entry:
                entries.append(entry)
        return entries
    
    def get_logs(self, limit: int = 100, 
                level: Optional[LogLevel] = None,
                component: Optional[str] = None,
                since: Optional[datetime] = None) -> List[LogEntry]:
        """Get filtered log entries from central buffer"""
        if not self.log_buffer:
            logger.warning("Log buffer not available")
            return []
        
        # Get raw log lines from buffer
        raw_lines = list(self.log_buffer)
        
        # Parse into LogEntry objects
        entries = self._parse_log_entries(raw_lines)
        
        # Apply filters
        if level:
            entries = [e for e in entries if e.level == level]
        
        if component:
            entries = [e for e in entries if component.lower() in e.component.lower()]
        
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        
        # Apply limit (most recent first)
        if limit and len(entries) > limit:
            entries = entries[-limit:]
        
        return entries
    
    def get_recent_logs(self, minutes: int = 60, limit: int = 100) -> List[LogEntry]:
        """Get logs from recent time period"""
        since = datetime.now() - timedelta(minutes=minutes)
        return self.get_logs(limit=limit, since=since)
    
    def get_error_logs(self, limit: int = 50) -> List[LogEntry]:
        """Get error and critical logs"""
        error_logs = self.get_logs(limit=limit*2, level=LogLevel.ERROR)
        critical_logs = self.get_logs(limit=limit*2, level=LogLevel.CRITICAL)
        
        all_logs = error_logs + critical_logs
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return all_logs[:limit]
    
    def get_component_logs(self, component: str, limit: int = 100) -> List[LogEntry]:
        """Get logs for specific component"""
        return self.get_logs(limit=limit, component=component)
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get log statistics from central buffer"""
        if not self.log_buffer:
            return {
                "total_entries": 0,
                "level_distribution": {},
                "component_distribution": {},
                "buffer_size": 0,
                "buffer_usage": "0/0"
            }
        
        # Parse all entries
        raw_lines = list(self.log_buffer)
        entries = self._parse_log_entries(raw_lines)
        
        # Calculate stats
        level_stats = defaultdict(int)
        component_stats = defaultdict(int)
        
        for entry in entries:
            level_stats[entry.level.value] += 1
            component_stats[entry.component] += 1
        
        buffer_size = self.log_buffer.maxlen if hasattr(self.log_buffer, 'maxlen') else 1000
        
        return {
            "total_entries": len(entries),
            "level_distribution": dict(level_stats),
            "component_distribution": dict(component_stats),
            "buffer_size": buffer_size,
            "buffer_usage": f"{len(raw_lines)}/{buffer_size}"
        }
    
    def search_logs(self, query: str, limit: int = 100) -> List[LogEntry]:
        """Search logs by message content"""
        if not self.log_buffer:
            return []
        
        raw_lines = list(self.log_buffer)
        entries = self._parse_log_entries(raw_lines)
        
        query_lower = query.lower()
        matching_entries = []
        
        for entry in reversed(entries):  # Start from most recent
            if query_lower in entry.message.lower() or query_lower in entry.component.lower():
                matching_entries.append(entry)
                if len(matching_entries) >= limit:
                    break
        
        return matching_entries
    
    def export_logs(self, filepath: Path, 
                   level: Optional[LogLevel] = None,
                   component: Optional[str] = None,
                   since: Optional[datetime] = None) -> bool:
        """Export logs to JSON file"""
        try:
            entries = self.get_logs(limit=None, level=level, component=component, since=since)
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "filters": {
                    "level": level.value if level else None,
                    "component": component,
                    "since": since.isoformat() if since else None
                },
                "entries": [entry.to_dict() for entry in entries]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Logs exported to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export logs: {e}")
            return False
    
    def clear_logs(self, component: Optional[str] = None):
        """
        Clear logs from central buffer.
        Note: This clears the entire buffer as it's a deque, component filtering not supported.
        """
        if not self.log_buffer:
            logger.warning("Log buffer not available")
            return
        
        if component:
            logger.warning("Component-specific clearing not supported with central buffer")
            # Would need to filter and rebuild buffer
        else:
            self.log_buffer.clear()
            logger.info("🧹 All logs cleared from central buffer")


# Global log manager instance
_log_manager = None


def get_log_manager(log_buffer: Optional[Deque[str]] = None, **kwargs) -> LogManager:
    """Get global log manager instance"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager(log_buffer=log_buffer, **kwargs)
        logger.info("📝 Log Manager singleton created")
    elif log_buffer and not _log_manager.log_buffer:
        # Set buffer if it wasn't available at initialization
        _log_manager.set_log_buffer(log_buffer)
    return _log_manager