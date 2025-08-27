#!/usr/bin/env python3
"""
Test script for CCU analysis debugging
"""

import sys
import os
sys.path.append('src_orbis/mqtt/dashboard')

def test_ccu_analysis():
    """Test CCU analysis without full dashboard initialization"""
    
    # Import the method directly
    from aps_dashboard import APSDashboard
    
    # Create a minimal dashboard instance
    try:
        # Find a session database
        session_dir = "mqtt-data/sessions"
        if not os.path.exists(session_dir):
            print(f"❌ Session directory not found: {session_dir}")
            return
        
        db_files = [f for f in os.listdir(session_dir) if f.endswith('.db')]
        if not db_files:
            print(f"❌ No session databases found in {session_dir}")
            return
        
        # Use the first database
        test_db = os.path.join(session_dir, db_files[0])
        print(f"🔍 Testing with database: {test_db}")
        
        # Create dashboard instance
        dashboard = APSDashboard(db_file=test_db)
        
        print("🏭 Starting CCU analysis...")
        results = dashboard.analyze_ccu_topics()
        
        if results:
            print(f"✅ CCU analysis successful: {len(results)} topics found")
            for topic, data in results.items():
                print(f"  📡 {topic}: {data.get('message_count', 0)} messages")
        else:
            print("⚠️ No CCU topics found")
            
    except Exception as e:
        print(f"❌ CCU analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ccu_analysis()
