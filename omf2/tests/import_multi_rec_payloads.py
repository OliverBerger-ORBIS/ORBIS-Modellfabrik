#!/usr/bin/env python3
"""
Import script für echte Test-Daten aus data/aps-data/*/

Konvertiert Dateien von:
- data/aps-data/topics/{session}/_topic_name__000001.json
Zu:
- tests/test_payloads_for_topic/_topic_name__000001.json

Extrahiert nur den Payload-Inhalt für Schema-Validierung.
Unterstützt: rec0, rec1, rec3, rec4, rec5, rec6, rec7, rec8
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class MultiRecPayloadImporter:
    """Importiert und konvertiert Payload-Dateien aus allen Recording-Sessions"""
    
    def __init__(self):
        self.base_source_dir = Path("/Users/oliver/Projects/ORBIS-Modellfabrik/data/aps-data/topics")
        self.target_dir = Path("/Users/oliver/Projects/ORBIS-Modellfabrik/omf2/tests/test_payloads_for_topic")
        
        # Available recording sessions
        self.available_sessions = ["rec0", "rec1", "rec3", "rec4", "rec5", "rec6", "rec7", "rec8"]
        
        # Ensure target directory exists
        self.target_dir.mkdir(parents=True, exist_ok=True)
    
    def import_all_payloads(self, sessions: List[str] = None) -> Dict[str, Any]:
        """
        Importiere alle Payload-Dateien aus den angegebenen Sessions
        
        Args:
            sessions: List of session names (e.g., ['rec5', 'rec7', 'rec8'])
        
        Returns:
            Import statistics
        """
        if sessions is None:
            sessions = self.available_sessions
        
        logger.info(f"🚀 Starte Import von {', '.join(sessions)} Payload-Dateien...")
        
        overall_stats = {
            'total_files': 0,
            'imported_files': 0,
            'skipped_files': 0,
            'error_files': 0,
            'topics': {},
            'sessions': {},
            'errors': []
        }
        
        # Process each session
        for session in sessions:
            session_stats = self.import_session_payloads(session)
            
            # Merge stats
            overall_stats['total_files'] += session_stats['total_files']
            overall_stats['imported_files'] += session_stats['imported_files']
            overall_stats['skipped_files'] += session_stats['skipped_files']
            overall_stats['error_files'] += session_stats['error_files']
            overall_stats['errors'].extend(session_stats['errors'])
            
            # Merge topics
            for topic, count in session_stats['topics'].items():
                if topic not in overall_stats['topics']:
                    overall_stats['topics'][topic] = 0
                overall_stats['topics'][topic] += count
            
            overall_stats['sessions'][session] = session_stats
        
        # Print overall summary
        logger.info(f"\n🎯 Gesamt-Import abgeschlossen:")
        logger.info(f"   📊 {overall_stats['imported_files']}/{overall_stats['total_files']} Dateien importiert")
        logger.info(f"   ⚠️ {overall_stats['skipped_files']} übersprungen")
        logger.info(f"   ❌ {overall_stats['error_files']} Fehler")
        logger.info(f"   📋 {len(overall_stats['topics'])} Topics verarbeitet")
        logger.info(f"   📁 {len(sessions)} Sessions verarbeitet")
        
        # Print session breakdown
        logger.info(f"\n📁 Session-Statistiken:")
        for session, stats in overall_stats['sessions'].items():
            logger.info(f"   🔍 {session}: {stats['imported_files']}/{stats['total_files']} Dateien")
        
        # Print topic statistics (top 10)
        if overall_stats['topics']:
            logger.info(f"\n📋 Top Topic-Statistiken:")
            sorted_topics = sorted(overall_stats['topics'].items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics[:10]:
                logger.info(f"   🔍 {topic}: {count} Sequenzen")
            if len(sorted_topics) > 10:
                logger.info(f"   ... und {len(sorted_topics) - 10} weitere Topics")
        
        return overall_stats
    
    def import_session_payloads(self, session: str) -> Dict[str, Any]:
        """
        Importiere alle Payload-Dateien aus einer Session
        
        Args:
            session: Session name (e.g., 'rec5')
        
        Returns:
            Import statistics for this session
        """
        source_dir = self.base_source_dir / session
        
        if not source_dir.exists():
            logger.warning(f"⚠️ Session directory nicht gefunden: {source_dir}")
            return {
                'total_files': 0,
                'imported_files': 0,
                'skipped_files': 0,
                'error_files': 0,
                'topics': {},
                'errors': [f"Session {session} not found"]
            }
        
        # Find all JSON files in session
        source_files = list(source_dir.glob("*.json"))
        logger.info(f"📁 {session}: {len(source_files)} Dateien gefunden")
        
        stats = {
            'total_files': len(source_files),
            'imported_files': 0,
            'skipped_files': 0,
            'error_files': 0,
            'topics': {},
            'errors': []
        }
        
        # Process each file
        for source_file in source_files:
            try:
                result = self.import_single_file(source_file, session)
                
                if result['success']:
                    stats['imported_files'] += 1
                    topic = result['topic']
                    if topic not in stats['topics']:
                        stats['topics'][topic] = 0
                    stats['topics'][topic] += 1
                    logger.debug(f"✅ {session}/{source_file.name} -> {result['target_file']}")
                else:
                    stats['skipped_files'] += 1
                    logger.debug(f"⚠️ {session}/{source_file.name}: {result['reason']}")
                    
            except Exception as e:
                stats['error_files'] += 1
                stats['errors'].append(f"{session}/{source_file.name}: {e}")
                logger.error(f"❌ {session}/{source_file.name}: {e}")
        
        logger.info(f"📊 {session}: {stats['imported_files']}/{stats['total_files']} Dateien importiert")
        return stats
    
    def import_single_file(self, source_file: Path, session: str = None) -> Dict[str, Any]:
        """
        Importiere eine einzelne Datei
        
        Args:
            source_file: Source file path
            session: Session name for logging
            
        Returns:
            Import result
        """
        try:
            # Load source file
            with open(source_file, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
            
            # Extract topic from filename or data
            topic = self.extract_topic_from_filename(source_file.name)
            if not topic:
                topic = source_data.get('topic')
            
            if not topic:
                return {
                    'success': False,
                    'reason': 'No topic found in filename or data',
                    'target_file': None,
                    'topic': None
                }
            
            # Extract payload content
            payload_content = self.extract_payload_content(source_data)
            if payload_content is None:
                return {
                    'success': False,
                    'reason': 'No valid payload found',
                    'target_file': None,
                    'topic': topic
                }
            
            # Generate target filename
            target_filename = self.generate_target_filename(source_file.name, topic)
            target_file = self.target_dir / target_filename
            
            # Write payload-only content
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(payload_content, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'reason': None,
                'target_file': target_filename,
                'topic': topic
            }
            
        except Exception as e:
            return {
                'success': False,
                'reason': f'Error processing file: {e}',
                'target_file': None,
                'topic': None
            }
    
    def extract_topic_from_filename(self, filename: str) -> str:
        """Extrahiere Topic aus Dateinamen"""
        # Remove extension
        name = filename.replace('.json', '')
        
        # Remove sequence number if present (__000001)
        if '__' in name:
            name = name.split('__')[0]
        
        # Remove leading underscore
        if name.startswith('_'):
            name = name[1:]
        
        # Convert underscores to slashes for topic format
        topic = name.replace('_', '/')
        
        return topic if topic else None
    
    def extract_payload_content(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiere Payload-Inhalt aus Source-Daten"""
        # If source_data has a 'payload' field, parse it
        if 'payload' in source_data:
            payload_str = source_data['payload']
            if isinstance(payload_str, str):
                try:
                    return json.loads(payload_str)
                except json.JSONDecodeError:
                    return None
            elif isinstance(payload_str, dict):
                return payload_str
        
        # If no payload field, return the whole data minus metadata
        metadata_fields = {'topic', 'qos', 'retain', 'timestamp', 'sequence', 'type'}
        payload_content = {k: v for k, v in source_data.items() if k not in metadata_fields}
        
        return payload_content if payload_content else None
    
    def generate_target_filename(self, source_filename: str, topic: str) -> str:
        """Generiere Target-Dateiname basierend auf Source-Filename und Topic"""
        # Keep the original filename structure
        return source_filename
    
    def cleanup_target_directory(self):
        """Leere das Target-Verzeichnis"""
        if self.target_dir.exists():
            for file in self.target_dir.glob("*.json"):
                file.unlink()
            logger.info(f"✅ Target-Verzeichnis geleert: {self.target_dir}")
    
    def list_available_sessions(self) -> List[str]:
        """Liste verfügbare Sessions auf"""
        available = []
        for session in self.available_sessions:
            session_dir = self.base_source_dir / session
            if session_dir.exists():
                file_count = len(list(session_dir.glob("*.json")))
                available.append(f"{session} ({file_count} files)")
            else:
                available.append(f"{session} (not found)")
        return available

