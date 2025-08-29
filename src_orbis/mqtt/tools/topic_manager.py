#!/usr/bin/env python3
"""
Topic Manager - Zentrale Verwaltung der MQTT-Topic-Konfiguration
Replaces topic_mapping.py with enhanced functionality
"""

import os
import yaml
from typing import Dict, List, Any


class TopicManager:
    """Zentrale Verwaltung der MQTT-Topic-Konfiguration"""

    def __init__(self, config_path: str = None):
        """Initialize TopicManager with YAML configuration"""
        if config_path is None:
            # Default path: config/topic_config.yml relative to this file
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "topic_config.yml"
            )

        self.config_path = config_path
        self.config = None
        self.load_yaml_config()

    def load_yaml_config(self) -> bool:
        """Load topic configuration from YAML file"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            return True
        except FileNotFoundError:
            print(f"Topic configuration file not found: {self.config_path}")
            self.config = {}
            return False
        except yaml.YAMLError as e:
            print(f"Error parsing topic configuration: {e}")
            self.config = {}
            return False
        except Exception as e:
            print(f"Error loading topic configuration: {e}")
            self.config = {}
            return False

    def reload_config(self) -> bool:
        """Reload configuration from file"""
        return self.load_yaml_config()

    def get_friendly_name(self, topic: str) -> str:
        """Get friendly name for topic"""
        if not self.config or "topics" not in self.config:
            return topic

        topic_info = self.config["topics"].get(topic)
        if topic_info:
            return topic_info.get("friendly_name", topic)

        return topic

    def get_topic_info(self, topic: str) -> Dict[str, Any]:
        """Get complete topic information"""
        if not self.config or "topics" not in self.config:
            return {}

        return self.config["topics"].get(topic, {})

    def get_topic_category(self, topic: str) -> str:
        """Get category for topic"""
        topic_info = self.get_topic_info(topic)
        return topic_info.get("category", "Unknown")

    def get_topic_sub_category(self, topic: str) -> str:
        """Get sub-category for topic (for modules)"""
        topic_info = self.get_topic_info(topic)
        return topic_info.get("sub_category", "")

    def get_topic_module(self, topic: str) -> str:
        """Get module name for topic (for module topics)"""
        topic_info = self.get_topic_info(topic)
        return topic_info.get("module", "")

    def get_topic_description(self, topic: str) -> str:
        """Get description for topic"""
        topic_info = self.get_topic_info(topic)
        return topic_info.get("description", "")

    def get_all_topics(self) -> Dict[str, Dict[str, Any]]:
        """Get all topics"""
        if not self.config or "topics" not in self.config:
            return {}

        return self.config["topics"]

    def get_topics_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get all topics for a specific category"""
        all_topics = self.get_all_topics()
        return {
            topic: info
            for topic, info in all_topics.items()
            if info.get("category") == category
        }

    def get_topics_by_module(self, module: str) -> Dict[str, Dict[str, Any]]:
        """Get all topics for a specific module"""
        all_topics = self.get_all_topics()
        return {
            topic: info
            for topic, info in all_topics.items()
            if info.get("module") == module
        }

    def get_topics_by_sub_category(
        self, sub_category: str
    ) -> Dict[str, Dict[str, Any]]:
        """Get all topics for a specific sub-category"""
        all_topics = self.get_all_topics()
        return {
            topic: info
            for topic, info in all_topics.items()
            if info.get("sub_category") == sub_category
        }

    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all categories with descriptions"""
        if not self.config or "categories" not in self.config:
            return {}

        return self.config["categories"]

    def get_category_description(self, category: str) -> str:
        """Get description for category"""
        categories = self.get_categories()
        category_info = categories.get(category, {})
        return category_info.get("description", "")

    def get_category_icon(self, category: str) -> str:
        """Get icon for category"""
        categories = self.get_categories()
        category_info = categories.get(category, {})
        return category_info.get("icon", "📋")

    def get_module_sub_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get module sub-categories"""
        if not self.config or "module_sub_categories" not in self.config:
            return {}

        return self.config["module_sub_categories"]

    def get_sub_category_description(self, sub_category: str) -> str:
        """Get description for sub-category"""
        sub_categories = self.get_module_sub_categories()
        sub_category_info = sub_categories.get(sub_category, {})
        return sub_category_info.get("description", "")

    def get_sub_category_icon(self, sub_category: str) -> str:
        """Get icon for sub-category"""
        sub_categories = self.get_module_sub_categories()
        sub_category_info = sub_categories.get(sub_category, {})
        return sub_category_info.get("icon", "📋")

    def is_known_topic(self, topic: str) -> bool:
        """Check if topic is known"""
        if not self.config or "topics" not in self.config:
            return False

        return topic in self.config["topics"]

    def get_all_friendly_names(self) -> Dict[str, str]:
        """Get all topic to friendly name mappings"""
        all_topics = self.get_all_topics()
        return {
            topic: info.get("friendly_name", topic)
            for topic, info in all_topics.items()
        }

    def get_template_placeholders(self) -> Dict[str, str]:
        """Get template placeholders"""
        if not self.config or "template_placeholders" not in self.config:
            return {}

        return self.config["template_placeholders"]

    def get_topic_patterns(self) -> List[List[str]]:
        """Get topic patterns for recognition"""
        if not self.config or "topic_patterns" not in self.config:
            return []

        return self.config["topic_patterns"]

    def get_statistics(self) -> Dict[str, Any]:
        """Get topic configuration statistics"""
        all_topics = self.get_all_topics()
        categories = self.get_categories()

        # Count topics by category
        category_counts = {}
        for topic, info in all_topics.items():
            category = info.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

        # Count topics by sub-category
        sub_category_counts = {}
        for topic, info in all_topics.items():
            sub_category = info.get("sub_category", "")
            if sub_category:
                sub_category_counts[sub_category] = (
                    sub_category_counts.get(sub_category, 0) + 1
                )

        # Count topics by module
        module_counts = {}
        for topic, info in all_topics.items():
            module = info.get("module", "")
            if module:
                module_counts[module] = module_counts.get(module, 0) + 1

        return {
            "total_topics": len(all_topics),
            "total_categories": len(categories),
            "category_counts": category_counts,
            "sub_category_counts": sub_category_counts,
            "module_counts": module_counts,
            "categories": list(categories.keys()),
            "sub_categories": list(sub_category_counts.keys()),
            "modules": list(module_counts.keys()),
        }

    def format_topic_display_name(self, topic: str) -> str:
        """Format topic for display with friendly name"""
        friendly_name = self.get_friendly_name(topic)
        if friendly_name != topic:
            return f"{friendly_name} ({topic})"
        return topic

    # Backward compatibility functions
    def get_friendly_topic_name(self, topic: str) -> str:
        """Backward compatibility: get friendly topic name"""
        return self.get_friendly_name(topic)

    def get_all_mapped_topics(self) -> Dict[str, str]:
        """Backward compatibility: get all topic mappings"""
        return self.get_all_friendly_names()

    def get_unmapped_topics(self, topics_list: List[str]) -> List[str]:
        """Get topics that are not in the configuration"""
        all_topics = self.get_all_topics()
        return [topic for topic in topics_list if topic not in all_topics]


