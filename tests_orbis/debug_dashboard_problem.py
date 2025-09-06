#!/usr/bin/env python3
"""
Debug Script: Dashboard MQTT Problem
Simuliert das echte Problem aus dem Dashboard
"""

import sys
import os

# Add src_orbis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src_orbis"))


def debug_dashboard_problem():
    """Debuggt das Dashboard MQTT-Problem"""

    print("🔍 Dashboard MQTT Problem Debug")
    print("=" * 50)

    try:
        # ...existing code...
    except Exception as e:
        print(f"❌ Fehler beim Debuggen: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_dashboard_problem()