def main():
    """Main function"""
    print("🚀 Multi-Rec Payload Import Tool")
    print("="*50)
    
    importer = MultiRecPayloadImporter()
    
    # List available sessions
    sessions = importer.list_available_sessions()
    print(f"\n📁 Verfügbare Sessions:")
    for session in sessions:
        print(f"   🔍 {session}")
    
    # Ask user
    print("\n🎯 Optionen:")
    print("1. Alle Sessions importieren (rec0, rec1, rec3, rec4, rec5, rec6, rec7, rec8)")
    print("2. Nur rec5, rec7, rec8 importieren")
    print("3. Spezifische Sessions importieren")
    print("4. Target-Verzeichnis leeren")
    print("5. Beenden")
    
    try:
        choice = input("\n🎯 Wähle Option (1-5): ").strip()
        
        if choice == "1":
            # Import all sessions
            stats = importer.import_all_payloads()
            if stats['imported_files'] > 0:
                print(f"\n✅ Import erfolgreich!")
                print(f"   📊 {stats['imported_files']} Dateien importiert")
                print(f"   📋 {len(stats['topics'])} Topics verarbeitet")
            else:
                print(f"\n⚠️ Keine Dateien importiert")
        
        elif choice == "2":
            # Import specific sessions
            stats = importer.import_all_payloads(['rec5', 'rec7', 'rec8'])
            if stats['imported_files'] > 0:
                print(f"\n✅ Import erfolgreich!")
                print(f"   📊 {stats['imported_files']} Dateien importiert")
                print(f"   📋 {len(stats['topics'])} Topics verarbeitet")
            else:
                print(f"\n⚠️ Keine Dateien importiert")
        
        elif choice == "3":
            # Custom sessions
            print("\n📁 Verfügbare Sessions: rec0, rec1, rec3, rec4, rec5, rec6, rec7, rec8")
            session_input = input("🎯 Eingabe Sessions (kommagetrennt): ").strip()
            sessions = [s.strip() for s in session_input.split(',')]
            stats = importer.import_all_payloads(sessions)
            if stats['imported_files'] > 0:
                print(f"\n✅ Import erfolgreich!")
                print(f"   📊 {stats['imported_files']} Dateien importiert")
                print(f"   📋 {len(stats['topics'])} Topics verarbeitet")
            else:
                print(f"\n⚠️ Keine Dateien importiert")
        
        elif choice == "4":
            # Cleanup
            importer.cleanup_target_directory()
            print("✅ Target-Verzeichnis geleert")
        
        elif choice == "5":
            print("👋 Auf Wiedersehen!")
        
        else:
            print("❌ Ungültige Option")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Import abgebrochen.")
        return 1
    except Exception as e:
        print(f"\n💥 Fehler: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
