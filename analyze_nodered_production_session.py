import pandas as pd
import sqlite3
import json
from datetime import datetime

def analyze_nodered_production_session():
    """Analyze the Node-RED production test session to understand what happened."""
    
    db_path = 'mqtt-data/sessions/aps_persistent_traffic_nodered_production_test.db'
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get all messages
        df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
        
        print(f"📊 Session Analysis: {len(df)} messages recorded")
        print("=" * 60)
        
        # Find Node-RED related messages
        nodered_messages = df[df['topic'].str.contains('NodeRed', na=False)]
        print(f"🔧 Node-RED Messages: {len(nodered_messages)}")
        
        if len(nodered_messages) > 0:
            print("\n🔍 Node-RED Message Topics:")
            for topic in nodered_messages['topic'].unique():
                print(f"  - {topic}")
        
        # Find any order messages sent to Node-RED
        order_messages = df[df['topic'].str.contains('order', na=False)]
        print(f"\n📋 Order Messages: {len(order_messages)}")
        
        if len(order_messages) > 0:
            print("\n🔍 Order Message Topics:")
            for topic in order_messages['topic'].unique():
                print(f"  - {topic}")
            
            # Show recent order messages
            recent_orders = order_messages.tail(10)
            print("\n🔍 Recent Order Messages:")
            for idx, row in recent_orders.iterrows():
                print(f"  Topic: {row['topic']}")
                try:
                    payload = json.loads(row['payload'])
                    print(f"  Payload: {json.dumps(payload, indent=2)}")
                except:
                    print(f"  Payload: {row['payload']}")
                print()
        
        # Find HBW-related messages
        hbw_messages = df[df['topic'].str.contains('SVR3QA0022', na=False)]
        print(f"🏭 HBW Messages: {len(hbw_messages)}")
        
        if len(hbw_messages) > 0:
            print("\n🔍 HBW Message Topics:")
            for topic in hbw_messages['topic'].unique():
                print(f"  - {topic}")
        
        # Find any instantAction messages (what Node-RED might send)
        instant_messages = df[df['topic'].str.contains('instantAction', na=False)]
        print(f"\n⚡ InstantAction Messages: {len(instant_messages)}")
        
        if len(instant_messages) > 0:
            print("\n🔍 InstantAction Details:")
            for idx, row in instant_messages.iterrows():
                print(f"  Topic: {row['topic']}")
                try:
                    payload = json.loads(row['payload'])
                    print(f"  Payload: {json.dumps(payload, indent=2)}")
                except:
                    print(f"  Payload: {row['payload']}")
                print()
        
        # Find any workflow or nodered specific messages
        workflow_messages = df[df['topic'].str.contains('workflow|nodered', na=False)]
        print(f"\n🔄 Workflow/Node-RED Messages: {len(workflow_messages)}")
        
        if len(workflow_messages) > 0:
            print("\n🔍 Workflow/Node-RED Details:")
            for idx, row in workflow_messages.iterrows():
                print(f"  Topic: {row['topic']}")
                try:
                    payload = json.loads(row['payload'])
                    print(f"  Payload: {json.dumps(payload, indent=2)}")
                except:
                    print(f"  Payload: {row['payload']}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing session: {e}")

if __name__ == "__main__":
    analyze_nodered_production_session()
