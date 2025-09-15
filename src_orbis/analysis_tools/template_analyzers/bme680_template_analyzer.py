#!/usr/bin/env python3
"""
BME680 Template Analyzer

Spezifischer Analyzer für BME680 Topics, die Base64-kodierte Bilddaten enthalten.
Diese Topics sind nicht für normale Template-Analyse geeignet.
"""

import os
import sys
import sqlite3
import glob
import json
import yaml
from datetime import datetime
from typing import Dict, List, Set, Any
import base64
import io
from PIL import Image

# Add project root to path for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

# No registry manager needed for BME680 analysis


class Bme680TemplateAnalyzer:
    """Analyzer für BME680 Topics mit Sensordaten (Temperatur, Luftfeuchtigkeit, Luftdruck)"""
    
    def __init__(self):
        """Initialize the BME680 Template Analyzer"""
        self.project_root = project_root
        
        # Set paths relative to project root
        self.output_dir = os.path.join(project_root, "registry/observations/payloads")
        self.session_dir = os.path.join(project_root, "data/omf-data/sessions")
        
        # BME680 specific topics
        self.target_topics = [
            "/j1/txt/1/c/bme680",
            "/j1/txt/1/i/bme680"
        ]
        
        # No registry manager needed for BME680 analysis
        
        print("🔧 BME680 Template Analyzer initialisiert")
        print(f"📁 Ausgabe-Verzeichnis: {self.output_dir}")
        print(f"📁 Session-Verzeichnis: {self.session_dir}")
    
    def load_all_sessions(self) -> List[Dict]:
        """Load messages from all session databases"""
        print("📂 Lade alle Session-Datenbanken...")
        
        all_messages = []
        session_files = glob.glob(f"{self.session_dir}/*.db")
        
        print(f"  📁 Gefunden: {len(session_files)} Session-Dateien")
        
        for session_file in session_files:
            try:
                session_name = os.path.basename(session_file).replace(".db", "")
                print(f"  📊 Lade Session: {session_name}")
                
                conn = sqlite3.connect(session_file)
                cursor = conn.cursor()
                
                # Check if session_label column exists
                cursor.execute("PRAGMA table_info(mqtt_messages)")
                columns = [column[1] for column in cursor.fetchall()]
                has_session_label = 'session_label' in columns
                
                # Get messages for target topics
                placeholders = ",".join(["?" for _ in self.target_topics])
                if has_session_label:
                    cursor.execute(
                        f"""
                        SELECT topic, payload, timestamp, session_label
                        FROM mqtt_messages
                        WHERE topic IN ({placeholders})
                        ORDER BY timestamp
                    """,
                        self.target_topics,
                    )
                else:
                    cursor.execute(
                        f"""
                        SELECT topic, payload, timestamp, '' as session_label
                        FROM mqtt_messages
                        WHERE topic IN ({placeholders})
                        ORDER BY timestamp
                    """,
                        self.target_topics,
                    )
                
                session_messages = cursor.fetchall()
                print(f"    ✅ {len(session_messages)} Nachrichten geladen")
                
                for row in session_messages:
                    all_messages.append({
                        "topic": row[0],
                        "payload": row[1],
                        "timestamp": row[2],
                        "session_name": row[3] or session_name,
                    })
                conn.close()
            except sqlite3.OperationalError as e:
                print(f"  ❌ Fehler beim Laden von {session_file}: {e}")
            except Exception as e:
                print(f"  ❌ Unerwarteter Fehler beim Laden von {session_file}: {e}")
        
        print(f"📊 Insgesamt {len(all_messages)} Nachrichten aus allen Sessions geladen")
        return all_messages
    
    def analyze_bme680_data(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze BME680 data specifically for image content"""
        results = {}
        
        for topic in self.target_topics:
            topic_messages = [msg for msg in messages if msg["topic"] == topic]
            
            if not topic_messages:
                continue
                
            print(f"🔍 Analysiere Topic: {topic}")
            print(f"  📊 Analysiere {len(topic_messages)} Nachrichten für {topic}")
            
            # Analyze image data
            image_stats = self._analyze_image_data(topic_messages)
            
            # Create observation for this topic
            results[topic] = {
                "statistics": {
                    "total_messages": len(topic_messages),
                    "image_count": image_stats["valid_images"],
                    "invalid_images": image_stats["invalid_images"],
                    "avg_image_size": image_stats["avg_size"],
                    "max_image_size": image_stats["max_size"],
                    "min_image_size": image_stats["min_size"]
                },
                "image_analysis": image_stats,
                "examples": topic_messages[:3]  # First 3 messages as examples
            }
            
            print(f"  ✅ BME680 Analyse abgeschlossen mit {image_stats['valid_images']} gültigen Bildern")
        
        return results
    
    def _analyze_image_data(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze Base64 image data in messages"""
        valid_images = 0
        invalid_images = 0
        total_size = 0
        max_size = 0
        min_size = float('inf')
        image_formats = set()
        
        for msg in messages:
            try:
                payload = json.loads(msg["payload"])
                
                # Look for image data in common fields
                image_data = None
                for field in ["image", "data", "payload", "content"]:
                    if field in payload and isinstance(payload[field], str):
                        if payload[field].startswith("data:image/"):
                            image_data = payload[field]
                            break
                        elif len(payload[field]) > 1000:  # Likely base64 data
                            image_data = payload[field]
                            break
                
                if not image_data:
                    continue
                
                # Extract base64 data
                if image_data.startswith("data:image/"):
                    # Data URI format
                    header, b64_data = image_data.split(",", 1)
                    format_info = header.split(";")[0].split("/")[1]
                    image_formats.add(format_info)
                else:
                    # Raw base64
                    b64_data = image_data
                    image_formats.add("unknown")
                
                # Decode and analyze
                try:
                    image_bytes = base64.b64decode(b64_data)
                    size = len(image_bytes)
                    
                    # Try to open as image
                    image = Image.open(io.BytesIO(image_bytes))
                    width, height = image.size
                    
                    valid_images += 1
                    total_size += size
                    max_size = max(max_size, size)
                    min_size = min(min_size, size)
                    
                except Exception as e:
                    invalid_images += 1
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                invalid_images += 1
                continue
        
        return {
            "valid_images": valid_images,
            "invalid_images": invalid_images,
            "avg_size": total_size // max(valid_images, 1),
            "max_size": max_size if max_size > 0 else 0,
            "min_size": min_size if min_size != float('inf') else 0,
            "formats": list(image_formats)
        }
    
    def save_observations(self, results: Dict) -> None:
        """Save analysis results in observation format"""
        print("💾 Speichere BME680 Observations...")
        
        for topic, analysis_data in results.items():
            # Create observation filename
            topic_clean = topic.replace("/", "_").replace("j1_txt_1_", "")
            observation_file = f"{datetime.now().strftime('%Y-%m-%d')}_bme680_{topic_clean}.yml"
            observation_path = os.path.join(self.output_dir, observation_file)
            
            # Create observation structure
            observation = {
                "metadata": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "author": "bme680_template_analyzer",
                    "source": "analysis",
                    "topic": topic,
                    "status": "open"
                },
                "observation": {
                    "type": "bme680_image_analysis",
                    "topic": topic,
                    "description": f"BME680 image data analysis for topic {topic}",
                    "source": "mqtt_sessions",
                    "message_count": analysis_data["statistics"]["total_messages"],
                    "image_count": analysis_data["statistics"]["image_count"],
                    "examples": analysis_data.get("examples", [])[:2]  # Only 2 examples for images
                },
                "analysis": {
                    "initial_assessment": f"BME680 topic {topic} contains Base64-encoded image data - not suitable for template analysis",
                    "image_statistics": analysis_data["image_analysis"],
                    "total_messages": analysis_data["statistics"]["total_messages"]
                },
                "proposed_action": [
                    f"Exclude BME680 topic {topic} from template analysis",
                    "Handle as sensor data, not template data",
                    "Consider separate sensor data analysis if needed"
                ],
                "tags": ["bme680", "image", "base64", "exclude"],
                "priority": "low"
            }
            
            # Save observation
            try:
                with open(observation_path, 'w', encoding='utf-8') as f:
                    yaml.dump(observation, f, default_flow_style=False, allow_unicode=True)
                print(f"  ✅ Observation gespeichert: {observation_file}")
            except Exception as e:
                print(f"  ❌ Fehler beim Speichern von {observation_file}: {e}")
    
    def migrate_to_registry_v2(self, analysis_data: Dict) -> None:
        """Migrate analysis results to Registry v2"""
        print("🔄 Migriere zu Registry v2...")
        
        registry_v2_dir = os.path.join(os.path.dirname(self.output_dir), "..", "model", "v2", "templates")
        os.makedirs(registry_v2_dir, exist_ok=True)
        
        for topic, data in analysis_data.items():
            # Create Registry v2 template
            topic_clean = topic.replace("/", ".").replace("j1.txt.1.", "")
            template_key = f"bme680.{topic_clean}"
            template_file = f"{template_key}.yml"
            template_path = os.path.join(registry_v2_dir, template_file)
            
            # Create template structure
            template = {
                "metadata": {
                    "key": template_key,
                    "category": "BME680",
                    "sub_category": "Sensor",
                    "description": f"BME680 sensor data template for {topic}",
                    "version": "1.0.0",
                    "created": datetime.now().strftime("%Y-%m-%d"),
                    "author": "bme680_template_analyzer"
                },
                "topic": topic,
                "template_structure": data.get("template_structure", {}),
                "examples": data.get("examples", [])[:3],
                "statistics": data["statistics"]
            }
            
            # Save template
            try:
                with open(template_path, 'w', encoding='utf-8') as f:
                    yaml.dump(template, f, default_flow_style=False, allow_unicode=True)
                print(f"  ✅ Registry v2 Template gespeichert: {template_file}")
            except Exception as e:
                print(f"  ❌ Fehler beim Speichern von {template_file}: {e}")
    
    def run_analysis(self) -> None:
        """Run the complete BME680 analysis"""
        print("=" * 60)
        print("🔧 BME680 TEMPLATE ANALYZER")
        print("=" * 60)
        print("🚀 Starte BME680 Template Analyse...")
        
        # Load all session data
        all_messages = self.load_all_sessions()
        
        if not all_messages:
            print("❌ Keine Nachrichten gefunden!")
            return
        
        # Analyze BME680 data
        results = self.analyze_bme680_data(all_messages)
        
        if not results:
            print("❌ Keine BME680 Topics gefunden!")
            return
        
        # Save results
        self.save_observations(results)
        
        # Migrate to Registry v2
        self.migrate_to_registry_v2(results)
        
        print("=" * 60)
        print("📊 ANALYSE ZUSAMMENFASSUNG")
        print("=" * 60)
        print(f"✅ Erfolgreich analysiert: {len(results)} BME680 Topics")
        
        for topic, data in results.items():
            stats = data["statistics"]
            print(f"  📋 {topic}: {stats['total_messages']} Nachrichten, {stats['image_count']} Bilder")
        
        print("✅ BME680 Template Analyse erfolgreich abgeschlossen!")
        print("🎉 Script erfolgreich beendet!")


if __name__ == "__main__":
    analyzer = Bme680TemplateAnalyzer()
    analyzer.run_analysis()
