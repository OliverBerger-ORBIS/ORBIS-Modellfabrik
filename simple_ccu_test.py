#!/usr/bin/env python3
"""
Simple test for CCU analysis method
"""

import sqlite3
from pathlib import Path

def simple_ccu_test():
    """Simple test without dashboard dependencies"""
    
    print("🔍 Simple CCU Test...")
    
    # Find session databases
    session_dir = Path("mqtt-data/sessions")
    db_files = list(session_dir.glob("*.db"))
    
    print(f"📊 Found {len(db_files)} database files")
    
    # Test first database
    if db_files:
        test_db = db_files[0]
        print(f"🔍 Testing: {test_db}")
        
        try:
            conn = sqlite3.connect(test_db)
            
            # Simple CCU query
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
            
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            print(f"✅ Query successful: {len(results)} topics found")
            for topic, count in results:
                print(f"   📡 {topic}: {count} messages")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    simple_ccu_test()