# Global instance for easy access
_topic_manager = None


def get_topic_manager() -> TopicManager:
    """Get global topic manager instance"""
    global _topic_manager
    if _topic_manager is None:
        _topic_manager = TopicManager()
    return _topic_manager


if __name__ == "__main__":
    """Test the TopicManager"""
    print("🔧 Topic Manager Test")
    print("=" * 50)

    manager = TopicManager()

    # Test basic functionality
    print(f"📋 Total Topics: {len(manager.get_all_topics())}")
    print(f"📂 Total Categories: {len(manager.get_categories())}")

    # Test category functionality
    categories = manager.get_categories()
    for category, info in categories.items():
        icon = info.get("icon", "📋")
        description = info.get("description", "")
        print(f"{icon} {category}: {description}")

    # Test topic functionality
    all_topics = manager.get_all_topics()
    print("\n📊 Topics by Category:")
    for topic, info in all_topics.items():
        category = info.get("category", "Unknown")
        friendly_name = info.get("friendly_name", topic)
        print(f"  {topic} → {friendly_name} ({category})")

    # Test statistics
    stats = manager.get_statistics()
    print("\n📈 Statistics:")
    print(f"  Total Topics: {stats['total_topics']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Category Counts: {stats['category_counts']}")

    print("\n✅ Topic Manager test completed")
