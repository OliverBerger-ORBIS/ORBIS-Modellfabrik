import pandas as pd
import sqlite3
import json
from datetime import datetime

def analyze_ccu_production_session():
    """Analyze the CCU production test session to understand what happened."""
    
    db_path = 'mqtt-data/sessions/aps_persistent_traffic_ccu_production_test.db'
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get all messages
        df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
        
        print(f"📊 Session Analysis: {len(df)} messages recorded")
        print("=" * 60)
        
        # Find CCU order messages
        ccu_order_messages = df[df['topic'].str.contains('ccu/order', na=False)]
        print(f"📋 CCU Order Messages: {len(ccu_order_messages)}")
        
        if len(ccu_order_messages) > 0:
            print("\n🔍 CCU Order Details:")
            for idx, row in ccu_order_messages.iterrows():
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
            
            # Show recent HBW messages
            recent_hbw = hbw_messages.tail(5)
            print("\n🔍 Recent HBW Messages:")
            for idx, row in recent_hbw.iterrows():
                print(f"  Topic: {row['topic']}")
                try:
                    payload = json.loads(row['payload'])
                    print(f"  Payload: {json.dumps(payload, indent=2)}")
                except:
                    print(f"  Payload: {row['payload']}")
                print()
        
        # Find TXT controller order messages
        txt_order_messages = df[df['topic'].str.contains('/j1/txt/1/f/i/order', na=False)]
        print(f"🎮 TXT Order Messages: {len(txt_order_messages)}")
        
        if len(txt_order_messages) > 0:
            print("\n🔍 TXT Order Details:")
            for idx, row in txt_order_messages.iterrows():
                print(f"  Topic: {row['topic']}")
                try:
                    payload = json.loads(row['payload'])
                    print(f"  Payload: {json.dumps(payload, indent=2)}")
                except:
                    print(f"  Payload: {row['payload']}")
                print()
        
        # Find any instantAction messages
        instant_messages = df[df['topic'].str.contains('instantAction', na=False)]
        print(f"⚡ InstantAction Messages: {len(instant_messages)}")
        
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
        
        # Find any order-related messages
        order_messages = df[df['topic'].str.contains('order', na=False)]
        print(f"📋 All Order Messages: {len(order_messages)}")
        
        if len(order_messages) > 0:
            print("\n🔍 All Order Topics:")
            for topic in order_messages['topic'].unique():
                print(f"  - {topic}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing session: {e}")

if __name__ == "__main__":
    analyze_ccu_production_session()
