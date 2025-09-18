"""
MQTT Topic-Prioritäten für die Nachrichten-Zentrale.

Definiert Topic-Filter mit Prioritäten 1-5 für gesteuerte Subscriptions.
"""

PRIORITY_FILTERS = {
    1: [
        # Critical control (Orders/Requests)
        "ccu/control/*",
        "ccu/set/reset",
        "module/v1/ff/*/order",
        "fts/v1/ff/*/order",
        "fts/v1/ff/*/instantAction",
        "ccu/pairing/state",
    ],
    2: [
        # Important status (States/Connections)
        "ccu/state/*",
        "ccu/status/*",
        "module/v1/ff/*/state",
        "module/v1/ff/*/connection",
        "fts/v1/ff/*/state",
        "fts/v1/ff/*/connection",
    ],
    3: [
        # Normal info
        "ccu/pairing/state",
        "module/v1/ff/*/factsheet",
        "fts/v1/ff/*/factsheet",
    ],
    4: [
        # Node-RED
        "module/v1/ff/NodeRed/*",
        "/j1/txt/1/c/*",
        "/j1/txt/1/i/*",
        "/j1/txt/1/o/*",
        "/j1/txt/1/f/*",
    ],
    5: [
        # High frequency (Sensor data) - Alle spezifischen Topics ohne Wildcards
        # CCU Topics
        "ccu/state",
        "ccu/state/flow",
        "ccu/state/status",
        "ccu/state/error",
        "ccu/control",
        "ccu/control/command",
        "ccu/control/order",
        "ccu/set/reset",
        "ccu/status",
        "ccu/status/connection",
        "ccu/pairing/state",
        "ccu/status/health",
        # TXT Controller Topics
        "/j1/txt/1/f/i/stock",
        "/j1/txt/1/f/o/order",
        "/j1/txt/1/f/i/order",
        "/j1/txt/1/f/o/stock",
        "/j1/txt/1/f/i/status",
        "/j1/txt/1/f/o/status",
        "/j1/txt/1/f/i/error",
        "/j1/txt/1/f/o/error",
        "/j1/txt/1/f/i/config/hbw",
        "/j1/txt/1/c/bme680",
        "/j1/txt/1/c/cam",
        "/j1/txt/1/c/ldr",
        "/j1/txt/1/i/bme680",
        "/j1/txt/1/i/broadcast",
        "/j1/txt/1/i/cam",
        "/j1/txt/1/i/ldr",
        "/j1/txt/1/o/broadcast",
        # Module Topics - MILL (SVR3QA2098)
        "module/v1/ff/SVR3QA2098/connection",
        "module/v1/ff/SVR3QA2098/state",
        "module/v1/ff/SVR3QA2098/order",
        "module/v1/ff/SVR3QA2098/factsheet",
        # Module Topics - DRILL (SVR4H76449)
        "module/v1/ff/SVR4H76449/connection",
        "module/v1/ff/SVR4H76449/state",
        "module/v1/ff/SVR4H76449/order",
        "module/v1/ff/SVR4H76449/factsheet",
        # Module Topics - AIQS (SVR4H76530)
        "module/v1/ff/SVR4H76530/connection",
        "module/v1/ff/SVR4H76530/state",
        "module/v1/ff/SVR4H76530/order",
        "module/v1/ff/SVR4H76530/factsheet",
        # Module Topics - DPS (SVR4H73275)
        "module/v1/ff/SVR4H73275/connection",
        "module/v1/ff/SVR4H73275/state",
        "module/v1/ff/SVR4H73275/order",
        "module/v1/ff/SVR4H73275/factsheet",
        # Module Topics - HBW (SVR3QA0022)
        "module/v1/ff/SVR3QA0022/connection",
        "module/v1/ff/SVR3QA0022/state",
        "module/v1/ff/SVR3QA0022/order",
        "module/v1/ff/SVR3QA0022/factsheet",
        # Node-RED Topics - AIQS (SVR4H76530)
        "module/v1/ff/NodeRed/SVR4H76530/connection",
        "module/v1/ff/NodeRed/SVR4H76530/state",
        "module/v1/ff/NodeRed/SVR4H76530/factsheet",
        # Node-RED Topics - DPS (SVR4H73275)
        "module/v1/ff/NodeRed/SVR4H73275/connection",
        "module/v1/ff/NodeRed/SVR4H73275/state",
        "module/v1/ff/NodeRed/SVR4H73275/factsheet",
        # Node-RED Topics - DRILL (SVR4H76449)
        "module/v1/ff/NodeRed/SVR4H76449/connection",
        "module/v1/ff/NodeRed/SVR4H76449/state",
        "module/v1/ff/NodeRed/SVR4H76449/factsheet",
        # Node-RED Topics - MILL (SVR3QA2098)
        "module/v1/ff/NodeRed/SVR3QA2098/connection",
        "module/v1/ff/NodeRed/SVR3QA2098/state",
        "module/v1/ff/NodeRed/SVR3QA2098/factsheet",
        # Node-RED Topics - HBW (SVR3QA0022)
        "module/v1/ff/NodeRed/SVR3QA0022/connection",
        "module/v1/ff/NodeRed/SVR3QA0022/state",
        "module/v1/ff/NodeRed/SVR3QA0022/factsheet",
        # Node-RED Status
        "module/v1/ff/NodeRed/status",
        # FTS Topics (5iO4)
        "fts/v1/ff/5iO4/connection",
        "fts/v1/ff/5iO4/state",
        "fts/v1/ff/5iO4/order",
        "fts/v1/ff/5iO4/factsheet",
    ],
    6: [
        # Alle Topics (Wildcard)
        "#",
    ],
}

def flatten_filters(upto: int) -> list[str]:
    """
    Gibt alle Topic-Filter bis zur angegebenen Prioritätsstufe zurück.

    Args:
        upto: Maximale Prioritätsstufe (1-6)

    Returns:
        Liste von Topic-Filtern
    """
    upto = max(1, min(6, int(upto)))
    result: list[str] = []

    for p in range(1, upto + 1):
        result.extend(PRIORITY_FILTERS.get(p, []))

    # Eindeutige Reihenfolge bewahren
    seen = set()
    out = []
    for f in result:
        if f not in seen:
            seen.add(f)
            out.append(f)

    return out

def get_priority_filters(level: int) -> list[str]:
    """
    Gibt die Topic-Filter für eine spezifische Prioritätsstufe zurück.

    Args:
        level: Prioritätsstufe (1-5)

    Returns:
        Liste von Topic-Filtern für diese Stufe
    """
    return PRIORITY_FILTERS.get(level, [])

def get_all_filters() -> list[str]:
    """
    Gibt alle verfügbaren Topic-Filter zurück.

    Returns:
        Liste aller Topic-Filter
    """
    return flatten_filters(6)
