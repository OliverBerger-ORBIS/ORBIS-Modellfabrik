import pandas as pd
import sqlite3
import json
from datetime import datetime

def analyze_dashboard_hbw_session():
    """Analyze the dashboard HBW test session to understand what happened."""
    
    db_path = 'mqtt-data/sessions/aps_persistent_traffic_dashboard_hbw_test.db'
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get all messages
        df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
        
        print(f"📊 Session Analysis: {len(df)} messages recorded")
        print("=" * 60)
        
        # Find HBW-related messages
        hbw_messages = df[df['topic'].str.contains('SVR3QA0022', na=False)]
        print(f"🏭 HBW Messages: {len(hbw_messages)}")
        
        if len(hbw_messages) > 0:
            print("\n🔍 HBW Message Topics:")
            for topic in hbw_messages['topic'].unique():
                print(f"  - {topic}")
        
        # Find CCU messages
        ccu_messages = df[df['topic'].str.contains('ccu', na=False)]
        print(f"\n🎛️ CCU Messages: {len(ccu_messages)}")
        
        if len(ccu_messages) > 0:
            print("\n🔍 CCU Message Topics:")
            for topic in ccu_messages['topic'].unique():
                print(f"  - {topic}")
        
        # Find order-related messages
        order_messages = df[df['topic'].str.contains('order', na=False)]
        print(f"\n📋 Order Messages: {len(order_messages)}")
        
        if len(order_messages) > 0:
            print("\n🔍 Order Message Topics:")
            for topic in order_messages['topic'].unique():
                print(f"  - {topic}")
        
        # Find instantAction messages (what dashboard sent)
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
        
        # Find TXT controller messages
        txt_messages = df[df['topic'].str.contains('txt', na=False)]
        print(f"\n🎮 TXT Controller Messages: {len(txt_messages)}")
        
        if len(txt_messages) > 0:
            print("\n🔍 TXT Message Topics:")
            for topic in txt_messages['topic'].unique():
                print(f"  - {topic}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing session: {e}")

if __name__ == "__main__":
    analyze_dashboard_hbw_session()
