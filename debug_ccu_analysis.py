#!/usr/bin/env python3
"""
Debug script for CCU analysis step by step
"""

import sys
import os
import sqlite3
from pathlib import Path
sys.path.append('src_orbis/mqtt/dashboard')

def debug_ccu_analysis():
    """Debug CCU analysis step by step"""
    
    print("🔍 Debugging CCU analysis step by step...")
    
    # Step 1: Check session directory
    session_dir = Path("mqtt-data/sessions")
    print(f"📁 Session directory: {session_dir}")
    print(f"   Exists: {session_dir.exists()}")
    
    if not session_dir.exists():
        print("❌ Session directory not found")
        return
    
    # Step 2: Find database files
    db_files = list(session_dir.glob("*.db"))
    print(f"📊 Found {len(db_files)} database files:")
    for db_file in db_files:
        print(f"   - {db_file}")
    
    if not db_files:
        print("❌ No database files found")
        return
    
    # Step 3: Test first database
    test_db = db_files[0]
    print(f"\n🔍 Testing database: {test_db}")
    
    try:
        conn = sqlite3.connect(test_db)
        
        # Check if mqtt_messages table exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mqtt_messages'")
        table_exists = cursor.fetchone()
        print(f"📋 mqtt_messages table exists: {table_exists is not None}")
        
        if table_exists:
            # Count total messages
            cursor.execute("SELECT COUNT(*) FROM mqtt_messages")
            total_messages = cursor.fetchone()[0]
            print(f"📨 Total messages in database: {total_messages}")
            
            # Check for CCU topics
            query = """
                SELECT DISTINCT topic, COUNT(*) as message_count
                FROM mqtt_messages 
                WHERE topic LIKE 'ccu/%' 
                   OR topic LIKE 'order/%' 
                   OR topic LIKE 'workflow/%'
                   OR topic LIKE 'state/%'
                   OR topic LIKE 'pairing/%'
                GROUP BY topic
                ORDER BY message_count DESC
            """
            
            print(f"\n🔍 Executing CCU query...")
            cursor.execute(query)
            ccu_topics = cursor.fetchall()
            
            print(f"✅ Found {len(ccu_topics)} CCU topics:")
            for topic, count in ccu_topics:
                print(f"   📡 {topic}: {count} messages")
            
            # Test sample message retrieval
            if ccu_topics:
                test_topic = ccu_topics[0][0]
                print(f"\n🔍 Testing sample retrieval for topic: {test_topic}")
                
                sample_query = """
                    SELECT payload, timestamp, session_label
                    FROM mqtt_messages 
                    WHERE topic = ?
                    ORDER BY timestamp DESC
                    LIMIT 3
                """
                
                cursor.execute(sample_query, (test_topic,))
                samples = cursor.fetchall()
                print(f"📄 Found {len(samples)} sample messages")
                
                for i, (payload, timestamp, session_label) in enumerate(samples):
                    print(f"   Sample {i+1}:")
                    print(f"     Timestamp: {timestamp}")
                    print(f"     Session: {session_label}")
                    print(f"     Payload: {payload[:100]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ccu_analysis()
