"""
Topic Mapping Configuration
Maps MQTT topics to user-friendly names
"""

# Default topic mappings
DEFAULT_TOPIC_MAPPINGS = {
    # Node-RED Topics
    "module/v1/ff/NodeRed/SVR4H76530/connection": "NodeRed → AIQS : connection",
    "module/v1/ff/NodeRed/SVR4H76530/state": "NodeRed → AIQS : state",
    "module/v1/ff/NodeRed/SVR4H76530/factsheet": "NodeRed → AIQS : factsheet",
    "module/v1/ff/NodeRed/SVR4H73275/connection": "NodeRed → DPS : connection",
    "module/v1/ff/NodeRed/SVR4H73275/state": "NodeRed → DPS : state",
    "module/v1/ff/NodeRed/SVR4H73275/factsheet": "NodeRed → DPS : factsheet",
    "module/v1/ff/NodeRed/SVR4H76449/connection": "NodeRed → DRILL : connection",
    "module/v1/ff/NodeRed/SVR4H76449/state": "NodeRed → DRILL : state",
    "module/v1/ff/NodeRed/SVR4H76449/factsheet": "NodeRed → DRILL : factsheet",
    "module/v1/ff/NodeRed/SVR3QA2098/connection": "NodeRed → MILL : connection",
    "module/v1/ff/NodeRed/SVR3QA2098/state": "NodeRed → MILL : state",
    "module/v1/ff/NodeRed/SVR3QA2098/factsheet": "NodeRed → MILL : factsheet",
    "module/v1/ff/NodeRed/SVR3QA0022/connection": "NodeRed → HBW : connection",
    "module/v1/ff/NodeRed/SVR3QA0022/state": "NodeRed → HBW : state",
    "module/v1/ff/NodeRed/SVR3QA0022/factsheet": "NodeRed → HBW : factsheet",
    "module/v1/ff/NodeRed/status": "NodeRed : status",
    
    # Direct Module Topics
    "module/v1/ff/SVR4H76530/connection": "AIQS : connection",
    "module/v1/ff/SVR4H76530/state": "AIQS : state",
    "module/v1/ff/SVR4H76530/order": "AIQS : order",
    "module/v1/ff/SVR4H76530/factsheet": "AIQS : factsheet",
    
    "module/v1/ff/SVR4H73275/connection": "DPS : connection",
    "module/v1/ff/SVR4H73275/state": "DPS : state",
    "module/v1/ff/SVR4H73275/order": "DPS : order",
    "module/v1/ff/SVR4H73275/factsheet": "DPS : factsheet",
    
    "module/v1/ff/SVR4H76449/connection": "DRILL : connection",
    "module/v1/ff/SVR4H76449/state": "DRILL : state",
    "module/v1/ff/SVR4H76449/order": "DRILL : order",
    "module/v1/ff/SVR4H76449/factsheet": "DRILL : factsheet",
    
    "module/v1/ff/SVR3QA2098/connection": "MILL : connection",
    "module/v1/ff/SVR3QA2098/state": "MILL : state",
    "module/v1/ff/SVR3QA2098/order": "MILL : order",
    "module/v1/ff/SVR3QA2098/factsheet": "MILL : factsheet",
    
    "module/v1/ff/SVR3QA0022/connection": "HBW : connection",
    "module/v1/ff/SVR3QA0022/state": "HBW : state",
    "module/v1/ff/SVR3QA0022/order": "HBW : order",
    "module/v1/ff/SVR3QA0022/factsheet": "HBW : factsheet",
    
    # FTS Topics
    "fts/v1/ff/5iO4/connection": "FTS : connection",
    "fts/v1/ff/5iO4/state": "FTS : state",
    "fts/v1/ff/5iO4/order": "FTS : order",
    "fts/v1/ff/5iO4/factsheet": "FTS : factsheet",
    
    # Charging Station Topics
    "module/v1/ff/CHRG0/connection": "CHRG : connection",
    "module/v1/ff/CHRG0/state": "CHRG : state",
    "module/v1/ff/CHRG0/order": "CHRG : order",
    "module/v1/ff/CHRG0/factsheet": "CHRG : factsheet",
}

# Module serial number to name mapping
MODULE_SERIAL_TO_NAME = {
    "SVR4H76530": "AIQS",
    "SVR4H73275": "DPS", 
    "SVR4H76449": "DRILL",
    "SVR3QA2098": "MILL",
    "SVR3QA0022": "HBW",
    "5iO4": "FTS",
    "CHRG0": "CHRG"
}

