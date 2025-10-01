#!/usr/bin/env python3
"""
Test Payload Generator - Generiert realistische Test-Payloads aus aufgezeichneten Daten
Verwendet aps-data/topics/*.json Dateien für realistische Test-Szenarien
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class TestPayloadGenerator:
    """
    Generiert realistische Test-Payloads aus aufgezeichneten Topic-Daten
    """
    
    def __init__(self, aps_data_path: str = "data/aps-data/topics"):
        self.aps_data_path = Path(aps_data_path)
        self.topic_examples = {}
        self._load_topic_examples()
    
    def _load_topic_examples(self):
        """Lädt alle aufgezeichneten Topic-Beispiele"""
        if not self.aps_data_path.exists():
            print(f"⚠️ APS data path not found: {self.aps_data_path}")
            return
        
        for json_file in self.aps_data_path.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extrahiere Topic aus der JSON-Datei
                topic = data.get('topic')
                if topic:
                    if topic not in self.topic_examples:
                        self.topic_examples[topic] = []
                    
                    # Speichere Payload-Beispiel
                    payload = data.get('payload')
                    if payload and payload != "NULL":
                        self.topic_examples[topic].append({
                            'payload': payload,
                            'timestamp': data.get('timestamp'),
                            'qos': data.get('qos'),
                            'retain': data.get('retain')
                        })
                        
            except Exception as e:
                print(f"⚠️ Error loading {json_file}: {e}")
    
    def get_available_topics(self) -> List[str]:
        """Gibt alle verfügbaren Topics zurück"""
        return list(self.topic_examples.keys())
    
    def get_topic_examples(self, topic: str) -> List[Dict]:
        """Gibt alle Beispiele für einen Topic zurück"""
        return self.topic_examples.get(topic, [])
    
    def generate_test_payload(self, topic: str, variation: str = "random") -> Optional[Dict]:
        """
        Generiert einen Test-Payload für einen Topic
        
        Args:
            topic: MQTT Topic
            variation: "random", "latest", "first", "template"
        """
        examples = self.get_topic_examples(topic)
        if not examples:
            return None
        
        if variation == "random":
            # Zufälliges Beispiel
            example = random.choice(examples)
            return self._create_variation(example['payload'])
        
        elif variation == "latest":
            # Neuestes Beispiel
            latest = max(examples, key=lambda x: x.get('timestamp', ''))
            return self._create_variation(latest['payload'])
        
        elif variation == "first":
            # Erstes Beispiel
            first = examples[0]
            return self._create_variation(first['payload'])
        
        elif variation == "template":
            # Template-basierte Variation
            return self._create_template_variation(topic, examples)
        
        return None
    
    def _create_variation(self, payload: Dict) -> Dict:
        """Erstellt eine Variation des Payloads"""
        if not isinstance(payload, dict):
            return payload
        
        variation = payload.copy()
        
        # Aktualisiere Timestamp
        if 'timestamp' in variation:
            variation['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Variationen für häufige Felder
        if 'headerId' in variation:
            variation['headerId'] = random.randint(1, 10000)
        
        if 'serialNumber' in variation:
            variation['serialNumber'] = f"SVR{random.randint(1000, 9999)}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}{random.randint(1000, 9999)}"
        
        if 'ip' in variation:
            variation['ip'] = f"192.168.1.{random.randint(100, 200)}"
        
        if 'client' in variation:
            variation['client'] = f"TestClient_{random.randint(1, 100)}"
        
        return variation
    
    def _create_template_variation(self, topic: str, examples: List[Dict]) -> Dict:
        """Erstellt eine Template-basierte Variation"""
        if not examples:
            return {}
        
        # Analysiere gemeinsame Struktur
        common_fields = set()
        for example in examples:
            if isinstance(example['payload'], dict):
                common_fields.update(example['payload'].keys())
        
        # Erstelle Template
        template = {}
        for field in common_fields:
            # Bestimme Feld-Typ basierend auf Beispielen
            field_type = self._determine_field_type(field, examples)
            template[field] = self._generate_field_value(field, field_type)
        
        return template
    
    def _determine_field_type(self, field: str, examples: List[Dict]) -> str:
        """Bestimmt den Typ eines Feldes basierend auf Beispielen"""
        values = []
        for example in examples:
            payload = example['payload']
            if isinstance(payload, dict) and field in payload:
                values.append(payload[field])
        
        if not values:
            return "string"
        
        # Analysiere Typen
        types = set(type(v).__name__ for v in values)
        
        if 'int' in types or 'float' in types:
            return "number"
        elif 'bool' in types:
            return "boolean"
        elif 'list' in types:
            return "array"
        else:
            return "string"
    
    def _generate_field_value(self, field: str, field_type: str) -> Any:
        """Generiert einen Wert für ein Feld basierend auf Typ und Name"""
        if field_type == "number":
            if "id" in field.lower() or "header" in field.lower():
                return random.randint(1, 10000)
            else:
                return random.uniform(0, 100)
        
        elif field_type == "boolean":
            return random.choice([True, False])
        
        elif field_type == "array":
            return []
        
        else:  # string
            if "timestamp" in field.lower():
                return datetime.now(timezone.utc).isoformat()
            elif "ip" in field.lower():
                return f"192.168.1.{random.randint(100, 200)}"
            elif "serial" in field.lower():
                return f"SVR{random.randint(1000, 9999)}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}{random.randint(1000, 9999)}"
            elif "client" in field.lower():
                return f"TestClient_{random.randint(1, 100)}"
            else:
                return f"test_{field}_{random.randint(1, 100)}"
    
    def generate_test_suite(self, topics: List[str] = None) -> Dict[str, Dict]:
        """Generiert eine komplette Test-Suite für Topics"""
        if topics is None:
            topics = self.get_available_topics()
        
        test_suite = {}
        for topic in topics:
            test_suite[topic] = {
                'random': self.generate_test_payload(topic, 'random'),
                'latest': self.generate_test_payload(topic, 'latest'),
                'template': self.generate_test_payload(topic, 'template')
            }
        
        return test_suite
    
    def export_test_suite(self, output_file: str = "omf2/registry/test_suite.json"):
        """Exportiert Test-Suite als JSON"""
        test_suite = self.generate_test_suite()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(test_suite, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Test suite exported to: {output_path}")
        return str(output_path)


def main():
    """Hauptfunktion für Test-Payload-Generator"""
    print("🚀 Test Payload Generator")
    print("=" * 50)
    
    generator = TestPayloadGenerator()
    
    available_topics = generator.get_available_topics()
    print(f"📊 Available Topics: {len(available_topics)}")
    
    if available_topics:
        # Test mit einem Topic
        test_topic = available_topics[0]
        print(f"\n🧪 Testing with topic: {test_topic}")
        
        examples = generator.get_topic_examples(test_topic)
        print(f"   Examples available: {len(examples)}")
        
        # Generiere verschiedene Variationen
        variations = ['random', 'latest', 'template']
        for variation in variations:
            payload = generator.generate_test_payload(test_topic, variation)
            if payload:
                print(f"   {variation}: {json.dumps(payload, indent=2)[:100]}...")
        
        # Exportiere Test-Suite
        print(f"\n📤 Exporting test suite...")
        output_file = generator.export_test_suite()
        print(f"✅ Test suite exported to: {output_file}")
    
    else:
        print("⚠️ No topics found in aps-data")


if __name__ == "__main__":
    main()
