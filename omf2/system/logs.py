#!/usr/bin/env python3
"""
Log Manager - System log management and analysis
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Generator
from datetime import datetime, timedelta
from collections import defaultdict, deque
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
    """Represents a single log entry"""
    
    def __init__(self, timestamp: datetime, level: LogLevel, component: str, 
                 message: str, context: Optional[Dict] = None):
        self.timestamp = timestamp
        self.level = level
        self.component = component
        self.message = message
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "component": self.component,
            "message": self.message,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            level=LogLevel(data["level"]),
            component=data["component"],
            message=data["message"],
            context=data.get("context", {})
        )


class LogBuffer:
    """In-memory log buffer with size limit"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.entries = deque(maxlen=max_size)
        self.stats = defaultdict(int)
    
    def add_entry(self, entry: LogEntry):
        """Add log entry to buffer"""
        self.entries.append(entry)
        self.stats[entry.level.value] += 1
        self.stats[entry.component] += 1
    
    def get_entries(self, limit: Optional[int] = None, 
                   level: Optional[LogLevel] = None,
                   component: Optional[str] = None,
                   since: Optional[datetime] = None) -> List[LogEntry]:
        """Get filtered log entries"""
        entries = list(self.entries)
        
        # Apply filters
        if level:
            entries = [e for e in entries if e.level == level]
        
        if component:
            entries = [e for e in entries if e.component == component]
        
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        
        # Apply limit
        if limit:
            entries = entries[-limit:]
        
        return entries
    
    def get_stats(self) -> Dict[str, Any]:
        """Get log statistics"""
        return dict(self.stats)


class LogManager:
    """
    Log Manager - Handles system log collection, storage and analysis
    """
    
    def __init__(self, logs_dir: Path = None, buffer_size: int = 10000):
        self.logs_dir = logs_dir or Path(__file__).parent.parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.buffer = LogBuffer(buffer_size)
        self.log_files = {}  # component -> file path mapping
        
        logger.info(f"📝 Log Manager initialized with logs dir: {self.logs_dir}")
    
    def add_log_entry(self, level: LogLevel, component: str, message: str, 
                     context: Optional[Dict] = None):
        """Add a log entry"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            component=component,
            message=message,
            context=context
        )
        
        # Add to buffer
        self.buffer.add_entry(entry)
        
        # Write to file
        self._write_to_file(entry)
        
        logger.debug(f"📝 Log entry added: {component} - {level.value} - {message}")
    
    def log_debug(self, component: str, message: str, context: Optional[Dict] = None):
        """Add debug log entry"""
        self.add_log_entry(LogLevel.DEBUG, component, message, context)
    
    def log_info(self, component: str, message: str, context: Optional[Dict] = None):
        """Add info log entry"""
        self.add_log_entry(LogLevel.INFO, component, message, context)
    
    def log_warning(self, component: str, message: str, context: Optional[Dict] = None):
        """Add warning log entry"""
        self.add_log_entry(LogLevel.WARNING, component, message, context)
    
    def log_error(self, component: str, message: str, context: Optional[Dict] = None):
        """Add error log entry"""
        self.add_log_entry(LogLevel.ERROR, component, message, context)
    
    def log_critical(self, component: str, message: str, context: Optional[Dict] = None):
        """Add critical log entry"""
        self.add_log_entry(LogLevel.CRITICAL, component, message, context)
    
    def get_logs(self, limit: int = 100, 
                level: Optional[LogLevel] = None,
                component: Optional[str] = None,
                since: Optional[datetime] = None) -> List[LogEntry]:
        """Get filtered log entries"""
        return self.buffer.get_entries(limit, level, component, since)
    
    def get_recent_logs(self, minutes: int = 60, limit: int = 100) -> List[LogEntry]:
        """Get logs from recent time period"""
        since = datetime.now() - timedelta(minutes=minutes)
        return self.get_logs(limit=limit, since=since)
    
    def get_error_logs(self, limit: int = 50) -> List[LogEntry]:
        """Get error and critical logs"""
        error_logs = self.get_logs(limit=limit//2, level=LogLevel.ERROR)
        critical_logs = self.get_logs(limit=limit//2, level=LogLevel.CRITICAL)
        
        all_logs = error_logs + critical_logs
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return all_logs[:limit]
    
    def get_component_logs(self, component: str, limit: int = 100) -> List[LogEntry]:
        """Get logs for specific component"""
        return self.get_logs(limit=limit, component=component)
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get log statistics"""
        stats = self.buffer.get_stats()
        
        # Calculate additional stats
        total_entries = len(self.buffer.entries)
        
        level_stats = {}
        component_stats = {}
        
        for key, count in stats.items():
            if key in [level.value for level in LogLevel]:
                level_stats[key] = count
            else:
                component_stats[key] = count
        
        return {
            "total_entries": total_entries,
            "level_distribution": level_stats,
            "component_distribution": component_stats,
            "buffer_size": self.buffer.max_size,
            "buffer_usage": f"{total_entries}/{self.buffer.max_size}"
        }
    
    def search_logs(self, query: str, limit: int = 100) -> List[LogEntry]:
        """Search logs by message content"""
        entries = list(self.buffer.entries)
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
    
    def _write_to_file(self, entry: LogEntry):
        """Write log entry to file"""
        try:
            # Create daily log file for component
            date_str = entry.timestamp.strftime("%Y-%m-%d")
            log_file = self.logs_dir / f"{entry.component}_{date_str}.log"
            
            # Format log line
            log_line = f"{entry.timestamp.isoformat()} [{entry.level.value}] {entry.message}"
            if entry.context:
                log_line += f" | Context: {json.dumps(entry.context)}"
            log_line += "\n"
            
            # Append to file
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
                
        except Exception as e:
            logger.error(f"❌ Failed to write log to file: {e}")
    
    def load_logs_from_file(self, filepath: Path) -> bool:
        """Load logs from exported JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entries = data.get("entries", [])
            for entry_data in entries:
                entry = LogEntry.from_dict(entry_data)
                self.buffer.add_entry(entry)
            
            logger.info(f"✅ Loaded {len(entries)} log entries from: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load logs from file: {e}")
            return False
    
    def clear_logs(self, component: Optional[str] = None):
        """Clear logs from buffer"""
        if component:
            # Remove entries for specific component
            self.buffer.entries = deque(
                [e for e in self.buffer.entries if e.component != component],
                maxlen=self.buffer.max_size
            )
            logger.info(f"🧹 Cleared logs for component: {component}")
        else:
            # Clear all logs
            self.buffer.entries.clear()
            self.buffer.stats.clear()
            logger.info("🧹 All logs cleared")


# Global log manager instance
_log_manager = None


def get_log_manager(**kwargs) -> LogManager:
    """Get global log manager instance"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager(**kwargs)
        logger.info("📝 Log Manager singleton created")
    return _log_manager