#!/usr/bin/env python3
"""
Integration Example: Auto-Refresh System

This script demonstrates the complete auto-refresh flow:
1. Start with Redis running
2. Simulate MQTT message processing
3. Show that refresh timestamp is updated
4. Show API endpoint working
"""

import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from omf2.backend.refresh import request_refresh, get_last_refresh
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def main():
    """Run the integration example"""
    print("\n" + "="*70)
    print("Auto-Refresh Integration Example")
    print("="*70 + "\n")
    
    # Check Redis connection
    print("1. Checking Redis connection...")
    result = request_refresh('test_group')
    if result:
        print("   ✅ Redis is available and working")
    else:
        print("   ⚠️  Redis is not available")
        print("   Please start Redis: docker run -d -p 6379:6379 redis:latest")
        return
    
    # Simulate MQTT message processing
    print("\n2. Simulating MQTT message processing...")
    groups = ['order_updates', 'module_updates', 'sensor_updates']
    
    for group in groups:
        success = request_refresh(group, min_interval=1.0)
        timestamp = get_last_refresh(group)
        print(f"   Group '{group}': timestamp={timestamp:.2f}, success={success}")
    
    # Test throttling
    print("\n3. Testing throttle (should be throttled within 1 second)...")
    time.sleep(0.5)
    
    for group in groups:
        success = request_refresh(group, min_interval=1.0)
        status = "throttled" if not success else "updated"
        print(f"   Group '{group}': {status}")
    
    # Wait and test again
    print("\n4. Waiting 1 second and trying again...")
    time.sleep(1.0)
    
    for group in groups:
        success = request_refresh(group, min_interval=1.0)
        timestamp = get_last_refresh(group)
        status = "updated" if success else "throttled"
        print(f"   Group '{group}': {status}, timestamp={timestamp:.2f}")
    
    # Show all refresh groups
    print("\n5. All refresh groups in Redis:")
    from omf2.backend.refresh import get_all_refresh_groups
    all_groups = get_all_refresh_groups()
    for group in all_groups:
        timestamp = get_last_refresh(group)
        print(f"   - {group}: {timestamp:.2f}")
    
    print("\n" + "="*70)
    print("Integration example completed successfully!")
    print("="*70 + "\n")
    
    print("Next steps:")
    print("1. Start the API server: python -m omf2.backend.api_refresh")
    print("2. Test the API: curl 'http://localhost:5001/api/last_refresh?group=order_updates'")
    print("3. Open Streamlit UI and observe auto-refresh\n")


if __name__ == '__main__':
    main()
