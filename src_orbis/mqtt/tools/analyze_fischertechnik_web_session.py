import pandas as pd
import sqlite3
import json
from datetime import datetime

def analyze_fischertechnik_web_session():
    """Analyze the Fischertechnik web interface test session to understand HTTP and MQTT patterns."""
    db_path = 'mqtt-data/sessions/aps_persistent_traffic_fischertechnik_web_test.db'
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
        print(f"📊 Fischertechnik Web Interface Analysis: {len(df)} messages recorded")
        print("=" * 80)
        
        # Analyze order-related messages
        order_messages = df[df['topic'].str.contains('order', na=False)]
        print(f"📋 Order Messages: {len(order_messages)}")
        if len(order_messages) > 0:
            print("\n🔍 Order Message Topics:")
            for topic in order_messages['topic'].unique():
                print(f"  - {topic}")
            print("\n🔍 Recent Order Messages:")
            recent_orders = order_messages.tail(10)
            for idx, row in recent_orders.iterrows():
                print(f"  Topic: {row['topic']}")
                try:
                    payload = json.loads(row['payload'])
                    print(f"  Payload: {json.dumps(payload, indent=2)}")
                except:
                    print(f"  Payload: {row['payload']}")
                print()
        
        # Analyze TXT Controller messages
        txt_messages = df[df['topic'].str.contains('txt', na=False)]
        print(f"🎮 TXT Controller Messages: {len(txt_messages)}")
        if len(txt_messages) > 0:
            print("\n🔍 TXT Message Topics:")
            for topic in txt_messages['topic'].unique():
                print(f"  - {topic}")
        
        # Analyze fischertechnik-specific messages
        fischertech_messages = df[df['topic'].str.contains('fischertechnik', na=False)]
        print(f"\n🏭 Fischertechnik Messages: {len(fischertech_messages)}")
        if len(fischertech_messages) > 0:
            print("\n🔍 Fischertechnik Message Topics:")
            for topic in fischertech_messages['topic'].unique():
                print(f"  - {topic}")
            print("\n🔍 Fischertechnik Message Details:")
            for idx, row in fischertech_messages.iterrows():
                print(f"  Topic: {row['topic']}")
                try:
                    payload = json.loads(row['payload'])
                    print(f"  Payload: {json.dumps(payload, indent=2)}")
                except:
                    print(f"  Payload: {row['payload']}")
                print()
        
        # Analyze module state changes
        state_messages = df[df['topic'].str.contains('/state', na=False)]
        print(f"\n📊 Module State Messages: {len(state_messages)}")
        if len(state_messages) > 0:
            print("\n🔍 State Message Topics:")
            for topic in state_messages['topic'].unique():
                print(f"  - {topic}")
        
        # Analyze instantAction messages
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
        
        # Analyze HTTP-like patterns (if any)
        http_patterns = df[df['topic'].str.contains('http|api|rest|web', na=False)]
        print(f"\n🌐 HTTP/Web Patterns: {len(http_patterns)}")
        if len(http_patterns) > 0:
            print("\n🔍 HTTP/Web Message Topics:")
            for topic in http_patterns['topic'].unique():
                print(f"  - {topic}")
        
        # Show message timeline
        print(f"\n⏰ Message Timeline:")
        print(f"  Start: {df['timestamp'].min()}")
        print(f"  End: {df['timestamp'].max()}")
        print(f"  Duration: {len(df)} messages")
        
        # Show most active topics
        topic_counts = df['topic'].value_counts().head(10)
        print(f"\n📈 Most Active Topics:")
        for topic, count in topic_counts.items():
            print(f"  {topic}: {count} messages")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing session: {e}")

if __name__ == "__main__":
    analyze_fischertechnik_web_session()
