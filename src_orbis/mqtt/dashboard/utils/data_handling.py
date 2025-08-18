"""
Utility functions for data handling in the APS Dashboard
"""
import pandas as pd
import json

def extract_module_info(df):
    """Extract module information from topics and payloads"""
    try:
        # Extract module type and serial number from topics
        def extract_module_from_topic(topic):
            topic_lower = topic.lower()
            
            # Module patterns in topics - more specific patterns first
            if 'svr3qa0022' in topic_lower:
                return 'HBW', 'SVR3QA0022'
            elif 'svr4h73275' in topic_lower:
                return 'DPS', 'SVR4H73275'
            elif 'svr4h76530' in topic_lower:
                return 'AIQS', 'SVR4H76530'
            elif 'svr3qa2098' in topic_lower:
                return 'MILL', 'SVR3QA2098'
            elif 'svr4h76449' in topic_lower:
                return 'DRILL', 'SVR4H76449'
            elif '5io4' in topic_lower:
                return 'FTS', '5IO4'
            elif 'ccu' in topic_lower:
                return 'CCU', 'CCU'
            elif 'txt' in topic_lower or 'j1' in topic_lower:
                return 'TXT', 'TXT'
            elif 'hbw' in topic_lower:
                return 'HBW', 'unknown'
            elif 'dps' in topic_lower:
                return 'DPS', 'unknown'
            elif 'aiqs' in topic_lower:
                return 'AIQS', 'unknown'
            elif 'mill' in topic_lower:
                return 'MILL', 'unknown'
            elif 'drill' in topic_lower:
                return 'DRILL', 'unknown'
            elif 'oven' in topic_lower:
                return 'OVEN', 'unknown'
            elif 'fts' in topic_lower:
                return 'FTS', 'unknown'
            else:
                return 'unknown', 'unknown'
        
        # Rename session labels to new format
        def rename_session_label(session_label):
            if 'bestellung_blau' in session_label.lower():
                return 'Order_cloud_blue_ok'
            elif 'bestellung_rot' in session_label.lower():
                return 'Order_cloud_red_ok'
            elif 'bestellung_gelb' in session_label.lower():
                return 'Order_cloud_yellow_ok'
            elif 'order_local' in session_label.lower():
                return 'Order_local_unknown_ok'
            elif 'wareneingang' in session_label.lower():
                return 'Wareneingang_manual_ok'
            elif 'test' in session_label.lower():
                return 'Test_unknown_ok'
            else:
                return session_label
        
        # Extract status from payloads
        def extract_status_from_payload(payload):
            try:
                if pd.isna(payload) or payload == '':
                    return 'unknown'
                
                # Try JSON first
                try:
                    data = json.loads(payload)
                    
                    # Check for status fields in JSON
                    if isinstance(data, dict):
                        if 'available' in data:
                            return str(data['available'])
                        elif 'status' in data:
                            return str(data['status'])
                        elif 'state' in data:
                            return str(data['state'])
                        elif 'connected' in data:
                            return 'CONNECTED' if data['connected'] else 'DISCONNECTED'
                        elif 'charging' in data:
                            return 'CHARGING' if data['charging'] else 'NOT_CHARGING'
                        elif 'type' in data:
                            return str(data['type'])
                        elif 'subType' in data:
                            return str(data['subType'])
                        elif 'messageType' in data:
                            return str(data['messageType'])
                        elif 'modules' in data:
                            return 'MODULE_LIST'
                        elif 'transports' in data:
                            return 'TRANSPORT_LIST'
                    
                    return 'unknown'
                    
                except json.JSONDecodeError:
                    # Handle non-JSON payloads
                    payload_str = str(payload).lower()
                    
                    # Check for common status patterns in text
                    if 'ready' in payload_str:
                        return 'READY'
                    elif 'busy' in payload_str:
                        return 'BUSY'
                    elif 'connected' in payload_str:
                        return 'CONNECTED'
                    elif 'disconnected' in payload_str:
                        return 'DISCONNECTED'
                    elif 'charging' in payload_str:
                        return 'CHARGING'
                    elif 'error' in payload_str:
                        return 'ERROR'
                    elif 'ok' in payload_str:
                        return 'OK'
                    elif 'true' in payload_str:
                        return 'TRUE'
                    elif 'false' in payload_str:
                        return 'FALSE'
                    elif 'data:image' in payload_str:
                        return 'CAMERA_DATA'
                    elif len(payload_str) < 50:  # Short text payloads
                        return payload_str.upper()
                    
                    return 'unknown'
                
            except Exception as e:
                return 'unknown'
        
        # Apply extraction
        module_info = df['topic'].apply(extract_module_from_topic)
        df['module_type_extracted'] = [info[0] for info in module_info]
        df['serial_number_extracted'] = [info[1] for info in module_info]
        df['status_extracted'] = df['payload'].apply(extract_status_from_payload)
        
        # Use extracted values if original are unknown
        df.loc[df['module_type'] == 'unknown', 'module_type'] = df.loc[df['module_type'] == 'unknown', 'module_type_extracted']
        df.loc[df['serial_number'] == 'unknown', 'serial_number'] = df.loc[df['serial_number'] == 'unknown', 'serial_number_extracted']
        df.loc[df['status'] == 'unknown', 'status'] = df.loc[df['status'] == 'unknown', 'status_extracted']
        
        # Rename session labels
        df['session_label'] = df['session_label'].apply(rename_session_label)
        
        # Clean up
        df = df.drop(['module_type_extracted', 'serial_number_extracted', 'status_extracted'], axis=1)
        
        return df
        
    except Exception as e:
        # In case of an error, return the original dataframe
        return df
