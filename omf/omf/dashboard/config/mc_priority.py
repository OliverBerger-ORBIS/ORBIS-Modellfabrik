"""
Prioritäts-Konfiguration für die Nachrichten-Zentrale.

Definiert Topic-Prioritäten speziell für die Message Center Komponente.
"""

from typing import List

from src_orbis.omf.tools.mqtt_topics import PRIORITY_FILTERS

# Prioritäts-Topics für Message Center (basierend auf mqtt_topics.py)
PRIORITY_TOPICS = PRIORITY_FILTERS


def get_priority_filters(level: int) -> List[str]:
    """
    Gibt die Topic-Filter für eine spezifische Prioritätsstufe zurück.

    Args:
        level: Prioritätsstufe (1-5)

    Returns:
        Liste von Topic-Filtern für diese Stufe
    """
    return PRIORITY_TOPICS.get(level, [])


def get_all_priority_filters(upto: int) -> List[str]:
    """
    Gibt alle Topic-Filter bis zur angegebenen Prioritätsstufe zurück.

    Args:
        upto: Maximale Prioritätsstufe (1-5)

    Returns:
        Liste aller Topic-Filter bis zu dieser Stufe
    """
    from src_orbis.omf.tools.mqtt_topics import flatten_filters

    return flatten_filters(upto)
