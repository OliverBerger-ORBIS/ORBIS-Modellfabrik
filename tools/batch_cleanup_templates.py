#!/usr/bin/env python3
"""
Batch-Cleanup für Template-Deskriptionen
Entfernt Topic-Strings aus Template-Descriptions und fügt Mappings hinzu
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def load_yaml(file_path: Path) -> dict:
    """Lädt YAML-Datei"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(data: dict, file_path: Path):
    """Speichert YAML-Datei"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

def extract_topic_from_description(description: str) -> str:
    """Extrahiert Topic-String aus Description"""
    # Pattern für verschiedene Topic-Formate
    patterns = [
        r'for ([a-zA-Z0-9/._-]+)',  # "for topic/name"
        r'Template for ([a-zA-Z0-9/._-]+)',  # "Template for topic/name"
        r'Auto-analyzed template for ([a-zA-Z0-9/._-]+)',  # "Auto-analyzed template for topic/name"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            topic = match.group(1)
            # Prüfe ob es ein Topic-ähnlicher String ist
            if any(x in topic for x in ['/', 'module/v1/', 'ccu/', 'fts/', 'txt/', 'nodered']):
                return topic
    return None

def clean_template_descriptions(template_file: Path) -> Tuple[str, str]:
    """Bereinigt Template-Descriptions und gibt Topic zurück"""
    data = load_yaml(template_file)
    extracted_topics = []
    
    # Metadata description bereinigen
    if 'metadata' in data and 'description' in data['metadata']:
        topic = extract_topic_from_description(data['metadata']['description'])
        if topic:
            extracted_topics.append(topic)
            # Topic-freie Description erstellen
            if 'ccu/' in topic:
                data['metadata']['description'] = f"Auto-analyzed template for CCU {topic.split('/')[-1]}"
            elif 'module/v1/' in topic:
                data['metadata']['description'] = f"Auto-analyzed template for Module {topic.split('/')[-1]}"
            elif 'txt/' in topic:
                data['metadata']['description'] = f"Auto-analyzed template for TXT {topic.split('/')[-1]}"
            elif 'nodered' in topic:
                data['metadata']['description'] = f"Auto-analyzed template for Node-RED {topic.split('/')[-1]}"
            else:
                data['metadata']['description'] = f"Auto-analyzed template for {topic.split('/')[-1]}"
    
    # Template descriptions bereinigen
    if 'templates' in data:
        for template_name, template_data in data['templates'].items():
            if 'description' in template_data:
                topic = extract_topic_from_description(template_data['description'])
                if topic:
                    if topic not in extracted_topics:
                        extracted_topics.append(topic)
                    # Topic-freie Description erstellen
                    if 'ccu/' in topic:
                        template_data['description'] = f"Template for CCU {topic.split('/')[-1]}"
                    elif 'module/v1/' in topic:
                        template_data['description'] = f"Template for Module {topic.split('/')[-1]}"
                    elif 'txt/' in topic:
                        template_data['description'] = f"Template for TXT {topic.split('/')[-1]}"
                    elif 'nodered' in topic:
                        template_data['description'] = f"Template for Node-RED {topic.split('/')[-1]}"
                    else:
                        template_data['description'] = f"Template for {topic.split('/')[-1]}"
    
    # Template speichern
    save_yaml(data, template_file)
    
    return extracted_topics[0] if extracted_topics else None, template_name if 'templates' in data else None

def add_mapping_to_yaml(mapping_file: Path, topic: str, template_name: str, category: str):
    """Fügt Mapping-Eintrag zur mapping.yml hinzu"""
    data = load_yaml(mapping_file)
    
    # Bestimme Sub-Category basierend auf Topic
    sub_category = "State"
    if "/order" in topic:
        sub_category = "Order"
    elif "/connection" in topic:
        sub_category = "Connection"
    elif "/factsheet" in topic:
        sub_category = "Factsheet"
    elif "/control" in topic:
        sub_category = "Control"
    elif "/config" in topic:
        sub_category = "State"
    
    # Bestimme Category
    meta_category = category
    if "CCU" in category:
        meta_category = "CCU"
    elif "TXT" in category:
        meta_category = "TXT"
    elif "Node-RED" in category:
        meta_category = "Node-RED"
    elif "MODULE" in category:
        meta_category = "MODULE"
    
    # Friendly Name erstellen
    friendly_name = topic.replace('/', ' : ').replace('_', ' ').title()
    
    # Neuen Mapping-Eintrag erstellen
    new_mapping = {
        "topic": topic,
        "template": template_name,
        "direction": "bidirectional",
        "meta": {
            "category": meta_category,
            "sub_category": sub_category,
            "friendly_name": friendly_name
        }
    }
    
    # Prüfen ob Topic bereits existiert
    existing_topics = [m.get('topic') for m in data.get('mappings', [])]
    if topic not in existing_topics:
        data['mappings'].append(new_mapping)
        print(f"✅ Added mapping: {topic} → {template_name}")
    else:
        print(f"⚠️  Topic already exists: {topic}")
    
    # Speichern
    save_yaml(data, mapping_file)

def main():
    """Hauptfunktion für Batch-Cleanup"""
    project_root = Path(__file__).parent.parent
    templates_dir = project_root / "registry" / "model" / "v1" / "templates"
    mapping_file = project_root / "registry" / "model" / "v1" / "mapping.yml"
    
    print(f"🔍 Scanning templates in: {templates_dir}")
    
    processed_count = 0
    error_count = 0
    
    # Alle Template-Dateien durchgehen
    for template_file in templates_dir.glob("*.yml"):
        try:
            print(f"\n📝 Processing: {template_file.name}")
            
            # Topic und Template-Name extrahieren
            topic, template_name = clean_template_descriptions(template_file)
            
            if topic and template_name:
                # Kategorie aus Dateiname ableiten
                category = "UNKNOWN"
                if "ccu." in template_file.name:
                    category = "CCU"
                elif "txt." in template_file.name:
                    category = "TXT"
                elif "nodered." in template_file.name:
                    category = "Node-RED"
                elif "module." in template_file.name:
                    category = "MODULE"
                
                # Mapping hinzufügen
                add_mapping_to_yaml(mapping_file, topic, template_name, category)
                processed_count += 1
            else:
                print(f"⚠️  No topic found in {template_file.name}")
                
        except Exception as e:
            print(f"❌ Error processing {template_file.name}: {e}")
            error_count += 1
    
    print(f"\n📊 Batch-Cleanup completed:")
    print(f"   ✅ Processed: {processed_count} templates")
    print(f"   ❌ Errors: {error_count} templates")

if __name__ == "__main__":
    main()
