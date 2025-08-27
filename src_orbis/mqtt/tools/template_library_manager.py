#!/usr/bin/env python3
"""
Template Library Manager
Manages persistent storage and retrieval of MQTT template analysis results
"""

import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class TemplateLibraryManager:
    def __init__(self, library_dir: str = "mqtt-data/template_library"):
        self.library_dir = Path(library_dir)
        self.library_dir.mkdir(parents=True, exist_ok=True)
        
        # Database for template library
        self.db_path = self.library_dir / "template_library.db"
        self.init_database()
    
    def init_database(self):
        """Initialize the template library database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT UNIQUE NOT NULL,
                topic TEXT NOT NULL,
                template_data TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                documentation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                template_type TEXT NOT NULL,
                category TEXT,
                message_count INTEGER DEFAULT 0,
                sessions_count INTEGER DEFAULT 0
            )
        """)
        
        # Create analysis sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                topics_count INTEGER DEFAULT 0,
                messages_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_txt_analysis(self, analysis_results: Dict[str, Any], session_name: str = None):
        """Save TXT template analysis results to library"""
        if not session_name:
            session_name = f"txt_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record analysis session
        cursor.execute("""
            INSERT INTO analysis_sessions (session_name, analysis_type, topics_count, messages_count)
            VALUES (?, ?, ?, ?)
        """, (session_name, 'txt', len(analysis_results), 
              sum(r.get('message_count', 0) for r in analysis_results.values())))
        
        # Save each template
        for topic, result in analysis_results.items():
            if result.get('message_count', 0) > 0:
                template_name = f"TXT_{topic.replace('/', '_').replace(':', '_')}"
                
                # Prepare template data
                template_data = {
                    'topic': topic,
                    'template': result.get('template', {}),
                    'variable_fields': result.get('variable_fields', []),
                    'enum_fields': result.get('enum_fields', {}),
                    'examples': result.get('examples', [])[:3]  # Keep only first 3 examples
                }
                
                # Prepare analysis data
                analysis_data = {
                    'message_count': result.get('message_count', 0),
                    'sessions': result.get('sessions', []),
                    'sessions_count': len(result.get('sessions', [])),
                    'created_at': datetime.now().isoformat()
                }
                
                # Prepare documentation
                documentation = {
                    'description': result.get('description', ''),
                    'usage': result.get('usage', ''),
                    'critical_for': result.get('critical_for', []),
                    'workflow_step': result.get('workflow_step', '')
                }
                
                # Insert or update template
                cursor.execute("""
                    INSERT OR REPLACE INTO templates 
                    (template_name, topic, template_data, analysis_data, documentation, 
                     template_type, category, message_count, sessions_count, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template_name,
                    topic,
                    json.dumps(template_data),
                    json.dumps(analysis_data),
                    json.dumps(documentation),
                    'txt',
                    'TXT',
                    result.get('message_count', 0),
                    len(result.get('sessions', [])),
                    datetime.now().isoformat()
                ))
        
        conn.commit()
        conn.close()
        
        return session_name
    
    def save_ccu_analysis(self, analysis_results: Dict[str, Any], session_name: str = None):
        """Save CCU template analysis results to library"""
        if not session_name:
            session_name = f"ccu_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record analysis session
        cursor.execute("""
            INSERT INTO analysis_sessions (session_name, analysis_type, topics_count, messages_count)
            VALUES (?, ?, ?, ?)
        """, (session_name, 'ccu', len(analysis_results), 
              sum(r.get('message_count', 0) for r in analysis_results.values())))
        
        # Save each template
        for topic, result in analysis_results.items():
            if result.get('message_count', 0) > 0:
                template_name = f"CCU_{topic.replace('/', '_').replace(':', '_')}"
                
                # Prepare template data
                template_data = {
                    'topic': topic,
                    'template': result.get('template', {}),
                    'variable_fields': result.get('variable_fields', []),
                    'examples': result.get('examples', [])[:3]  # Keep only first 3 examples
                }
                
                # Prepare analysis data
                analysis_data = {
                    'message_count': result.get('message_count', 0),
                    'sessions': result.get('sessions', []),
                    'sessions_count': len(result.get('sessions', [])),
                    'created_at': datetime.now().isoformat()
                }
                
                # Prepare documentation
                documentation = {
                    'description': result.get('description', ''),
                    'usage': '',
                    'critical_for': [],
                    'workflow_step': ''
                }
                
                # Insert or update template
                cursor.execute("""
                    INSERT OR REPLACE INTO templates 
                    (template_name, topic, template_data, analysis_data, documentation, 
                     template_type, category, message_count, sessions_count, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template_name,
                    topic,
                    json.dumps(template_data),
                    json.dumps(analysis_data),
                    json.dumps(documentation),
                    'ccu',
                    'CCU',
                    result.get('message_count', 0),
                    len(result.get('sessions', [])),
                    datetime.now().isoformat()
                ))
        
        conn.commit()
        conn.close()
        
        return session_name
    
    def get_all_templates(self, template_type: str = None) -> List[Dict[str, Any]]:
        """Get all templates from library"""
        conn = sqlite3.connect(self.db_path)
        
        if template_type:
            query = "SELECT * FROM templates WHERE template_type = ? ORDER BY updated_at DESC"
            df = pd.read_sql_query(query, conn, params=(template_type,))
        else:
            query = "SELECT * FROM templates ORDER BY updated_at DESC"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        templates = []
        for _, row in df.iterrows():
            template = {
                'id': row['id'],
                'template_name': row['template_name'],
                'topic': row['topic'],
                'template_type': row['template_type'],
                'category': row.get('category', row['template_type'].upper()),
                'message_count': row['message_count'],
                'sessions_count': row['sessions_count'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'template_data': json.loads(row['template_data']),
                'analysis_data': json.loads(row['analysis_data']),
                'documentation': json.loads(row['documentation'])
            }
            templates.append(template)
        
        return templates
    
    def get_template_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM templates WHERE template_name = ?"
        df = pd.read_sql_query(query, conn, params=(template_name,))
        conn.close()
        
        if df.empty:
            return None
        
        row = df.iloc[0]
        return {
            'id': row['id'],
            'template_name': row['template_name'],
            'topic': row['topic'],
            'template_type': row['template_type'],
            'message_count': row['message_count'],
            'sessions_count': row['sessions_count'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'template_data': json.loads(row['template_data']),
            'analysis_data': json.loads(row['analysis_data']),
            'documentation': json.loads(row['documentation'])
        }
    
    def get_analysis_sessions(self, analysis_type: str = None) -> List[Dict[str, Any]]:
        """Get analysis sessions history"""
        conn = sqlite3.connect(self.db_path)
        
        if analysis_type:
            query = "SELECT * FROM analysis_sessions WHERE analysis_type = ? ORDER BY created_at DESC"
            df = pd.read_sql_query(query, conn, params=(analysis_type,))
        else:
            query = "SELECT * FROM analysis_sessions ORDER BY created_at DESC"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        sessions = []
        for _, row in df.iterrows():
            session = {
                'id': row['id'],
                'session_name': row['session_name'],
                'analysis_type': row['analysis_type'],
                'topics_count': row['topics_count'],
                'messages_count': row['messages_count'],
                'created_at': row['created_at'],
                'status': row['status']
            }
            sessions.append(session)
        
        return sessions
    
    def update_template_documentation(self, template_name: str, documentation: Dict[str, Any]):
        """Update documentation for a specific template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE templates 
            SET documentation = ?, updated_at = ?
            WHERE template_name = ?
        """, (json.dumps(documentation), datetime.now().isoformat(), template_name))
        
        conn.commit()
        conn.close()
    
    def delete_template(self, template_name: str):
        """Delete a template from library"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM templates WHERE template_name = ?", (template_name,))
        
        conn.commit()
        conn.close()
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        conn = sqlite3.connect(self.db_path)
        
        # Get template counts by type
        template_counts = pd.read_sql_query(
            "SELECT template_type, COUNT(*) as count FROM templates GROUP BY template_type",
            conn
        )
        
        # Get total messages
        total_messages = pd.read_sql_query(
            "SELECT SUM(message_count) as total FROM templates",
            conn
        ).iloc[0]['total'] or 0
        
        # Get latest analysis
        latest_analysis = pd.read_sql_query(
            "SELECT * FROM analysis_sessions ORDER BY created_at DESC LIMIT 1",
            conn
        )
        
        conn.close()
        
        return {
            'template_counts': template_counts.to_dict('records'),
            'total_messages': total_messages,
            'latest_analysis': latest_analysis.to_dict('records')[0] if not latest_analysis.empty else None
        }

if __name__ == "__main__":
    # Test the Template Library Manager
    manager = TemplateLibraryManager()
    
    # Get library stats
    stats = manager.get_library_stats()
    print("📊 Template Library Stats:")
    print(f"  Total Messages: {stats['total_messages']}")
    print(f"  Template Counts: {stats['template_counts']}")
    
    # Get all templates
    templates = manager.get_all_templates()
    print(f"\n📋 Total Templates: {len(templates)}")
    
    # Get analysis sessions
    sessions = manager.get_analysis_sessions()
    print(f"📈 Analysis Sessions: {len(sessions)}")
