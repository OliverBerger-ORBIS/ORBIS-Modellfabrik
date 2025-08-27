#!/usr/bin/env python3
"""
CCU Template Analyzer
Independent tool for analyzing CCU topics and saving to template library
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class CCUTemplateAnalyzer:
    def __init__(self, template_library_path: str = "mqtt-data/template_library"):
        self.template_library_path = Path(template_library_path)
        self.template_library_path.mkdir(parents=True, exist_ok=True)
        
        # Template library database
        self.library_db = self.template_library_path / "template_library.db"
        self.init_library()
    
    def init_library(self):
        """Initialize template library database"""
        conn = sqlite3.connect(self.library_db)
        cursor = conn.cursor()
        
        # Create templates table if not exists
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
                message_count INTEGER DEFAULT 0,
                sessions_count INTEGER DEFAULT 0
            )
        """)
        
        # Create analysis sessions table if not exists
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
    
    def analyze_all_ccu_topics(self) -> Dict[str, Any]:
        """Analyze all CCU topics from all session databases"""
        print("🏭 Starting CCU Template Analysis...")
        
        # Find all session databases
        session_dir = Path("mqtt-data/sessions")
        if not session_dir.exists():
            print(f"❌ Session directory not found: {session_dir}")
            return {}
        
        session_files = list(session_dir.glob("*.db"))
        if not session_files:
            print(f"❌ No session databases found in {session_dir}")
            return {}
        
        print(f"🔍 Found {len(session_files)} session databases")
        
        # Collect all CCU topics from all sessions
        all_ccu_topics = {}
        total_messages = 0
        
        for session_file in session_files:
            try:
                print(f"📊 Analyzing {session_file.name}...")
                conn = sqlite3.connect(session_file)
                
                # Query for CCU topics in this session
                query = """
                    SELECT DISTINCT topic, COUNT(*) as message_count
                    FROM mqtt_messages 
                    WHERE topic LIKE 'ccu/%' 
                       OR topic LIKE 'order/%' 
                       OR topic LIKE 'workflow/%'
                       OR topic LIKE 'state/%'
                       OR topic LIKE 'pairing/%'
                    GROUP BY topic
                """
                
                df = pd.read_sql_query(query, conn)
                
                # Aggregate results across sessions
                for _, row in df.iterrows():
                    topic = row['topic']
                    message_count = row['message_count']
                    
                    if topic in all_ccu_topics:
                        all_ccu_topics[topic]['message_count'] += message_count
                        all_ccu_topics[topic]['sessions'].add(session_file.stem)
                    else:
                        all_ccu_topics[topic] = {
                            'topic': topic,
                            'message_count': message_count,
                            'sessions': {session_file.stem}
                        }
                
                total_messages += df['message_count'].sum()
                conn.close()
                
            except Exception as e:
                print(f"⚠️ Error reading {session_file.name}: {e}")
                continue
        
        if not all_ccu_topics:
            print("⚠️ No CCU topics found in any session")
            return {}
        
        print(f"✅ Found {len(all_ccu_topics)} CCU topics with {total_messages} total messages")
        
        # Get detailed analysis for each topic
        results = {}
        for topic_name, topic_data in sorted(all_ccu_topics.items(), 
                                           key=lambda x: x[1]['message_count'], reverse=True):
            topic = topic_data['topic']
            message_count = topic_data['message_count']
            sessions = list(topic_data['sessions'])
            
            print(f"🔍 Analyzing topic: {topic} ({message_count} messages)")
            
            # Get sample messages for this topic from all sessions
            all_samples = []
            for session_file in session_files:
                try:
                    conn = sqlite3.connect(session_file)
                    sample_query = """
                        SELECT payload, timestamp, session_label
                        FROM mqtt_messages 
                        WHERE topic = ?
                        ORDER BY timestamp DESC
                        LIMIT 3
                    """
                    
                    sample_df = pd.read_sql_query(sample_query, conn, params=(topic,))
                    if not sample_df.empty:
                        all_samples.extend(sample_df.to_dict('records'))
                    conn.close()
                except Exception as e:
                    continue
            
            # Analyze payload structure
            templates = []
            examples = []
            variable_fields = set()
            
            for sample in all_samples:
                try:
                    payload = json.loads(sample['payload']) if sample['payload'] else {}
                    
                    # Check if payload is a dict (not a list or other type)
                    if not isinstance(payload, dict):
                        continue
                    
                    # Check if this is a real message (not a template placeholder)
                    if self.is_real_message(payload):
                        examples.append(payload)
                    else:
                        templates.append(payload)
                    
                    # Identify variable fields
                    for key, value in payload.items():
                        if isinstance(value, (str, int, float, bool)):
                            variable_fields.add(key)
                except json.JSONDecodeError:
                    continue
            
            # Create template from first message
            template = templates[0] if templates else {}
            
            # Generate description based on topic
            if 'order' in topic:
                description = "Auftragsverwaltung - Bestellung, Status und Antworten"
            elif 'workflow' in topic:
                description = "Workflow-Orchestrierung - Start, Status und Abschluss"
            elif 'state' in topic:
                description = "Systemstatus - Aktuelle Zustände und Informationen"
            elif 'config' in topic:
                description = "Konfiguration - Systemeinstellungen und Parameter"
            elif 'error' in topic:
                description = "Fehlerbehandlung - Fehlermeldungen und Diagnose"
            else:
                description = "CCU-Nachricht - Zentrale Steuerungseinheit"
            
            results[topic] = {
                'topic': topic,
                'message_count': message_count,
                'template': template,
                'variable_fields': sorted(list(variable_fields)),
                'examples': examples[:3],
                'sessions': sessions,
                'description': description
            }
        
        return results
    
    def is_real_message(self, payload: Dict) -> bool:
        """Check if a CCU payload is a real message (not a template placeholder)"""
        def contains_template_placeholders(obj):
            if isinstance(obj, str):
                # Check for CCU template placeholder patterns
                placeholder_patterns = [
                    '<orderId>', '<status>', '<timestamp>', '<state>',
                    '<config>', '<error>', '<workflow>', '<pairing>',
                    '<active>', '<completed>', '<request>', '<response>',
                    '<flows>', '<layout>', '<stock>', '<version>'
                ]
                return any(pattern in obj for pattern in placeholder_patterns)
            elif isinstance(obj, dict):
                return any(contains_template_placeholders(v) for v in obj.values())
            elif isinstance(obj, list):
                return any(contains_template_placeholders(item) for item in obj)
            return False
        
        return not contains_template_placeholders(payload)
    
    def save_to_library(self, results: Dict[str, Any]) -> str:
        """Save CCU analysis results to template library"""
        if not results:
            print("⚠️ No results to save")
            return ""
        
        session_name = f"ccu_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.library_db)
        cursor = conn.cursor()
        
        # Record analysis session
        cursor.execute("""
            INSERT INTO analysis_sessions (session_name, analysis_type, topics_count, messages_count)
            VALUES (?, ?, ?, ?)
        """, (session_name, 'ccu', len(results), 
              sum(r.get('message_count', 0) for r in results.values())))
        
        # Save each template
        for topic, result in results.items():
            if result.get('message_count', 0) > 0:
                template_name = f"CCU_{topic.replace('/', '_').replace(':', '_')}"
                
                # Prepare template data
                template_data = {
                    'topic': topic,
                    'template': result.get('template', {}),
                    'variable_fields': result.get('variable_fields', []),
                    'examples': result.get('examples', [])[:3]
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
        
        print(f"✅ CCU Templates saved to library: {session_name}")
        return session_name

def main():
    """Main function to run CCU analysis"""
    analyzer = CCUTemplateAnalyzer()
    
    print("🏭 CCU Template Analysis Tool")
    print("=" * 50)
    
    # Run analysis
    results = analyzer.analyze_all_ccu_topics()
    
    if results:
        # Save to library
        session_name = analyzer.save_to_library(results)
        
        # Show summary
        print(f"\n📊 Analysis Summary:")
        print(f"   Topics analyzed: {len(results)}")
        print(f"   Total messages: {sum(r.get('message_count', 0) for r in results.values())}")
        print(f"   Session saved: {session_name}")
        
        # Show top topics
        print(f"\n🔝 Top CCU Topics:")
        sorted_results = sorted(results.items(), key=lambda x: x[1].get('message_count', 0), reverse=True)
        for i, (topic, data) in enumerate(sorted_results[:5]):
            print(f"   {i+1}. {topic}: {data.get('message_count', 0)} messages")
    else:
        print("❌ No CCU topics found")

if __name__ == "__main__":
    main()