# CCU Topics mapping
CCU_TOPIC_MAPPINGS = {
    "ccu/state": "CCU : state",
    "ccu/state/flow": "CCU : state : flow",
    "ccu/state/status": "CCU : state : status",
    "ccu/state/error": "CCU : state : error",
    "ccu/control": "CCU : control",
    "ccu/control/command": "CCU : control : command",
    "ccu/control/order": "CCU : control : order",
    "ccu/status": "CCU : status",
    "ccu/status/connection": "CCU : status : connection",
    "ccu/status/health": "CCU : status : health"
}

# Topic patterns for dynamic mapping
TOPIC_PATTERNS = {
    r"module/v1/ff/NodeRed/([^/]+)/([^/]+)": "NodeRed → {module} : {action}",
    r"module/v1/ff/([^/]+)/([^/]+)": "{module} : {action}",
    r"fts/v1/ff/([^/]+)/([^/]+)": "FTS : {action}",
    r"module/v1/ff/([^/]+)/([^/]+)": "{module} : {action}"
}

def get_friendly_topic_name(topic: str) -> str:
    """
    Get user-friendly name for a topic
    
    Args:
        topic: MQTT topic string
        
    Returns:
        User-friendly topic name
    """
    # First check exact mapping
    if topic in DEFAULT_TOPIC_MAPPINGS:
        return DEFAULT_TOPIC_MAPPINGS[topic]
    
    # Check CCU mappings
    if topic in CCU_TOPIC_MAPPINGS:
        return CCU_TOPIC_MAPPINGS[topic]
    
    # Try pattern matching
    import re
    
    # CCU pattern
    if topic.startswith("ccu/"):
        parts = topic.split("/")
        if len(parts) >= 2:
            if len(parts) == 2:
                return f"CCU : {parts[1]}"
            elif len(parts) == 3:
                return f"CCU : {parts[1]} : {parts[2]}"
            else:
                return f"CCU : {parts[1]} : {parts[2]} : {parts[3]}"
    
    # Node-RED pattern
    match = re.match(r"module/v1/ff/NodeRed/([^/]+)/([^/]+)", topic)
    if match:
        serial, action = match.groups()
        module_name = MODULE_SERIAL_TO_NAME.get(serial, serial)
        return f"NodeRed → {module_name} : {action}"
    
    # Direct module pattern
    match = re.match(r"module/v1/ff/([^/]+)/([^/]+)", topic)
    if match:
        serial, action = match.groups()
        module_name = MODULE_SERIAL_TO_NAME.get(serial, serial)
        return f"{module_name} : {action}"
    
    # FTS pattern
    match = re.match(r"fts/v1/ff/([^/]+)/([^/]+)", topic)
    if match:
        serial, action = match.groups()
        return f"FTS : {action}"
    
    # Charging station pattern
    match = re.match(r"module/v1/ff/CHRG0/([^/]+)", topic)
    if match:
        action = match.group(1)
        return f"CHRG : {action}"
    
    # If no pattern matches, return original topic
    return topic

def get_all_mapped_topics() -> dict:
    """
    Get all topic mappings including dynamic ones
    
    Returns:
        Dictionary of topic mappings
    """
    mappings = DEFAULT_TOPIC_MAPPINGS.copy()
    
    # Add CCU mappings
    mappings.update(CCU_TOPIC_MAPPINGS)
    
    # Add dynamic mappings for all possible combinations
    for serial, module_name in MODULE_SERIAL_TO_NAME.items():
        for action in ["connection", "state", "order", "factsheet"]:
            # Direct module topics
            topic = f"module/v1/ff/{serial}/{action}"
            if topic not in mappings:
                mappings[topic] = f"{module_name} : {action}"
            
            # Node-RED topics
            topic = f"module/v1/ff/NodeRed/{serial}/{action}"
            if topic not in mappings:
                mappings[topic] = f"NodeRed → {module_name} : {action}"
    
    # FTS topics
    for action in ["connection", "state", "order", "factsheet"]:
        topic = f"fts/v1/ff/5iO4/{action}"
        if topic not in mappings:
            mappings[topic] = f"FTS : {action}"
    
    # Charging station topics
    for action in ["connection", "state", "order", "factsheet"]:
        topic = f"module/v1/ff/CHRG0/{action}"
        if topic not in mappings:
            mappings[topic] = f"CHRG : {action}"
    
    return mappings

def get_unmapped_topics(topics_list: list) -> list:
    """
    Get topics that don't have friendly names
    
    Args:
        topics_list: List of topics to check
        
    Returns:
        List of unmapped topics
    """
    unmapped = []
    for topic in topics_list:
        friendly_name = get_friendly_topic_name(topic)
        if friendly_name == topic:  # No mapping found
            unmapped.append(topic)
    
    return unmapped
